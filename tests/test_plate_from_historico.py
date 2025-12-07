"""
Testes para criação do mapa da placa a partir do historico_analises.csv,
sem necessidade de login ou abertura da interface gráfica.

Estes testes focam na lógica de:
- leitura do CSV de histórico;
- construção do PlateModel;
- consistência entre a coluna `poco` e os poços do modelo;
- coerência básica de status e controles.
"""

from __future__ import annotations

from pathlib import Path
import importlib.util
from typing import Any

import pandas as pd


# ---------------------------------------------------------------------------
# Helpers para carregar o módulo teste_plate_viewer_historico.py dinamicamente
# ---------------------------------------------------------------------------


def load_historico_module() -> Any:
    """
    Carrega o módulo services/teste_plate_viewer_historico.py por caminho
    absoluto, sem depender de pacotes Python.

    Se este carregamento falhar, significa que:
    - a estrutura de pastas foi alterada; ou
    - o arquivo foi movido/renomeado.

    Nesse caso, ajuste o caminho abaixo para refletir a nova localização.
    """
    root_dir = Path(__file__).resolve().parents[1]  # pasta Integragal/
    module_path = root_dir / "services" / "teste_plate_viewer_historico.py"

    if not module_path.exists():
        raise FileNotFoundError(
            f"Não foi possível localizar {module_path}. "
            "Verifique se o arquivo teste_plate_viewer_historico.py "
            "continua em Integragal/services/."
        )

    spec = importlib.util.spec_from_file_location(
        "teste_plate_viewer_historico", module_path
    )
    if spec is None or spec.loader is None:
        raise ImportError(
            "Falha ao criar spec para teste_plate_viewer_historico. "
            "Verifique permissões e integridade do arquivo."
        )

    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_plate_model_and_constants():
    """
    Facilita o acesso ao PlateModel e às constantes de status definidas
    em teste_plate_viewer_historico.

    Se falhar, significa que a API interna do módulo foi alterada
    (por exemplo, renomearam PlateModel ou as constantes de status).
    """
    mod = load_historico_module()
    PlateModel = mod.PlateModel

    NEGATIVE = mod.NEGATIVE
    POSITIVE = mod.POSITIVE
    INCONCLUSIVE = mod.INCONCLUSIVE
    INVALID = mod.INVALID
    CONTROL_CN = mod.CONTROL_CN
    CONTROL_CP = mod.CONTROL_CP
    EMPTY = mod.EMPTY

    return (
        PlateModel,
        NEGATIVE,
        POSITIVE,
        INCONCLUSIVE,
        INVALID,
        CONTROL_CN,
        CONTROL_CP,
        EMPTY,
    )


def get_historico_csv_path() -> Path:
    """
    Retorna o caminho para reports/historico_analises.csv a partir da
    raiz do projeto.

    Se falhar, significa que o arquivo foi movido, renomeado ou não foi
    incluído no repositório.
    """
    root_dir = Path(__file__).resolve().parents[1]  # Integragal/
    csv_path = root_dir / "reports" / "historico_analises.csv"
    if not csv_path.exists():
        # fallback: alguns ambientes podem manter também em logs/
        alt_path = root_dir / "logs" / "historico_analises.csv"
        if alt_path.exists():
            return alt_path

        raise FileNotFoundError(
            f"Arquivo historico_analises.csv não encontrado em {csv_path} "
            f"nem em {alt_path}. Verifique se o arquivo foi movido ou excluído."
        )
    return csv_path


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------


def test_historico_csv_existe_e_tem_colunas_minimas():
    """
    Verifica se o arquivo historico_analises.csv existe e contém as colunas
    mínimas esperadas (poco, amostra, codigo, exame, arquivo_corrida).

    Se este teste falhar, o problema está na base de dados de histórico:
    - caminho incorreto;
    - arquivo ausente;
    - alteração nos nomes das colunas.
    """
    csv_path = get_historico_csv_path()
    df = pd.read_csv(csv_path, sep=";")

    required_cols = {"poco", "amostra", "codigo", "exame", "arquivo_corrida"}
    missing = required_cols.difference(df.columns)

    assert not missing, (
        "O arquivo historico_analises.csv não possui todas as colunas mínimas. "
        f"Faltando: {missing}. Verifique a geração do relatório de histórico "
        "ou ajuste as constantes COL_* em teste_plate_viewer_historico.py."
    )


def test_plate_model_carrega_wells_validos_a_partir_do_historico():
    """
    Garante que o PlateModel construído a partir do histórico:
    - contenha pelo menos 1 poço;
    - não crie poços com IDs fora do padrão 8x12 (A1..H12).

    Se falhar:
    - a lógica de parse da coluna `poco` (ROW_LABELS/COL_LABELS) pode ter sido
      alterada;
    - ou o CSV passou a ter valores inválidos/fora da placa sem tratamento.
    """
    (
        PlateModel,
        NEGATIVE,
        POSITIVE,
        INCONCLUSIVE,
        INVALID,
        CONTROL_CN,
        CONTROL_CP,
        EMPTY,
    ) = load_plate_model_and_constants()

    csv_path = get_historico_csv_path()
    model = PlateModel.from_historico_csv(str(csv_path), sep=";")

    # Deve haver ao menos 1 poço mapeado
    assert model.wells, (
        "PlateModel.from_historico_csv não carregou nenhum poço. "
        "Verifique se o CSV possui dados na coluna `poco` e se os filtros "
        "de exame/arquivo_corrida não estão eliminando tudo."
    )

    # Todos os IDs precisam estar no range A1..H12
    valid_rows = {"A", "B", "C", "D", "E", "F", "G", "H"}
    valid_cols = {str(i) for i in range(1, 13)}

    invalid_ids = []
    for well_id in model.wells.keys():
        if len(well_id) < 2:
            invalid_ids.append(well_id)
            continue
        row_label = well_id[0]
        col_label = well_id[1:]
        if row_label not in valid_rows or col_label not in valid_cols:
            invalid_ids.append(well_id)

    assert not invalid_ids, (
        "Foram encontrados poços com IDs fora do layout 8x12 (A1..H12): "
        f"{invalid_ids}. Isso indica problema na interpretação da coluna "
        "`poco` ou na validação de ROW_LABELS/COL_LABELS."
    )


def test_quantidade_de_pocos_modelo_vs_csv_filtrado():
    """
    Compara a quantidade de poços do PlateModel com o número de valores
    únicos válidos da coluna `poco` no CSV, considerando que a coluna
    pode conter múltiplos poços por linha (ex.: "A1+A2").

    Estratégia:
    - Considera apenas linhas com `arquivo_corrida` NÃO nulo.
    - Ordena por `data_hora_analise` para pegar o último arquivo_corrida real.
    - Filtra o DataFrame para esse arquivo_corrida.
    - Expande a coluna `poco`, dividindo por '+' (A1+A2 -> A1, A2).
    - Calcula o conjunto de poços válidos (A1..H12) do CSV filtrado.
    - Compara com o conjunto de poços presentes no PlateModel.
    """
    PlateModel, *_ = load_plate_model_and_constants()
    csv_path = get_historico_csv_path()

    df = pd.read_csv(csv_path, sep=";")

    if "data_hora_analise" not in df.columns or "arquivo_corrida" not in df.columns:
        raise AssertionError(
            "O CSV de histórico não possui as colunas 'data_hora_analise' "
            "e/ou 'arquivo_corrida', necessárias para identificar a corrida mais recente."
        )

    # Mantém só linhas com arquivo_corrida preenchido
    df_non_null = df[df["arquivo_corrida"].notna()].copy()
    if df_non_null.empty:
        pytest.skip(
            "Não há linhas com 'arquivo_corrida' preenchido no CSV; "
            "não é possível comparar modelo vs CSV para uma corrida específica."
        )

    # Ordena por data/hora e pega o último arquivo_corrida REAL (não NaN)
    df_sorted = df_non_null.sort_values("data_hora_analise")
    last_run = str(df_sorted["arquivo_corrida"].iloc[-1])

    df_run = df_sorted[df_sorted["arquivo_corrida"] == last_run].copy()

    valid_rows = {"A", "B", "C", "D", "E", "F", "G", "H"}
    valid_cols = {str(i) for i in range(1, 13)}

    expanded_wells = set()

    for raw in df_run["poco"].dropna().astype(str):
        # Remove espaços e divide grupos "A1+A2" em ["A1", "A2"]
        tokens = raw.replace(" ", "").split("+")
        for token in tokens:
            if len(token) < 2:
                continue
            row = token[0].upper()
            col = token[1:]
            if row in valid_rows and col in valid_cols:
                expanded_wells.add(row + col)

    expected_unique_wells = expanded_wells

    model = PlateModel.from_historico_csv(str(csv_path), sep=";")
    model_wells = set(model.wells.keys())

    assert model_wells == expected_unique_wells, (
        "Diferença entre os poços carregados no PlateModel e os poços válidos "
        "presentes no CSV (já expandidos a partir de 'poco' com múltiplos poços "
        "e filtrados para o arquivo_corrida mais recente).\n"
        f"Arquivo_corrida mais recente (não nulo): {last_run}\n"
        f"Esperados (do CSV): {len(expected_unique_wells)} poços\n"
        f"No modelo: {len(model_wells)} poços\n"
        f"Wells faltando no modelo: {expected_unique_wells - model_wells}\n"
        f"Wells que sobram no modelo: {model_wells - expected_unique_wells}"
    )


def test_status_e_controles_sao_coerentes():
    """
    Verifica apenas coerência básica de status:

    - Poços marcados como controle (is_control=True) devem receber status
      CONTROL_CN, CONTROL_CP ou INVALID.
    - Poços não controle devem ter status em {NEGATIVE, POSITIVE,
      INCONCLUSIVE, INVALID}.

    Se falhar, indica que a regra de _recompute_status foi alterada ou que
    há estados inesperados sendo atribuídos aos poços.
    """
    (
        PlateModel,
        NEGATIVE,
        POSITIVE,
        INCONCLUSIVE,
        INVALID,
        CONTROL_CN,
        CONTROL_CP,
        EMPTY,
    ) = load_plate_model_and_constants()

    csv_path = get_historico_csv_path()
    model = PlateModel.from_historico_csv(str(csv_path), sep=";")

    allowed_status_controls = {CONTROL_CN, CONTROL_CP, INVALID}
    allowed_status_samples = {NEGATIVE, POSITIVE, INCONCLUSIVE, INVALID}

    invalid_controls = []
    invalid_samples = []

    for wid, wd in model.wells.items():
        if wd.is_control:
            if wd.status not in allowed_status_controls:
                invalid_controls.append((wid, wd.status, wd.metadata))
        else:
            if wd.status not in allowed_status_samples:
                invalid_samples.append((wid, wd.status, wd.metadata))

    assert not invalid_controls, (
        "Foram encontrados poços de controle com status inesperado. "
        "Verifique a lógica de _detect_control_type e _recompute_status.\n"
        f"Controles problemáticos: {invalid_controls}"
    )

    assert not invalid_samples, (
        "Foram encontrados poços de amostra com status fora do conjunto "
        "{NEGATIVE, POSITIVE, INCONCLUSIVE, INVALID}. "
        "Verifique a lógica de _recompute_status.\n"
        f"Amostras problemáticas: {invalid_samples}"
    )


def test_filtros_por_exame_e_arquivo_corrida():
    """
    Valida se os filtros opcionais `exame` e `arquivo_corrida` em
    PlateModel.from_historico_csv estão sendo aplicados de forma coerente.

    Estratégia:
    - Escolhe um (exame, arquivo_corrida) existentes no CSV.
    - Aplica manualmente o filtro via pandas.
    - Compara quantos poços são criados pelo PlateModel com a quantidade
      de poços válidos para esse filtro no CSV.

    Se falhar, indica que a implementação dos filtros no método de classe
    está divergindo do comportamento esperado.
    """
    PlateModel, *_ = load_plate_model_and_constants()
    csv_path = get_historico_csv_path()
    df = pd.read_csv(csv_path, sep=";")

    # Pega a primeira combinação válida (exame, arquivo_corrida)
    df_valid_pairs = df.dropna(subset=["exame", "arquivo_corrida"])
    if df_valid_pairs.empty:
        # Se não houver pares válidos, o teste não faz sentido
        # e deve ser ajustado conforme o formato do CSV.
        return

    first_row = df_valid_pairs.iloc[0]
    exame = str(first_row["exame"])
    arquivo_corrida = str(first_row["arquivo_corrida"])

    # Filtro manual no DataFrame
    df_filtered = df[
        (df["exame"] == exame) & (df["arquivo_corrida"] == arquivo_corrida)
    ].copy()

    df_filtered = df_filtered[df_filtered["poco"].astype(str).str.len() >= 2]
    df_filtered["row"] = df_filtered["poco"].str[0].str.upper()
    df_filtered["col"] = df_filtered["poco"].str[1:]

    valid_rows = {"A", "B", "C", "D", "E", "F", "G", "H"}
    valid_cols = {str(i) for i in range(1, 13)}
    df_filtered = df_filtered[
        df_filtered["row"].isin(valid_rows) & df_filtered["col"].isin(valid_cols)
    ]

    expected_wells = set(df_filtered["row"] + df_filtered["col"])

    # Carrega pelo PlateModel com filtros
    model = PlateModel.from_historico_csv(
        str(csv_path),
        sep=";",
        exame=exame,
        arquivo_corrida=arquivo_corrida,
    )
    model_wells = set(model.wells.keys())

    assert model_wells == expected_wells, (
        "Divergência entre o filtro manual (pandas) e o filtro aplicado por "
        "PlateModel.from_historico_csv.\n"
        f"Exame: {exame} | Arquivo corr.: {arquivo_corrida}\n"
        f"Esperados do CSV: {len(expected_wells)} poços\n"
        f"No modelo: {len(model_wells)} poços\n"
        f"Wells faltando no modelo: {expected_wells - model_wells}\n"
        f"Wells extras no modelo: {model_wells - expected_wells}"
    )

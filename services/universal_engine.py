from __future__ import annotations

"""
services.universal_engine
-------------------------

Motor universal de análise para o Integragal.

Responsabilidades principais:
- Garantir o fluxo completo de análise, a partir de:
    * Metadados de exame, equipamento, placa e regras de análise.
    * Arquivo de resultados da corrida (exportado pelo equipamento).
    * Gabarito de extração (mapa da placa) armazenado no AppState.
- Ler e normalizar o arquivo de resultados.
- Integrar com o gabarito de extração (amostra ↔ poço ↔ RP_1/RP_2).
- Aplicar as regras de CT, RP e interpretação parametrizadas.
- Determinar o status da corrida (controles CN/CP).
- Devolver um DataFrame padronizado e metadados da corrida.

A lógica de RP e controles é inspirada e simplificada a partir de
analise/vr1e2_biomanguinhos_7500.py, mas parametrizada por metadados
e amarrada ao gabarito de extração.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


@dataclass
class AnaliseContexto:
    """
    Estrutura de contexto para análise universal.
    Reúne todos os parâmetros necessários em um único objeto.
    """

    app_state: Any
    exame: str
    config_exame: Dict[str, str]
    config_placa: Dict[str, str]
    config_equip: Dict[str, str]
    config_regras: Dict[str, str]
    caminho_arquivo_corrida: str


# ---------------------------------------------------------------------------
# Função principal
# ---------------------------------------------------------------------------


def executar_analise_universal(
    contexto: AnaliseContexto,
) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Função principal do motor universal.

    1. Lê e normaliza o arquivo de corrida com base em config_equip.
    2. Integra com o gabarito de extração (se disponível).
    3. Aplica regras de CT/RP e interpretação com base em config_regras.
    4. Determina o status da corrida (usando controles CN/CP).
    5. Retorna DataFrame final e metadados da corrida.
    """
    df_norm = _ler_e_normalizar_arquivo(contexto)
    df_norm = _integrar_com_gabarito_extracao(df_norm, contexto)
    df_interpretado = _aplicar_regras_ct_e_interpretacao(df_norm, contexto)
    df_final, meta = _determinar_status_corrida(
        df_interpretado, contexto, df_norm=df_norm
    )
    return df_final, meta


# ---------------------------------------------------------------------------
# Etapa 1 – Leitura e normalização do arquivo
# ---------------------------------------------------------------------------


def _ler_e_normalizar_arquivo(contexto: AnaliseContexto) -> pd.DataFrame:
    """
    Etapa 1 – Leitura e normalização do arquivo.

    - Verifica tipo_arquivo a partir de config_equip.
    - Lê o arquivo com a biblioteca adequada.
    - Valida características do arquivo com base em config_equip
      (caracteristica_1/celula_caracteristica_1, etc.).
    - Renomeia/seleciona colunas para um formato padronizado:
        * well
        * sample_name
        * target_name
        * ct
    """
    tipo_arquivo = (contexto.config_equip.get("tipo_arquivo") or "").lower().strip()
    caminho = contexto.caminho_arquivo_corrida

    if not tipo_arquivo:
        raise ValueError("tipo_arquivo não definido em equipamentos_metadata.csv")

    # Leitura bruta do arquivo
    if tipo_arquivo == "csv":
        df_raw = pd.read_csv(caminho)
    elif tipo_arquivo in ("xlsx", "xls"):
        df_raw = pd.read_excel(caminho)
    else:
        raise ValueError(
            f"Tipo de arquivo '{tipo_arquivo}' não suportado para o equipamento."
        )

    # Validação das características 1 e 2 definidas em config_equip
    _validar_caracteristicas_arquivo(df_raw, contexto.config_equip)

    # Normalização de colunas com base em config_equip
    col_poco = (contexto.config_equip.get("coluna_poco") or "").strip()
    col_amostra = (contexto.config_equip.get("coluna_amostra") or "").strip()
    col_alvo = (contexto.config_equip.get("coluna_alvo") or "").strip()
    col_ct = (contexto.config_equip.get("coluna_ct") or "").strip()

    for nome, col in [
        ("coluna_poco", col_poco),
        ("coluna_amostra", col_amostra),
        ("coluna_alvo", col_alvo),
        ("coluna_ct", col_ct),
    ]:
        if not col:
            raise ValueError(
                f"{nome} não definido em equipamentos_metadata.csv para o equipamento."
            )

        if col not in df_raw.columns:
            raise ValueError(
                f"Coluna '{col}' (configurada em {nome}) não encontrada no arquivo de corrida."
            )

    df_norm = pd.DataFrame()
    df_norm["well"] = df_raw[col_poco]
    df_norm["sample_name"] = df_raw[col_amostra]
    df_norm["target_name"] = df_raw[col_alvo]
    df_norm["ct_raw"] = df_raw[col_ct]

    # Normalização de valores especiais de CT (UNDETERMINED, NA, vazios, etc.)
    df_norm["ct"] = _normalizar_ct(df_norm["ct_raw"])

    return df_norm


def _validar_caracteristicas_arquivo(
    df_raw: pd.DataFrame, config_equip: Dict[str, str]
) -> None:
    """
    Verifica as características 1 e 2 definidas em equipamentos_metadata.

    Convenção adotada:
    - Se celula_caracteristica_X começar com "HEADER:", exige que a coluna exista
      no cabeçalho do arquivo.
    """
    pares: List[Tuple[str, str]] = [
        (
            config_equip.get("caracteristica_1") or "",
            config_equip.get("celula_caracteristica_1") or "",
        ),
        (
            config_equip.get("caracteristica_2") or "",
            config_equip.get("celula_caracteristica_2") or "",
        ),
    ]

    for descricao, celula in pares:
        if not descricao or not celula:
            continue

        celula = celula.strip()
        if celula.upper().startswith("HEADER:"):
            col_name = celula.split("HEADER:", 1)[1].strip()
            if col_name and col_name not in df_raw.columns:
                raise ValueError(
                    f"Característica de arquivo não atendida: esperada coluna '{col_name}'. "
                    f"Descrição: {descricao}"
                )


def _normalizar_ct(series_ct: pd.Series) -> pd.Series:
    """
    Converte valores especiais (UNDETERMINED, NA, etc.) em None/NaN
    e transforma valores numéricos em float.
    """

    def conv(x: Any) -> Any:
        if x is None:
            return None
        s = str(x).strip().upper()
        if s in ("", "NA", "N/A", "UNDETERMINED", "UND"):
            return None
        try:
            return float(s.replace(",", "."))
        except ValueError:
            return None

    return series_ct.apply(conv)


# ---------------------------------------------------------------------------
# Integração com gabarito de extração
# ---------------------------------------------------------------------------


def _obter_gabarito_extracao(app_state: Any) -> Optional[pd.DataFrame]:
    """
    Tenta localizar o DataFrame de gabarito de extração no AppState.

    Para manter compatibilidade com versões anteriores do sistema, são
    testados vários nomes de atributo comuns. Se nada for encontrado,
    devolve None.
    """
    candidatos = [
        "df_gabarito_extracao",
        "gabarito_extracao",
        "df_mapa_extracao",
        "df_mapa_placa",
        "df_mapa_rodada",
    ]
    for nome in candidatos:
        df = getattr(app_state, nome, None)
        if isinstance(df, pd.DataFrame) and not df.empty:
            return df
    return None


def _integrar_com_gabarito_extracao(
    df_norm: pd.DataFrame, contexto: AnaliseContexto
) -> pd.DataFrame:
    """
    Integra o DataFrame normalizado de resultados (df_norm) com o
    gabarito de extração, amarrando explicitamente:
        amostra ↔ poços ↔ RP_1/RP_2

    Estratégia:
    - Localiza o DataFrame de gabarito no AppState.
    - Identifica a coluna de poço e a(s) coluna(s) de identificação
      da amostra no gabarito.
    - Faz merge de df_norm com o gabarito via coluna de poço.
    - Preserva o sample_name original em 'sample_name_raw' e substitui
      'sample_name' pelo valor vindo do gabarito (quando disponível).

    Isso replica de forma mais fiel o comportamento do script VR1/VR2,
    onde o mapa da placa é a fonte de verdade para a identidade das
    amostras, e o arquivo do equipamento traz apenas os sinais.
    """
    gabarito = _obter_gabarito_extracao(contexto.app_state)
    if gabarito is None or gabarito.empty:
        # Sem gabarito disponível: mantém comportamento anterior.
        return df_norm

    # Tentativa de identificação das colunas de poço e de amostra no gabarito
    cols_lower = {c: c.lower().strip() for c in gabarito.columns}

    # Colunas candidatas a representar o poço
    candidatos_poco = [
        c
        for c, lc in cols_lower.items()
        if lc in ("well", "poço", "poco", "poc", "posicao", "posição", "position")
        or "poço" in lc
        or "poco" in lc
    ]

    # Colunas candidatas a representar a identificação da amostra
    candidatos_amostra = [
        c
        for c, lc in cols_lower.items()
        if any(
            tok in lc
            for tok in (
                "amostra",
                "sample",
                "código",
                "codigo",
                "id",
                "identificacao",
                "identificação",
            )
        )
    ]

    if not candidatos_poco or not candidatos_amostra:
        # Estrutura do gabarito não é reconhecível -> não altera df_norm
        return df_norm

    col_poco_gab = candidatos_poco[0]
    col_amostra_gab = candidatos_amostra[0]

    # Prepara subconjunto do gabarito para merge
    gabarito_sub = gabarito[[col_poco_gab, col_amostra_gab]].copy()
    gabarito_sub.columns = ["well", "sample_name_gab"]

    # Normaliza a coluna de poço do gabarito para string maiúscula, como df_norm
    gabarito_sub["well"] = gabarito_sub["well"].astype(str).str.strip()

    df_norm_merge = df_norm.copy()
    df_norm_merge["well"] = df_norm_merge["well"].astype(str).str.strip()

    df_merged = df_norm_merge.merge(
        gabarito_sub,
        how="left",
        on="well",
    )

    # Preserva o sample_name original e substitui por aquele do gabarito, se existir
    df_merged["sample_name_raw"] = df_merged["sample_name"]
    df_merged["sample_name"] = df_merged["sample_name_gab"].combine_first(
        df_merged["sample_name"]
    )

    # Mantém a coluna de poço e descarta a auxiliar
    df_merged = df_merged.drop(columns=["sample_name_gab"])

    return df_merged


# ---------------------------------------------------------------------------
# Etapa 2 – Aplicação das regras de CT/RP e interpretação
# ---------------------------------------------------------------------------


def _aplicar_regras_ct_e_interpretacao(
    df_norm: pd.DataFrame,
    contexto: AnaliseContexto,
) -> pd.DataFrame:
    """
    Aplica regras de CT e interpretação com base em config_regras.

    Lógica inspirada em vr1e2_biomanguinhos_7500:
    - RP funciona como gate de validade da amostra (se RP fora da faixa, alvo fica 'Invalido').
    - Se RP válido e não houver CT para o alvo, interpretamos como 'Nao Detectado'.
    - CT dentro de CT_DETECTAVEL_MAX -> 'Detectado'.
    - CT entre CT_INCONCLUSIVO_MIN e CT_INCONCLUSIVO_MAX -> 'Inconclusivo'.
    - Fora dessas faixas -> 'Nao Detectado'.

    Foi adotada uma abordagem consolidada de RP por amostra, usando média de RP/RP_1/RP_2.
    """
    cfg = contexto.config_regras

    def as_float(key: str, default: float) -> float:
        try:
            v = (cfg.get(key) or "").replace(",", ".")
            return float(v)
        except Exception:
            return default

    ct_detect_min = as_float("CT_DETECTAVEL_MIN", 0.0)
    ct_detect_max = as_float("CT_DETECTAVEL_MAX", 40.0)
    ct_inconc_min = as_float("CT_INCONCLUSIVO_MIN", 40.01)
    ct_inconc_max = as_float("CT_INCONCLUSIVO_MAX", 45.0)
    ct_rp_min = as_float("CT_RP_MIN", 0.0)
    ct_rp_max = as_float("CT_RP_MAX", 45.0)

    alvos_str = cfg.get("alvos") or ""
    alvos = [a.strip() for a in alvos_str.split(";") if a.strip()]
    # Remove RP da lista de alvos de relatório
    alvos_sem_rp = [a for a in alvos if a.upper() not in ("RP", "RP_1", "RP_2")]

    # --- RP por amostra (média de RP/RP_1/RP_2) ---
    df_rp = df_norm[
        df_norm["target_name"].astype(str).str.upper().isin(["RP", "RP_1", "RP_2"])
    ]
    rp_por_amostra: Dict[str, float] = {}
    if not df_rp.empty:
        for amostra, sub in df_rp.groupby("sample_name"):
            vals = [v for v in sub["ct"].tolist() if v is not None]
            if vals:
                rp_por_amostra[amostra] = float(sum(vals) / len(vals))

    # --- CT por alvo, pivotado por amostra ---
    if not alvos_sem_rp:
        # nada a interpretar (configuração mínima para alvo não fornecida)
        return pd.DataFrame(columns=["sample_name"])

    df_targets = df_norm[
        df_norm["target_name"]
        .astype(str)
        .str.upper()
        .isin([t.upper() for t in alvos_sem_rp])
    ].copy()

    if df_targets.empty:
        # sem linhas de alvo, mas ainda assim devolve estrutura mínima
        return pd.DataFrame(columns=["sample_name"])

    df_targets["target_upper"] = df_targets["target_name"].astype(str).str.upper()

    pivot_ct = df_targets.pivot_table(
        index="sample_name",
        columns="target_upper",
        values="ct",
        aggfunc="first",
    )

    resultados: List[Dict[str, Any]] = []
    for amostra, row in pivot_ct.iterrows():
        linha_res: Dict[str, Any] = {"sample_name": amostra}
        ct_rp = rp_por_amostra.get(amostra)

        for target_upper in row.index:
            ct_val = row[target_upper]
            alvo_label = target_upper.replace(" ", "")
            coluna_resultado = f"Resultado_{alvo_label}"

            resultado = _interpretar_com_rp(
                ct_rp=ct_rp,
                ct_alvo=ct_val,
                ct_detect_min=ct_detect_min,
                ct_detect_max=ct_detect_max,
                ct_inconc_min=ct_inconc_min,
                ct_inconc_max=ct_inconc_max,
                ct_rp_min=ct_rp_min,
                ct_rp_max=ct_rp_max,
            )
            linha_res[coluna_resultado] = resultado

        resultados.append(linha_res)

    df_res = pd.DataFrame(resultados)
    return df_res


def _interpretar_com_rp(
    ct_rp: Any,
    ct_alvo: Any,
    ct_detect_min: float,
    ct_detect_max: float,
    ct_inconc_min: float,
    ct_inconc_max: float,
    ct_rp_min: float,
    ct_rp_max: float,
) -> str:
    """
    Interpreta o resultado de um alvo considerando o RP da amostra.

    Regras:
    - Se RP ausente ou fora da faixa [CT_RP_MIN, CT_RP_MAX] -> "Invalido".
    - Se RP ok e alvo sem CT -> "Nao Detectado".
    - Se RP ok e CT <= CT_DETECTAVEL_MAX -> "Detectado".
    - Se RP ok e CT em [CT_INCONCLUSIVO_MIN, CT_INCONCLUSIVO_MAX] -> "Inconclusivo".
    - Caso contrário -> "Nao Detectado".
    """
    # Gate de RP
    if ct_rp is None:
        return "Invalido"
    try:
        valor_rp = float(ct_rp)
    except Exception:
        return "Invalido"

    if not (ct_rp_min <= valor_rp <= ct_rp_max):
        return "Invalido"

    # RP válido; agora interpreta alvo
    if ct_alvo is None:
        return "Nao Detectado"

    try:
        valor_ct = float(ct_alvo)
    except Exception:
        return "Nao Detectado"

    # Notar que CT_DETECTAVEL_MIN é mantido para futura sofisticação;
    # aqui seguimos a lógica do VR1/VR2 (limite superior).
    if valor_ct <= ct_detect_max:
        return "Detectado"

    if ct_inconc_min <= valor_ct <= ct_inconc_max:
        return "Inconclusivo"

    return "Nao Detectado"


# ---------------------------------------------------------------------------
# Etapa 3 – Determinação do status da corrida (CN/CP)
# ---------------------------------------------------------------------------


def _determinar_status_corrida(
    df_interpretado: pd.DataFrame,
    contexto: AnaliseContexto,
    df_norm: pd.DataFrame,
) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Determina o status da corrida com base em critérios parametrizados.

    Lógica inspirada em vr1e2_biomanguinhos_7500:
    - Usa controles CN (negativo) e CP (positivo), detectados por
      substring do nome da amostra (contendo 'CN' ou 'CP').
    - Usa o alvo principal (primeiro da lista de `alvos`) para avaliar
      os controles.
    - Regras simplificadas:
        * Se faltarem CN ou CP -> "Invalida (Controles Ausentes)"
        * Se CN tiver CT detectável -> "Invalida (CN Detectado)"
        * Se CP fora da faixa detectável -> "Invalida (CP Fora do Intervalo)"
        * Caso contrário -> "Valida"
    """
    cfg = contexto.config_regras

    def as_float(key: str, default: float) -> float:
        try:
            v = (cfg.get(key) or "").replace(",", ".")
            return float(v)
        except Exception:
            return default

    ct_detect_min = as_float("CT_DETECTAVEL_MIN", 0.0)
    ct_detect_max = as_float("CT_DETECTAVEL_MAX", 40.0)

    alvos_str = cfg.get("alvos") or ""
    alvos = [a.strip() for a in alvos_str.split(";") if a.strip()]
    alvo_principal = alvos[0] if alvos else None

    # Caso extremo: sem resultados ou sem alvo principal configurado
    if df_norm.empty or alvo_principal is None:
        status_corrida = "Invalida (sem resultados)"
        meta = {
            "status_corrida": status_corrida,
            "exame": contexto.exame,
            "equipamento": contexto.config_exame.get("equipamento", ""),
        }
        df_final = df_interpretado.copy()
        df_final["Status_Corrida"] = status_corrida
        return df_final, meta

    # Helpers para achar CT de CN/CP para o alvo principal
    alvo_upper = alvo_principal.upper()

    def _ct_controle(tag: str) -> Any:
        mask_ctrl = (
            df_norm["sample_name"].astype(str).str.contains(tag, case=False, na=False)
        )
        mask_tgt = df_norm["target_name"].astype(str).str.upper() == alvo_upper
        sub = df_norm[mask_ctrl & mask_tgt]
        vals = [v for v in sub["ct"].tolist() if v is not None]
        return vals[0] if vals else None

    ct_cn = _ct_controle("CN")
    ct_cp = _ct_controle("CP")

    # Avaliação dos controles
    if ct_cn is None or ct_cp is None:
        status_corrida = "Invalida (Controles Ausentes)"
    else:
        try:
            v_cn = float(ct_cn)
        except Exception:
            v_cn = None
        try:
            v_cp = float(ct_cp)
        except Exception:
            v_cp = None

        if v_cn is not None and v_cn <= ct_detect_max:
            status_corrida = "Invalida (CN Detectado)"
        elif v_cp is None or not (ct_detect_min <= v_cp <= ct_detect_max):
            status_corrida = "Invalida (CP Fora do Intervalo)"
        else:
            status_corrida = "Valida"

    meta = {
        "status_corrida": status_corrida,
        "exame": contexto.exame,
        "equipamento": contexto.config_exame.get("equipamento", ""),
    }

    df_final = df_interpretado.copy()
    if not df_final.empty:
        df_final["Status_Corrida"] = status_corrida
    else:
        df_final = pd.DataFrame({"Status_Corrida": [status_corrida]})

    return df_final, meta

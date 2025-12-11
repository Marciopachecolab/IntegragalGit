import os

import uuid

from datetime import datetime

from pathlib import Path

from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from services.exam_registry import get_exam_cfg

def _map_result(val: any) -> str:

    """Converte resultado textual em código padronizado "1" (Detectado), "2" (Não Detectado), "3" (Inconclusivo).

    A lógica é alinhada ao visualizador de placa:

        1 -> Detectado / positivo / reagente

        2 -> Não detectado / negativo

        3 -> Inconclusivo

    """

    if val is None:

        return ""

    try:

        if isinstance(val, float) and pd.isna(val):

            return ""

    except Exception:

        pass

    s = str(val).strip().lower()

    # Se já vier em formato "ALVO - 1/2/3" ou apenas "1/2/3"

    if " - " in s:

        parts = s.split(" - ")

        last = parts[-1].strip()

        if last in {"1", "2", "3"}:

            return last

    if s in {"1", "2", "3"}:

        return s

    # Mapeia por palavras-chave

    if any(k in s for k in ["inc", "incon"]):

        return "3"

    if ("nao" in s or "não" in s) and "detect" in s:

        return "2"

    if any(k in s for k in ["neg", "nd"]):

        return "2"

    if any(k in s for k in ["det", "pos", "reag"]):

        return "1"

    # inválido / falha não recebe código numérico

    if "inv" in s:

        return ""

    return ""

def _fmt_ct(val: any) -> str:

    """Formata CT em string com 3 casas decimais; vazio se None/NaN/Undetermined."""

    if val is None:

        return ""

    try:

        if isinstance(val, float) and pd.isna(val):

            return ""

    except Exception:

        pass

    try:

        if isinstance(val, str) and val.strip().upper() == "UNDETERMINED":

            return ""

        f = float(val)

        return f"{f:.3f}".replace(".", ",")

    except Exception:

        return str(val)

def gerar_historico_csv(

    df_final: pd.DataFrame,

    exame: str,

    usuario: str,

    lote: str = "",

    arquivo_corrida: str = "",

    caminho_csv: str = "logs/historico_analises.csv",

) -> None:

    """

    Versão evoluída que gera/atualiza o histórico de análises em CSV (append).



    Melhorias:

    - âœ… Suporta QUALQUER exame (VR1e2, ZDC, VR1, VR2, etc.)

    - âœ… Gera UUID único (id_registro) para cada linha

    - âœ… Inicializa campos de rastreamento GAL (data_hora_envio, usuario_envio, sucesso_envio, detalhes_envio)

    - âœ… Status_gal muda para "não enviado" ou "não enviável"

    - âœ… Suporta colunas dinâmicas conforme alvos do exame

    """

    cfg = get_exam_cfg(exame)



    if cfg is None:

        raise ValueError(f"Exame '{exame}' não encontrado no registry")

    # Normaliza dataframe de entrada
    df_final = df_final.copy()

    # Propaga nome do arquivo de corrida
    if arquivo_corrida:
        try:
            df_final["arquivo_corrida"] = Path(arquivo_corrida).name
        except Exception:
            df_final["arquivo_corrida"] = str(arquivo_corrida)
    elif "arquivo_corrida" in df_final.columns:
        try:
            df_final["arquivo_corrida"] = df_final["arquivo_corrida"].apply(
                lambda x: Path(x).name if x else x
            )
        except Exception:
            pass

    def _norm(nome: str) -> str:

        return str(nome).lower().replace(" ", "").replace("_", "")

    cols_norm_map = {_norm(c): c for c in df_final.columns}

    def _find_ct_col(base: str) -> str | None:

        """Encontra a coluna de CT correspondente a um alvo/base.

        Usa nomes com e sem espaço, com sufixo/prefixo "CT" e variaçÃµes simples.

        """

        if not base:

            return None

        base = str(base).strip()

        base_ns = base.replace(" ", "")

        candidatos = [

            base,

            base_ns,

            base.upper(),

            base.lower(),

            base.replace(" ", "_"),

            f"{base} - CT",

            f"{base_ns} - CT",

            f"CT_{base}",

            f"CT_{base_ns}",

            f"{base}_CT",

            f"{base_ns}_CT",

        ]

        for cand in candidatos:

            norm_cand = _norm(cand)

            if norm_cand in cols_norm_map:

                return cols_norm_map[norm_cand]

        return None

    # monta targets (Resultado_<ALVO_NO_SPACE>, coluna de CT correspondente)

    targets: List[Tuple[str, str]] = []

    for alvo in cfg.alvos:

        try:

            alvo_norm = cfg.normalize_target(alvo)

        except Exception:

            alvo_norm = alvo

        alvo_no_space = str(alvo_norm).replace(" ", "")

        col_res = f"Resultado_{alvo_no_space}"

        ct_found = _find_ct_col(alvo_norm) or _find_ct_col(alvo_no_space)

        targets.append((col_res, ct_found))

    # inclui demais colunas Resultado_* que aparecerem no df_final

    resultado_cols = [c for c in df_final.columns if str(c).startswith("Resultado_")]

    alvos_existentes = {t[0] for t in targets}

    for col_res in resultado_cols:

        if col_res in alvos_existentes:

            continue

        base = col_res[len("Resultado_") :].strip()

        ct_found = _find_ct_col(base)

        targets.append((col_res, ct_found))

        alvos_existentes.add(col_res)

    # RPs - Procurar por CT_RP_1, CT_RP_2, etc.

    extra_ct = []

    from utils.logger import registrar_log
    registrar_log("History Debug", f"Procurando colunas RP no DataFrame...", "DEBUG")
    registrar_log("History Debug", f"Colunas do DataFrame: {df_final.columns.tolist()}", "DEBUG")

    for col in df_final.columns:

        up = str(col).upper()
        
        # Procura por CT_RP_1, CT_RP_2, Resultado_RP_1, Resultado_RP_2, etc.
        if "_RP_" in up or up.startswith("CT_RP") or up.startswith("RESULTADO_RP"):
            registrar_log("History Debug", f"  RP ENCONTRADO: '{col}' (upper='{up}')", "INFO")
            extra_ct.append(col)

    linhas = []

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for _, r in df_final.iterrows():

        codigo = str(r.get("Codigo", "")).strip()

        amostra = str(r.get("Amostra", "")).strip()

        poco = str(r.get("Poco", "")).strip()

        status_corrida = str(r.get("Status_Corrida", "")).strip()

        # preserva arquivo_corrida vindo da linha se não foi passado

        arq_corrida = arquivo_corrida or str(r.get("arquivo_corrida", "")).strip()

        # âœ… NOVO: Gera UUID único para cada registro

        id_registro = str(uuid.uuid4())



        status_gal = "não enviado"  # âœ… NOVO: Status padrão melhorado

        mensagem_gal = ""

        cod_lower = codigo.lower()

        if (not codigo.isdigit()) or ("cn" in cod_lower) or ("cp" in cod_lower):

            status_gal = "não enviável"  # âœ… NOVO: Nome normalizado

            mensagem_gal = "Código não numérico ou controle"  # âœ… NOVO: Mensagem melhorada

        # âœ… NOVA ESTRUTURA: Com UUID e campos de rastreamento GAL

        linha = {

            # Identificação (novo)

            "id_registro": id_registro,



            # Rastreabilidade de análise

            "data_hora_analise": timestamp,

            "usuario_analise": usuario,

            "exame": exame,

            "lote": lote or "",

            "arquivo_corrida": arq_corrida or "",



            # Dados da amostra

            "poco": poco,

            "amostra": amostra,

            "codigo": codigo,

            "status_corrida": status_corrida,



            # Controle GAL

            "status_gal": status_gal,

            "mensagem_gal": mensagem_gal,

            "data_hora_envio": None,      # âœ… NOVO: Preenchido após envio

            "usuario_envio": None,         # âœ… NOVO: Preenchido após envio

            "sucesso_envio": None,         # âœ… NOVO: None=não enviável, False/True=resultado

            "detalhes_envio": "",          # âœ… NOVO: Resposta do servidor



            # Auditoria

            "criado_em": timestamp,

            "atualizado_em": timestamp,

        }

        # Resultados qualitativos e CTs

        for col_res, col_ct in targets:

            # extrai nome bruto (removendo prefixo Resultado_ quando presente)

            base_raw = str(col_res).replace("Resultado_", "").strip()

            try:

                base = cfg.normalize_target(base_raw)

            except Exception:

                base = base_raw

            res_val = r.get(col_res)

            res_code = _map_result(res_val)

            linha[f"{base} - R"] = f"{base} - {res_code}" if res_code else ""

            if col_ct and (col_ct in r):

                linha[f"{base} - CT"] = _fmt_ct(r.get(col_ct))

        # Extras de CT (RPs)

        from utils.logger import registrar_log
        registrar_log("History Debug", f"Extra_ct final para gravar: {extra_ct}", "DEBUG")

        for ct_col in extra_ct:

            if ct_col in r:
                ct_val = _fmt_ct(r.get(ct_col))
                # Limpar nome: CT_RP_1 -> RP_1, Resultado_RP_1 -> RP_1
                col_name = ct_col.replace("CT_", "").replace("Resultado_", "")
                linha[f"{col_name} - CT"] = ct_val
                registrar_log("History Debug", f"  Gravando: '{col_name} - CT' = {ct_val} (coluna original: {ct_col})", "DEBUG")
            else:
                registrar_log("History Debug", f"  AVISO: Coluna RP '{ct_col}' nao existe na linha!", "WARNING")

            # Resultado do RP (se existir)
            res_rp = r.get(f"Resultado_{ct_col}") or r.get(f"{ct_col} - R")
            if res_rp:
                res_code_rp = _map_result(res_rp)
                linha[f"{ct_col} - R"] = f"{ct_col} - {res_code_rp}" if res_code_rp else ""

        linhas.append(linha)

    if not linhas:

        return

    df_hist = pd.DataFrame(linhas)

    os.makedirs(os.path.dirname(caminho_csv), exist_ok=True)

    colunas_ordenadas = list(df_hist.columns)

    # âœ… NOVO: Se arquivo existe, verifica se precisa adicionar colunas faltantes
    csv_path_obj = Path(caminho_csv)

    if csv_path_obj.exists():

        df_existente = pd.read_csv(csv_path_obj, sep=";", encoding="utf-8")

        # Colunas que devem estar sempre presentes (mantém ordem definida pelo df_hist)
        colunas_esperadas = list(df_hist.columns)
        colunas_existentes = set(df_existente.columns)

        # Se faltam colunas no CSV (ex: primeira vez com novo exame)
        if colunas_existentes != set(colunas_esperadas):
            # Adiciona colunas faltantes no histórico anterior
            for col in colunas_esperadas:
                if col not in df_existente.columns:
                    df_existente[col] = None

        # Reordena: primeiro as esperadas, depois eventuais extras já existentes
        colunas_ordenadas = list(
            dict.fromkeys(colunas_esperadas + [c for c in df_existente.columns if c not in colunas_esperadas])
        )
        df_existente = df_existente.reindex(columns=colunas_ordenadas)

        # Escreve de novo
        df_existente.to_csv(
            csv_path_obj,
            sep=";",
            index=False,
            encoding="utf-8"
        )

    # Garante que df_hist siga a mesma ordem de colunas ao anexar
    df_hist = df_hist.reindex(columns=colunas_ordenadas, fill_value=None)

    # Escreve novas linhas

    header = not csv_path_obj.exists()

    df_hist.to_csv(caminho_csv, sep=";", index=False, mode="a", header=header, encoding="utf-8")

def atualizar_status_gal(

    csv_path: str,

    id_registros: List[str],

    sucesso: bool,

    usuario_envio: str,

    detalhes: str = ""

) -> Dict[str, Any]:

    """

    Atualiza status_gal de registros após envio para o GAL.



    Args:

        csv_path: Caminho do histórico CSV

        id_registros: Lista de IDs (UUIDs) para atualizar

        sucesso: True se envio foi bem-sucedido, False se falhou

        usuario_envio: Quem fez o envio

        detalhes: Mensagem de resposta/erro (opcional)



    Returns:

        Dict com estatísticas: {

            'sucesso': bool,

            'registros_atualizados': int,

            'registros_nao_encontrados': list,

            'timestamp': str,

            'status': str,

            'usuario': str

        }

    """



    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")



    try:

        # 1. Lê o CSV completo

        csv_path_obj = Path(csv_path)

        if not csv_path_obj.exists():

            raise FileNotFoundError(f"Arquivo não encontrado: {csv_path}")



        df = pd.read_csv(csv_path_obj, sep=";", encoding="utf-8")



        registros_atualizados = 0

        registros_nao_encontrados = []



        # 2. Para cada ID fornecido

        for id_reg in id_registros:

            mask = df["id_registro"] == id_reg



            if not mask.any():

                registros_nao_encontrados.append(id_reg)

                continue



            # 3. Atualiza campos de envio (com conversão de dtype)

            novo_status = "enviado" if sucesso else "falha no envio"

            df.loc[mask, "status_gal"] = novo_status

            df.loc[mask, "data_hora_envio"] = timestamp

            df.loc[mask, "usuario_envio"] = usuario_envio

            df.loc[mask, "sucesso_envio"] = str(sucesso)  # âœ… Converte para string

            df.loc[mask, "detalhes_envio"] = detalhes

            df.loc[mask, "atualizado_em"] = timestamp



            registros_atualizados += 1



        # 4. Escreve de volta (sobrescreve)

        df.to_csv(csv_path_obj, sep=";", index=False, encoding="utf-8")



        # 5. Resposta

        novo_status = "enviado" if sucesso else "falha no envio"

        resultado = {

            "sucesso": True,

            "registros_atualizados": registros_atualizados,

            "registros_nao_encontrados": registros_nao_encontrados,

            "timestamp": timestamp,

            "status": novo_status,

            "usuario": usuario_envio

        }



        return resultado



    except Exception as e:

        return {

            "sucesso": False,

            "erro": str(e),

            "registros_atualizados": 0,

            "registros_nao_encontrados": id_registros

        }


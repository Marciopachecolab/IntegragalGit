"""
MÃ“DULO OFICIAL para formatação GAL - ÚNICA FONTE DE VERDADE
======================================================================

âš ï¸ IMPORTANTE: Este é o ÚNICO módulo responsável por formatação GAL.
   NUNCA implemente lógica de formatação GAL em outros lugares.

RESPONSABILIDADES:
------------------
âœ… Formatar DataFrames de resultados para padrão GAL
âœ… Aplicar metadados de exames (exam_cfg) para mapeamento
âœ… Gerar painéis CSV para envio GAL
âœ… Validar formato de saída conforme especificação GAL

ARQUITETURA (FASE 2 - R8):
--------------------------
- Fonte: Movido de main.py para centralizar lógica GAL
- Usado por: ui/menu_handler.py, exportacao/envio_gal.py
- Depende de: services/exam_registry.py (metadados)

Este módulo centraliza a formatação de DataFrames de resultados para o padrão GAL,
utilizando metadados do exame (exam_cfg) para determinar mapeamento de colunas,
painéis, e alvos exportáveis.

Ver: RELATORIO_REDUNDANCIA_CONFLITOS.md (FASE 2, Etapa 2.1)
"""

import os
import unicodedata
import pandas as pd
from datetime import datetime
from services.system_paths import BASE_DIR
from services.exam_registry import get_exam_cfg


def formatar_para_gal(df, exam_cfg=None, exame: str | None = None):
    """
    Formata o resultado para layout GAL usando metadados do exame (registry).
    
    Args:
        df: DataFrame com resultados brutos
        exam_cfg: Configuração do exame (ExamConfig object) - opcional
        exame: Nome do exame para buscar configuração - opcional
        
    Returns:
        DataFrame formatado no padrão GAL com colunas:
        - codigoAmostra, codigo, requisicao, paciente, exame, metodo
        - registroInterno, kit, reteste, loteKit, dataProcessamentoFim
        - valorReferencia, observacao, painel, resultado
        - Colunas de alvos (influenzaa, influenzab, adenovirus, etc.)
    """
    cfg = exam_cfg or (get_exam_cfg(exame) if exame else get_exam_cfg(""))

    df_in = df.copy()
    for c in ["Unnamed: 0", "index"]:
        if c in df_in.columns:
            df_in = df_in.drop(columns=[c])

    def _strip_accents(txt: str) -> str:
        return (
            unicodedata.normalize("NFKD", txt)
            .encode("ASCII", "ignore")
            .decode("ASCII")
        )

    def _norm(col: str) -> str:
        col2 = str(col).strip()
        col2 = _strip_accents(col2)
        return col2.replace(" ", "_").lower()

    colmap = {_norm(c): c for c in df_in.columns}

    def _get(col_names, default=""):
        for name in col_names:
            key = _norm(name)
            if key in colmap:
                return df_in[colmap[key]]
        return pd.Series([default] * len(df_in))

    def _map_result(val):
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return ""
        s = str(val).strip().upper()
        
        # Aceita: "Det", "Detectado", "DETECTADO"
        if s in ("DET", "DETECTADO"):
            return "1"
        
        # Aceita: "ND", "Não Detectado", "NAO DETECTADO"
        if s in ("ND", "NÃƒO DETECTADO", "NAO DETECTADO"):
            return "2"
        
        # Aceita: "Inc", "Inconclusivo"
        if s in ("INC", "INCONCLUSIVO"):
            return "3"
        
        # Fallback para textos antigos
        if "INCONCL" in s:
            return "3"
        if ("NAO" in s or "NÃƒO" in s) and "DETECT" in s:
            return "2"
        if "DETECT" in s:
            return "1"
        
        return ""

    df_out = pd.DataFrame()
    cod_col = _get(["codigo", "amostra"])
    df_out["codigoAmostra"] = cod_col
    df_out["codigo"] = cod_col
    df_out["requisicao"] = ""
    df_out["paciente"] = ""
    df_out["exame"] = cfg.nome_exame or "VRSRT"
    df_out["metodo"] = "RTTR"
    df_out["registroInterno"] = cod_col
    df_out["kit"] = str(cfg.kit_codigo or "427")
    df_out["reteste"] = ""
    df_out["loteKit"] = ""
    df_out["dataProcessamentoFim"] = datetime.now().strftime("%d/%m/%Y")
    df_out["valorReferencia"] = ""
    df_out["observacao"] = ""
    df_out["painel"] = cfg.panel_tests_id or "1"
    df_out["resultado"] = ""

    export_fields = cfg.export_fields or []
    if not export_fields:
        export_fields = [
            "Influenzaa",
            "influenzab",
            "coronavirusncov",
            "adenovirus",
            "vsincicialresp",
            "metapneumovirus",
            "rinovirus",
        ]

    def _find_result_col(target_norm: str):
        """
        Procura coluna de resultado compatível com o analito exportado,
        usando alias para mapear nomes de painel (influenzaa, adenovirus, etc.)
        para os alvos internos (INF A, ADV, ...).
        """
        # aliases básicos painel -> alvo interno
        aliases = {
            "INFLUENZAA": "INF A",
            "INFLUENZAB": "INF B",
            "ADENOVIRUS": "ADV",
            "ADENOVÃRUS": "ADV",
            "METAPNEUMOVIRUS": "HMPV",
            "RINOVIRUS": "HRV",
            "RINOVÃRUS": "HRV",
            "SARS-COV-2": "SC2",
            "SARSCOV2": "SC2",
            "CORONAVIRUSNCOV": "SC2",
            # Vírus Sincicial Respiratório (VSR/RSV)
            "VSINCICIALRESP": "RSV",
            "VSINCICIALRESPA": "RSV",
            "VSINCICIALRESPB": "RSV",
            "VSR": "RSV",
        }
        # normaliza alvo exportado
        tnorm_raw = _strip_accents(target_norm).upper().replace("_", " ").replace("-", " ").strip()
        if tnorm_raw in aliases:
            tnorm_raw = aliases[tnorm_raw]
        # aplica normalize_target do exame (mapeia INFA -> INF A, etc.)
        tnorm = cfg.normalize_target(tnorm_raw).upper()

        def _clean(s: str) -> str:
            return (
                _strip_accents(s)
                .upper()
                .replace("RESULTADO", "")
                .replace("_", "")
                .replace(" ", "")
            )

        # tenta bater com colunas existentes
        for k, v in colmap.items():
            if _clean(k) == _clean(tnorm):
                return v
        # tenta prefácio Resultado_<alvo>
        cand = f"Resultado_{tnorm}"
        for k, v in colmap.items():
            if _clean(k) == _clean(cand):
                return v
        return None

    def _exportavel(code: str) -> bool:
        if not code:
            return False
        c = code.upper()
        # Usa lista de controles definida no exam_cfg quando disponível
        try:
            controles = cfg.controles or {"cn": [], "cp": []}
            cn_list = [str(x).upper() for x in (controles.get("cn") or [])]
            cp_list = [str(x).upper() for x in (controles.get("cp") or [])]
            # comparar igualdade ou substring para cobrir variaçÃµes como 'CN', 'CONTROLE N'
            for v in cn_list:
                if v and v in c:
                    return False
            for v in cp_list:
                if v and v in c:
                    return False
        except Exception:
            # fallback para checagem simples
            if "CN" in c or "CP" in c:
                return False
        # somente códigos numéricos são exportáveis
        return c.isdigit()

    export_mask = cod_col.apply(_exportavel)
    df_out = df_out.loc[export_mask].reset_index(drop=True)
    df_in = df_in.loc[export_mask].reset_index(drop=True)

    for analito in export_fields:
        alvo_norm = cfg.normalize_target(analito)
        res_col = _find_result_col(alvo_norm)
        
        # DEBUG: Log para diagnóstico
        from utils.logger import registrar_log
        registrar_log("GAL Debug", f"Procurando '{analito}' â†’ normalizado: '{alvo_norm}' â†’ coluna encontrada: '{res_col}'", "DEBUG")
        
        if res_col and res_col in df_in.columns:
            serie_res = df_in[res_col].apply(_map_result)
            registrar_log("GAL Debug", f"  â””â”€ Valores: {serie_res.value_counts().to_dict()}", "DEBUG")
        else:
            serie_res = pd.Series([""] * len(df_in))
            if res_col:
                registrar_log("GAL Debug", f"  â””â”€ AVISO: Coluna '{res_col}' não existe no DataFrame! Colunas disponíveis: {[c for c in df_in.columns if 'Resultado' in c]}", "WARNING")
            else:
                registrar_log("GAL Debug", f"  â””â”€ AVISO: Não encontrou coluna para '{alvo_norm}'", "WARNING")
        
        col_nome = _strip_accents(analito).replace(" ", "").replace("-", "").replace("_", "").lower()
        df_out[col_nome] = serie_res

    return df_out


def gerar_painel_csvs(df_resultados, exam_cfg=None, exame: str | None = None, output_dir: str | None = None):
    """
    Gera CSVs separados por painel (panel_tests_id) usando export_fields do exam_cfg.
    
    Cada painel recebe um CSV com:
    - Colunas padrão (codigoAmostra, codigo, etc.)
    - Apenas alvos de export_fields correspondentes ao painel
    
    Args:
        df_resultados: DataFrame com resultados brutos
        exam_cfg: Configuração do exame (ExamConfig object) - opcional
        exame: Nome do exame para buscar configuração - opcional
        output_dir: Diretório de saída (padrão: reports/)
        
    Returns:
        dict {panel_id: caminho_arquivo}
    """
    if output_dir is None:
        output_dir = os.path.join(BASE_DIR, "reports")
    os.makedirs(output_dir, exist_ok=True)
    
    cfg = exam_cfg or (get_exam_cfg(exame) if exame else get_exam_cfg(""))
    
    df_in = df_resultados.copy()
    for c in ["Unnamed: 0", "index"]:
        if c in df_in.columns:
            df_in = df_in.drop(columns=[c])
    
    def _strip_accents(txt: str) -> str:
        return (
            unicodedata.normalize("NFKD", txt)
            .encode("ASCII", "ignore")
            .decode("ASCII")
        )
    
    def _norm(col: str) -> str:
        col2 = str(col).strip()
        col2 = _strip_accents(col2)
        return col2.replace(" ", "_").lower()
    
    colmap = {_norm(c): c for c in df_in.columns}
    
    def _get(col_names, default=""):
        for name in col_names:
            key = _norm(name)
            if key in colmap:
                return df_in[colmap[key]]
        return pd.Series([default] * len(df_in))
    
    def _map_result(val):
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return ""
        s = str(val).strip().upper()
        
        # Aceita: "Det", "Detectado", "DETECTADO"
        if s in ("DET", "DETECTADO"):
            return "1"
        
        # Aceita: "ND", "Não Detectado", "NAO DETECTADO"
        if s in ("ND", "NÃƒO DETECTADO", "NAO DETECTADO"):
            return "2"
        
        # Aceita: "Inc", "Inconclusivo"
        if s in ("INC", "INCONCLUSIVO"):
            return "3"
        
        # Fallback para textos antigos
        if "INCONCL" in s:
            return "3"
        if ("NAO" in s or "NÃƒO" in s) and "DETECT" in s:
            return "2"
        if "DETECT" in s:
            return "1"
        
        return ""
    
    # Base de colunas padrão para todos os painéis
    cod_col = _get(["codigo", "amostra"])
    base_df = pd.DataFrame()
    base_df["codigoAmostra"] = cod_col
    base_df["codigo"] = cod_col
    base_df["requisicao"] = ""
    base_df["paciente"] = ""
    base_df["exame"] = cfg.nome_exame or "VRSRT"
    base_df["metodo"] = "RTTR"
    base_df["registroInterno"] = cod_col
    base_df["kit"] = str(cfg.kit_codigo or "427")
    base_df["reteste"] = ""
    base_df["loteKit"] = ""
    base_df["dataProcessamentoFim"] = datetime.now().strftime("%d/%m/%Y")
    base_df["valorReferencia"] = ""
    base_df["observacao"] = ""
    base_df["resultado"] = ""
    
    # Agrupa alvos por painel (atualmente assume um único painel; pode expandir)
    export_fields = cfg.export_fields or []
    if not export_fields:
        export_fields = ["Influenzaa", "influenzab", "coronavirusncov", "adenovirus", "vsincicialresp"]
    
    panel_id = cfg.panel_tests_id or "1"
    
    def _find_result_col(target_norm: str):
        """Procura coluna compatível (idem formatar_para_gal)"""
        aliases = {
            "INFLUENZAA": "INF A", "INFLUENZAB": "INF B", "ADENOVIRUS": "ADV",
            "METAPNEUMOVIRUS": "HMPV", "RINOVIRUS": "HRV", 
            "SARS-COV-2": "SC2", "SARSCOV2": "SC2", "CORONAVIRUSNCOV": "SC2",
            "VSINCICIALRESP": "RSV", "VSINCICIALRESPA": "RSV", "VSINCICIALRESPB": "RSV", "VSR": "RSV",
        }
        tnorm_raw = _strip_accents(target_norm).upper().replace("_", " ").replace("-", " ").strip()
        if tnorm_raw in aliases:
            tnorm_raw = aliases[tnorm_raw]
        tnorm = cfg.normalize_target(tnorm_raw).upper()
        
        def _clean(s: str) -> str:
            return _strip_accents(s).upper().replace("RESULTADO", "").replace("_", "").replace(" ", "")
        
        for k, v in colmap.items():
            if _clean(k) == _clean(tnorm):
                return v
        cand = f"Resultado_{tnorm}"
        for k, v in colmap.items():
            if _clean(k) == _clean(cand):
                return v
        return None
    
    df_painel = base_df.copy()
    df_painel["painel"] = panel_id
    
    for analito in export_fields:
        alvo_norm = cfg.normalize_target(analito)
        res_col = _find_result_col(alvo_norm)
        if res_col and res_col in df_in.columns:
            serie_res = df_in[res_col].apply(_map_result)
        else:
            serie_res = pd.Series([""] * len(df_in))
        col_nome = _strip_accents(analito).replace(" ", "").replace("-", "").replace("_", "").lower()
        df_painel[col_nome] = serie_res
    
    # Salva CSV para painel
    ts = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    painel_path = os.path.join(output_dir, f"painel_{panel_id}_{ts}_exame.csv")
    df_painel.to_csv(painel_path, index=False, sep=";")
    
    return {panel_id: painel_path}

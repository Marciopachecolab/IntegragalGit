import os
from datetime import datetime
from typing import Dict, List, Tuple

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
    Gera/atualiza o histórico de análises em CSV (append).
    Inclui CN/CP e códigos não numéricos; marca status_gal apropriado.
    Usa ExamRegistry para determinar alvos/CTs.
    """
    cfg = get_exam_cfg(exame)

    def _norm(nome: str) -> str:
        return str(nome).lower().replace(" ", "").replace("_", "")

    cols_norm_map = {_norm(c): c for c in df_final.columns}

    def _find_ct_col(base: str) -> str | None:
        """Encontra a coluna de CT correspondente a um alvo/base.

        Usa nomes com e sem espaço, com sufixo/prefixo "CT" e variações simples.
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

    # RPs
    extra_ct = list(cfg.rps or [])
    for col in df_final.columns:
        up = str(col).upper()
        if up.startswith("RP") and col not in extra_ct:
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

        status_gal = "analizado e nao enviado"
        mensagem_gal = ""
        cod_lower = codigo.lower()
        if (not codigo.isdigit()) or ("cn" in cod_lower) or ("cp" in cod_lower):
            status_gal = "tipo nao enviavel"
            mensagem_gal = "codigo nao numerico ou controle"

        linha = {
            "data_hora_analise": timestamp,
            "usuario_analise": usuario,
            "exame": exame,
            "lote": lote or "",
            "arquivo_corrida": arq_corrida or "",
            "poco": poco,
            "amostra": amostra,
            "codigo": codigo,
            "status_corrida": status_corrida,
            "status_gal": status_gal,
            "mensagem_gal": mensagem_gal,
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
        for ct_col in extra_ct:
            if ct_col in r:
                linha[f"{ct_col} - CT"] = _fmt_ct(r.get(ct_col))

        linhas.append(linha)

    if not linhas:
        return

    df_hist = pd.DataFrame(linhas)
    os.makedirs(os.path.dirname(caminho_csv), exist_ok=True)
    header = not os.path.exists(caminho_csv)
    df_hist.to_csv(caminho_csv, sep=";", index=False, mode="a", header=header, encoding="utf-8")

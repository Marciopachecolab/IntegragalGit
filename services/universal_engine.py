from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from services.config_loader import (
    carregar_equipamentos_metadata,
    carregar_exames_metadata,
    carregar_placas_metadata,
    carregar_regras_analise_metadata,
)
from services.exam_registry import get_exam_cfg
from utils.logger import registrar_log

# ================================================================
# Helpers básicos
# ================================================================


def _normalize_col_key(name: str) -> str:
    if name is None:
        return ""
    translation = str.maketrans({"Ñ": "c", "Ð¡": "c", "Ñ‚": "t", "Ð¢": "t"})
    s = str(name).strip().translate(translation)
    return s.casefold().replace(" ", "").replace("_", "")


def _find_column(cols: List[str], expected: str) -> Optional[str]:
    if not expected:
        return None
    expected_norm = _normalize_col_key(expected)
    for c in cols:
        if _normalize_col_key(c) == expected_norm:
            return c
    if expected_norm in ("ct", "ctmean", "ctsd"):
        for c in cols:
            if _normalize_col_key(c).startswith("ct"):
                return c
    return None


def _to_str_series(series: pd.Series) -> pd.Series:
    """
    Converte valores para strings stripadas, evitando uso direto de .str em objetos nï¿½o string.
    """
    if isinstance(series, pd.DataFrame):
        # se vier coluna duplicada/multiindex, pega a primeira coluna
        series = series.iloc[:, 0]
    def conv(v: Any) -> str:
        try:
            if v is None or (isinstance(v, float) and pd.isna(v)):
                return ""
            if isinstance(v, (pd.Series, pd.DataFrame)):
                # representaï¿½ï¿½o enxuta para objetos complexos
                try:
                    return str(v.to_dict())
                except Exception:
                    return str(v)
            return str(v).strip()
        except Exception:
            return str(v)
    return series.apply(conv)

def _sanitize_gabarito(df: pd.DataFrame) -> pd.DataFrame:
    """
    Garante colunas unicas (Poco, Amostra, Codigo) e valores escalares em string.
    """
    if df is None or getattr(df, "empty", True):
        return df
    df_out = df.copy()
    try:
        if hasattr(df_out.columns, "to_flat_index"):
            df_out.columns = [
                " ".join([str(p) for p in tup if p not in (None, "")]) if isinstance(tup, tuple) else str(tup)
                for tup in df_out.columns.to_flat_index()
            ]
    except Exception:
        pass
    try:
        df_out = df_out.loc[:, ~df_out.columns.duplicated()]
    except Exception:
        pass
    rename_map = {}
    for c in df_out.columns:
        key = _normalize_col_key(c)
        if key in ("poï¿½ï¿½o", "poco", "poc", "poço", "poï¿½o"):
            rename_map[c] = "Poco"
        elif key in ("amostra", "sample"):
            rename_map[c] = "Amostra"
        elif key in ("cï¿½ï¿½digo", "codigo", "cod", "código", "cï¿½digo"):
            rename_map[c] = "Codigo"
    if rename_map:
        df_out = df_out.rename(columns=rename_map)
    cols_interesse = [c for c in ["Poco", "Amostra", "Codigo"] if c in df_out.columns]
    if cols_interesse:
        df_out = df_out[cols_interesse]
    for col in ["Poco", "Amostra", "Codigo"]:
        if col not in df_out.columns:
            df_out[col] = ""
    df_out["Poco"] = _to_str_series(df_out["Poco"])
    df_out["Amostra"] = _to_str_series(df_out["Amostra"])
    df_out["Codigo"] = _to_str_series(df_out["Codigo"])
    return df_out


def _try_reheader(df_raw: pd.DataFrame, required: List[str]) -> pd.DataFrame:
    need = [_normalize_col_key(c) for c in required if c]
    have = [_normalize_col_key(c) for c in df_raw.columns]
    if all(n in have for n in need):
        return df_raw
    for idx, row in df_raw.iterrows():
        vals = ["" if pd.isna(v) else str(v).strip() for v in row.tolist()]
        vals_norm = [_normalize_col_key(v) for v in vals]
        if all(n in vals_norm for n in need):
            cols = [v if v else f"col_{i}" for i, v in enumerate(vals)]
            data = df_raw.iloc[idx + 1 :].copy()
            data.columns = cols
            return data
    return df_raw


def _normalizar_ct(series_ct: pd.Series) -> pd.Series:
    def conv(x: Any) -> Any:
        if x is None:
            return None
        s = str(x).strip().upper()
        if s in ("", "NA", "N/A", "UNDETERMINED", "UND", "N/D"):
            return None
        try:
            val = float(s.replace(",", "."))
            return round(val, 3)
        except Exception:
            return None

    return series_ct.apply(conv)


def _ensure_sample_id(df: pd.DataFrame) -> pd.DataFrame:
    df_out = df.copy()
    df_out["sample_name"] = df_out["sample_name"].astype(str)
    df_out["well"] = df_out["well"].astype(str)
    sample_id = df_out["sample_name"].fillna("")
    if sample_id.duplicated().any():
        sample_id = df_out["sample_name"].fillna("") + "|" + df_out["well"].fillna("")
    df_out["sample_id"] = sample_id
    return df_out


@dataclass
class AnaliseContexto:
    app_state: Any
    exame: str
    config_exame: Dict[str, str]
    config_placa: Dict[str, str]
    config_equip: Dict[str, str]
    config_regras: Dict[str, str]
    caminho_arquivo_corrida: str


def _obter_gabarito_extracao(app_state: Any) -> Optional[pd.DataFrame]:
    """
    Recupera o gabarito de extracao a partir do app_state, testando varios nomes de atributo
    e fazendo uma varredura generica por DataFrames com coluna de poco/amostra.
    """
    if app_state is None:
        return None

    def _log(msg: str) -> None:
        try:
            registrar_log("debug", f"[UniversalEngine][gabarito] {msg}", "DEBUG")
        except Exception:
            pass

    candidatos = [
        "df_gabarito_extracao",
        "gabarito_extracao",
        "dados_extracao",
        "dados_extracao_df",
        "df_extracao",
        "extraction_map",
        "mapa_extracao",
    ]
    for nome in candidatos:
        df_cand = getattr(app_state, nome, None)
        if df_cand is not None and not getattr(df_cand, "empty", False):
            _log(f"Encontrado gabarito em '{nome}' shape={getattr(df_cand, 'shape', None)}")
            return _sanitize_gabarito(df_cand)
    try:
        for attr, val in vars(app_state).items():
            if isinstance(val, pd.DataFrame) and not getattr(val, "empty", False):
                cols_lower = [str(c).lower() for c in val.columns]
                if any("poco" in c or "poco" in c or "well" in c for c in cols_lower):
                    if any("amostra" in c or "sample" in c or "codigo" in c or "codigo" in c for c in cols_lower):
                        _log(f"Gabarito via scan attr '{attr}' cols={list(val.columns)} shape={val.shape}")
                        return _sanitize_gabarito(val)
    except Exception:
        _log("Falha na varredura generica do app_state.")
    _log(f"Nenhum gabarito encontrado nos atributos: {', '.join(candidatos)}")
    return None


# ================================================================
# Fluxo universal (genérico)
# ================================================================


def executar_analise_universal(
    contexto: AnaliseContexto,
) -> Tuple[pd.DataFrame, Dict[str, str]]:
    df_norm = _ler_e_normalizar_arquivo(contexto)
    df_norm = _integrar_com_gabarito_extracao(df_norm, contexto)
    df_interpretado = _aplicar_regras_ct_e_interpretacao(df_norm, contexto)
    df_final, meta = _determinar_status_corrida(
        df_interpretado, contexto, df_norm=df_norm
    )
    return df_final, meta


def _ler_e_normalizar_arquivo(contexto: AnaliseContexto) -> pd.DataFrame:
    tipo = (contexto.config_equip.get("tipo_arquivo") or "").lower().strip()
    caminho = contexto.caminho_arquivo_corrida
    if tipo == "csv":
        df_raw = pd.read_csv(caminho)
    elif tipo in ("xlsx", "xls"):
        df_raw = pd.read_excel(caminho)
    else:
        raise ValueError("tipo_arquivo inválido ou não definido.")

    col_p = (contexto.config_equip.get("coluna_poco") or "").strip()
    col_a = (contexto.config_equip.get("coluna_amostra") or "").strip()
    col_t = (contexto.config_equip.get("coluna_alvo") or "").strip()
    col_ct = (contexto.config_equip.get("coluna_ct") or "").strip()

    df_raw = _try_reheader(df_raw, [col_p, col_a, col_t, col_ct])
    col_poco = _find_column(df_raw.columns.tolist(), col_p)
    col_amostra = _find_column(df_raw.columns.tolist(), col_a)
    col_alvo = _find_column(df_raw.columns.tolist(), col_t)
    col_ct = _find_column(df_raw.columns.tolist(), col_ct)
    for nome, cfg, found in [
        ("poco", col_p, col_poco),
        ("amostra", col_a, col_amostra),
        ("alvo", col_t, col_alvo),
        ("ct", col_ct, col_ct),
    ]:
        if not cfg or found is None:
            raise ValueError(f"Coluna '{cfg}' (config {nome}) não encontrada.")

    df_norm = pd.DataFrame()
    df_norm["well"] = df_raw[col_poco]
    df_norm["sample_name"] = df_raw[col_amostra]
    df_norm["target_name"] = df_raw[col_alvo]
    df_norm["ct_raw"] = df_raw[col_ct]
    df_norm["ct"] = _normalizar_ct(df_norm["ct_raw"])
    return df_norm


def _integrar_com_gabarito_extracao(df_norm: pd.DataFrame, contexto: AnaliseContexto) -> pd.DataFrame:
    gabarito = _obter_gabarito_extracao(contexto.app_state)
    if gabarito is None or gabarito.empty:
        return df_norm
    gabarito = _sanitize_gabarito(gabarito)
    cols_lower = {c: c.lower().strip() for c in gabarito.columns}
    cand_poco = [c for c, lc in cols_lower.items() if "poco" in lc or "poço" in lc or "well" in lc]
    cand_amostra = [c for c, lc in cols_lower.items() if "amostra" in lc or "sample" in lc or "codigo" in lc or "código" in lc]
    if not cand_poco or not cand_amostra:
        return df_norm
    g_sub = gabarito[[cand_poco[0], cand_amostra[0]]].copy()
    g_sub.columns = ["well", "sample_name_gab"]
    g_sub["well"] = _to_str_series(g_sub["well"])

    df_norm = df_norm.copy()
    df_norm["well"] = _to_str_series(df_norm["well"])
    df_out = df_norm.merge(g_sub, how="left", on="well")
    df_out["sample_name"] = df_out["sample_name_gab"].combine_first(df_out["sample_name"])
    df_out = df_out.drop(columns=["sample_name_gab"])
    return df_out


def _aplicar_regras_ct_e_interpretacao(
    df_norm: pd.DataFrame, contexto: AnaliseContexto
) -> pd.DataFrame:
    # Preferir faixas definidas no ExamRegistry; fallback para config_regras legado
    exame_nome = None
    try:
        exame_nome = (contexto.config_equip or {}).get("exame")
    except Exception:
        exame_nome = None

    try:
        exam_cfg = get_exam_cfg(exame_nome or "")
    except Exception:
        exam_cfg = None

    if exam_cfg and getattr(exam_cfg, "faixas_ct", None):
        faixas = exam_cfg.faixas_ct or {}
        ct_detect_max = float(faixas.get("detect_max", faixas.get("detectMax", 40.0)))
        ct_inconc_min = float(faixas.get("inconc_min", faixas.get("inconcMin", 40.01)))
        ct_inconc_max = float(faixas.get("inconc_max", faixas.get("inconcMax", 45.0)))
        ct_rp_min = float(faixas.get("rp_min", faixas.get("rpMin", 15.0)))
        ct_rp_max = float(faixas.get("rp_max", faixas.get("rpMax", 35.0)))
    else:
        cfg = contexto.config_regras or {}
        def as_float(key: str, default: float) -> float:
            try:
                return float((cfg.get(key) or "").replace(",", "."))
            except Exception:
                return default

        ct_detect_max = as_float("CT_DETECTAVEL_MAX", 40.0)
        ct_inconc_min = as_float("CT_INCONCLUSIVO_MIN", 40.01)
        ct_inconc_max = as_float("CT_INCONCLUSIVO_MAX", 45.0)
        ct_rp_min = as_float("CT_RP_MIN", 15.0)
        ct_rp_max = as_float("CT_RP_MAX", 35.0)

    alvos = [a.strip() for a in (cfg.get("alvos") or "").split(";") if a.strip()]
    alvos_sem_rp = [a for a in alvos if a.upper() not in ("RP", "RP_1", "RP_2")]
    df_sid = _ensure_sample_id(df_norm)

    df_rp = df_sid[df_sid["target_name"].astype(str).str.upper().isin(["RP", "RP_1", "RP_2"])]
    rp_por_amostra: Dict[str, float] = {}
    for amostra, sub in df_rp.groupby("sample_id"):
        vals = [v for v in sub["ct"].tolist() if v is not None]
        if vals:
            rp_por_amostra[amostra] = float(sum(vals) / len(vals))

    df_targets = df_sid[
        df_sid["target_name"].astype(str).str.upper().isin([t.upper() for t in alvos_sem_rp])
    ].copy()
    if df_targets.empty:
        return pd.DataFrame(columns=["sample_name"])
    df_targets["target_upper"] = df_targets["target_name"].astype(str).str.upper()

    pivot_ct = df_targets.pivot_table(index="sample_id", columns="target_upper", values="ct", aggfunc="first")
    sample_name_map = df_targets.groupby("sample_id")["sample_name"].first().to_dict()

    linhas: List[Dict[str, Any]] = []
    for sample_id, row in pivot_ct.iterrows():
        linha: Dict[str, Any] = {"sample_id": sample_id, "sample_name": sample_name_map.get(sample_id, sample_id)}
        ct_rp = rp_por_amostra.get(sample_id)
        for target_upper in row.index:
            ct_val = row[target_upper]
            col_res = f"Resultado_{target_upper.replace(' ', '')}"
            linha[col_res] = _interpretar_com_rp(
                ct_rp=ct_rp,
                ct_alvo=ct_val,
                ct_detect_min=0.0,
                ct_detect_max=ct_detect_max,
                ct_inconc_min=ct_inconc_min,
                ct_inconc_max=ct_inconc_max,
                ct_rp_min=ct_rp_min,
                ct_rp_max=ct_rp_max,
            )
        linhas.append(linha)
    return pd.DataFrame(linhas)


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
    if ct_rp is None:
        return "Invalido"
    try:
        valor_rp = float(ct_rp)
    except Exception:
        return "Invalido"
    if not (ct_rp_min <= valor_rp <= ct_rp_max):
        return "Invalido"
    if ct_alvo is None:
        return "Nao Detectado"
    try:
        valor_ct = float(ct_alvo)
    except Exception:
        return "Nao Detectado"
    if valor_ct <= ct_detect_max:
        return "Detectado"
    if ct_inconc_min <= valor_ct <= ct_inconc_max:
        return "Inconclusivo"
    return "Nao Detectado"


def _montar_df_final_vr1_like(
    df_norm: pd.DataFrame,
    df_interpretado: pd.DataFrame,
    status_corrida: str,
) -> pd.DataFrame:
    if df_interpretado is None or df_interpretado.empty:
        return pd.DataFrame({"Status_Corrida": [status_corrida]})

    df_base = df_interpretado.copy().reset_index(drop=True)
    if "sample_id" not in df_base.columns:
        df_base["sample_id"] = df_base.get("sample_name")
    df_base["sample_id"] = df_base["sample_id"].astype(str)
    df_base["sample_name"] = df_base.get("sample_name", df_base["sample_id"]).astype(str)

    colunas_resultado = [c for c in df_base.columns if c.startswith("Resultado_")]
    target_ct_cols = [c.replace("Resultado_", "").upper() for c in colunas_resultado]

    df_ct_sel = pd.DataFrame({"sample_id": df_base["sample_id"].unique()}).set_index("sample_id")
    if df_norm is not None and not df_norm.empty:
        df_tmp = _ensure_sample_id(df_norm)
        df_tmp["target_upper"] = df_tmp["target_name"].astype(str).str.upper()
        pivot_ct_all = df_tmp.pivot_table(index="sample_id", columns="target_upper", values="ct", aggfunc="first")
        for col_res in colunas_resultado:
            alvo_label = col_res[len("Resultado_") :]
            ct_col_name = alvo_label.upper()
            if ct_col_name in pivot_ct_all.columns:
                df_ct_sel[ct_col_name] = pivot_ct_all.reindex(df_ct_sel.index)[ct_col_name]
            else:
                df_ct_sel[ct_col_name] = pd.NA
        df_rp = df_tmp[df_tmp["target_upper"].isin(["RP", "RP_1", "RP_2"])]
        rp_map: Dict[str, float] = {}
        for amostra, sub in df_rp.groupby("sample_id"):
            vals = [v for v in sub["ct"].tolist() if v is not None]
            if vals:
                rp_map[amostra] = float(sum(vals) / len(vals))
        df_ct_sel["RP_1"] = df_ct_sel.index.to_series().map(rp_map)
        df_ct_sel["RP_2"] = df_ct_sel.index.to_series().map(rp_map)
    else:
        for col_res in colunas_resultado:
            alvo_label = col_res[len("Resultado_") :]
            ct_col_name = alvo_label.upper()
            df_ct_sel[ct_col_name] = pd.NA
        df_ct_sel["RP_1"] = pd.NA
        df_ct_sel["RP_2"] = pd.NA
    df_ct_sel = df_ct_sel.reset_index()

    df_meta = pd.DataFrame({"sample_id": df_base["sample_id"].unique()})
    if df_norm is not None and not df_norm.empty:
        df_tmp = _ensure_sample_id(df_norm)
        df_tmp["sample_name"] = df_tmp["sample_name"].astype(str)
        df_tmp["sample_id"] = df_tmp["sample_id"].astype(str)
        cols_lower = {c: c.lower().strip() for c in df_tmp.columns}
        cand_poco = [c for c, lc in cols_lower.items() if "poco" in lc or "poço" in lc or "well" in lc]
        cand_cod = [c for c, lc in cols_lower.items() if "codigo" in lc or "código" in lc or lc.startswith("cod")]
        grp = df_tmp.groupby("sample_id")
        if cand_poco:
            df_poco = grp[cand_poco[0]].first().reset_index().rename(columns={cand_poco[0]: "Poco"})
            df_meta = df_meta.merge(df_poco, on="sample_id", how="left")
        else:
            df_meta["Poco"] = pd.NA
        sample_name_first = grp["sample_name"].first().reset_index()
        df_meta = df_meta.merge(sample_name_first, on="sample_id", how="left")
        df_meta = df_meta.rename(columns={"sample_name": "Amostra"})
        if cand_cod:
            df_cod = grp[cand_cod[0]].first().reset_index().rename(columns={cand_cod[0]: "Codigo"})
            df_meta = df_meta.merge(df_cod, on="sample_id", how="left")
        else:
            df_meta["Codigo"] = df_meta["Amostra"]
    else:
        df_meta["Poco"] = pd.NA
        df_meta["Amostra"] = df_meta["sample_id"]
        df_meta["Codigo"] = df_meta["Amostra"]

    df_final = df_meta.merge(df_base, on="sample_id", how="left").merge(df_ct_sel, on="sample_id", how="left")
    for col_rm in ["sample_id", "sample_name"]:
        if col_rm in df_final.columns:
            df_final = df_final.drop(columns=[col_rm])
    if "Poco" not in df_final.columns and "Poço" in df_final.columns:
        df_final["Poco"] = df_final["Poço"]
    if "Codigo" not in df_final.columns and "Código" in df_final.columns:
        df_final["Codigo"] = df_final["Código"]

    colunas_ct = target_ct_cols + ["RP_1", "RP_2"]
    colunas_finais = ["Poco", "Amostra", "Codigo"] + colunas_resultado + colunas_ct + ["Status_Corrida"]
    for col in colunas_finais:
        if col not in df_final.columns:
            df_final[col] = pd.NA
    df_final["Status_Corrida"] = status_corrida
    return df_final


def _determinar_status_corrida(
    df_interpretado: pd.DataFrame,
    contexto: AnaliseContexto,
    df_norm: pd.DataFrame,
) -> Tuple[pd.DataFrame, Dict[str, str]]:
    cfg_regra = contexto.config_regras
    app_state = getattr(contexto, "app_state", None)
    exam_cfg = getattr(app_state, "exam_cfg", None) if app_state is not None else None

    def as_float(key: str, default: float) -> float:
        try:
            return float((cfg_regra.get(key) or "").replace(",", "."))
        except Exception:
            return default

    ct_detect_max = as_float("CT_DETECTAVEL_MAX", 40.0)
    ct_inconc_min = as_float("CT_INCONCLUSIVO_MIN", 38.01)
    ct_inconc_max = as_float("CT_INCONCLUSIVO_MAX", 45.0)
    ct_rp_min = as_float("CT_RP_MIN", 15.0)
    ct_rp_max = as_float("CT_RP_MAX", 35.0)

    alvos = [a.strip() for a in (cfg_regra.get("alvos") or "").split(";") if a.strip()]
    if exam_cfg is not None and getattr(exam_cfg, "alvos", None):
        alvos = [a.strip() for a in exam_cfg.alvos]
    alvos_upper = [a.upper() for a in alvos]
    alvo_principal = alvos_upper[0] if alvos_upper else None
    rp_names = ["RP", "RP_1", "RP_2"]
    if exam_cfg is not None and getattr(exam_cfg, "rps", None):
        rp_names = [r.upper() for r in exam_cfg.rps]

    if df_norm.empty or alvo_principal is None:
        status_corrida = "Invalida (sem resultados)"
        meta = {"status_corrida": status_corrida, "exame": contexto.exame, "equipamento": contexto.config_exame.get("equipamento", "")}
        df_final = _montar_df_final_vr1_like(df_norm, df_interpretado, status_corrida)
        return df_final, meta

    df_tmp = _ensure_sample_id(df_norm.copy())
    df_tmp["target_upper"] = df_tmp["target_name"].astype(str).str.upper()

    def _any_detect(mask_ctrl: pd.Series) -> bool:
        sub = df_tmp[mask_ctrl & ~df_tmp["target_upper"].isin(rp_names)]
        vals = [v for v in sub["ct"].tolist() if v is not None]
        return any(v is not None and v != "" and float(v) <= ct_detect_max for v in vals)

    # Controles
    mask_cn_sample = df_tmp["sample_name"].astype(str).str.contains("CN", case=False, na=False)
    mask_cp_sample = df_tmp["sample_name"].astype(str).str.contains("CP", case=False, na=False)

    status_corrida = "Valida"
    if not mask_cn_sample.any() or not mask_cp_sample.any():
        status_corrida = "Invalida (Controles Ausentes)"
    elif _any_detect(mask_cn_sample):
        status_corrida = "Invalida (CN Detectado)"
    else:
        # CP: validar RP na faixa
        sub_cp_rp = df_tmp[mask_cp_sample & df_tmp["target_upper"].isin(rp_names)]
        rp_cp_vals = [v for v in sub_cp_rp["ct"].tolist() if v is not None]
        if not rp_cp_vals or not all(ct_rp_min <= float(v) <= ct_rp_max for v in rp_cp_vals):
            status_corrida = "Invalida (CP Fora do Intervalo)"

    # Validação de RP por amostra
    if status_corrida.startswith("Valida") and not df_tmp.empty:
        ok = True
        df_rp = df_tmp[df_tmp["target_upper"].isin(rp_names)]
        for _, sub in df_rp.groupby("sample_id"):
            vals = [v for v in sub["ct"].tolist() if v is not None]
            if not vals:
                ok = False
                break
            if not all(ct_rp_min <= float(v) <= ct_rp_max for v in vals):
                ok = False
                break
        if not ok:
            status_corrida = "Invalida (RP fora do intervalo)"

    meta = {
        "status_corrida": status_corrida,
        "exame": contexto.exame,
        "equipamento": contexto.config_exame.get("equipamento", ""),
    }
    # Consolida resultado/cor por bloco de poços (para mapa/df_final)
    bloco_tam = getattr(app_state, "bloco_tamanho", None)
    if bloco_tam is None:
        bloco_tam = _inferir_bloco(exam_cfg) if exam_cfg is not None else 1
    try:
        bloco_tam = int(bloco_tam) if bloco_tam else 1
    except Exception:
        bloco_tam = 1
    df_final = _montar_df_final_vr1_like(df_norm, df_interpretado, status_corrida)
    if bloco_tam > 1 and "Poco" in df_final.columns:
        df_final = _consolidar_por_bloco(df_final, bloco_tam)

    return df_final, meta


# =====================================================================
# VR1/VR2 legado (7500)
# =====================================================================

CT_RP_MIN_LEGACY = 15
CT_RP_MAX_LEGACY = 35
CT_DETECTAVEL_MAX_LEGACY = 38
CT_INCONC_MIN_LEGACY = 38.01
CT_INCONC_MAX_LEGACY = 40
TARGETS_LEGACY = ["SC2", "HMPV", "INF A", "INF B", "ADV", "RSV", "HRV"]
TARGETS_POCO1 = ["HMPV", "INF A", "INF B", "SC2"]


def _consolidar_por_bloco(df_final: pd.DataFrame, bloco_tam: int) -> pd.DataFrame:
    """
    Ajusta a cor/resultado por bloco horizontal (par/trio) para mapas/saídas finais.
    Prioridade: Invalida > Detectado > Inconclusivo > Nao Detectado > "".
    O resultado do bloco é replicado nos poços do bloco.
    """
    if df_final.empty or bloco_tam <= 1:
        return df_final
    if "Poco" not in df_final.columns or "Status_Corrida" not in df_final.columns:
        return df_final

    def _parse_poco(p: str):
        if not p:
            return None, None
        row = p[0].upper()
        try:
            col = int(p[1:])
        except Exception:
            return row, None
        return row, col

    prioridade = ["Invalida", "Detectado", "Inconclusivo", "Nao Detectado", ""]
    df_out = df_final.copy()
    for _, row in df_final.iterrows():
        row_letter, colnum = _parse_poco(str(row.get("Poco", "")))
        if row_letter is None or colnum is None:
            continue
        start = (colnum // bloco_tam) * bloco_tam
        block_cols = [start + i for i in range(bloco_tam)]
        wells_block = [f"{row_letter}{c}" for c in block_cols]
        subs = df_final[df_final["Poco"].isin(wells_block)]
        status_set = [str(s) for s in subs["Status_Corrida"].unique()]
        status_block = ""
        for s in prioridade:
            if s in status_set:
                status_block = s
                break
        df_out.loc[df_out["Poco"].isin(wells_block), "Status_Corrida"] = status_block
    return df_out


def _legacy_extract_table(df_raw: pd.DataFrame) -> pd.DataFrame:
    required = {"samplename", "targetname"}
    df_str = df_raw.fillna("").astype(str)
    header_idx = None
    header_vals: List[str] = []
    for idx, row in df_str.iterrows():
        vals = [v.strip() for v in row.tolist()]
        norm = {v.lower().replace(" ", "") for v in vals if v.strip()}
        if required.issubset(norm):
            header_idx = idx
            header_vals = vals
            break
    if header_idx is None:
        return df_raw
    data = df_raw.iloc[header_idx + 1 :].copy()
    cols = [v.strip() if v else f"col_{i}" for i, v in enumerate(header_vals)]
    data.columns = cols
    return data


def _legacy_processar_ct(val: Any) -> Optional[float]:
    res = _normalizar_ct(pd.Series([val]))[0]
    if res is None:
        return None
    try:
        return round(float(res), 3)
    except Exception:
        return res


def _legacy_interpretar(ct_rp1: Optional[float], ct_rp2: Optional[float], ct_alvo: Any) -> str:
    if isinstance(ct_alvo, str) and ct_alvo.strip().upper() == "UNDETERMINED":
        return "Nao Detectado"
    if ct_alvo is None:
        return "Invalido"
    if ct_rp1 is None or ct_rp2 is None:
        return "Invalido"
    if not (CT_RP_MIN_LEGACY <= ct_rp1 <= CT_RP_MAX_LEGACY and CT_RP_MIN_LEGACY <= ct_rp2 <= CT_RP_MAX_LEGACY):
        return "Invalido"
    try:
        ct_val = float(ct_alvo)
    except Exception:
        return "Invalido"
    if ct_val <= CT_DETECTAVEL_MAX_LEGACY:
        return "Detectado"
    if CT_INCONC_MIN_LEGACY <= ct_val <= CT_INCONC_MAX_LEGACY:
        return "Inconclusivo"
    return "Invalido"


def _legacy_ct_for(df_proc: pd.DataFrame, df_filtered: pd.DataFrame, target: str, well: Optional[str]) -> Any:
    if well is None:
        return None
    s = df_proc[(df_proc["WELL"] == str(well)) & (df_proc["Target"] == target.upper())]["CT"]
    s_valid = [v for v in s.tolist() if v is not None and pd.notna(v)]
    if s_valid:
        return s_valid[0]
    s_raw = df_filtered[(df_filtered["WELL"] == str(well)) & (df_filtered["TARGET NAME"] == target.upper())]["CT"]
    for rv in s_raw.tolist():
        if isinstance(rv, str) and rv.strip().upper() == "UNDETERMINED":
            return "Undetermined"
    return None


def _legacy_status_corrida(df_pivot: pd.DataFrame) -> str:
    rp1_vals = [float(v) for v in df_pivot.get("RP_1", []).tolist() if isinstance(v, (int, float)) and pd.notna(v)]
    rp2_vals = [float(v) for v in df_pivot.get("RP_2", []).tolist() if isinstance(v, (int, float)) and pd.notna(v)]
    if not rp1_vals or not rp2_vals:
        return "Invalida (Controles Ausentes)"
    if all(CT_RP_MIN_LEGACY <= v <= CT_RP_MAX_LEGACY for v in rp1_vals) and all(
        CT_RP_MIN_LEGACY <= v <= CT_RP_MAX_LEGACY for v in rp2_vals
    ):
        return "Valida"
    return "Invalida (RP fora do intervalo)"


def _legacy_montar_df(
    df_proc: pd.DataFrame,
    df_filtered: pd.DataFrame,
    dados_extracao_df: pd.DataFrame,
) -> Tuple[pd.DataFrame, str]:
    df_gab = _sanitize_gabarito(dados_extracao_df)

    def _as_series(obj: Any) -> pd.Series:
        return obj.iloc[:, 0] if isinstance(obj, pd.DataFrame) else obj
    rename_map = {}
    for c in df_gab.columns:
        key = _normalize_col_key(c)
        if key in ("poço", "poco", "poc"):
            rename_map[c] = "Poco"
        elif key in ("amostra", "sample"):
            rename_map[c] = "Amostra"
        elif key in ("código", "codigo", "cod"):
            rename_map[c] = "Codigo"
    if rename_map:
        df_gab = df_gab.rename(columns=rename_map)
    for col in ["Poco", "Amostra", "Codigo"]:
        if col not in df_gab.columns:
            df_gab[col] = ""
    df_gab["Poco"] = _to_str_series(_as_series(df_gab["Poco"]))
    df_gab["Amostra"] = _to_str_series(_as_series(df_gab["Amostra"]))
    df_gab["Codigo"] = _to_str_series(_as_series(df_gab["Codigo"]))
    # remove linhas vazias ou marcadas como X
    df_gab = df_gab[~df_gab["Amostra"].isin(["", "X", "x", "nan", "None"])].copy()

    samples = [s for s in df_gab["Amostra"].astype(str).unique()]
    rows = []
    import re

    def _parse_well(well: str):
        m = re.match(r"^([A-Za-z]+)(\d+)$", str(well).strip())
        if not m:
            return None, None
        return m.group(1).upper(), int(m.group(2))

    for samp in samples:
        pocos_sel = df_gab.loc[df_gab["Amostra"] == str(samp), "Poco"]
        if isinstance(pocos_sel, pd.DataFrame):
            pocos_sel = pocos_sel.iloc[:, 0]
        pocos = pocos_sel.tolist()
        well1, well2 = None, None
        if len(pocos) >= 1:
            r, c = _parse_well(pocos[0])
            if r and c:
                well1 = f"{r}{c}"
                well2 = f"{r}{c+1}"

        row = {"Sample": str(samp)}
        rp1 = _legacy_ct_for(df_proc, df_filtered, "RP", well1)
        rp2 = _legacy_ct_for(df_proc, df_filtered, "RP", well2)

        def _count_targets(well, targets):
            if well is None:
                return 0
            return sum(1 for t in targets if _legacy_ct_for(df_proc, df_filtered, t, well) is not None)

        swap = False
        if rp1 is None and rp2 is not None:
            swap = True
        else:
            if _count_targets(well2, TARGETS_POCO1) > _count_targets(well1, TARGETS_POCO1):
                swap = True
        if swap:
            well1, well2 = well2, well1
            rp1, rp2 = rp2, rp1

        row["RP_1"] = rp1
        row["RP_2"] = rp2
        row["Valid"] = not (rp1 is None or rp2 is None)
        row["Well1"] = well1
        row["Well2"] = well2

        for t in TARGETS_LEGACY:
            if t.upper() in [x.upper() for x in TARGETS_POCO1]:
                row[t.upper()] = _legacy_ct_for(df_proc, df_filtered, t, well1)
            else:
                row[t.upper()] = _legacy_ct_for(df_proc, df_filtered, t, well2)
        row["Poco"] = f"{well1}+{well2}" if well1 and well2 else well1 or well2
        rows.append(row)

    df_pivot = pd.DataFrame(rows)
    for target in TARGETS_LEGACY:
        col_res = f"Resultado_{target.upper().replace(' ', '')}"
        df_pivot[col_res] = df_pivot.apply(
            lambda r, tgt=target: _legacy_interpretar(r.get("RP_1"), r.get("RP_2"), r.get(tgt.upper()))
            if r.get("Valid", True)
            else "Invalido",
            axis=1,
        )

    status_corrida = _legacy_status_corrida(df_pivot)

    df_final = pd.merge(df_gab, df_pivot, left_on="Amostra", right_on="Sample", how="left")
    if "Poco_y" in df_final.columns:
        df_final["Poco"] = df_final["Poco_y"].combine_first(df_final.get("Poco_x"))
    if "Poco" not in df_final.columns and "Poco_x" in df_final.columns:
        df_final["Poco"] = df_final["Poco_x"]
    for col_drop in ["Poco_x", "Poco_y"]:
        if col_drop in df_final.columns:
            df_final = df_final.drop(columns=[col_drop])
    # garante uma linha por amostra/poço
    df_final = df_final.drop_duplicates(subset=["Amostra", "Poco"])

    colunas_resultado = [f"Resultado_{t.upper().replace(' ', '')}" for t in TARGETS_LEGACY]
    colunas_ct = [t.upper() for t in TARGETS_LEGACY] + ["RP_1", "RP_2"]
    colunas_finais = ["Poco", "Amostra", "Codigo"] + colunas_resultado + colunas_ct + ["Status_Corrida"]
    for col in colunas_finais:
        if col not in df_final.columns:
            df_final[col] = None
    df_final["Status_Corrida"] = status_corrida
    return df_final[colunas_finais], status_corrida


# =====================================================================
# Classe principal
# =====================================================================


class UniversalEngine:
    def __init__(self, contexto_padrao: Optional[AnaliseContexto] = None) -> None:
        if contexto_padrao is None:
            self.contexto_padrao = None
            self.app_state = None
        else:
            # se recebeu um contexto com app_state, usa-o; se recebeu o próprio AppState, preserva direto
            self.contexto_padrao = contexto_padrao if hasattr(contexto_padrao, "app_state") else None
            self.app_state = getattr(contexto_padrao, "app_state", contexto_padrao)

    def processar_exame(
        self,
        exame: str,
        df_resultados: pd.DataFrame,
        df_extracao: Optional[pd.DataFrame] = None,
        lote: Optional[str] = None,
    ):
        # metadados via registry (fallback se não existir JSON/YAML)
        cfg = get_exam_cfg(exame)
        if self.app_state is not None:
            try:
                self.app_state.exam_cfg = cfg
            except Exception:
                pass
        # VR1e2 legado
        if exame.strip().lower() == "vr1e2 biomanguinhos 7500".lower():
            # tenta gabarito vindo do parâmetro ou de vários atributos do app_state
            def _obter_gabarito(df_param: Optional[pd.DataFrame], app_state: Any) -> Optional[pd.DataFrame]:
                def _dbg(msg: str) -> None:
                    try:
                        registrar_log("debug", f"[UniversalEngine][VR1e2] {msg}")
                    except Exception:
                        pass

                if df_param is not None and not getattr(df_param, "empty", False):
                    _dbg("Gabarito recebido por parâmetro.")
                    return df_param
                if app_state is None:
                    return None
                candidatos = [
                    "dados_extracao",
                    "df_gabarito_extracao",
                    "gabarito_extracao",
                    "df_extracao",
                    "dados_extracao_df",
                ]
                found_info = []
                for nome in candidatos:
                    df_cand = getattr(app_state, nome, None)
                    if df_cand is not None and not getattr(df_cand, "empty", False):
                        found_info.append(f"{nome} shape={getattr(df_cand, 'shape', None)}")
                        _dbg(f"Gabarito encontrado em {nome}.")
                        return _sanitize_gabarito(df_cand)
                # varredura genérica no __dict__ para achar um DataFrame com colunas de poço/amostra
                try:
                    for _, val in vars(app_state).items():
                        if isinstance(val, pd.DataFrame) and not getattr(val, "empty", False):
                            cols_lower = [str(c).lower() for c in val.columns]
                            if any("po" in c or "poço" in c for c in cols_lower):
                                found_info.append(f"__dict__ DF cols={list(val.columns)} shape={val.shape}")
                                _dbg("Gabarito encontrado via varredura genérica do app_state.")
                                return val
                except Exception:
                    pass
                try:
                    df_cand = _obter_gabarito_extracao(app_state)
                    if df_cand is not None and not getattr(df_cand, "empty", False):
                        _dbg("Gabarito obtido via _obter_gabarito_extracao.")
                        return df_cand
                except Exception:
                    _dbg("Falha ao obter gabarito via _obter_gabarito_extracao.")
                _dbg(f"Nenhum gabarito encontrado. Candidates verificados: {', '.join(candidatos)}; encontrados: {found_info}")
                return None

            df_gabarito = _obter_gabarito(df_extracao, self.app_state)
            df_table = _legacy_extract_table(df_resultados)
            expected_cols = [
                "WELL",
                "SAMPLE NAME",
                "TARGET NAME",
                "TASK",
                "REPORTER",
                "QUENCHER",
                "CT",
                "CT MEAN",
                "CT SD",
                "QUANTITY",
                "QUANTITY MEAN",
                "QUANTITY SD",
                "AUTOMATIC CT THRESHOLD",
                "CT THRESHOLD",
                "AUTOMATIC BASELINE",
                "BASELINE START",
                "BASELINE END",
                "COMMENTS",
                "HIGHSD",
                "EXPFAIL",
            ]
            if df_table.shape[1] < len(expected_cols):
                raise ValueError(f"Arquivo de corrida inesperado: apenas {df_table.shape[1]} colunas.")
            df_table = df_table.iloc[:, : len(expected_cols)].copy()
            df_table.columns = expected_cols
            df_table["TARGET NAME"] = df_table["TARGET NAME"].apply(lambda x: str(x).upper().strip() if pd.notna(x) else x)
            df_filtered = df_table[["WELL", "SAMPLE NAME", "TARGET NAME", "CT"]].copy()
            df_filtered = df_filtered[df_filtered["TARGET NAME"].isin(TARGETS_LEGACY + ["RP"])]
            df_filtered.dropna(subset=["SAMPLE NAME"], inplace=True)

            if df_gabarito is None or df_gabarito.empty:
                raise ValueError("dados_extracao não fornecido para VR1e2.")

            df_proc = pd.DataFrame()
            df_proc["WELL"] = df_filtered["WELL"].astype(str).str.strip()
            df_proc["SampleName"] = df_filtered["SAMPLE NAME"].astype(str).str.replace(".0", "", regex=False).str.strip()
            df_proc["Target"] = df_filtered["TARGET NAME"]
            df_proc["CT"] = df_filtered["CT"].apply(_legacy_processar_ct)

            # expõe df_norm-like no app_state para uso no mapa de placa
            try:
                if self.app_state is not None:
                    df_norm_like = pd.DataFrame(
                        {
                            "well": df_proc["WELL"],
                            "sample_name": df_proc["SampleName"],
                            "target_name": df_proc["Target"],
                            "ct": df_proc["CT"],
                        }
                    )
                    self.app_state.df_norm = df_norm_like
                    self.app_state.dados_extracao = df_gabarito
            except Exception:
                pass

            df_final, status_corrida = _legacy_montar_df(df_proc, df_filtered, df_gabarito)
            meta = {"status_corrida": status_corrida, "exame": exame}
            resumo = {"status_corrida": status_corrida, "lote": lote or ""}
            return SimpleNamespace(df_final=df_final, resumo=resumo, metadados=meta)

        # Fluxo universal
        if self.app_state is not None and df_extracao is not None:
            try:
                self.app_state.df_gabarito_extracao = df_extracao
            except Exception:
                pass

        config_exame = carregar_exames_metadata().get(exame, {})
        config_equip = carregar_equipamentos_metadata().get(config_exame.get("equipamento", ""), {})
        config_placa = carregar_placas_metadata().get(config_exame.get("tipo_placa", ""), {})
        config_regras = carregar_regras_analise_metadata().get(exame, {})
        if not config_equip:
            raise ValueError(f"Configuração de equipamento não encontrada para exame '{exame}'.")

        # sobrescreve regras com dados do registry (alvos/faixas CT)
        if cfg.alvos:
            config_regras["alvos"] = ";".join(cfg.alvos)
        fc = cfg.faixas_ct or {}
        def _set_regra(key_csv: str, key_cfg: str, default: float) -> None:
            val = fc.get(key_cfg)
            if val is not None:
                try:
                    config_regras[key_csv] = float(val)
                except Exception:
                    config_regras[key_csv] = default
            elif key_csv not in config_regras:
                config_regras[key_csv] = default
        _set_regra("CT_DETECTAVEL_MAX", "detect_max", 40.0)
        _set_regra("CT_INCONCLUSIVO_MIN", "inconc_min", 38.01)
        _set_regra("CT_INCONCLUSIVO_MAX", "inconc_max", 45.0)
        _set_regra("CT_RP_MIN", "rp_min", 15.0)
        _set_regra("CT_RP_MAX", "rp_max", 35.0)

        df_norm = _normalizar_resultados_em_memoria(df_resultados, config_equip)
        try:
            df_norm = df_norm.copy()
            df_norm["target_name"] = df_norm["target_name"].apply(cfg.normalize_target)
        except Exception:
            pass
        ctx = AnaliseContexto(
            app_state=self.app_state,
            exame=exame,
            config_exame=config_exame,
            config_placa=config_placa,
            config_equip=config_equip,
            config_regras=config_regras,
            caminho_arquivo_corrida="",
        )
        # guarda df_norm para uso posterior (ex.: mapa da placa)
        try:
            if self.app_state is not None:
                self.app_state.df_norm = df_norm
        except Exception:
            pass
        df_norm = _integrar_com_gabarito_extracao(df_norm, ctx)
        df_interpretado = _aplicar_regras_ct_e_interpretacao(df_norm, ctx)
        df_final, meta = _determinar_status_corrida(df_interpretado, ctx, df_norm=df_norm)
        # anexa informaçÕÂ§es de agrupamento/bloco derivadas do exam_cfg
        bloco_tamanho = _inferir_bloco(cfg)
        meta["esquema_agrupamento"] = cfg.esquema_agrupamento
        meta["bloco_tamanho"] = bloco_tamanho
        try:
            if self.app_state is not None:
                self.app_state.exam_cfg = cfg
                self.app_state.bloco_tamanho = bloco_tamanho
        except Exception:
            pass
        resumo = {"status_corrida": meta.get("status_corrida", ""), "lote": lote or ""}
        return SimpleNamespace(df_final=df_final, resumo=resumo, metadados=meta)

    def executar(self, contexto: Optional[AnaliseContexto] = None) -> Tuple[pd.DataFrame, Dict[str, str]]:
        ctx = contexto or self.contexto_padrao
        if ctx is None:
            raise ValueError("UniversalEngine.executar: contexto não fornecido nem definido como padrão.")
        return executar_analise_universal(ctx)

    def __call__(self, contexto: Optional[AnaliseContexto] = None) -> Tuple[pd.DataFrame, Dict[str, str]]:
        return self.executar(contexto)

    @staticmethod
    def executar_analise_universal(contexto: AnaliseContexto) -> Tuple[pd.DataFrame, Dict[str, str]]:
        return executar_analise_universal(contexto)

    @classmethod
    def run(cls, contexto: AnaliseContexto) -> Tuple[pd.DataFrame, Dict[str, str]]:
        return executar_analise_universal(contexto)


def universal_engine(contexto: AnaliseContexto) -> Tuple[pd.DataFrame, Dict[str, str]]:
    return executar_analise_universal(contexto)


def _inferir_bloco(cfg: Any) -> int:
    """
    Retorna o tamanho do bloco de poços (1=sem agrupamento, 2=pares, 3=trios) com base no esquema_agrupamento.
    """
    try:
        esquema = (cfg.esquema_agrupamento or "").lower()
    except Exception:
        esquema = ""
    if "->48" in esquema or "1:2" in esquema:
        return 2
    if "->36" in esquema or "1:3" in esquema:
        return 3
    return 1

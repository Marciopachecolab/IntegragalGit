"""
Visualização interativa da placa (CustomTkinter) consumindo dados em memória
vindo da análise (df_final/df_norm). Inspirado em services/teste_plate_viewer_historico_ctk.py,
mas sem ler CSV e sem exportar XLS automaticamente.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import customtkinter as ctk
import pandas as pd
import tkinter as tk
from tkinter import ttk

from services.exam_registry import get_exam_cfg

# ---------------------------------------------------------------------------
# Aparência / Cores
# ---------------------------------------------------------------------------

NEGATIVE = "NEGATIVE"
POSITIVE = "POSITIVE"
INCONCLUSIVE = "INCONCLUSIVE"
INVALID = "INVALID"
CONTROL_CN = "CONTROL_CN"
CONTROL_CP = "CONTROL_CP"
EMPTY = "EMPTY"

STATUS_COLORS = {
    NEGATIVE: "#d4f4d4",  # verde claro
    POSITIVE: "#ffb3b3",  # vermelho claro
    INCONCLUSIVE: "#ffcc99",  # laranja claro
    INVALID: "#f0f0f0",  # cinza
    CONTROL_CN: "#b3d9ff",  # azul claro
    CONTROL_CP: "#b3d9ff",  # azul claro (mesma cor CN)
    EMPTY: "#ffffff",  # branco
}

# Cores para diferentes tamanhos de grupos (exames de 48, 32, 24 testes)
GROUP_COLORS = {
    2: "#0000FF",  # Azul para pares (48 testes)
    3: "#00FF00",  # Verde para trios (32 testes)
    4: "#FF00FF",  # Magenta para quartetos (24 testes)
}

ROW_LABELS = ["A", "B", "C", "D", "E", "F", "G", "H"]
COL_LABELS = [str(i) for i in range(1, 13)]

# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------


@dataclass
class TargetResult:
    result: str = ""  # "Det", "ND", "Inc", "Inv"...
    ct: Optional[float] = None


@dataclass
class WellData:
    row_label: str
    col_label: str
    well_id: str
    sample_id: Optional[str] = None
    code: Optional[str] = None
    status: str = EMPTY
    is_control: bool = False
    targets: Dict[str, TargetResult] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    # Campos para grupos de poços
    paired_wells: List[str] = field(default_factory=list)
    is_grouped: bool = False
    group_id: Optional[str] = None
    group_size: int = 1
    group_position: int = 0


class PlateModel:
    def __init__(self) -> None:
        self.wells: Dict[str, WellData] = {}
        self.group_dict: Dict[str, List[str]] = {}  # Novo: dicionário de grupos
        self.pair_groups: Dict[str, List[str]] = {}  # Legado: compatibilidade
        self.exam_type: str = "96"  # Tipo de exame: 96, 48, 32, 24 testes
        self.requires_group_frames: bool = False
        self.group_size: int = 1  # Mantido para compatibilidade
        self.exam_cfg: Optional[Any] = None

    # ------------------ construção a partir de df ------------------ #
    
    @classmethod
    def from_df(
        cls,
        df_final: pd.DataFrame,
        group_size: Optional[int] = None,
        exame: Optional[str] = None,
    ) -> "PlateModel":
        """
        Constrói o modelo de placa a partir dos dados da corrida.

        Aceita dois formatos:
        - df_final consolidado, com colunas Poço/Poco, Amostra, Código e Resultado_<ALVO>,
          mais colunas de CT por alvo (ex.: SC2, HMPV, INF A, INF B, ADV, RSV, HRV, RP_1, RP_2).
        - df_norm (linha por poço/alvo), com colunas WELL/well, SampleName, Target/target_name,
          CT/ct e possivelmente Resultado/resultado.
        
        Parâmetros:
            df_final: DataFrame com dados consolidados por poço
            group_size: Tamanho de grupo manual (sobrescreve inferência)
            exame: Nome do exame (para buscar config do registry)
        """
        model = cls()
        # se foi passado nome do exame, carregue a configuração correspondente
        if exame:
            try:
                model.exam_cfg = get_exam_cfg(exame)
            except Exception:
                model.exam_cfg = None

        # determina tamanho de grupo preferindo valor do registry se não fornecido
        if group_size is None and getattr(model, "exam_cfg", None) is not None:
            try:
                group_size = model.exam_cfg.bloco_size()
            except Exception:
                group_size = None
        model.group_size = group_size or 1
        if df_final is None or df_final.empty:
            return model
        
        # Carrega config do registry se exame foi fornecido
        exam_cfg = None
        if exame:
            try:
                exam_cfg = get_exam_cfg(exame)
            except Exception:
                exam_cfg = None

        df_use = df_final.copy()

        # Mapeia nomes de colunas para upper/lower
        cols_upper = {c: str(c).upper() for c in df_use.columns}
        cols_lower = {str(c).lower(): c for c in df_use.columns}

        # Se não houver coluna de poço estilo df_final, mas houver WELL, converte df_norm -> df_final-like
        has_poco = any(cu in {"POÇO", "POCO"} for cu in cols_upper.values())
        has_well = any(cu == "WELL" or cu == "WELL_ID" for cu in cols_upper.values())
        if not has_poco and has_well:
            df_use = cls._convert_df_norm(df_use)
            cols_upper = {c: str(c).upper() for c in df_use.columns}
            cols_lower = {str(c).lower(): c for c in df_use.columns}

        # ------------------ identificação de colunas básicas ------------------ #
        # Poço / Poco
        poco_col = None
        for key in ["poço", "poco", "well", "well_id"]:
            c = cols_lower.get(key)
            if c:
                poco_col = c
                break
        if poco_col is None:
            # sem coluna de poço não há como desenhar a placa
            return model

        # Amostra
        sample_col = None
        for key in ["amostra", "sample", "samplename", "sample_name"]:
            c = cols_lower.get(key)
            if c:
                sample_col = c
                break

        # Código
        code_col = None
        for key in ["código", "codigo", "code"]:
            c = cols_lower.get(key)
            if c:
                code_col = c
                break

        # Descobre targets a partir das colunas Resultado_*
        targets: List[str] = []
        for c in df_use.columns:
            cu = cols_upper[c]
            if cu.startswith("RESULTADO_"):
                alvo = cu.replace("RESULTADO_", "").strip()
                if alvo and alvo not in targets:
                    targets.append(alvo)
            elif cu.endswith(" - R") or cu.endswith("- R"):
                base = cu.replace(" - R", "").replace("- R", "").strip()
                if base and base not in targets:
                    targets.append(base)
        
        # DEBUG temporário
        print(f"DEBUG CSV: Colunas disponíveis: {list(df_use.columns[:20])}")
        print(f"DEBUG CSV: Targets descobertos: {targets}")
        print(f"DEBUG CSV: Total de linhas no DataFrame: {len(df_use)}")
        
        # Análise de valores CT disponíveis no DataFrame
        ct_analysis = {}
        for alvo in targets:
            ct_col = None
            for c in df_use.columns:
                cu = str(c).upper()
                if " - CT" in cu or "- CT" in cu:
                    base = cu.split(" - CT")[0].split("- CT")[0]
                    if base == alvo.upper():
                        ct_col = c
                        break
                elif cu.startswith("CT_"):
                    base = cu[3:]
                    if base == alvo.upper().replace(" ", ""):
                        ct_col = c
                        break
            
            if ct_col:
                # Contar valores não vazios de CT
                non_null = df_use[ct_col].notna().sum()
                ct_analysis[alvo] = {"coluna": ct_col, "valores_disponiveis": non_null}
            else:
                ct_analysis[alvo] = {"coluna": None, "valores_disponiveis": 0}
        
        print(f"DEBUG CSV: Análise de CT disponíveis:")
        for alvo, info in ct_analysis.items():
            print(f"  {alvo}: coluna='{info['coluna']}', valores={info['valores_disponiveis']}")
        
        if len(df_use) > 0:
            print(f"\nDEBUG CSV: Primeira linha - poco_col='{poco_col}', valor='{df_use.iloc[0].get(poco_col, 'N/A')}'")
            if sample_col:
                print(f"DEBUG CSV: Primeira linha - sample_col='{sample_col}', valor='{df_use.iloc[0].get(sample_col, 'N/A')}'")
            if code_col:
                print(f"DEBUG CSV: Primeira linha - code_col='{code_col}', valor='{df_use.iloc[0].get(code_col, 'N/A')}'")
            print()

        # Função de normalização para matching alvo vs coluna de CT
        def _norm_key(txt: str) -> str:
            return "".join(ch for ch in str(txt).upper() if ch.isalnum())

        def _find_ct_column_for_target(alvo: str) -> Optional[str]:
            """
            Procura coluna de CT compatível com o alvo, aceitando formatos:
            - Nome do alvo em si (ex.: SC2, HMPV, "INF A")
            - <ALVO> - CT (ex.: SC2 - CT)
            - CT_<ALVO> (ex.: CT_SC2, CT_INFA)
            """
            target_key = _norm_key(alvo)
            for c in df_use.columns:
                cu = str(c).upper()
                # ignora colunas de resultado
                if cu.startswith("RESULTADO_") or cu.endswith(" - R") or cu.endswith("- R"):
                    continue
                base = cu
                if " - CT" in base:
                    base = base.split(" - CT")[0]
                if base.startswith("CT_"):
                    base = base[3:]
                col_key = _norm_key(base)
                if col_key == target_key:
                    return c
            return None

        # Deduz tamanho de agrupamento se não vier
        model.group_size = group_size or cls._infer_group_size(df_use)

        # ------------------ construção dos poços ------------------ #
        for idx, row in df_use.iterrows():
            poco_raw = str(
                row.get("Poco", "")
                or row.get("POCO", "")
                or row.get(cols_lower.get("poco", ""), "")
                or row.get(poco_col, "")
            ).strip()
            if not poco_raw:
                continue

            # suporta múltiplos poços no mesmo registro (ex.: "A01+B01")
            pocos = [p.strip() for p in poco_raw.split("+") if p.strip()]
            if not pocos:
                continue

            sample = None
            if sample_col:
                sample = str(row.get(sample_col, "")).strip() or None

            # Detecta código preferindo campos usuais
            code = None
            code_candidates = []
            if code_col:
                code_candidates.append(row.get(code_col, ""))
            code_candidates.extend(
                [
                    row.get("Codigo", ""),
                    row.get("CÓDIGO", ""),
                    row.get("C�digo", ""),  # encoding antigo
                    row.get("CODE", ""),
                    sample,
                ]
            )
            for cval in code_candidates:
                s = str(cval).strip()
                if s:
                    code = s
                    break
            if code is None:
                code = sample

            # Resultados por alvo e CT
            target_data: Dict[str, TargetResult] = {}

            # Primeiro, CTs de RP (RP, RP_1, RP_2, ...)
            expected_rps = 0
            for c in df_use.columns:
                cu = cols_upper[c]
                if cu == "RP" or cu.startswith("RP_"):
                    expected_rps += 1
                    try:
                        ct_val = row.get(c, None)
                        if ct_val is not None and str(ct_val).strip() != "":
                            ct_val = float(str(ct_val).replace(",", "."))
                        else:
                            ct_val = None
                    except Exception:
                        ct_val = None
                    target_data[cu] = TargetResult("", ct_val)

            # Depois, alvos analíticos principais
            for alvo in targets:
                # resultado qualitativo - tentar múltiplos formatos
                res_val = ""
                
                # Formato 1: "Resultado_SC2"
                res_col = f"Resultado_{alvo}"
                if res_col in row:
                    res_val = row.get(res_col, "")
                
                # Formato 2: "SC2 - R"
                if not res_val:
                    alt_col = f"{alvo} - R"
                    if alt_col in row:
                        res_val = row.get(alt_col, "")
                
                # Formato 3: Coluna com nome do alvo contendo resultado completo
                # (ex: coluna "SC2" com valor "SC2 - 2")
                if not res_val:
                    if alvo in row:
                        res_val = row.get(alvo, "")
                
                norm_res = normalize_result(str(res_val))

                # CT associado
                ct_col = _find_ct_column_for_target(alvo)
                ct_val = None
                if ct_col is not None and ct_col in row:
                    try:
                        raw_ct = row.get(ct_col, None)
                        if raw_ct is not None and str(raw_ct).strip() != "":
                            ct_val = float(str(raw_ct).replace(",", "."))
                    except Exception:
                        ct_val = None

                target_data[alvo] = TargetResult(norm_res, ct_val)

            # Preenche wells (poços) e grupos
            normalized_pocos = []
            for poco in pocos:
                if len(poco) < 2:
                    continue
                row_label = poco[0].upper()
                col_label = poco[1:]
                try:
                    col_idx = int(col_label)
                    normalized_well = f"{row_label}{col_idx:02d}"
                    normalized_pocos.append(normalized_well)
                except Exception:
                    continue
            
            for idx_poco, well_id in enumerate(normalized_pocos):
                row_label = well_id[0]
                col_label = well_id[1:]

                if well_id not in model.wells:
                    wd = WellData(
                        row_label=row_label,
                        col_label=col_label,
                        well_id=well_id,
                        sample_id=sample or "",
                        code=code or "",
                        status=EMPTY,
                        is_control=False,
                        targets={},
                        metadata={},
                        paired_wells=[],
                        is_grouped=False,
                        group_id=None,
                        group_size=1,
                        group_position=0,
                    )
                    model.wells[well_id] = wd
                else:
                    wd = model.wells[well_id]
                    # Atualiza sample_id e code se ainda não tiverem sido definidos
                    if not wd.sample_id and sample:
                        wd.sample_id = sample
                    if not wd.code and code:
                        wd.code = code

                # merges targets (caso haja múltiplas linhas para o mesmo poço)
                for alvo, tr in target_data.items():
                    if alvo in wd.targets:
                        # mantém primeiro resultado, apenas atualiza CT se ainda não houver
                        if wd.targets[alvo].ct is None and tr.ct is not None:
                            wd.targets[alvo].ct = tr.ct
                    else:
                        wd.targets[alvo] = tr

                # grupos (pares/trios/quartetos) - sistema completo
                if len(normalized_pocos) > 1:
                    sorted_pocos = sorted(normalized_pocos)
                    group_id = "+".join(sorted_pocos)
                    wd.is_grouped = True
                    wd.group_id = group_id
                    wd.group_size = len(normalized_pocos)
                    wd.group_position = idx_poco
                    wd.paired_wells = [p for p in normalized_pocos if p != well_id]
                    # Adiciona ao group_dict
                    if group_id not in model.group_dict:
                        model.group_dict[group_id] = []
                    if well_id not in model.group_dict[group_id]:
                        model.group_dict[group_id].append(well_id)
                    # Mantém compatibilidade com sistema legado
                    wd.pair_group_id = group_id
                    model.pair_groups.setdefault(group_id, []).append(well_id)

                # Detecta controles usando cfg do exame quando disponível
                try:
                    ctrl = PlateModel._detect_control(wd.sample_id, wd.code, exam_cfg)
                    if ctrl:
                        wd.is_control = True
                        wd.metadata["control_type"] = ctrl
                    else:
                        wd.is_control = False
                        wd.metadata.pop("control_type", None)
                except Exception:
                    wd.is_control = False

                model._recompute_status(wd)
                model.wells[well_id] = wd

        # Define tamanho de bloco: prioritário é group_size, depois config do exame, por fim inferência
        if group_size:
            model.group_size = group_size
        elif exam_cfg:
            try:
                model.group_size = exam_cfg.bloco_size()
            except Exception:
                model.group_size = cls._infer_group_size(df_use)
        else:
            model.group_size = cls._infer_group_size(df_use)
        
        # Armazena config para uso em _recompute_status
        model.exam_cfg = exam_cfg
        
        # Determina tipo de exame e se requer frames de grupo
        model._determine_exam_type()
        model._determine_group_frame_requirement()
        
        return model
    @staticmethod
    def _convert_df_norm(df_norm: pd.DataFrame) -> pd.DataFrame:
        """
        Converte df_norm (linha por poço/target) em um df_final-like por poço,
        criando colunas Resultado_<ALVO> e CT_<ALVO>.
        """
        # normaliza nomes esperados (aliases)
        cols = {c.lower(): c for c in df_norm.columns}
        well_col = cols.get("well", cols.get("well_id", cols.get("poco", cols.get("poço", ""))))
        sample_col = cols.get("samplename", cols.get("sample_name", cols.get("amostra", cols.get("sample", ""))))
        code_col = cols.get("codigo", cols.get("code", sample_col))
        target_col = cols.get("target", cols.get("target name", cols.get("target_name", "")))
        ct_col = cols.get("ct", cols.get("ct_value", cols.get("ct_media", cols.get("ct mean", ""))))
        res_col = cols.get("resultado", cols.get("resultado_final", cols.get("result", "resultado")))

        records = []
        for _, r in df_norm.iterrows():
            w = str(r.get(well_col, "")).strip()
            if not w:
                continue
            sample = str(r.get(sample_col, "")).strip()
            code = str(r.get(code_col, sample)).strip()
            alvo = str(r.get(target_col, "")).strip()
            ct_val = r.get(ct_col, None)
            try:
                ct_val = float(str(ct_val).replace(",", "."))
            except Exception:
                ct_val = None
            res_val = r.get(res_col, "")
            records.append(
                {
                    "Poco": w,
                    "Amostra": sample,
                    "Codigo": code,
                    f"Resultado_{alvo}": normalize_result(res_val),
                    f"CT_{alvo}": ct_val,
                }
            )
        if not records:
            return pd.DataFrame()
        df_flat = pd.DataFrame(records)
        # agrega por poço mantendo primeiro valor para amostra/código e combinando colunas
        def _agg(series):
            # pega primeiro não vazio
            for v in series:
                if pd.notna(v) and str(v).strip():
                    return v
            return ""

        group_cols = [c for c in df_flat.columns if c.startswith("Resultado_") or c.startswith("CT_")]
        df_grouped = (
            df_flat.groupby("Poco")
            .agg({**{"Amostra": _agg, "Codigo": _agg}, **{c: _agg for c in group_cols}})
            .reset_index()
        )
        return df_grouped

    @staticmethod
    def _infer_group_size(df: pd.DataFrame) -> int:
        sizes = []
        for v in df.get("Poco", df.get("POCO", [])).fillna(""):
            if v:
                sizes.append(len(str(v).split("+")))
        if not sizes:
            return 1
        # pega o tamanho mais frequente
        return max(set(sizes), key=sizes.count)

    @staticmethod
    def _detect_control(sample: Optional[str], code: Optional[str], exam_cfg: Optional[Any] = None) -> Optional[str]:
        """
        Detecta se a amostra/código representa um controle.
        Primeiro tenta usar `exam_cfg.controles` (se fornecido), senão faz heurística por nomes comuns.
        Retorna 'CN' ou 'CP' ou None.
        """
        vals = []
        if sample:
            vals.append(str(sample).upper())
        if code:
            vals.append(str(code).upper())

        # se a config do exame fornece listas de controles, compare contra elas
        try:
            if exam_cfg and getattr(exam_cfg, "controles", None):
                cn_list = [str(x).upper() for x in (exam_cfg.controles.get("cn") or [])]
                cp_list = [str(x).upper() for x in (exam_cfg.controles.get("cp") or [])]
                for v in vals:
                    if v in cn_list:
                        return "CN"
                    if v in cp_list:
                        return "CP"
        except Exception:
            pass

        # Fallback heuristics
        for v in vals:
            if v in {"CN", "CONTROLE NEGATIVO", "C-", "NEGATIVO CONTROLE", "NEGATIVO", "CONTROLE N"}:
                return "CN"
            if v in {"CP", "CONTROLE POSITIVO", "C+", "POSITIVO CONTROLE", "POSITIVO", "CONTROLE P"}:
                return "CP"
        return None

    def _recompute_status(self, well: WellData) -> None:
        """Determina o status do poço baseado APENAS nos resultados textuais dos alvos."""
        if well.is_control:
            ctype = well.metadata.get("control_type", "")
            well.status = CONTROL_CN if ctype == "CN" else CONTROL_CP
            return

        has_pos = False
        has_inc = False
        has_nd = False
        
        # Analisar cada alvo (exceto RP)
        for alvo, tr in well.targets.items():
            if alvo.upper().startswith("RP"):
                continue
            
            # Analisar APENAS resultado textual
            u = tr.result.upper() if tr.result else ""
            
            if "DET" in u or "POS" in u:
                has_pos = True
            elif "INC" in u:
                has_inc = True
            elif "ND" in u:
                has_nd = True
        
        # Determinar status final
        if has_pos:
            well.status = POSITIVE
        elif has_inc:
            well.status = INCONCLUSIVE
        elif has_nd:
            well.status = NEGATIVE
        else:
            well.status = INVALID

    # utilidades
    def get_well(self, well_id: str) -> Optional[WellData]:
        return self.wells.get(well_id)

    def get_group(self, well_id: str) -> List[str]:
        """Retorna lista de poços no mesmo grupo (exceto o próprio well_id)"""
        w = self.get_well(well_id)
        if not w:
            return []
        # Suporta ambos os sistemas: novo (group_id) e legado (pair_group_id)
        if w.group_id:
            return [x for x in self.group_dict.get(w.group_id, []) if x != well_id]
        elif w.pair_group_id:
            return [x for x in self.pair_groups.get(w.pair_group_id, []) if x != well_id]
        return []
    
    def get_group_wells_including_self(self, well_id: str) -> List[str]:
        """Retorna todos os poços do grupo incluindo o próprio well_id"""
        w = self.get_well(well_id)
        if not w:
            return []
        if w.group_id:
            return self.group_dict.get(w.group_id, [])
        elif w.pair_group_id:
            return self.pair_groups.get(w.pair_group_id, [])
        return [well_id]

    def recompute_all(self) -> None:
        for w in self.wells.values():
            self._recompute_status(w)
    
    def _determine_exam_type(self) -> None:
        """Determina o tipo de exame (96, 48, 32, 24 testes) baseado nos tamanhos de grupo"""
        if not self.group_dict:
            self.exam_type = "96"
            return
        
        group_sizes = {}
        for wells in self.group_dict.values():
            size = len(wells)
            group_sizes[size] = group_sizes.get(size, 0) + 1
        
        if not group_sizes:
            self.exam_type = "96"
            return
        
        most_common_size = max(group_sizes, key=group_sizes.get)
        
        if most_common_size == 2:
            self.exam_type = "48"
        elif most_common_size == 3:
            self.exam_type = "32"
        elif most_common_size == 4:
            self.exam_type = "24"
        else:
            self.exam_type = "96"
    
    def _determine_group_frame_requirement(self) -> None:
        """Determina se é necessário criar frames de grupo com contorno"""
        self.requires_group_frames = self.exam_type in ["48", "32", "24"]


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------


def normalize_result(value: str) -> str:
    """Normaliza textos de resultado do CSV (ex: 'SC2 - 1', 'HMPV - 2')."""
    if not value:
        return ""
    
    txt = value.strip().upper()
    
    # Formato específico do CSV: "ALVO - NÚMERO" (ex: "SC2 - 1", "HMPV - 2")
    if " - " in txt:
        # Extrair o número após o hífen
        parts = txt.split(" - ")
        if len(parts) >= 2:
            num = parts[-1].strip()
            # Mapear números para resultados
            if num == "1":
                return "Det"      # Detectado
            elif num == "2":
                return "ND"       # Não Detectado
            else:
                return "Inc"      # Inconclusivo para outros números
    
    # Fallback para outras formatações
    # IMPORTANTE: Verificar termos mais específicos primeiro para evitar matches incorretos
    if any(k in txt for k in ["INC", "3"]):
        return "Inc"
    if any(k in txt for k in ["NAO DETECTADO", "NÃO DETECTADO", "NAO DETECTAVEL", "NÃO DETECTÁVEL"]):
        return "ND"
    if any(k in txt for k in ["DETECTADO", "DETECTAVEL", "DETECTÁVEL", "POSITIVO", "REAGENTE", "1"]):
        return "Det"
    if any(k in txt for k in ["NAO", "NÃO", "NEGATIVO", "ND", "2"]):
        return "ND"
    
    return txt


class WellButton(ctk.CTkButton):
    def __init__(self, master, well_id: str, text: str, color: str, on_click=None, **kwargs):
        super().__init__(master, **kwargs)
        self.well_id = well_id
        self.on_click_callback = on_click
        self.group_size = 1
        self.group_position = 0
        self.is_group_highlight = False
        
        # Configuração do botão
        self.configure(
            width=90,
            height=70,
            fg_color=color,
            text_color="black",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            corner_radius=5,
            border_width=2,
            border_color="#888888",
            text=self._truncate(text, 10),
            command=self._on_click
        )
    
    def _truncate(self, text: str, max_length: int) -> str:
        """Trunca texto se muito longo."""
        if len(text) > max_length:
            return text[:max_length-2] + ".."
        return text
    
    def _on_click(self):
        """Manipula clique no botão."""
        if self.on_click_callback:
            self.on_click_callback(self.well_id)

    def update_appearance(self, text: str, color: str, is_selected: bool, 
                         is_group_highlight: bool = False, group_size: int = 1,
                         group_position: int = 0):
        """Atualiza a aparência do botão."""
        # Atualizar cor de fundo e texto
        self.configure(
            fg_color=color,
            text=self._truncate(text, 10)
        )
        
        # Atualizar propriedades do grupo
        self.group_size = group_size
        self.group_position = group_position
        self.is_group_highlight = is_group_highlight
        
        # Definir borda com prioridades: selecionado > destaque de grupo > normal
        if is_selected:
            self.configure(border_color="#FF0000", border_width=3)  # Vermelho para selecionado
        elif is_group_highlight:
            # Cor específica para o tamanho do grupo
            group_color = GROUP_COLORS.get(group_size, "#00AA00")
            self.configure(border_color=group_color, border_width=2)
        else:
            # Para poços em grupos, manter borda normal
            if group_size > 1:
                self.configure(border_color="#888888", border_width=1)
            else:
                self.configure(border_color="#888888", border_width=2)


class GroupFrame(ctk.CTkFrame):
    """Frame que agrupa múltiplos poços para contorná-los juntos."""
    
    def __init__(self, master, group_size: int, border_color: str, corner_radius: int = 15):
        # Configurar o frame com borda de 10px
        super().__init__(
            master,
            fg_color="transparent",
            border_width=10,
            border_color=border_color,
            corner_radius=corner_radius
        )
        self.group_size = group_size
        
        # Ajustar o layout baseado no tamanho do grupo
        if group_size == 2:
            # Para pares, organizar horizontalmente (1x2)
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=1)
            self.grid_rowconfigure(0, weight=1)
        elif group_size == 3:
            # Para trios, organizar em linha (1x3)
            for i in range(3):
                self.grid_columnconfigure(i, weight=1)
            self.grid_rowconfigure(0, weight=1)
        elif group_size == 4:
            # Para quartetos, organizar em 2x2
            for i in range(2):
                self.grid_columnconfigure(i, weight=1)
                self.grid_rowconfigure(i, weight=1)
    
    def get_position_in_group(self, position: int) -> tuple:
        """Retorna (row, col) dentro do GroupFrame baseado na posição do poço no grupo."""
        if self.group_size == 2:
            # Par: posição 0 -> (0, 0), posição 1 -> (0, 1)
            return (0, position)
        elif self.group_size == 3:
            # Trio: posição 0 -> (0, 0), posição 1 -> (0, 1), posição 2 -> (0, 2)
            return (0, position)
        elif self.group_size == 4:
            # Quarteto 2x2: posição 0 -> (0, 0), posição 1 -> (0, 1), posição 2 -> (1, 0), posição 3 -> (1, 1)
            return (position // 2, position % 2)
        return (0, 0)


class PlateView(ctk.CTkFrame):
    def __init__(self, master, plate_model: PlateModel, meta: Dict[str, str]):
        super().__init__(master)
        self.plate_model = plate_model
        self.meta = meta or {}
        self.selected_well_id: Optional[str] = None
        self.current_target: Optional[str] = None
        self.highlight_group: List[str] = []
        self.group_wells_highlight: List[str] = []  # Lista para destacar grupo
        self.group_size_highlight: int = 1
        self.well_widgets: Dict[str, WellButton] = {}
        self.group_frames: Dict[str, GroupFrame] = {}

        self._build_ui()
        self.render_plate()

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=0)

        # Cabeçalho (compacto) - espaçamento mínimo superior
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 1), padx=5)
        header.grid_columnconfigure(4, weight=1)
        infos = [
            f"Data: {self.meta.get('data', '')}",
            f"Extração: {self.meta.get('extracao', self.meta.get('arquivo', ''))}",
            f"Exame: {self.meta.get('exame', '')}",
            f"Usuário: {self.meta.get('usuario', '')}",
            f"Tamanho bloco: {self.plate_model.group_size} (tot amostras: {self._calc_total_samples()})",
        ]
        for i, txt in enumerate(infos):
            ctk.CTkLabel(header, text=txt, font=("", 10, "bold")).grid(row=0, column=i, padx=3, pady=1, sticky="w")

        # Container placa - espaçamento reduzido para aumentar área visível
        plate_container = ctk.CTkFrame(self)
        plate_container.grid(row=1, column=0, padx=5, pady=(1, 3), sticky="nsew")
        plate_container.grid_rowconfigure(0, weight=1)
        plate_container.grid_columnconfigure(0, weight=1)

        self.plate_frame = ctk.CTkFrame(plate_container)
        self.plate_frame.grid(row=0, column=0, sticky="nsew")

        # Títulos colunas
        font_labels = ctk.CTkFont(family="Segoe UI", size=11, weight="bold")
        ctk.CTkLabel(self.plate_frame, text="", width=30, height=30).grid(row=0, column=0, padx=1, pady=1)
        for j, col in enumerate(COL_LABELS, start=1):
            label = ctk.CTkLabel(
                self.plate_frame, 
                text=col, 
                font=font_labels,
                width=90,
                height=30
            )
            label.grid(row=0, column=j, padx=1, pady=1)
        
        # Rótulos de linha
        for i, row_lbl in enumerate(ROW_LABELS, start=1):
            label = ctk.CTkLabel(
                self.plate_frame,
                text=row_lbl,
                font=font_labels,
                width=30,
                height=50
            )
            label.grid(row=i, column=0, padx=1, pady=1)

        # Criar frames de grupo se necessário
        if self.plate_model.requires_group_frames:
            print(f"DEBUG: Criando group frames. group_dict={len(self.plate_model.group_dict)} grupos")
            self._create_group_frames()
        else:
            print(f"DEBUG: requires_group_frames=False. exam_type={self.plate_model.exam_type}")
        
        # Criar botões de poços
        print(f"DEBUG: Total wells={len(self.plate_model.wells)}")
        self._create_well_buttons()

    def _create_group_frames(self):
        """Cria frames com bordas coloridas para agrupar poços."""
        for group_id, wells in self.plate_model.group_dict.items():
            if not wells:
                continue
            
            # Determinar tamanho do grupo
            group_size = len(wells)
            if group_size not in GROUP_COLORS:
                continue
            
            color = GROUP_COLORS[group_size]
            
            # Calcular posição mínima e máxima do grupo
            rows = [ROW_LABELS.index(w[0]) for w in wells]
            # Remover zeros à esquerda da coluna (A01 -> 1, A12 -> 12)
            cols = [COL_LABELS.index(str(int(w[1:]))) for w in wells]
            min_row = min(rows)
            max_row = max(rows)
            min_col = min(cols)
            max_col = max(cols)
            
            # Determinar corner_radius baseado no tamanho do grupo
            corner_radius_map = {2: 12, 3: 15, 4: 18}
            corner_radius = corner_radius_map.get(group_size, 15)
            
            # Criar o GroupFrame
            group_frame = GroupFrame(
                self.plate_frame,
                group_size=group_size,
                border_color=color,
                corner_radius=corner_radius
            )
            
            # Posicionar no grid (+1 para compensar os labels)
            group_frame.grid(
                row=min_row + 1,
                column=min_col + 1,
                rowspan=max_row - min_row + 1,
                columnspan=max_col - min_col + 1,
                padx=1,
                pady=1,
                sticky="nsew"
            )
            
            self.group_frames[group_id] = group_frame

    def _create_well_buttons(self):
        """Cria todos os botões de poços, usando frames de grupo quando necessário."""
        for i, row_lbl in enumerate(ROW_LABELS):
            for j, col_lbl in enumerate(COL_LABELS):
                # Criar well_id com zero à esquerda (A01, A02, etc)
                well_id = f"{row_lbl}{int(col_lbl):02d}"
                well = self.plate_model.get_well(well_id)
                
                # Preparar texto do botão
                text = ""
                if well:
                    text = well.code or well.sample_id or ""
                    if text and well.is_control:
                        ct_type = well.metadata.get("control_type", "")
                        if ct_type:
                            text = f"{ct_type}:{text}"
                
                # Determinar cor baseada no status
                color = STATUS_COLORS.get(well.status if well else EMPTY, "#ffffff")
                
                # Determinar frame pai e posição no grid
                if well and well.is_grouped and self.plate_model.requires_group_frames:
                    parent_frame = self.group_frames.get(well.group_id)
                    if parent_frame:
                        # Calcular posição dentro do grupo
                        grid_row, grid_col = parent_frame.get_position_in_group(well.group_position)
                        grid_kwargs = {"row": grid_row, "column": grid_col}
                    else:
                        # Fallback se não encontrar o frame
                        parent_frame = self.plate_frame
                        grid_kwargs = {"row": i + 1, "column": j + 1}
                else:
                    parent_frame = self.plate_frame
                    grid_kwargs = {"row": i + 1, "column": j + 1}
                
                # Criar botão
                btn = WellButton(parent_frame, well_id, text, color, on_click=self.on_well_click)
                btn.grid(padx=1, pady=1, sticky="nsew", **grid_kwargs)
                self.well_widgets[well_id] = btn

        # Painel lateral - aumentado para 340px para acomodar melhor as colunas do TreeView
        self.detail_frame = ctk.CTkFrame(self, width=340)
        self.detail_frame.grid(row=1, column=1, padx=(0, 20), pady=(1, 3), sticky="nsew")
        self.detail_frame.grid_propagate(False)

        for i in range(10):
            self.detail_frame.grid_rowconfigure(i, weight=0)
        self.detail_frame.grid_rowconfigure(6, weight=1)

        title_font = ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        ctk.CTkLabel(self.detail_frame, text="Poço selecionado:", font=title_font).grid(
            row=0, column=0, columnspan=2, pady=(4, 1), padx=5, sticky="w"
        )

        f_label = ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        f_val = ctk.CTkFont(family="Segoe UI", size=12)

        ctk.CTkLabel(self.detail_frame, text="Poço:", font=f_label).grid(row=1, column=0, padx=(5, 3), pady=1, sticky="e")
        self.lbl_well = ctk.CTkLabel(self.detail_frame, text="-", font=f_val)
        self.lbl_well.grid(row=1, column=1, padx=(3, 5), pady=1, sticky="w")

        ctk.CTkLabel(self.detail_frame, text="Amostra:", font=f_label).grid(row=2, column=0, padx=(5, 3), pady=1, sticky="e")
        self.lbl_sample = ctk.CTkLabel(self.detail_frame, text="-", font=f_val)
        self.lbl_sample.grid(row=2, column=1, padx=(3, 5), pady=1, sticky="w")

        ctk.CTkLabel(self.detail_frame, text="Código:", font=f_label).grid(row=3, column=0, padx=(5, 3), pady=1, sticky="e")
        code_frame = ctk.CTkFrame(self.detail_frame, fg_color="transparent")
        code_frame.grid(row=3, column=1, padx=(3, 5), pady=1, sticky="ew")
        code_frame.grid_columnconfigure(0, weight=1)
        self.entry_code = ctk.CTkEntry(code_frame, font=f_val, height=35)
        self.entry_code.grid(row=0, column=0, sticky="ew", padx=(0, 3))
        ctk.CTkButton(code_frame, text="✓", width=40, height=35, font=f_val, command=self.apply_code_change).grid(
            row=0, column=1
        )

        ctk.CTkLabel(self.detail_frame, text="Poços agrupados:", font=f_label).grid(
            row=4, column=0, padx=(5, 3), pady=1, sticky="e"
        )
        self.lbl_group = ctk.CTkLabel(self.detail_frame, text="-", font=f_val)
        self.lbl_group.grid(row=4, column=1, padx=(3, 5), pady=1, sticky="w")

        ctk.CTkLabel(self.detail_frame, text="Resultados:", font=f_label).grid(
            row=5, column=0, columnspan=2, padx=5, pady=(1, 1), sticky="w"
        )

        tree_frame = ctk.CTkFrame(self.detail_frame)
        tree_frame.grid(row=6, column=0, columnspan=2, padx=5, pady=(0, 5), sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            foreground="black",
            background="white",
            fieldbackground="white",
            font=("Segoe UI", 15),
            rowheight=42,
        )
        style.configure("Treeview.Heading", foreground="black", background="#f0f0f0", font=("Segoe UI", 15, "bold"))
        self.tree = ttk.Treeview(tree_frame, columns=("alvo", "resultado", "ct"), show="headings", selectmode="browse", height=28)
        self.tree.heading("alvo", text="Alvo")
        self.tree.heading("resultado", text="Resultado")
        self.tree.heading("ct", text="CT")
        self.tree.column("alvo", width=65, anchor="w")
        self.tree.column("resultado", width=95, anchor="center")
        self.tree.column("ct", width=70, anchor="center")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        edit_frame = ctk.CTkFrame(self.detail_frame)
        edit_frame.grid(row=7, column=0, columnspan=2, padx=5, pady=(1, 3), sticky="ew")
        edit_frame.grid_columnconfigure(1, weight=1)
        edit_frame.grid_columnconfigure(3, weight=1)
        
        # Campo de Alvo (editável)
        ctk.CTkLabel(edit_frame, text="Alvo:", font=f_label).grid(row=0, column=0, padx=3, pady=3, sticky="e")
        self.entry_target = ctk.CTkEntry(edit_frame, width=120, font=f_val, height=35)
        self.entry_target.grid(row=0, column=1, padx=3, pady=3, sticky="ew")
        
        # Campo de Resultado
        ctk.CTkLabel(edit_frame, text="Resultado:", font=f_label).grid(row=1, column=0, padx=3, pady=3, sticky="e")
        self.entry_res = ctk.CTkEntry(edit_frame, width=90, font=f_val, height=35)
        self.entry_res.grid(row=1, column=1, padx=3, pady=3, sticky="ew")
        
        # Campo de CT
        ctk.CTkLabel(edit_frame, text="CT:", font=f_label).grid(row=1, column=2, padx=(5, 3), pady=3, sticky="e")
        self.entry_ct = ctk.CTkEntry(edit_frame, width=90, font=f_val, height=35)
        self.entry_ct.grid(row=1, column=3, padx=3, pady=3, sticky="ew")
        
        ctk.CTkButton(
            edit_frame, text="Aplicar", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), height=38, command=self.apply_target_changes
        ).grid(row=2, column=0, columnspan=4, pady=(5, 3))

        ctk.CTkButton(
            self.detail_frame,
            text="Salvar edições (apenas memória)",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=40,
            command=self._on_save_clicked,
        ).grid(row=8, column=0, columnspan=2, padx=5, pady=(0, 4))

    def _calc_total_samples(self) -> int:
        # total de grupos = total_wells / group_size
        if not self.plate_model.wells:
            return 0
        return math.ceil(len(self.plate_model.wells) / max(1, self.plate_model.group_size))

    def _status_color(self, status: str) -> str:
        return STATUS_COLORS.get(status, "#ffffff")

    # ------------------ interação ------------------ #
    def on_well_click(self, well_id: str) -> None:
        self.selected_well_id = well_id
        
        # Obter informações do grupo
        well = self.plate_model.get_well(well_id)
        if well and well.is_grouped:
            group_wells = self.plate_model.get_group_wells_including_self(well_id)
            self.group_wells_highlight = set(group_wells)
            self.group_size_highlight = well.group_size
        else:
            self.group_wells_highlight = set()
            self.group_size_highlight = 0
        
        self.render_plate()
        if well:
            self._fill_details(well)

    def render_plate(self):
        for well_id, btn in self.well_widgets.items():
            well = self.plate_model.get_well(well_id)
            text = ""
            if well:
                text = well.code or well.sample_id or ""
                if text and well.is_control:
                    ctype = well.metadata.get("control_type", "")
                    if ctype:
                        text = f"{ctype}:{text}"
            
            color = self._status_color(well.status if well else EMPTY)
            is_selected = (well_id == self.selected_well_id)
            is_group_highlight = (well_id in self.group_wells_highlight)
            
            # Passar informações de grupo para o botão
            group_size = 0
            group_position = 0
            if well and well.is_grouped:
                group_size = well.group_size
                group_position = well.group_position
            
            btn.update_appearance(text, color, is_selected, is_group_highlight, group_size, group_position)

    def _fill_details(self, well: WellData):
        self.lbl_well.configure(text=well.well_id)
        self.lbl_sample.configure(text=well.sample_id or "-")
        self.entry_code.delete(0, tk.END)
        if well.code:
            self.entry_code.insert(0, well.code)
        self.lbl_group.configure(text=", ".join(well.paired_wells) if well.paired_wells else "-")

        self.tree.delete(*self.tree.get_children())
        # ordenar alvos: primeiro não-RP, depois RPs
        def _sort_key(item):
            name = item[0]
            is_rp = name.upper().startswith("RP")
            return (1 if is_rp else 0, name)

        for alvo, tr in sorted(well.targets.items(), key=_sort_key):
            # Usar vírgula como separador decimal
            ct_txt = "" if tr.ct is None else f"{tr.ct:.3f}".replace(".", ",")
            item_id = self.tree.insert("", "end", values=(alvo, tr.result, ct_txt))
            self.tree.item(item_id, tags=(alvo,))
        self.entry_target.delete(0, tk.END)
        self.entry_res.delete(0, tk.END)
        self.entry_ct.delete(0, tk.END)
        self.current_target = None

    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            self.current_target = None
            return
        vals = self.tree.item(sel[0], "values")
        if not vals:
            return
        self.current_target = vals[0]
        
        # Popular campo de alvo
        self.entry_target.delete(0, tk.END)
        self.entry_target.insert(0, vals[0])
        
        # Popular campo de resultado
        self.entry_res.delete(0, tk.END)
        self.entry_res.insert(0, vals[1])
        
        # Popular campo de CT (já está com vírgula)
        self.entry_ct.delete(0, tk.END)
        self.entry_ct.insert(0, vals[2])

    def apply_code_change(self):
        if not self.selected_well_id:
            return
        well = self.plate_model.get_well(self.selected_well_id)
        if not well:
            return
        new_code = self.entry_code.get().strip()
        well.code = new_code or None
        ctrl = PlateModel._detect_control(well.sample_id, well.code, self.plate_model.exam_cfg)
        if ctrl:
            well.is_control = True
            well.metadata["control_type"] = ctrl
        else:
            well.is_control = False
            well.metadata.pop("control_type", None)
        # se code mudou, propaga para wells do mesmo grupo (mesma amostra)
        group_wells = self.plate_model.get_group_wells_including_self(well.well_id)
        for wid in group_wells:
            if wid == well.well_id:
                continue
            w2 = self.plate_model.get_well(wid)
            if w2:
                w2.code = well.code
                w2.sample_id = well.sample_id
                if ctrl:
                    w2.is_control = True
                    w2.metadata["control_type"] = ctrl
                else:
                    w2.is_control = False
                    w2.metadata.pop("control_type", None)
                self.plate_model._recompute_status(w2)

        self.plate_model._recompute_status(well)
        self.render_plate()

    def apply_target_changes(self):
        if not self.selected_well_id or not self.current_target:
            return
        well = self.plate_model.get_well(self.selected_well_id)
        if not well:
            return
        
        # Obter valores originais para comparação
        original_target = well.targets.get(self.current_target)
        original_res = original_target.result if original_target else ""
        original_ct = original_target.ct if original_target else None
        
        # Obter novos valores
        new_target_name = self.entry_target.get().strip()
        new_res = normalize_result(self.entry_res.get())
        ct_text = self.entry_ct.get().strip()
        new_ct = None
        if ct_text:
            try:
                # Aceitar tanto vírgula quanto ponto como separador decimal
                new_ct = float(ct_text.replace(",", "."))
            except Exception:
                new_ct = None
        
        # Se apenas o CT foi alterado (resultado não mudou), reavaliar o resultado baseado no CT
        if new_res == normalize_result(original_res) and new_ct != original_ct and new_ct is not None:
            # Reanalisar resultado baseado no novo CT
            # Regras básicas: CT < 35 = Detectado, CT >= 35 = Inconclusivo, sem CT = não detectado
            if new_ct < 35:
                new_res = "Det"
            elif new_ct >= 35:
                new_res = "Inc"
        
        # Se o nome do alvo mudou, remover o antigo
        if new_target_name and new_target_name != self.current_target:
            if self.current_target in well.targets:
                del well.targets[self.current_target]
        
        # Atualizar o alvo (novo ou existente)
        target_key = new_target_name if new_target_name else self.current_target
        well.targets[target_key] = TargetResult(new_res, new_ct)
        
        # Reanalisar este poço pelas regras
        self.plate_model._recompute_status(well)
        
        # Propagar mudanças para todos os poços do grupo
        if well.is_grouped:
            group_wells = self.plate_model.get_group_wells_including_self(self.selected_well_id)
            for well_id in group_wells:
                if well_id == self.selected_well_id:
                    continue  # Já atualizamos o poço atual
                w2 = self.plate_model.get_well(well_id)
                if w2:
                    # Obter valores originais do poço do grupo
                    original_target_w2 = w2.targets.get(self.current_target)
                    original_res_w2 = original_target_w2.result if original_target_w2 else ""
                    original_ct_w2 = original_target_w2.ct if original_target_w2 else None
                    
                    # Aplicar a mesma lógica de reanálise se apenas CT mudou
                    new_res_w2 = new_res
                    if normalize_result(original_res_w2) == normalize_result(original_res) and new_ct != original_ct_w2 and new_ct is not None:
                        if new_ct < 35:
                            new_res_w2 = "Det"
                        elif new_ct >= 35:
                            new_res_w2 = "Inc"
                    
                    # Se o nome do alvo mudou, remover o antigo
                    if new_target_name and new_target_name != self.current_target:
                        if self.current_target in w2.targets:
                            del w2.targets[self.current_target]
                    
                    # Atualizar o alvo no poço do grupo
                    w2.targets[target_key] = TargetResult(new_res_w2, new_ct)
                    
                    # Reanalisar este poço também
                    self.plate_model._recompute_status(w2)
        
        # Atualizar o current_target para o novo nome
        self.current_target = target_key
        
        # Atualizar interface
        self._fill_details(well)
        self.render_plate()

    def _on_save_clicked(self):
        # No-op placeholder: salvamento persistente pode ser implementado depois
        self.plate_model.recompute_all()
        self.render_plate()


class PlateWindow(ctk.CTkToplevel):
    def __init__(self, root, plate_model: PlateModel, meta: Dict[str, str]):
        super().__init__(master=root)
        self.title("Visualização da Placa")
        
        # Definir tamanho inicial (90% da tela para maximizar área da placa)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Proteção contra TclError ao fechar
        self._is_closing = False
        self.protocol("WM_DELETE_WINDOW", self._on_close_window)
        
        view = PlateView(self, plate_model, meta)
        view.pack(fill="both", expand=True, padx=5, pady=3)
    
    def _on_close_window(self):
        """Fecha a janela com segurança."""
        if not self._is_closing:
            self._is_closing = True
            try:
                self.grab_release()
                self.destroy()
            except Exception:
                pass


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------


def abrir_placa_ctk(df_final: pd.DataFrame, meta_extra: Optional[Dict[str, Any]] = None, group_size: Optional[int] = None, parent=None):
    """
    Abre a janela CTk para visualização/edição da placa usando df_final em memória.
    meta_extra pode conter data, extracao/arquivo, exame, usuario.
    """
    try:
        print(f"DEBUG abrir_placa_ctk: DataFrame shape={df_final.shape if df_final is not None else 'None'}")
        
        if df_final is None or df_final.empty:
            print("DEBUG abrir_placa_ctk: DataFrame vazio ou None")
            return
        
        meta = meta_extra or {}
        # garantir chaves esperadas
        meta.setdefault("data", meta.get("data_placa", ""))
        meta.setdefault("extracao", meta.get("arquivo_corrida", meta.get("extracao", "")))
        meta.setdefault("exame", meta.get("exame", ""))
        meta.setdefault("usuario", meta.get("usuario", ""))
        
        print(f"DEBUG abrir_placa_ctk: meta={meta}, group_size={group_size}")
        
        # Passa exame para PlateModel.from_df para carregação do registry
        exame = meta.get("exame", "")
        
        print(f"DEBUG abrir_placa_ctk: Criando PlateModel.from_df...")
        plate_model = PlateModel.from_df(df_final, group_size=group_size, exame=exame)
        
        print(f"DEBUG abrir_placa_ctk: PlateModel criado, wells={len(plate_model.wells)}")
        
        print(f"DEBUG abrir_placa_ctk: Criando PlateWindow...")
        win = PlateWindow(parent or ctk.CTk(), plate_model, meta)
        win.focus_force()
        
        print(f"DEBUG abrir_placa_ctk: PlateWindow criada com sucesso")
        return win
    except Exception as e:
        print(f"DEBUG abrir_placa_ctk: ERRO - {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise


# Compatibilidade legada: funções vazias (Excel removido nesta fase)
def construir_well_results(*args, **kwargs):
    raise NotImplementedError("Função legada não suportada nesta versão.")


def exportar_placa_excel(*args, **kwargs):
    raise NotImplementedError("Exportação Excel desativada nesta versão interativa.")


def mostrar_placa_gui(*args, **kwargs):
    # wrapper simples para seguir nomes antigos
    return abrir_placa_ctk(*args, **kwargs)


# Configuração inicial do tema
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

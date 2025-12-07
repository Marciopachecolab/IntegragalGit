"""
Visualização interativa da placa (CustomTkinter) consumindo dados em memória
vindo da análise (df_final/df_norm). Inspirado em services/teste_plate_viewer_historico_ctk.py,
mas sem ler CSV e sem exportar XLS automaticamente.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import customtkinter as ctk
import pandas as pd
import tkinter as tk
from tkinter import ttk

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
    INCONCLUSIVE: "#ffe89a",  # amarelo
    INVALID: "#f0f0f0",  # cinza
    CONTROL_CN: "#b3d9ff",  # azul claro
    CONTROL_CP: "#b3d9ff",
    EMPTY: "#ffffff",  # branco
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
    paired_wells: List[str] = field(default_factory=list)
    pair_group_id: Optional[str] = None


class PlateModel:
    def __init__(self) -> None:
        self.wells: Dict[str, WellData] = {}
        self.pair_groups: Dict[str, List[str]] = {}
        self.group_size: int = 1
    # ------------------ carregamento direto do CSV de histórico ------------------ #
    @classmethod
    def from_historico_csv(
        cls,
        csv_path: str,
        sep: str = ';',
        exame: Optional[str] = None,
        arquivo_corrida: Optional[str] = None,
        group_size: Optional[int] = None,
    ) -> 'PlateModel':
        """
        Lê reports/historico_analises.csv (ou similar), aplica filtros opcionais
        e reaproveita a lógica de from_df.
        """
        try:
            df = pd.read_csv(csv_path, sep=sep, dtype=str)
        except Exception:
            return cls()
        if df.empty:
            return cls()

        # filtros opcionais
        if exame is not None and 'exame' in df.columns:
            df = df[df['exame'] == exame]
        if arquivo_corrida is not None and 'arquivo_corrida' in df.columns:
            df = df[df['arquivo_corrida'] == arquivo_corrida]
        if df.empty:
            return cls()

        df_use = df.copy()
        # renomeia para colunas esperadas por from_df
        if 'poco' in df_use.columns:
            df_use['Poco'] = df_use['poco']
        if 'amostra' in df_use.columns:
            df_use['Amostra'] = df_use['amostra']
        if 'codigo' in df_use.columns:
            df_use['Codigo'] = df_use['codigo']

        return cls.from_df(df_use, group_size=group_size)

    # ------------------ construção a partir de df ------------------ #
    @classmethod
    def from_df(
        cls,
        df_final: pd.DataFrame,
        group_size: Optional[int] = None,
    ) -> "PlateModel":
        """
        Aceita dois formatos:
        - df_final consolidado com colunas Poco/Amostra/Codigo/Resultado_<ALVO>.
        - df_norm (por poço/target) com colunas WELL/SampleName/Target/CT/Resultado (qualquer variação).
        """
        model = cls()
        if df_final is None or df_final.empty:
            return model

        df_use = df_final.copy()
        cols_upper = {c: str(c).upper() for c in df_use.columns}
        cols_lower = {str(c).lower(): c for c in df_use.columns}

        # Se não houver coluna Poco mas houver WELL, converte df_norm -> df_final-like
        if not any(cu in {"POCO", "POCO"} for cu in cols_upper.values()) and "WELL" in cols_upper.values():
            df_use = cls._convert_df_norm(df_use)
            cols_upper = {c: str(c).upper() for c in df_use.columns}
            cols_lower = {str(c).lower(): c for c in df_use.columns}

        # Detecta alvos pelas colunas "RESULTADO_<ALVO>" ou "<ALVO> - R" (formato histórico)
        targets: List[str] = []
        for col in df_use.columns:
            cu = cols_upper[col]
            if cu.startswith("RESULTADO_"):
                alvo = cu.replace("RESULTADO_", "").strip().replace(" ", "")
                if alvo:
                    targets.append(alvo)
            elif cu.endswith(" - R") or cu.endswith("- R") or cu.endswith(" - R".upper()):
                # exemplo: "SC2 - R"
                base = cu.replace(" - R", "").replace("- R", "").strip().replace(" ", "")
                if base and base not in targets:
                    targets.append(base)

        # Deduz tamanho de agrupamento se não vier
        group_size = group_size or cls._infer_group_size(df_use)
        model.group_size = group_size

        for _, row in df_use.iterrows():
            # Poço / amostra / código (aceita minúsculas)
            poco_raw = str(
                row.get("Poco", "")
                or row.get("POCO", "")
                or row.get(cols_lower.get("poco", ""), "")
            ).strip()
            if not poco_raw:
                continue
            pocos = [p.strip() for p in poco_raw.split("+") if p.strip()]
            sample = str(
                row.get("Amostra", "")
                or row.get("AMOSTRA", "")
                or row.get(cols_lower.get("amostra", ""), "")
            ).strip() or None
            # Detecta código preferindo campos usuais
            code_candidates = [
                row.get("Codigo", ""),
                row.get("CODIGO", ""),
                row.get("code", ""),
                row.get("sample_code", ""),
                row.get(cols_lower.get("codigo", ""), ""),
                row.get(cols_lower.get("amostra", ""), ""),
            ]
            code = None
            for cval in code_candidates:
                s = str(cval).strip()
                if s:
                    code = s
                    break
            if code is None:
                code = sample

            # Prepara resultados por alvo
            target_data: Dict[str, TargetResult] = {}
            # RPs por CT (RP, RP_1, RP_2, ...)
            rp_ct_cols = []
            for c in df_use.columns:
                cu = cols_upper.get(c, "")
                if ("RP" in cu) and ("CT" in cu) and (not cu.startswith("CT_RP")):
                    rp_ct_cols.append(c)
            for rp_col in rp_ct_cols:
                try:
                    ct_val = row.get(rp_col, None)
                    ct_val = float(str(ct_val).replace(",", "."))
                except Exception:
                    ct_val = None
                rp_key = rp_col.split()[0].upper().replace("-", "_").replace(" ", "_")
                target_data[rp_key] = TargetResult("", ct_val)
            # Garante placeholder de RPs conforme group_size
            expected_rps = 1
            if model.group_size == 2:
                expected_rps = 2
            elif model.group_size == 3:
                expected_rps = 3
            elif model.group_size == 4:
                expected_rps = 4
            rp_names = [f"RP_{i}" for i in range(1, expected_rps + 1)] if expected_rps > 1 else ["RP_1"]
            for rp_name in rp_names:
                if rp_name not in target_data:
                    target_data[rp_name] = TargetResult("", None)

            for alvo in targets:
                # tenta formato Resultado_<ALVO>, sen?o <ALVO> - R
                res_col = f"Resultado_{alvo}"
                res_val = row.get(res_col, "")
                if not res_val:
                    alt_col = f"{alvo} - R"
                    res_val = row.get(alt_col, "")
                norm_res = normalize_result(str(res_val))

                # heur?stica para CT: procura colunas que contenham o alvo e "CT"
                ct_val = None
                for c in df_use.columns:
                    cu = cols_upper[c]
                    val_str = str(row.get(c, "")).strip()
                    if not val_str:
                        continue
                    if alvo in cu.replace(" ", "") and "CT" in cu:
                        try:
                            ct_val = float(val_str.replace(",", "."))
                        except Exception:
                            ct_val = None
                        break
                    if cu == f"CT_{alvo}".upper():
                        try:
                            ct_val = float(val_str.replace(",", "."))
                        except Exception:
                            ct_val = None
                        break
                if ct_val is None and "RP_1" in target_data:
                    ct_val = target_data["RP_1"].ct
                target_data[alvo] = TargetResult(norm_res, ct_val)
            for poco in pocos:
                if len(poco) < 2:
                    continue
                row_label = poco[0].upper()
                col_label = poco[1:]
                if row_label not in ROW_LABELS or col_label not in COL_LABELS:
                    continue
                well_id = f"{row_label}{col_label}"
                if well_id in model.wells:
                    continue

                wd = WellData(
                    row_label=row_label,
                    col_label=col_label,
                    well_id=well_id,
                    sample_id=sample,
                    code=code,
                    targets=target_data.copy(),
                )

                ctrl = cls._detect_control(sample, code)
                if ctrl:
                    wd.is_control = True
                    wd.metadata["control_type"] = ctrl

                # grupos (pares/trios/quartetos)
                if len(pocos) > 1:
                    group_id = "+".join(sorted(pocos))
                    wd.paired_wells = [p for p in pocos if p != poco]
                    wd.pair_group_id = group_id
                    model.pair_groups.setdefault(group_id, []).append(well_id)

                model._recompute_status(wd)
                model.wells[well_id] = wd

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
    def _detect_control(sample: Optional[str], code: Optional[str]) -> Optional[str]:
        vals = []
        if sample:
            vals.append(sample.upper())
        if code:
            vals.append(code.upper())
        for v in vals:
            if v in {"CN", "CONTROLE NEGATIVO", "C-", "NEGATIVO CONTROLE", "NEGATIVO", "CONTROLE N"}:
                return "CN"
            if v in {"CP", "CONTROLE POSITIVO", "C+", "POSITIVO CONTROLE", "POSITIVO", "CONTROLE P"}:
                return "CP"
        return None

    def _recompute_status(self, well: WellData) -> None:
        if well.is_control:
            ctype = well.metadata.get("control_type", "")
            well.status = CONTROL_CN if ctype == "CN" else CONTROL_CP
            return

        has_pos = False
        has_inc = False
        has_nd = False
        for alvo, tr in well.targets.items():
            if alvo.upper().startswith("RP"):
                continue
            u = tr.result.upper()
            if "DET" in u or "POS" in u:
                has_pos = True
            elif "INC" in u:
                has_inc = True
            elif "ND" in u or "NAO" in u or "NÃO" in u:
                has_nd = True
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
        w = self.get_well(well_id)
        if not w or not w.pair_group_id:
            return []
        return [x for x in self.pair_groups.get(w.pair_group_id, []) if x != well_id]

    def recompute_all(self) -> None:
        for w in self.wells.values():
            self._recompute_status(w)


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------


def normalize_result(value: str) -> str:
    if not value:
        return ""
    txt = str(value).strip().upper()
    if " - " in txt:
        parts = txt.split(" - ")
        if len(parts) >= 2:
            num = parts[-1].strip()
            if num == "1":
                return "Det"
            if num == "2":
                return "ND"
            if num == "3":
                return "Inc"
    if any(k in txt for k in ["DET", "POS", "REAG", "1"]):
        return "Det"
    if any(k in txt for k in ["NAO", "NÃO", "NEG", "ND", "2"]):
        return "ND"
    if "INC" in txt or "INCON" in txt or "3" == txt:
        return "Inc"
    if "INV" in txt:
        return "Inv"
    return txt


class WellButton(ctk.CTkButton):
    def __init__(self, master, well_id: str, text: str, color: str, on_click=None):
        super().__init__(
            master,
            width=80,
            height=80,
            fg_color=color,
            text_color="black",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            corner_radius=6,
            border_width=2,
            border_color="#888888",
            text=self._truncate(text),
            command=lambda: on_click(well_id) if on_click else None,
        )
        self.well_id = well_id
        self.is_selected = False
        self.is_group_highlight = False

    @staticmethod
    def _truncate(text: str, max_len: int = 12) -> str:
        return text if len(text) <= max_len else text[: max_len - 2] + ".."

    def update_appearance(self, text: str, color: str, selected: bool, highlight: bool):
        self.configure(fg_color=color, text=self._truncate(text))
        if selected:
            self.configure(border_color="#FF0000", border_width=3)
        elif highlight:
            self.configure(border_color="#00AA00", border_width=2)
        else:
            self.configure(border_color="#888888", border_width=2)


class PlateView(ctk.CTkFrame):
    def __init__(self, master, plate_model: PlateModel, meta: Dict[str, str]):
        super().__init__(master)
        self.plate_model = plate_model
        self.meta = meta or {}
        self.selected_well_id: Optional[str] = None
        self.current_target: Optional[str] = None
        self.highlight_group: List[str] = []
        self.well_widgets: Dict[str, WellButton] = {}

        self._build_ui()
        self.render_plate()

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)

        # Cabeçalho
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(5, 10), padx=10)
        header.grid_columnconfigure(4, weight=1)
        infos = [
            f"Data: {self.meta.get('data', '')}",
            f"Extração: {self.meta.get('extracao', self.meta.get('arquivo', ''))}",
            f"Exame: {self.meta.get('exame', '')}",
            f"Usuário: {self.meta.get('usuario', '')}",
            f"Tamanho bloco: {self.plate_model.group_size} (tot amostras: {self._calc_total_samples()})",
        ]
        for i, txt in enumerate(infos):
            ctk.CTkLabel(header, text=txt, font=("", 12, "bold")).grid(row=0, column=i, padx=8, sticky="w")

        # Container placa
        plate_container = ctk.CTkFrame(self)
        plate_container.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        plate_container.grid_rowconfigure(0, weight=1)
        plate_container.grid_columnconfigure(0, weight=1)

        self.plate_frame = ctk.CTkFrame(plate_container)
        self.plate_frame.grid(row=0, column=0, sticky="nsew")

        # Títulos colunas
        font_labels = ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        ctk.CTkLabel(self.plate_frame, text="", width=35, height=35).grid(row=0, column=0, padx=1, pady=1)
        for j, col in enumerate(COL_LABELS, start=1):
            ctk.CTkLabel(self.plate_frame, text=col, font=font_labels, width=1, height=1).grid(
                row=0, column=j, padx=1, pady=1
            )

        # Grelha de poços
        for i, row_lbl in enumerate(ROW_LABELS, start=1):
            ctk.CTkLabel(self.plate_frame, text=row_lbl, font=font_labels, width=35, height=50).grid(
                row=i, column=0, padx=1, pady=1
            )
            for j, col_lbl in enumerate(COL_LABELS, start=1):
                well_id = f"{row_lbl}{col_lbl}"
                well = self.plate_model.get_well(well_id)
                text = ""
                if well:
                    text = well.code or well.sample_id or ""
                    if text and well.is_control:
                        ct_type = well.metadata.get("control_type", "")
                        if ct_type:
                            text = f"{ct_type}:{text}"
                color = STATUS_COLORS.get(well.status if well else EMPTY, "#ffffff")
                btn = WellButton(self.plate_frame, well_id, text, color, on_click=self.on_well_click)
                btn.grid(row=i, column=j, padx=1, pady=1)
                self.well_widgets[well_id] = btn

        # Painel lateral
        self.detail_frame = ctk.CTkFrame(self, width=360)
        self.detail_frame.grid(row=1, column=1, padx=(0, 10), pady=10, sticky="nsew")
        self.detail_frame.grid_propagate(False)

        for i in range(10):
            self.detail_frame.grid_rowconfigure(i, weight=0)
        self.detail_frame.grid_rowconfigure(6, weight=1)

        title_font = ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        ctk.CTkLabel(self.detail_frame, text="Poço selecionado:", font=title_font).grid(
            row=0, column=0, columnspan=2, pady=(15, 10), padx=15, sticky="w"
        )

        f_label = ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        f_val = ctk.CTkFont(family="Segoe UI", size=12)

        ctk.CTkLabel(self.detail_frame, text="Poço:", font=f_label).grid(row=1, column=0, padx=(15, 5), pady=8, sticky="e")
        self.lbl_well = ctk.CTkLabel(self.detail_frame, text="-", font=f_val)
        self.lbl_well.grid(row=1, column=1, padx=(5, 15), pady=8, sticky="w")

        ctk.CTkLabel(self.detail_frame, text="Amostra:", font=f_label).grid(row=2, column=0, padx=(15, 5), pady=8, sticky="e")
        self.lbl_sample = ctk.CTkLabel(self.detail_frame, text="-", font=f_val)
        self.lbl_sample.grid(row=2, column=1, padx=(5, 15), pady=8, sticky="w")

        ctk.CTkLabel(self.detail_frame, text="Código:", font=f_label).grid(row=3, column=0, padx=(15, 5), pady=8, sticky="e")
        code_frame = ctk.CTkFrame(self.detail_frame, fg_color="transparent")
        code_frame.grid(row=3, column=1, padx=(5, 15), pady=8, sticky="ew")
        code_frame.grid_columnconfigure(0, weight=1)
        self.entry_code = ctk.CTkEntry(code_frame, font=f_val, height=35)
        self.entry_code.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkButton(code_frame, text="?", width=40, height=35, font=f_val, command=self.apply_code_change).grid(
            row=0, column=1
        )

        ctk.CTkLabel(self.detail_frame, text="Poços agrupados:", font=f_label).grid(
            row=4, column=0, padx=(15, 5), pady=8, sticky="e"
        )
        self.lbl_group = ctk.CTkLabel(self.detail_frame, text="-", font=f_val)
        self.lbl_group.grid(row=4, column=1, padx=(5, 15), pady=8, sticky="w")

        ctk.CTkLabel(self.detail_frame, text="Resultados:", font=f_label).grid(
            row=5, column=0, columnspan=2, padx=15, pady=(5, 5), sticky="w"
        )

        tree_frame = ctk.CTkFrame(self.detail_frame)
        tree_frame.grid(row=6, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            foreground="black",
            background="white",
            fieldbackground="white",
            font=("Segoe UI", 13),
            rowheight=32,
        )
        style.configure("Treeview.Heading", foreground="black", background="#f0f0f0", font=("Segoe UI", 13, "bold"))
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("alvo", "resultado", "ct"),
            show="headings",
            selectmode="browse",
            height=10,
        )
        self.tree.heading("alvo", text="Alvo")
        self.tree.heading("resultado", text="Resultado")
        self.tree.heading("ct", text="CT")
        self.tree.column("alvo", width=80, anchor="w")
        self.tree.column("resultado", width=90, anchor="center")
        self.tree.column("ct", width=80, anchor="center")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Label para exibir CTs de controles internos (RP) separados dos alvos
        self.lbl_rp_info = ctk.CTkLabel(self.detail_frame, text="Controles internos (RP): -", font=f_val)
        self.lbl_rp_info.grid(row=7, column=0, columnspan=2, padx=15, pady=(0, 5), sticky="w")

        edit_frame = ctk.CTkFrame(self.detail_frame)
        edit_frame.grid(row=8, column=0, columnspan=2, padx=15, pady=(5, 10), sticky="ew")
        ctk.CTkLabel(edit_frame, text="Resultado:", font=f_label).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_res = ctk.CTkEntry(edit_frame, width=90, font=f_val, height=35)
        self.entry_res.grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkLabel(edit_frame, text="CT:", font=f_label).grid(row=0, column=2, padx=(10, 5), pady=5, sticky="e")
        self.entry_ct = ctk.CTkEntry(edit_frame, width=90, font=f_val, height=35)
        self.entry_ct.grid(row=0, column=3, padx=5, pady=5)
        ctk.CTkButton(
            edit_frame,
            text="Aplicar",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=38,
            command=self.apply_target_changes,
        ).grid(row=1, column=0, columnspan=4, pady=(10, 5))

        ctk.CTkButton(
            self.detail_frame,
            text="Salvar edições (apenas memória)",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=40,
            command=self._on_save_clicked,
        ).grid(row=9, column=0, columnspan=2, padx=15, pady=(0, 15))

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
        self.highlight_group = self.plate_model.get_group(well_id)
        self.render_plate()
        well = self.plate_model.get_well(well_id)
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
            btn.update_appearance(text, color, well_id == self.selected_well_id, well_id in self.highlight_group)

    def _fill_details(self, well: WellData):
        self.lbl_well.configure(text=well.well_id)
        self.lbl_sample.configure(text=well.sample_id or "-")
        self.entry_code.delete(0, tk.END)
        if well.code:
            self.entry_code.insert(0, well.code)
        self.lbl_group.configure(text=", ".join(well.paired_wells) if well.paired_wells else "-")

        # Limpa árvore de resultados
        self.tree.delete(*self.tree.get_children())

        # Separa alvos principais (não-RP) e controles internos (RP)
        non_rp_targets = []
        rp_targets = []
        for alvo, tr in (well.targets or {}).items():
            if str(alvo).upper().startswith("RP"):
                rp_targets.append((alvo, tr))
            else:
                non_rp_targets.append((alvo, tr))

        # Preenche a árvore apenas com alvos principais (não-RP)
        for alvo, tr in sorted(non_rp_targets, key=lambda it: str(it[0])):
            ct_txt = "-" if tr.ct is None else f"{tr.ct:.2f}"
            item_id = self.tree.insert("", "end", values=(alvo, tr.result, ct_txt))
            self.tree.item(item_id, tags=(alvo,))

        # Atualiza label de RPs com CTs de controles internos
        if rp_targets:
            parts = []
            for alvo, tr in sorted(rp_targets, key=lambda it: str(it[0])):
                if tr.ct is not None:
                    parts.append(f"{alvo}: CT {tr.ct:.2f}")
                else:
                    parts.append(f"{alvo}: CT -")
            rp_text = "Controles internos (RP): " + " | ".join(parts)
        else:
            rp_text = "Controles internos (RP): -"
        self.lbl_rp_info.configure(text=rp_text)

        # Limpa campos de edição
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
        self.entry_res.delete(0, tk.END)
        self.entry_res.insert(0, vals[1])
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
        ctrl = PlateModel._detect_control(well.sample_id, well.code)
        if ctrl:
            well.is_control = True
            well.metadata["control_type"] = ctrl
        else:
            well.is_control = False
            well.metadata.pop("control_type", None)
        # se code mudou, propaga para wells do mesmo grupo (mesma amostra)
        if well.pair_group_id:
            for wid in self.plate_model.pair_groups.get(well.pair_group_id, []):
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
        new_res = normalize_result(self.entry_res.get())
        ct_text = self.entry_ct.get().strip()
        new_ct = None
        if ct_text:
            try:
                new_ct = float(ct_text.replace(",", "."))
            except Exception:
                new_ct = None
        well.targets[self.current_target] = TargetResult(new_res, new_ct)
        self.plate_model._recompute_status(well)
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
        self.state("zoomed")
        view = PlateView(self, plate_model, meta)
        view.pack(fill="both", expand=True, padx=10, pady=10)


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------


def abrir_placa_ctk(df_final: pd.DataFrame, meta_extra: Optional[Dict[str, Any]] = None, group_size: Optional[int] = None, parent=None):
    """
    Abre a janela CTk para visualização/edição da placa usando df_final em memória.
    meta_extra pode conter data, extracao/arquivo, exame, usuario.
    """
    if df_final is None or df_final.empty:
        return
    plate_model = PlateModel.from_df(df_final, group_size=group_size)
    meta = meta_extra or {}
    # garantir chaves esperadas
    meta.setdefault("data", meta.get("data_placa", ""))
    meta.setdefault("extracao", meta.get("arquivo_corrida", meta.get("extracao", "")))
    meta.setdefault("exame", meta.get("exame", ""))
    meta.setdefault("usuario", meta.get("usuario", ""))
    win = PlateWindow(parent or ctk.CTk(), plate_model, meta)
    win.focus_force()
    return win


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




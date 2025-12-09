"""
teste_plate_viewer_historico_ctk.py

Visualizador de placa de 48 TESTES (pares em placa 96 poços) em CustomTkinter
usando dados do arquivo historico_analises.csv.

- Lê C:/Users/marci/Downloads/Integragal/reports/historico_analises.csv
- Constrói um modelo de placa a partir da coluna "poco" (que pode ter múltiplos poços separados por +)
- Usa as colunas de resultados/CT para SC2, HMPV, INFA, INFB, ADV, RSV, HRV, RP_1, RP_2
- Exibe uma placa 8x12 com cores por status e painel de detalhes editável.
- Inclui informações de cabeçalho: data, extração, teste, usuário e exame
- Destaca grupos de poços (pares, trios, quartetos) conforme o tipo de placa
- Para placas de 48 testes (pares), o contorno do grupo é de 5 pixels
"""

import argparse
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

import pandas as pd
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

# --------------------------------------------------------------------
# CONFIGURAÇÃO DO CSV
# --------------------------------------------------------------------

CSV_DEFAULT_PATH = r"C:/Users/marci/Downloads/Integragal/reports/historico_analises.csv"
CSV_SEP = ";"  # separador correto para o CSV

# Colunas base
COL_POCO = "poco"
COL_AMOSTRA = "amostra"
COL_CODIGO = "codigo"
COL_EXAME = "exame"
COL_ARQUIVO = "arquivo_corrida"
COL_DATA = "data"       # coluna para data
COL_EXTRACAO = "extracao"  # coluna para extração
COL_TESTE = "teste"        # coluna para teste
COL_USUARIO = "usuario"    # coluna para usuário

# Mapeamento de alvos â†’ (coluna_resultado, coluna_ct ou None)
TARGET_COLUMNS: Dict[str, tuple[str, Optional[str]]] = {
    "SC2": ("SC2 - R", "SC2 - CT"),
    "HMPV": ("HMPV - R", "HMPV - CT"),
    "INF A": ("INFA - R", "INFA - CT"),
    "INF B": ("INFB - R", "INFB - CT"),
    "ADV": ("ADV - R", "ADV - CT"),
    "RSV": ("RSV - R", "RSV - CT"),
    "HRV": ("HRV - R", "HRV - CT"),
    # RPs – CT apenas
    "RP_1": ("", "RP_1 - CT"),
    "RP_2": ("", "RP_2 - CT"),
}

ROW_LABELS = ["A", "B", "C", "D", "E", "F", "G", "H"]
COL_LABELS = [str(i) for i in range(1, 13)]

# --------------------------------------------------------------------
# STATUS E CORES
# --------------------------------------------------------------------

NEGATIVE = "NEGATIVE"
POSITIVE = "POSITIVE"
INCONCLUSIVE = "INCONCLUSIVE"
INVALID = "INVALID"
CONTROL_CN = "CONTROL_CN"
CONTROL_CP = "CONTROL_CP"
EMPTY = "EMPTY"

STATUS_COLORS = {
    NEGATIVE: "#d4f4d4",      # verde claro
    POSITIVE: "#ffb3b3",      # vermelho claro
    INCONCLUSIVE: "#ffe89a",  # amarelo
    INVALID: "#f0f0f0",       # cinza
    CONTROL_CN: "#b3d9ff",    # azul claro
    CONTROL_CP: "#b3d9ff",
    EMPTY: "#ffffff",         # branco
}

# Cores para diferentes tamanhos de grupos
GROUP_COLORS = {
    2: "#00FF00",  # Verde para pares (48 testes)
    3: "#0000FF",  # Azul para trios (32 testes)
    4: "#FF00FF",  # Magenta para quartetos (24 testes)
}

# Configurar aparência do CTk
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# --------------------------------------------------------------------
# MODELO DE DADOS COM SUPORTE PARA DIFERENTES TAMANHOS DE GRUPOS
# --------------------------------------------------------------------

@dataclass
class PlateHeaderInfo:
    """Classe para armazenar informações do cabeçalho da placa."""
    data: str = ""
    extracao: str = ""
    teste: str = ""
    usuario: str = ""
    exame: str = ""
    arquivo_corrida: str = ""
    total_amostras: int = 0
    plate_type: str = "48"  # 48 testes (pares em 96 poços) como padrão


@dataclass
class TargetResult:
    result: str  # "Det", "ND", "Inc", etc.
    ct: Optional[float] = None


@dataclass
class WellData:
    row_label: str
    col_label: str
    well_id: str
    sample_id: Optional[str] = None   # coluna "amostra"
    code: Optional[str] = None        # coluna "codigo"
    status: str = EMPTY
    is_control: bool = False
    targets: Dict[str, TargetResult] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    # Campos para grupos de poços
    paired_wells: List[str] = field(default_factory=list)  # IDs dos poços no grupo
    is_grouped: bool = False  # Indica se este poço faz parte de um grupo
    group_id: Optional[str] = None  # ID do grupo
    group_size: int = 1  # Tamanho do grupo (2, 3, 4)


class PlateModel:
    def __init__(self):
        self.wells: Dict[str, WellData] = {}
        # Dicionário para mapear grupos de poços
        self.group_dict: Dict[str, List[str]] = {}
        self.header_info = PlateHeaderInfo()
        self.plate_type = "48"  # Padrão: placa de 48 testes (pares em 96 poços)

    # ------------------ carregamento a partir do CSV ------------------ #
    @classmethod
    def from_historico_csv(
        cls,
        csv_path: str,
        sep: str = ";",
        exame: Optional[str] = None,
        arquivo_corrida: Optional[str] = None,
    ) -> "PlateModel":
        try:
            df = pd.read_csv(csv_path, sep=sep, dtype=str)
            print(f"[INFO] CSV carregado. Colunas: {list(df.columns)}")
            print(f"[INFO] Total de linhas: {len(df)}")
        except Exception as e:
            print(f"[ERRO] Falha ao ler CSV: {e}")
            return cls()

        # Verificar colunas obrigatórias
        obrigatorias = [COL_POCO, COL_AMOSTRA, COL_CODIGO]
        for col in obrigatorias:
            if col not in df.columns:
                print(f"[ERRO] Coluna '{col}' não encontrada no CSV!")
                print(f"[ERRO] Colunas disponíveis: {list(df.columns)}")
                return cls()

        # filtros opcionais
        if exame and COL_EXAME in df.columns:
            df = df[df[COL_EXAME] == exame]
            print(f"[INFO] Filtrado por exame '{exame}': {len(df)} linhas")

        if arquivo_corrida and COL_ARQUIVO in df.columns:
            df = df[df[COL_ARQUIVO] == arquivo_corrida]
            print(f"[INFO] Filtrado por arquivo_corrida '{arquivo_corrida}': {len(df)} linhas")
        elif COL_ARQUIVO in df.columns and not df.empty:
            # por padrão, usa o último arquivo_corrida presente
            arquivos_validos = df[COL_ARQUIVO].dropna()
            if not arquivos_validos.empty:
                last_file = arquivos_validos.iloc[-1]
                df = df[df[COL_ARQUIVO] == last_file]
                print(f"[INFO] Usando arquivo_corrida mais recente: {last_file}")
                print(f"[INFO] Linhas após filtro: {len(df)}")
            else:
                print(f"[INFO] Coluna '{COL_ARQUIVO}' existe mas todos os valores são nulos.")

        if df.empty:
            print("[AVISO] Nenhum dado após aplicar filtros!")
            return cls()

        model = cls()
        model._load_header_info(df)
        model._load_from_dataframe(df)
        model._determine_plate_type()
        return model

    def _load_header_info(self, df: pd.DataFrame) -> None:
        """Carrega informações do cabeçalho do CSV."""
        if not df.empty:
            first_row = df.iloc[0]

            if COL_DATA in df.columns:
                self.header_info.data = (
                    str(first_row[COL_DATA])
                    if not pd.isna(first_row[COL_DATA])
                    else datetime.now().strftime("%d/%m/%Y")
                )

            if COL_EXTRACAO in df.columns:
                self.header_info.extracao = (
                    str(first_row[COL_EXTRACAO])
                    if not pd.isna(first_row[COL_EXTRACAO])
                    else "N/A"
                )

            if COL_TESTE in df.columns:
                self.header_info.teste = (
                    str(first_row[COL_TESTE])
                    if not pd.isna(first_row[COL_TESTE])
                    else "N/A"
                )

            if COL_USUARIO in df.columns:
                self.header_info.usuario = (
                    str(first_row[COL_USUARIO])
                    if not pd.isna(first_row[COL_USUARIO])
                    else "N/A"
                )

            if COL_EXAME in df.columns:
                self.header_info.exame = (
                    str(first_row[COL_EXAME])
                    if not pd.isna(first_row[COL_EXAME])
                    else "N/A"
                )

            if COL_ARQUIVO in df.columns:
                self.header_info.arquivo_corrida = (
                    str(first_row[COL_ARQUIVO])
                    if not pd.isna(first_row[COL_ARQUIVO])
                    else "N/A"
                )

            print(
                f"[INFO] Cabeçalho carregado: "
                f"Data={self.header_info.data}, "
                f"Extração={self.header_info.extracao}, "
                f"Teste={self.header_info.teste}, "
                f"Usuário={self.header_info.usuario}, "
                f"Exame={self.header_info.exame}"
            )

    def _load_from_dataframe(self, df: pd.DataFrame) -> None:
        """Carrega dados do DataFrame para o modelo."""
        wells_created = 0

        # Primeira passagem: criar todos os poços individuais
        temp_wells: Dict[str, Tuple[WellData, List[str]]] = {}  # (well_data, pocos_originais)

        for idx, row in df.iterrows():
            poco_raw = str(row[COL_POCO]).strip() if not pd.isna(row[COL_POCO]) else ""
            if not poco_raw:
                continue

            # Separar múltiplos poços (ex: "A1+A2" -> ["A1", "A2"])
            pocos = poco_raw.split("+")
            # Extrair dados da linha
            sample = None if pd.isna(row[COL_AMOSTRA]) else str(row[COL_AMOSTRA]).strip()
            code = None if pd.isna(row[COL_CODIGO]) else str(row[COL_CODIGO]).strip()

            # Dados para todos os alvos desta linha
            target_data: Dict[str, TargetResult] = {}
            for alvo, (col_res, col_ct) in TARGET_COLUMNS.items():
                res_text = ""
                if col_res and col_res in df.columns:
                    val = row[col_res]
                    if not pd.isna(val):
                        res_text = normalize_result(str(val))

                ct_val: Optional[float] = None
                if col_ct and col_ct in df.columns and not pd.isna(row[col_ct]):
                    ct_raw = str(row[col_ct]).replace(",", ".")
                    try:
                        ct_val = float(ct_raw)
                    except ValueError:
                        ct_val = None

                target_data[alvo] = TargetResult(result=res_text, ct=ct_val)

            # Para cada poço nesta linha
            for poco in pocos:
                poco = poco.strip()
                if len(poco) < 2:
                    continue

                row_label = poco[0].upper()
                col_label = poco[1:]

                # Validar se o poço está dentro da placa 96
                if row_label not in ROW_LABELS:
                    print(f"[AVISO] Linha {idx}: Letra de linha inválida '{row_label}' em '{poco}'")
                    continue

                if col_label not in COL_LABELS:
                    print(f"[AVISO] Linha {idx}: Número de coluna inválido '{col_label}' em '{poco}'")
                    continue

                well_id = f"{row_label}{col_label}"

                # Verificar se já existe um poço com este ID
                if well_id in temp_wells:
                    print(f"[AVISO] Poço {well_id} duplicado, mantendo o primeiro")
                    continue

                wd = WellData(
                    row_label=row_label,
                    col_label=col_label,
                    well_id=well_id,
                    sample_id=sample,
                    code=code,
                    targets=target_data.copy(),
                    group_size=len(pocos),
                )

                # heurística simples para CN/CP a partir de amostra/código
                control_type = self._detect_control_type(sample, code)
                if control_type:
                    wd.is_control = True
                    wd.metadata["control_type"] = control_type

                # Armazenar temporariamente com lista de poços associados
                temp_wells[well_id] = (wd, pocos)
                wells_created += 1

        # Segunda passagem: identificar e configurar grupos
        for well_id, (wd, pocos) in temp_wells.items():
            if len(pocos) > 1:
                wd.is_grouped = True
                wd.paired_wells = [p.strip() for p in pocos if p.strip() != well_id]

                # Criar ID de grupo baseado nos poços ordenados
                sorted_pocos = sorted(pocos)
                group_id = "+".join(sorted_pocos)
                wd.group_id = group_id

                # Adicionar ao dicionário de grupos
                if group_id not in self.group_dict:
                    self.group_dict[group_id] = []
                if well_id not in self.group_dict[group_id]:
                    self.group_dict[group_id].append(well_id)

            # Calcular status baseado nos resultados
            self._recompute_status(wd)
            self.wells[well_id] = wd

        self.header_info.total_amostras = wells_created
        print(f"[INFO] Total de poços criados: {wells_created}")
        print(f"[INFO] Total de grupos: {len(self.group_dict)}")

        # Mostrar estatísticas de grupos
        group_stats: Dict[int, int] = {}
        for group_id, wells in self.group_dict.items():
            size = len(wells)
            group_stats[size] = group_stats.get(size, 0) + 1
            print(f"[DEBUG] Grupo {group_id} (tamanho {size}): {wells}")

        print(f"[INFO] Estatísticas de grupos: {group_stats}")

    def _determine_plate_type(self) -> None:
        """Determina o tipo de placa com base nos tamanhos dos grupos.

        Para este visualizador, o uso principal é 48 TESTES (pares â†’ size=2).
        """
        if not self.group_dict:
            # Se não houver grupos, mantemos padrão 48 apenas como informação de testes,
            # mas a placa física continua 96 poços.
            self.plate_type = "48"
            self.header_info.plate_type = "48"
            print("[INFO] Placa tipo: 48 testes (sem grupos explícitos no CSV)")
            return

        # Encontrar o tamanho de grupo mais comum
        group_sizes: Dict[int, int] = {}
        for wells in self.group_dict.values():
            size = len(wells)
            group_sizes[size] = group_sizes.get(size, 0) + 1

        if not group_sizes:
            self.plate_type = "48"
            self.header_info.plate_type = "48"
            print("[INFO] Placa tipo: 48 testes (fallback)")
            return

        # Determinar tipo com base no tamanho mais comum
        most_common_size = max(group_sizes, key=group_sizes.get)

        if most_common_size == 2:
            self.plate_type = "48"
            self.header_info.plate_type = "48"
            print("[INFO] Placa tipo: 48 testes (pares em placa 96)")
        elif most_common_size == 3:
            self.plate_type = "32"
            self.header_info.plate_type = "32"
            print("[INFO] Placa tipo: 32 testes (trios)")
        elif most_common_size == 4:
            self.plate_type = "24"
            self.header_info.plate_type = "24"
            print("[INFO] Placa tipo: 24 testes (quartetos)")
        else:
            # fallback, mas mantendo foco em 48 testes
            self.plate_type = "48"
            self.header_info.plate_type = "48"
            print(f"[INFO] Placa tipo: 48 testes (tamanho de grupo não padrão: {most_common_size})")

    @staticmethod
    def _detect_control_type(sample: Optional[str], code: Optional[str]) -> Optional[str]:
        """Heurística simples para identificar CN/CP."""
        candidates: List[str] = []
        if sample:
            candidates.append(sample.upper())
        if code:
            candidates.append(code.upper())

        for val in candidates:
            if val in ("CN", "CONTROLE NEGATIVO", "C-", "NEGATIVO CONTROLE", "NEGATIVO", "CONTROLE N"):
                return "CN"
            if val in ("CP", "CONTROLE POSITIVO", "C+", "POSITIVO CONTROLE", "POSITIVO", "CONTROLE P"):
                return "CP"
        return None

    # ------------------------ operações no modelo ------------------------ #
    def get_well(self, well_id: str) -> Optional[WellData]:
        return self.wells.get(well_id)

    def get_group_wells(self, well_id: str) -> List[str]:
        """Retorna lista de poços no mesmo grupo (sem o próprio poço)."""
        well = self.get_well(well_id)
        if not well or not well.group_id:
            return []
        group_id = well.group_id
        return [w for w in self.group_dict.get(group_id, []) if w != well_id]

    def get_group_wells_including_self(self, well_id: str) -> List[str]:
        """Retorna todos os poços do grupo, incluindo o próprio poço."""
        well = self.get_well(well_id)
        if not well or not well.group_id:
            return [well_id]
        group_id = well.group_id
        return list(self.group_dict.get(group_id, [well_id]))

    def get_group_size(self, well_id: str) -> int:
        """Retorna o tamanho do grupo para um poço específico."""
        well = self.get_well(well_id)
        if not well or not well.is_grouped:
            return 1
        return well.group_size

    def _recompute_status(self, well: WellData) -> None:
        """Regra simplificada de status baseada nos resultados."""
        if well.is_control:
            ctype = well.metadata.get("control_type", "")
            if ctype == "CN":
                well.status = CONTROL_CN
            elif ctype == "CP":
                well.status = CONTROL_CP
            else:
                well.status = INVALID
            return

        # resultados dos alvos (exceto RPs)
        has_positive = False
        has_inconclusive = False

        for alvo, tr in well.targets.items():
            if alvo.startswith("RP"):
                continue

            result_upper = tr.result.upper()
            if "DET" in result_upper or "POS" in result_upper:
                has_positive = True
            elif "INC" in result_upper:
                has_inconclusive = True

        if has_positive:
            well.status = POSITIVE
        elif has_inconclusive:
            well.status = INCONCLUSIVE
        else:
            # Verificar se tem algum resultado ND (não detectado)
            has_nd = any(
                "ND" in tr.result.upper()
                for alvo, tr in well.targets.items()
                if not alvo.startswith("RP")
            )
            if has_nd:
                well.status = NEGATIVE
            else:
                well.status = INVALID


def normalize_result(value: str) -> str:
    """Normaliza textos de resultado do CSV (ex: 'SC2 - 1', 'HMPV - 2')."""
    if not value:
        return ""

    txt = value.strip().upper()

    # Formato específico do CSV: "ALVO - NÚMERO" (ex: "SC2 - 1", "HMPV - 2")
    if " - " in txt:
        parts = txt.split(" - ")
        if len(parts) >= 2:
            num = parts[-1].strip()
            if num == "1":
                return "Det"      # Detectado
            if num == "2":
                return "ND"       # Não Detectado
            return "Inc"         # Inconclusivo para outros números

    # Fallback para outras formatações
    if any(k in txt for k in ["DET", "POSI", "REAG", "1"]):
        return "Det"
    if any(k in txt for k in ["NAO", "NÃO", "NEG", "ND", "2"]):
        return "ND"
    if "INC" in txt or "INCON" in txt:
        return "Inc"

    return value.strip()


# --------------------------------------------------------------------
# GUI – CTk Implementation
# --------------------------------------------------------------------

class HeaderFrame(ctk.CTkFrame):
    """Frame para exibir informações do cabeçalho da placa."""

    def __init__(self, master, plate_model: PlateModel, **kwargs):
        super().__init__(master, **kwargs)
        self.plate_model = plate_model
        self._init_ui()

    def _init_ui(self):
        """Inicializa a interface do cabeçalho."""
        for i in range(4):
            self.grid_rowconfigure(i, weight=0)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_columnconfigure(4, weight=1)

        font_label = ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        font_value = ctk.CTkFont(family="Segoe UI", size=16)

        title_label = ctk.CTkLabel(
            self,
            text="MAPEAMENTO DE PLACA - 48 TESTES (PARES EM 96 POÇOS)",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color="#2E86C1",
        )
        title_label.grid(row=0, column=0, columnspan=5, pady=(3, 4), sticky="ew")

        # Linha 1: Data e Extração
        ctk.CTkLabel(self, text="Data:", font=font_label).grid(
            row=1, column=0, padx=3, pady=1, sticky="e"
        )
        self.lbl_data = ctk.CTkLabel(
            self, text=self.plate_model.header_info.data, font=font_value
        )
        self.lbl_data.grid(row=1, column=1, padx=3, pady=1, sticky="w")

        ctk.CTkLabel(self, text="Extração:", font=font_label).grid(
            row=1, column=2, padx=3, pady=1, sticky="e"
        )
        self.lbl_extracao = ctk.CTkLabel(
            self, text=self.plate_model.header_info.extracao, font=font_value
        )
        self.lbl_extracao.grid(row=1, column=3, padx=3, pady=1, sticky="w")

        # Linha 2: Teste e Usuário
        ctk.CTkLabel(self, text="Teste:", font=font_label).grid(
            row=2, column=0, padx=3, pady=1, sticky="e"
        )
        self.lbl_teste = ctk.CTkLabel(
            self, text=self.plate_model.header_info.teste, font=font_value
        )
        self.lbl_teste.grid(row=2, column=1, padx=3, pady=1, sticky="w")

        ctk.CTkLabel(self, text="Usuário:", font=font_label).grid(
            row=2, column=2, padx=3, pady=1, sticky="e"
        )
        self.lbl_usuario = ctk.CTkLabel(
            self, text=self.plate_model.header_info.usuario, font=font_value
        )
        self.lbl_usuario.grid(row=2, column=3, padx=3, pady=1, sticky="w")

        # Linha 3: Exame e Tipo de Placa
        ctk.CTkLabel(self, text="Exame:", font=font_label).grid(
            row=3, column=0, padx=3, pady=1, sticky="e"
        )
        self.lbl_exame = ctk.CTkLabel(
            self, text=self.plate_model.header_info.exame, font=font_value
        )
        self.lbl_exame.grid(row=3, column=1, padx=3, pady=1, sticky="w")

        ctk.CTkLabel(self, text="Tipo de Placa:", font=font_label).grid(
            row=3, column=2, padx=3, pady=1, sticky="e"
        )
        plate_type_text = f"{self.plate_model.plate_type} TESTES"
        if self.plate_model.plate_type == "48":
            plate_type_text += " (pares em 96 poços)"
        elif self.plate_model.plate_type == "32":
            plate_type_text += " (trios)"
        elif self.plate_model.plate_type == "24":
            plate_type_text += " (quartetos)"

        self.lbl_plate_type = ctk.CTkLabel(
            self,
            text=plate_type_text,
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#E74C3C",
        )
        self.lbl_plate_type.grid(row=3, column=3, padx=3, pady=1, sticky="w")

        # Linha 4: Total de Amostras e Arquivo
        ctk.CTkLabel(self, text="Total de Testes:", font=font_label).grid(
            row=4, column=0, padx=3, pady=1, sticky="e"
        )

        total_samples = self._calculate_total_samples()
        self.lbl_total = ctk.CTkLabel(
            self,
            text=str(total_samples),
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#27AE60",
        )
        self.lbl_total.grid(row=4, column=1, padx=3, pady=1, sticky="w")

        ctk.CTkLabel(self, text="Arquivo:", font=font_label).grid(
            row=4, column=2, padx=3, pady=1, sticky="e"
        )
        arq = self.plate_model.header_info.arquivo_corrida
        arq_text = arq[:20] + "..." if len(arq) > 20 else arq
        self.lbl_arquivo = ctk.CTkLabel(self, text=arq_text, font=font_value)
        self.lbl_arquivo.grid(row=4, column=3, padx=3, pady=1, sticky="w")

        separator = ctk.CTkLabel(self, text="", height=1, fg_color="#7D3C98")
        separator.grid(row=5, column=0, columnspan=5, sticky="ew", padx=3, pady=(2, 1))

    def _calculate_total_samples(self) -> int:
        """Calcula o total de testes baseado no tipo de placa."""
        total_wells = self.plate_model.header_info.total_amostras

        if self.plate_model.plate_type == "96":
            return total_wells
        if self.plate_model.plate_type == "48":
            return total_wells // 2
        if self.plate_model.plate_type == "32":
            return total_wells // 3
        if self.plate_model.plate_type == "24":
            return total_wells // 4
        return total_wells


class WellButton(ctk.CTkButton):
    """Botão personalizado para representar um poço na placa."""

    def __init__(self, master, well_id: str, text: str, color: str, on_click_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.well_id = well_id
        self.on_click_callback = on_click_callback

        self.configure(
            width=90,
            height=70,
            fg_color=color,
            text_color="black",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            corner_radius=5,
            border_width=2,
            border_color="#888888",
            text=self._truncate_text(text, 10),
            command=self._on_click,
        )

    def _truncate_text(self, text: str, max_length: int) -> str:
        if len(text) > max_length:
            return text[: max_length - 2] + ".."
        return text

    def _on_click(self):
        if self.on_click_callback:
            self.on_click_callback(self.well_id)

    def update_appearance(
        self,
        text: str,
        color: str,
        is_selected: bool,
        is_group_highlight: bool = False,
        group_size: int = 1,
        plate_type: str = "48",
    ):
        """Atualiza a aparência do botão.

        Regras de borda (contorno):
        - Espessura padrão: 2 pixels.
        - Quando selecionado ou em grupo destacado: 5 pixels de espessura.
        - Cor da borda do grupo:
            * placas de 48/32/24: GROUP_COLORS por tamanho.
            * placa 96 (sem grupos): vermelho para o poço selecionado.
        """
        self.configure(
            fg_color=color,
            text=self._truncate_text(text, 10),
        )

        # Placa 96 (sem agrupamento "visual"): só destaca o selecionado em vermelho
        if plate_type == "96":
            if is_selected:
                self.configure(border_color="#FF0000", border_width=5)
            else:
                self.configure(border_color="#888888", border_width=2)
            return

        # Placas com agrupamento (48/32/24)
        if is_group_highlight:
            group_color = GROUP_COLORS.get(group_size, "#00AA00")
            if is_selected:
                # Poço selecionado dentro do grupo â†’ mesma cor, borda mais grossa
                self.configure(border_color=group_color, border_width=5)
            else:
                # Demais poços do grupo â†’ mesma cor, também 5 pixels para contornar o grupo inteiro
                self.configure(border_color=group_color, border_width=5)
        else:
            # Fora do grupo
            if is_selected:
                # Selecionado sem grupo explícito (fallback)
                self.configure(border_color="#FF0000", border_width=5)
            else:
                self.configure(border_color="#888888", border_width=2)


class PlateView(ctk.CTkFrame):
    """Frame principal que contém toda a visualização da placa."""

    def __init__(self, master, plate_model: PlateModel, on_save_changes=None, **kwargs):
        super().__init__(master, **kwargs)
        self.plate_model = plate_model
        self.on_save_changes = on_save_changes

        self.well_widgets: Dict[str, WellButton] = {}
        self.selected_well_id: Optional[str] = None
        self.current_target: Optional[str] = None
        # lista de poços do grupo selecionado (incluindo o poço clicado)
        self.group_wells_highlight: List[str] = []
        self.group_size_highlight: int = 1

        self._init_ui()
        self.render_plate()

    def _init_ui(self):
        """Inicializa todos os componentes da interface."""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # ----------------- PAINEL DA PLACA -----------------
        plate_container = ctk.CTkFrame(self)
        plate_container.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        plate_container.grid_rowconfigure(0, weight=1)
        plate_container.grid_columnconfigure(0, weight=1)

        self.plate_frame = ctk.CTkFrame(plate_container)
        self.plate_frame.grid(row=0, column=0, sticky="nsew")

        font_labels = ctk.CTkFont(family="Segoe UI", size=11, weight="bold")

        # Cabeçalho das colunas
        ctk.CTkLabel(self.plate_frame, text="", width=30, height=30).grid(
            row=0, column=0, padx=1, pady=1
        )

        for j, col in enumerate(COL_LABELS, start=1):
            label = ctk.CTkLabel(
                self.plate_frame,
                text=col,
                font=font_labels,
                width=90,
                height=30,
            )
            label.grid(row=0, column=j, padx=1, pady=1)

        # Linhas e poços
        for i, row in enumerate(ROW_LABELS, start=1):
            label = ctk.CTkLabel(
                self.plate_frame,
                text=row,
                font=font_labels,
                width=30,
                height=70,
            )
            label.grid(row=i, column=0, padx=1, pady=1)

            for j, col in enumerate(COL_LABELS, start=1):
                well_id = f"{row}{col}"
                well = self.plate_model.get_well(well_id)

                text = ""
                if well:
                    text = well.code or well.sample_id or ""
                    if text and well.is_control:
                        ctype = well.metadata.get("control_type", "")
                        if ctype:
                            text = f"{ctype}:{text}"

                color = self._status_to_color(well.status if well else EMPTY)

                btn = WellButton(
                    self.plate_frame,
                    well_id=well_id,
                    text=text,
                    color=color,
                    on_click_callback=self.on_well_click,
                    width=90,
                    height=70,
                )
                btn.grid(row=i, column=j, padx=1, pady=1)
                self.well_widgets[well_id] = btn

        # ----------------- PAINEL DE DETALHES -----------------
        self.detail_frame = ctk.CTkFrame(self, width=400)
        self.detail_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
        self.detail_frame.grid_propagate(False)

        for i in range(10):
            self.detail_frame.grid_rowconfigure(i, weight=0)
        self.detail_frame.grid_rowconfigure(7, weight=1)

        title_font = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        title_label = ctk.CTkLabel(
            self.detail_frame,
            text="POÇO SELECIONADO",
            font=title_font,
            text_color="#2E86C1",
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(15, 10), padx=15, sticky="w")

        font_label = ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        font_value = ctk.CTkFont(family="Segoe UI", size=12)

        # Poço
        ctk.CTkLabel(self.detail_frame, text="Poço:", font=font_label).grid(
            row=1, column=0, padx=(15, 5), pady=8, sticky="e"
        )
        self.lbl_well_id = ctk.CTkLabel(self.detail_frame, text="-", font=font_value)
        self.lbl_well_id.grid(row=1, column=1, padx=(5, 15), pady=8, sticky="w")

        # Amostra
        ctk.CTkLabel(self.detail_frame, text="Amostra:", font=font_label).grid(
            row=2, column=0, padx=(15, 5), pady=8, sticky="e"
        )
        self.lbl_sample_id = ctk.CTkLabel(self.detail_frame, text="-", font=font_value)
        self.lbl_sample_id.grid(row=2, column=1, padx=(5, 15), pady=8, sticky="w")

        # Código (editável)
        ctk.CTkLabel(self.detail_frame, text="Código:", font=font_label).grid(
            row=3, column=0, padx=(15, 5), pady=8, sticky="e"
        )

        code_frame = ctk.CTkFrame(self.detail_frame, fg_color="transparent")
        code_frame.grid(row=3, column=1, padx=(5, 15), pady=8, sticky="ew")
        code_frame.grid_columnconfigure(0, weight=1)

        self.entry_code = ctk.CTkEntry(code_frame, font=font_value, height=35)
        self.entry_code.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        self.btn_apply_code = ctk.CTkButton(
            code_frame,
            text="✓",
            width=35,
            height=35,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self.apply_code_change,
        )
        self.btn_apply_code.grid(row=0, column=1)

        # Informação do grupo
        ctk.CTkLabel(self.detail_frame, text="Grupo:", font=font_label).grid(
            row=4, column=0, padx=(15, 5), pady=8, sticky="e"
        )
        self.lbl_group_info = ctk.CTkLabel(self.detail_frame, text="-", font=font_value)
        self.lbl_group_info.grid(row=4, column=1, padx=(5, 15), pady=8, sticky="w")

        ctk.CTkLabel(self.detail_frame, text="", height=10).grid(
            row=5, column=0, columnspan=2
        )

        # Título do TreeView
        ctk.CTkLabel(self.detail_frame, text="RESULTADOS DOS ALVOS:", font=font_label).grid(
            row=6, column=0, columnspan=2, padx=15, pady=(5, 5), sticky="w"
        )

        tree_frame = ctk.CTkFrame(self.detail_frame)
        tree_frame.grid(row=7, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            foreground="black",
            background="white",
            fieldbackground="white",
            font=("Segoe UI", 12),
            rowheight=35,
        )
        style.configure(
            "Treeview.Heading",
            foreground="black",
            background="#f0f0f0",
            font=("Segoe UI", 12, "bold"),
            relief="flat",
        )
        style.map("Treeview", background=[("selected", "#347083")])

        self.tree_widget = ttk.Treeview(
            tree_frame,
            columns=("alvo", "resultado", "ct"),
            show="headings",
            selectmode="browse",
            height=12,
        )

        self.tree_widget.heading("alvo", text="Alvo")
        self.tree_widget.heading("resultado", text="Resultado")
        self.tree_widget.heading("ct", text="CT")

        self.tree_widget.column("alvo", width=100, anchor="w", minwidth=80)
        self.tree_widget.column("resultado", width=100, anchor="center", minwidth=80)
        self.tree_widget.column("ct", width=80, anchor="center", minwidth=60)

        tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_widget.yview)
        tree_scroll_y.grid(row=0, column=1, sticky="ns")

        self.tree_widget.configure(yscrollcommand=tree_scroll_y.set)
        self.tree_widget.grid(row=0, column=0, sticky="nsew")

        self.tree_widget.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Frame de edição de alvo
        edit_frame = ctk.CTkFrame(self.detail_frame)
        edit_frame.grid(row=8, column=0, columnspan=2, padx=15, pady=(5, 10), sticky="ew")

        ctk.CTkLabel(edit_frame, text="Resultado:", font=font_label).grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        self.entry_result = ctk.CTkEntry(edit_frame, width=90, font=font_value, height=35)
        self.entry_result.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(edit_frame, text="CT:", font=font_label).grid(
            row=0, column=2, padx=(10, 5), pady=5, sticky="e"
        )
        self.entry_ct = ctk.CTkEntry(edit_frame, width=90, font=font_value, height=35)
        self.entry_ct.grid(row=0, column=3, padx=5, pady=5)

        self.btn_apply_target = ctk.CTkButton(
            edit_frame,
            text="Aplicar Alterações",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=35,
            command=self.apply_target_changes,
        )
        self.btn_apply_target.grid(row=1, column=0, columnspan=4, pady=(10, 5))

        self.btn_save = ctk.CTkButton(
            self.detail_frame,
            text="SALVAR ALTERAÇÕES",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=40,
            fg_color="#27AE60",
            hover_color="#229954",
            command=self._on_save_clicked,
        )
        self.btn_save.grid(row=9, column=0, columnspan=2, padx=15, pady=(0, 15))

    @staticmethod
    def _status_to_color(status: str) -> str:
        return STATUS_COLORS.get(status, "#ffffff")

    def on_well_click(self, well_id: str):
        """Manipula clique em um poço."""
        print(f"[DEBUG] Poço clicado: {well_id}")
        self.selected_well_id = well_id

        # Para placas com agrupamento (48/32/24), destacamos o grupo inteiro.
        if self.plate_model.plate_type != "96":
            self.group_wells_highlight = self.plate_model.get_group_wells_including_self(well_id)
            self.group_size_highlight = self.plate_model.get_group_size(well_id)
        else:
            # Placa 96: sem grupo
            self.group_wells_highlight = []
            self.group_size_highlight = 1

        print(
            f"[DEBUG] Poços do grupo para {well_id}: "
            f"{self.group_wells_highlight} (tamanho: {self.group_size_highlight})"
        )

        self.render_plate()

        well = self.plate_model.get_well(well_id)
        if not well:
            print(f"[DEBUG] Poço {well_id} não encontrado no modelo")
            self.lbl_well_id.configure(text="-")
            self.lbl_sample_id.configure(text="-")
            self.lbl_group_info.configure(text="-")
            self.entry_code.delete(0, tk.END)
            self.tree_widget.delete(*self.tree_widget.get_children())
            self.entry_result.delete(0, tk.END)
            self.entry_ct.delete(0, tk.END)
            return

        print(f"[DEBUG] Preenchendo detalhes do poço {well_id}")
        self.fill_detail_panel(well)

    def render_plate(self):
        """Atualiza a exibição de todos os poços."""
        for well_id, btn in self.well_widgets.items():
            well = self.plate_model.get_well(well_id)

            text = ""
            if well:
                text = well.code or well.sample_id or ""
                if text and well.is_control:
                    ctype = well.metadata.get("control_type", "")
                    if ctype:
                        text = f"{ctype}:{text}"

            color = self._status_to_color(well.status if well else EMPTY)

            is_selected = (well_id == self.selected_well_id)

            # Destacar grupo apenas para placas com tipo != 96
            if self.plate_model.plate_type != "96":
                is_group_highlight = well_id in self.group_wells_highlight
                group_size = self.group_size_highlight
            else:
                is_group_highlight = False
                group_size = 1

            btn.update_appearance(
                text=text,
                color=color,
                is_selected=is_selected,
                is_group_highlight=is_group_highlight,
                group_size=group_size,
                plate_type=self.plate_model.plate_type,
            )

    def fill_detail_panel(self, well: WellData):
        """Preenche o painel de detalhes com informações do poço."""
        self.lbl_well_id.configure(text=well.well_id)
        self.lbl_sample_id.configure(text=well.sample_id or "-")

        if well.is_grouped and well.paired_wells:
            group_text = f"{', '.join(well.paired_wells)} (tamanho: {well.group_size})"
            group_color = GROUP_COLORS.get(well.group_size, "#000000")
            self.lbl_group_info.configure(text=group_text, text_color=group_color)
        else:
            self.lbl_group_info.configure(text="Sem grupo", text_color="#000000")

        self.entry_code.delete(0, tk.END)
        if well.code:
            self.entry_code.insert(0, well.code)

        self.tree_widget.delete(*self.tree_widget.get_children())

        if well.targets:
            print(f"[DEBUG] Mostrando {len(well.targets)} alvos para o poço {well.well_id}")
            sorted_targets = sorted(well.targets.items(), key=lambda x: x[0])

            for alvo, tr in sorted_targets:
                ct_text = "" if tr.ct is None else f"{tr.ct:.3f}"
                item_id = self.tree_widget.insert(
                    "", "end", values=(alvo, tr.result, ct_text)
                )
                self.tree_widget.item(item_id, tags=(alvo,))
        else:
            print(f"[DEBUG] Nenhum alvo encontrado para o poço {well.well_id}")
            self.tree_widget.insert("", "end", values=("Nenhum dado", "", ""))

        self.entry_result.delete(0, tk.END)
        self.entry_ct.delete(0, tk.END)
        self.current_target = None

    def on_tree_select(self, event):
        """Manipula seleção de um alvo no tree."""
        selection = self.tree_widget.selection()
        if not selection:
            self.current_target = None
            return

        item_id = selection[0]
        values = self.tree_widget.item(item_id, "values")
        if values and values[0] != "Nenhum dado":
            self.current_target = values[0]
            self.entry_result.delete(0, tk.END)
            self.entry_result.insert(0, values[1])
            self.entry_ct.delete(0, tk.END)
            self.entry_ct.insert(0, values[2])
        else:
            self.current_target = None

    def apply_code_change(self):
        """Aplica alteração do código de amostra."""
        if not self.selected_well_id:
            return

        well = self.plate_model.get_well(self.selected_well_id)
        if not well:
            return

        new_code = self.entry_code.get().strip()
        well.code = new_code if new_code else None

        control_type = PlateModel._detect_control_type(well.sample_id, well.code)
        if control_type:
            well.is_control = True
            well.metadata["control_type"] = control_type
        else:
            well.is_control = False
            well.metadata.pop("control_type", None)

        self.plate_model._recompute_status(well)
        self.render_plate()
        print(f"[INFO] Código do poço {well.well_id} atualizado para: {well.code}")

    def apply_target_changes(self):
        """Aplica alterações no resultado/CT do alvo selecionado."""
        if not self.selected_well_id or not self.current_target:
            return

        well = self.plate_model.get_well(self.selected_well_id)
        if not well:
            return

        new_result = self.entry_result.get().strip()
        ct_text = self.entry_ct.get().strip()
        new_ct: Optional[float] = None

        if ct_text:
            try:
                new_ct = float(ct_text.replace(",", "."))
            except ValueError:
                new_ct = None

        well.targets[self.current_target] = TargetResult(new_result, new_ct)
        self.plate_model._recompute_status(well)

        self.fill_detail_panel(well)
        self.render_plate()

    def _on_save_clicked(self):
        """Manipula clique no botão Salvar."""
        if self.on_save_changes:
            self.on_save_changes(self.plate_model)
        print("[INFO] Alterações salvas com sucesso!")


class MainWindow(ctk.CTk):
    """Janela principal da aplicação."""

    def __init__(self, plate_model: PlateModel):
        super().__init__()
        self.plate_model = plate_model

        self.title("Visualizador de Placa - 48 Testes (Histórico de Análises)")

        self.geometry("1600x900")
        self.after(0, lambda: self.state("zoomed"))

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.header_frame = HeaderFrame(self, plate_model)
        self.header_frame.grid(row=0, column=0, padx=10, pady=(5, 3), sticky="ew")

        self.plate_view = PlateView(self, plate_model, self.on_save_changes)
        self.plate_view.grid(row=1, column=0, padx=10, pady=(3, 10), sticky="nsew")

        self.update_idletasks()

    def on_save_changes(self, model_atualizado: PlateModel):
        """Callback para salvar alterações."""
        print("\n=== DEBUG - Status dos poços ===")
        for row in ROW_LABELS:
            for col in COL_LABELS:
                well_id = f"{row}{col}"
                w = model_atualizado.get_well(well_id)
                if w:
                    print(
                        f"{well_id}: status={w.status}, código={w.code}, amostra={w.sample_id}"
                    )


# --------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Teste do PlateView com historico_analises.csv (48 testes)")
    parser.add_argument(
        "--csv",
        type=str,
        default=CSV_DEFAULT_PATH,
        help="Caminho do historico_analises.csv",
    )
    parser.add_argument(
        "--sep",
        type=str,
        default=CSV_SEP,
        help="Separador do CSV (padrão: ';').",
    )
    parser.add_argument(
        "--exame",
        type=str,
        default=None,
        help="Filtrar por nome de exame (opcional).",
    )
    parser.add_argument(
        "--arquivo_corrida",
        type=str,
        default=None,
        help="Filtrar por arquivo_corrida específico (opcional).",
    )
    parser.add_argument(
        "--list-arquivos",
        action="store_true",
        help="Lista os arquivos de corrida disponíveis e sai.",
    )
    args = parser.parse_args()

    if args.list_arquivos:
        try:
            df = pd.read_csv(args.csv, sep=args.sep, dtype=str)
            if COL_ARQUIVO in df.columns:
                arquivos = df[COL_ARQUIVO].dropna().unique()
                print(f"Arquivos de corrida disponíveis ({len(arquivos)}):")
                for i, arquivo in enumerate(sorted(arquivos), 1):
                    print(f"{i:3d}. {arquivo}")
            else:
                print(f"Coluna '{COL_ARQUIVO}' não encontrada!")
                print(f"Colunas disponíveis: {list(df.columns)}")
        except Exception as e:
            print(f"Erro ao ler CSV: {e}")
        return

    model = PlateModel.from_historico_csv(
        csv_path=args.csv,
        sep=args.sep,
        exame=args.exame,
        arquivo_corrida=args.arquivo_corrida,
    )

    app = MainWindow(model)
    app.mainloop()


if __name__ == "__main__":
    main()

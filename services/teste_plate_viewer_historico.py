'''
Docstring for services.teste_plate_viewer_historico
teste_plate_viewer_historico_pyqt.py

Visualizador de placa (96 poços) em PyQt5 usando dados do
arquivo historico_analises.csv.

- Lê C:/Users/marci/Downloads/Integragal/reports/historico_analises.csv
- Constrói um modelo de placa a partir da coluna "poco" (que pode ter múltiplos poços separados por +)
- Usa as colunas de resultados/CT para SC2, HMPV, INFA, INFB, ADV, RSV, HRV, RP_1, RP_2
- Exibe uma placa 8x12 com cores por status e painel de detalhes editável.
'''

import argparse
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

import pandas as pd
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem,
    QScrollArea, QFrame, QMessageBox, QHeaderView, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette

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

# --------------------------------------------------------------------
# MODELO DE DADOS
# --------------------------------------------------------------------

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


class PlateModel:
    def __init__(self):
        self.wells: Dict[str, WellData] = {}

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
        model._load_from_dataframe(df)
        return model

    def _load_from_dataframe(self, df: pd.DataFrame) -> None:
        wells_created = 0
        wells_skipped = 0
        
        for idx, row in df.iterrows():
            poco_raw = str(row[COL_POCO]).strip() if not pd.isna(row[COL_POCO]) else ""
            if not poco_raw:
                continue
            
            # Separar múltiplos poços (ex: "A1+A2" -> ["A1", "A2"])
            pocos = poco_raw.split('+')
            
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
                
                # Verificar se já existe um poço com este ID (evitar duplicatas)
                if well_id in self.wells:
                    print(f"[AVISO] Poço {well_id} duplicado, mantendo o primeiro")
                    continue
                
                sample = None if pd.isna(row[COL_AMOSTRA]) else str(row[COL_AMOSTRA]).strip()
                code = None if pd.isna(row[COL_CODIGO]) else str(row[COL_CODIGO]).strip()
                
                wd = WellData(
                    row_label=row_label,
                    col_label=col_label,
                    well_id=well_id,
                    sample_id=sample,
                    code=code,
                    targets={},
                )
                
                # heurística simples para CN/CP a partir de amostra/código
                control_type = self._detect_control_type(sample, code)
                if control_type:
                    wd.is_control = True
                    wd.metadata["control_type"] = control_type
                
                # carrega alvos
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
                    
                    wd.targets[alvo] = TargetResult(result=res_text, ct=ct_val)
                
                self._recompute_status(wd)
                self.wells[well_id] = wd
                wells_created += 1
        
        print(f"[INFO] Total de poços criados: {wells_created}")
        print(f"[INFO] Poços no modelo: {list(self.wells.keys())}")

    @staticmethod
    def _detect_control_type(sample: Optional[str], code: Optional[str]) -> Optional[str]:
        """Heurística simples para identificar CN/CP."""
        candidates = []
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
            has_nd = any("ND" in tr.result.upper() for alvo, tr in well.targets.items() if not alvo.startswith("RP"))
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
    if any(k in txt for k in ["DET", "POSI", "REAG", "1"]):
        return "Det"
    if any(k in txt for k in ["NAO", "NÃO", "NEG", "ND", "2"]):
        return "ND"
    if "INC" in txt or "INCON" in txt:
        return "Inc"
    
    return value.strip()


# --------------------------------------------------------------------
# GUI – PyQt5 Implementation
# --------------------------------------------------------------------

class WellButton(QPushButton):
    """Botão personalizado para representar um poço na placa."""
    clicked_with_id = pyqtSignal(str)
    
    def __init__(self, well_id: str, text: str, color: str, parent=None):
        super().__init__(text, parent)
        self.well_id = well_id
        
        # AUMENTEI O TAMANHO DO BOTÃO para acomodar fonte maior
        self.setFixedSize(120, 80)
        
        # FONTE MUITO MAIOR para os códigos de amostra - aumentei de 10 para 16
        font = QFont("Segoe UI", 24, QFont.Bold)  # Aumentei significativamente o tamanho da fonte
        self.setFont(font)
        
        # Estilo com cor de fundo
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: 2px solid #888888;
                border-radius: 5px;
                padding: 2px;
                color: black;
                font-weight: bold;
                font-size: 16px;  /* Fonte maior */
            }}
            QPushButton:hover {{
                border: 3px solid #000000;
                background-color: {self._lighten_color(color)};
            }}
        """)
        
        self.clicked.connect(self.on_click)
    
    def _lighten_color(self, color_hex: str) -> str:
        """Clareia a cor para efeito hover."""
        try:
            color = QColor(color_hex)
            color = color.lighter(110)  # Clareia em 10%
            return color.name()
        except:
            return color_hex
    
    def on_click(self):
        self.clicked_with_id.emit(self.well_id)
    
    def update_appearance(self, text: str, color: str, is_selected: bool):
        """Atualiza o texto e aparência do botão."""
        # Formatar texto para caber no botão
        if len(text) > 12:
            text = text[:11] + ".."
        
        self.setText(text)
        
        border = "3px solid #FF0000" if is_selected else "2px solid #888888"
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: {border};
                border-radius: 5px;
                padding: 2px;
                color: black;
                font-weight: bold;
                font-size: 16px;  /* Fonte maior */
            }}
            QPushButton:hover {{
                border: 3px solid #000000;
                background-color: {self._lighten_color(color)};
            }}
        """)


class PlateView(QWidget):
    def __init__(self, plate_model: PlateModel, on_save_changes=None):
        super().__init__()
        self.plate_model = plate_model
        self.on_save_changes = on_save_changes
        
        self.well_widgets: Dict[str, WellButton] = {}
        self.selected_well_id: Optional[str] = None
        self.current_target: Optional[str] = None
        
        self._init_ui()
        self.render_plate()
    
    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Painel da placa
        plate_panel = QWidget()
        plate_layout = QGridLayout(plate_panel)
        plate_layout.setSpacing(3)
        plate_layout.setContentsMargins(5, 5, 5, 5)
        
        # AUMENTEI O TAMANHO DOS RÓTULOS DAS COLUNAS E LINHAS
        font_labels = QFont("Segoe UI", 12, QFont.Bold)
        
        # Cabeçalho das colunas
        plate_layout.addWidget(QLabel(""), 0, 0)
        for j, col in enumerate(COL_LABELS, start=1):
            label = QLabel(col)
            label.setAlignment(Qt.AlignCenter)
            label.setFont(font_labels)
            label.setFixedSize(70, 35)  # Aumentei para corresponder aos botões maiores
            plate_layout.addWidget(label, 0, j)
        
        # Linhas e poços
        for i, row in enumerate(ROW_LABELS, start=1):
            label = QLabel(row)
            label.setAlignment(Qt.AlignCenter)
            label.setFont(font_labels)
            label.setFixedSize(35, 50)  # Aumentei para corresponder aos botões maiores
            plate_layout.addWidget(label, i, 0)
            
            for j, col in enumerate(COL_LABELS, start=1):
                well_id = f"{row}{col}"
                well = self.plate_model.get_well(well_id)
                
                # Texto para exibir no botão
                text = ""
                if well:
                    text = well.code or well.sample_id or ""
                    if text and well.is_control:
                        ctype = well.metadata.get("control_type", "")
                        if ctype:
                            text = f"{ctype}:{text}"
                
                # Se texto muito longo, encurta
                if len(text) > 12:
                    text = text[:11] + ".."
                
                color = self._status_to_color(well.status if well else EMPTY)
                btn = WellButton(well_id, text, color)
                btn.clicked_with_id.connect(self.on_well_click)
                plate_layout.addWidget(btn, i, j)
                self.well_widgets[well_id] = btn
        
        # Container para a placa com scroll se necessário
        scroll_area = QScrollArea()
        scroll_area.setWidget(plate_panel)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedWidth(1700)  # Largura maior para acomodar botões maiores
        main_layout.addWidget(scroll_area)
        
        # Painel de detalhes
        detail_panel = QFrame()
        detail_panel.setFixedWidth(450)  # Largura um pouco maior
        detail_panel.setFixedHeight(1100)
        detail_panel.setFrameStyle(QFrame.Box | QFrame.Raised)
        detail_layout = QVBoxLayout(detail_panel)
        detail_layout.setContentsMargins(15, 15, 15, 15)
        
        # Título com fonte maior
        title_label = QLabel("Poço selecionado:")
        title_font = QFont("Segoe UI", 16, QFont.Bold)
        title_label.setFont(title_font)
        detail_layout.addWidget(title_label)
        
        # Adicionar espaço
        detail_layout.addSpacing(10)
        
        # Informações do poço
        info_frame = QFrame()
        info_layout = QGridLayout(info_frame)
        info_layout.setSpacing(8)
        
        # Fonte para labels de informação
        font_info_label = QFont("Segoe UI", 12, QFont.Bold)
        font_info_value = QFont("Segoe UI", 12)
        
        info_layout.addWidget(QLabel("Poço:"), 0, 0)
        self.lbl_well_id = QLabel("-")
        self.lbl_well_id.setFont(font_info_value)
        info_layout.addWidget(self.lbl_well_id, 0, 1)
        
        info_layout.addWidget(QLabel("Amostra:"), 1, 0)
        self.lbl_sample_id = QLabel("-")
        self.lbl_sample_id.setFont(font_info_value)
        info_layout.addWidget(self.lbl_sample_id, 1, 1)
        
        info_layout.addWidget(QLabel("Código:"), 2, 0)
        
        code_frame = QWidget()
        code_layout = QHBoxLayout(code_frame)
        code_layout.setContentsMargins(0, 0, 0, 0)
        
        self.entry_code = QLineEdit()
        self.entry_code.setFont(QFont("Segoe UI", 12))
        self.entry_code.setMinimumHeight(35)
        code_layout.addWidget(self.entry_code)
        
        self.btn_apply_code = QPushButton("✓")
        self.btn_apply_code.setFixedSize(40, 35)
        self.btn_apply_code.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.btn_apply_code.clicked.connect(self.apply_code_change)
        code_layout.addWidget(self.btn_apply_code)
        
        info_layout.addWidget(code_frame, 2, 1)
        detail_layout.addWidget(info_frame)
        
        # Adicionar espaço
        detail_layout.addSpacing(15)
        
        # TreeView para alvos
        detail_layout.addWidget(QLabel("Resultados dos Alvos:"))
        
        self.tree_widget = QTreeWidget()
        self.tree_widget.setFixedHeight(600)
        self.tree_widget.setColumnCount(3)
        self.tree_widget.setHeaderLabels(["Alvo", "Resultado", "CT"])
        
        # FONTE MAIOR no tree widget também
        tree_font = QFont("Segoe UI", 12)
        self.tree_widget.setFont(tree_font)
        
        header = self.tree_widget.header()
        header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        # Definir altura mínima para os itens do tree
        self.tree_widget.setStyleSheet("""
            QTreeWidget::item {
                min-height: 35px;
                padding: 5px;
            }
        """)
        
        self.tree_widget.itemSelectionChanged.connect(self.on_tree_select)
        detail_layout.addWidget(self.tree_widget)
        
        # Painel de edição
        edit_frame = QFrame()
        edit_layout = QGridLayout(edit_frame)
        edit_layout.setSpacing(10)
        
        font_edit_label = QFont("Segoe UI", 12)
        
        edit_layout.addWidget(QLabel("Resultado:"), 0, 0)
        self.entry_result = QLineEdit()
        self.entry_result.setFont(font_edit_label)
        self.entry_result.setMinimumHeight(35)
        edit_layout.addWidget(self.entry_result, 0, 1)
        
        edit_layout.addWidget(QLabel("CT:"), 0, 2)
        self.entry_ct = QLineEdit()
        self.entry_ct.setFont(font_edit_label)
        self.entry_ct.setMaximumWidth(120)
        self.entry_ct.setMinimumHeight(35)
        edit_layout.addWidget(self.entry_ct, 0, 3)
        
        self.btn_apply_target = QPushButton("Aplicar ao alvo selecionado")
        self.btn_apply_target.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.btn_apply_target.setMinimumHeight(40)
        self.btn_apply_target.clicked.connect(self.apply_target_changes)
        edit_layout.addWidget(self.btn_apply_target, 1, 0, 1, 4)
        
        detail_layout.addWidget(edit_frame)
        
        # Adicionar espaço
        detail_layout.addSpacing(10)
        
        # Botão Salvar
        self.btn_save = QPushButton("Salvar alterações (teste)")
        self.btn_save.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.btn_save.setMinimumHeight(40)
        self.btn_save.clicked.connect(self._on_save_clicked)
        detail_layout.addWidget(self.btn_save)
        
        # Adicionar espaço expansível
        detail_layout.addStretch(1)
        
        main_layout.addWidget(detail_panel)
    
    @staticmethod
    def _status_to_color(status: str) -> str:
        return STATUS_COLORS.get(status, "#ffffff")
    
    def render_plate(self):
        """Atualiza a exibição de todos os poços."""
        for well_id, btn in self.well_widgets.items():
            well = self.plate_model.get_well(well_id)
            
            # Texto para exibir no botão
            text = ""
            if well:
                text = well.code or well.sample_id or ""
                if text and well.is_control:
                    ctype = well.metadata.get("control_type", "")
                    if ctype:
                        text = f"{ctype}:{text}"
            
            # Se texto muito longo, encurta
            if len(text) > 12:
                text = text[:11] + ".."
            
            color = self._status_to_color(well.status if well else EMPTY)
            
            # Verificar se este é o poço selecionado
            is_selected = (well_id == self.selected_well_id)
            
            # Atualizar aparência do botão
            btn.update_appearance(text, color, is_selected)
    
    def on_well_click(self, well_id: str):
        """Manipula o clique em um poço."""
        self.selected_well_id = well_id
        
        # Atualizar todos os botões para refletir a nova seleção
        self.render_plate()
        
        # Preencher painel de detalhes
        well = self.plate_model.get_well(well_id)
        if not well:
            self.lbl_well_id.setText("-")
            self.lbl_sample_id.setText("-")
            self.entry_code.clear()
            self.tree_widget.clear()
            self.entry_result.clear()
            self.entry_ct.clear()
            return
        
        self.fill_detail_panel(well)
    
    def fill_detail_panel(self, well: WellData):
        """Preenche o painel de detalhes com informações do poço."""
        self.lbl_well_id.setText(well.well_id)
        self.lbl_sample_id.setText(well.sample_id or "-")
        self.entry_code.setText(well.code or "")
        
        # Limpar e preencher tree widget
        self.tree_widget.clear()
        for alvo, tr in well.targets.items():
            ct_text = "" if tr.ct is None else f"{tr.ct:.3f}"
            item = QTreeWidgetItem([alvo, tr.result, ct_text])
            item.setData(0, Qt.UserRole, alvo)
            self.tree_widget.addTopLevelItem(item)
        
        self.entry_result.clear()
        self.entry_ct.clear()
        self.current_target = None
    
    def on_tree_select(self):
        """Manipula a seleção de um alvo na tree."""
        items = self.tree_widget.selectedItems()
        if not items:
            self.current_target = None
            return
        
        item = items[0]
        self.current_target = item.data(0, Qt.UserRole)
        self.entry_result.setText(item.text(1))
        self.entry_ct.setText(item.text(2))
    
    def apply_code_change(self):
        """Aplica a alteração do código de amostra."""
        if not self.selected_well_id:
            return
        
        well = self.plate_model.get_well(self.selected_well_id)
        if not well:
            return
        
        new_code = self.entry_code.text().strip()
        well.code = new_code if new_code else None
        
        # Reavaliar se é controle
        control_type = PlateModel._detect_control_type(well.sample_id, well.code)
        if control_type:
            well.is_control = True
            well.metadata["control_type"] = control_type
        else:
            well.is_control = False
            well.metadata.pop("control_type", None)
        
        # Recalcular status
        self.plate_model._recompute_status(well)
        
        # Atualizar exibição
        self.render_plate()
        print(f"[INFO] Código do poço {well.well_id} atualizado para: {well.code}")
    
    def apply_target_changes(self):
        """Aplica alterações no resultado/CT do alvo selecionado."""
        if not self.selected_well_id or not self.current_target:
            return
        
        well = self.plate_model.get_well(self.selected_well_id)
        if not well:
            return
        
        new_result = self.entry_result.text().strip()
        ct_text = self.entry_ct.text().strip()
        new_ct: Optional[float] = None
        
        if ct_text:
            try:
                new_ct = float(ct_text.replace(",", "."))
            except ValueError:
                new_ct = None
        
        well.targets[self.current_target] = TargetResult(new_result, new_ct)
        self.plate_model._recompute_status(well)
        
        # Atualizar exibição
        self.fill_detail_panel(well)
        self.render_plate()
    
    def _on_save_clicked(self):
        if self.on_save_changes:
            self.on_save_changes(self.plate_model)


class MainWindow(QMainWindow):
    def __init__(self, plate_model: PlateModel):
        super().__init__()
        self.plate_model = plate_model
        
        self.setWindowTitle("Visualização de Placa - historico_analises.csv")
        self.setGeometry(100, 100, 1500, 800)  # Janela maior para acomodar botões maiores
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Criar visualizador
        self.plate_view = PlateView(plate_model, self.on_save_changes)
        main_layout.addWidget(self.plate_view)
    
    def on_save_changes(self, model_atualizado: PlateModel):
        print("\n=== DEBUG - Status dos poços ===")
        for row in ROW_LABELS:
            for col in COL_LABELS:
                well_id = f"{row}{col}"
                w = model_atualizado.get_well(well_id)
                if w:
                    print(f"{well_id}: status={w.status}, código={w.code}, amostra={w.sample_id}")


# --------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Teste do PlateView com historico_analises.csv")
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

    # Opção para listar arquivos de corrida
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

    # Carregar modelo
    model = PlateModel.from_historico_csv(
        csv_path=args.csv,
        sep=args.sep,
        exame=args.exame,
        arquivo_corrida=args.arquivo_corrida,
    )

    # Criar aplicação PyQt
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Estilo moderno
    
    window = MainWindow(model)
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
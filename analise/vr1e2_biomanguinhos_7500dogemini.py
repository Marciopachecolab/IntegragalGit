import os
import re
from datetime import datetime
from tkinter import filedialog, messagebox
from typing import Any, Dict, List, Optional, Tuple

import customtkinter as ctk
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from pandas.errors import ParserError

# Adiciona o diretÃ³rio base no sys.path para imports locais
from services.system_paths import BASE_DIR

from ..db.db_utils import salvar_historico_processamento
from ..utils.after_mixin import AfterManagerMixin
# ImportaÃ§Ãµes centralizadas
from ..utils.logger import registrar_log

# ---------- ConfiguraÃ§Ãµes e constantes globais ----------

CT_RP_MIN = 10
CT_RP_MAX = 35
CT_DETECTAVEL_MIN = 10
CT_DETECTAVEL_MAX = 38
CT_INCONCLUSIVO_MIN = 38.01
CT_INCONCLUSIVO_MAX = 40

TARGET_LIST = ["SC2", "HMPV", "INF A", "INF B", "ADV", "RSV", "HRV"]

RESULT_MAPPING_TO_CSV = {"DetectÃ¡vel": "1", "ND": "2", "Inconclusivo": "3"}

CSV_COLUMNS_MODEL = [
    "codigoAmostra",
    "codigo",
    "requisicao",
    "paciente",
    "exame",
    "metodo",
    "registroInterno",
    "kit",
    "reteste",
    "loteKit",
    "dataProcessamentoFim",
    "valorReferencia",
    "observacao",
    "painel",
    "resultado",
    "influenzaa",
    "influenzab",
    "coronavirusncov",
    "coronavirus229e",
    "coronavirusnl63",
    "coronavirushku1",
    "coronavirusoc43",
    "adenovirus",
    "vsincicialresp",
    "metapneumovirus",
    "rinovirus",
    "bocavirus",
    "enterovirus",
    "parainflu_1",
    "parainflu_2",
    "parainflu_3",
    "parainflu_4",
    "coronavirus",
    "influenzaahn",
    "metapneumovirua",
    "metapneumovirub",
    "mycoplasma",
    "parechovÃ­rus",
    "vsincicialrespa",
    "vsincicialrespb",
    "influenzaah_3",
    "influenzaah_1",
    "influenzaah_7",
]

TARGET_RESULT_TO_CSV_COLUMN_MAPPING = {
    "Resultado(INF A)": "influenzaa",
    "Resultado(INF B)": "influenzab",
    "Resultado(SC2)": "coronavirusncov",
    "Resultado(HMPV)": "metapneumovirus",
    "Resultado(ADV)": "adenovirus",
    "Resultado(RSV)": "vsincicialresp",
    "Resultado(HRV)": "rinovirus",
}

HUMAN_READABLE_TARGET_NAMES = {
    "coronavirusncov": "SC2",
    "metapneumovirus": "HMPV",
    "influenzaa": "INF A",
    "influenzab": "INF B",
    "adenovirus": "ADV",
    "vsincicialresp": "RSV",
    "rinovirus": "HRV",
}

CONTROL_NEGATIVE_IDENTIFIERS = ["CN", "NEG"]
CONTROL_POSITIVE_IDENTIFIERS = ["CP", "POS"]

DEFAULT_CSV_VALUES = {
    "paciente": "",
    "exame": "VRSRT",
    "metodo": "RTTR",
    "kit": "427",
    "painel": "1",
    "resultado": "",
}

# Cores para visualizaÃ§Ã£o
COLOR_VALID_SELECTED = "#d4edda"
COLOR_INVALID = "#f8d7da"
COLOR_INCONCLUSIVE = "#fff3cd"
COLOR_UNDEFINED = "#e2e3e5"


def _convert_ct_value(value: Any) -> Optional[float]:
    """Converte valores de CT para float, tratando diferentes formatos."""
    if pd.isna(value) or str(value).strip().lower() in ["", "undetermined", "nan"]:
        return np.nan
    try:
        cleaned = str(value).replace(",", ".").strip()
        # Remove caracteres nÃ£o numÃ©ricos, exceto pontos
        cleaned = re.sub(r"[^\d.]", "", cleaned)
        return round(float(cleaned), 2)
    except (ValueError, TypeError):
        registrar_log(
            "ConversÃ£o", f"Falha ao converter valor de CT: '{value}'", level="WARNING"
        )
        return np.nan


def _generate_well_pairs() -> List[Tuple[str, str]]:
    """Gera pares de poÃ§os (ex: A1+A2, A3+A4, ..., H11+H12) para anÃ¡lise."""
    return [
        (f"{row}{col}", f"{row}{col + 1}")
        for row in "ABCDEFGH"
        for col in range(1, 13, 2)
    ]


def load_and_preprocess_data(filepath: str) -> pd.DataFrame:
    """Carrega e prÃ©-processa dados da placa com tratamento robusto."""
    registrar_log(
        "AnÃ¡lise Dados", f"Carregando: {os.path.basename(filepath)}", level="INFO"
    )

    ext = os.path.splitext(filepath)[1].lower()
    df = None

    # LÃ³gica de tentativa unificada para leitura de arquivos
    for skip in range(30):
        try:
            if ext in [".xls", ".xlsx", ".xlsm"]:
                # Tenta a aba 'Results' primeiro, depois a primeira aba
                try:
                    df = pd.read_excel(filepath, sheet_name="Results", skiprows=skip)
                except (IOError, ValueError):
                    df = pd.read_excel(filepath, skiprows=skip)

            elif ext == ".csv":
                # Tenta diferentes separadores e encodings para CSV
                separators = [";", ",", "\t"]
                for sep in separators:
                    try:
                        df = pd.read_csv(
                            filepath, sep=sep, skiprows=skip, on_bad_lines="skip"
                        )
                        break  # Sai do loop de separadores se a leitura for bem-sucedida
                    except (ParserError, UnicodeDecodeError):
                        continue

            if df is not None and not df.empty:
                # Normaliza nomes de colunas para encontrar colunas essenciais
                df.columns = [str(col).strip() for col in df.columns]
                if any(
                    "Well" in col or "PoÃ§o" in col or "Poco" in col
                    for col in df.columns
                ):
                    registrar_log(
                        "Leitura", f"Arquivo lido, pulando {skip} linhas", level="INFO"
                    )
                    break  # Sai do loop de `skip` se as colunas forem encontradas
        except Exception:
            df = None
            continue

    if df is None:
        raise ValueError(
            f"NÃ£o foi possÃ­vel identificar o cabeÃ§alho em {os.path.basename(filepath)}"
        )

    # Mapeamento de nomes de colunas para padronizaÃ§Ã£o
    column_mapping = {
        "CÑ‚": "CT",
        "Cq": "CT",
        "Cycle Threshold": "CT",
        "Ct": "CT",
        "Threshold Cycle": "CT",
        "Cicles": "CT",
        "Target Name": "Target",
        "Alvo": "Target",
        "Nome do Alvo": "Target",
        "Marker": "Target",
        "Sample Name": "Sample",
        "Amostra": "Sample",
        "IdentificaÃ§Ã£o": "Sample",
        "ID": "Sample",
        "Well Position": "Well",
        "PoÃ§o": "Well",
        "Poco": "Well",
        "PosiÃ§Ã£o": "Well",
        "Location": "Well",
    }

    normalized_columns = {}
    for col in df.columns:
        found = False
        for old_name, new_name in column_mapping.items():
            if old_name.lower() == str(col).lower():
                normalized_columns[col] = new_name
                found = True
                break
        if not found:
            normalized_columns[col] = col

    df.rename(columns=normalized_columns, inplace=True)

    # Garante as colunas essenciais
    required_cols = ["Well", "Target", "Sample"]
    missing = [col for col in required_cols if col not in df.columns]

    if missing:
        available = ", ".join(df.columns)
        raise ValueError(
            f"Colunas essenciais faltando: {', '.join(missing)}\n"
            f"Colunas disponÃ­veis: {available}"
        )

    if "CT" in df.columns:
        df["CT"] = df["CT"].apply(_convert_ct_value)
    else:
        registrar_log("AnÃ¡lise Dados", "Coluna CT nÃ£o encontrada", level="WARNING")

    return df


class PlateAnalysisProcessor:
    """Processa os dados brutos de uma placa de PCR para determinar resultados e status de validaÃ§Ã£o das amostras."""

    def __init__(
        self,
        df_raw_data: pd.DataFrame,
        filename: str,
        extraction_data: Optional[dict] = None,
    ):
        self.df_raw_data = df_raw_data
        self.filename = filename
        self.extraction_data = extraction_data or {}
        self.analysis_info: Dict[str, Any] = {}
        self.df_processed_results: Optional[pd.DataFrame] = None
        registrar_log(
            "PlateAnalysisProcessor",
            f"Processador inicializado para arquivo: {os.path.basename(filename)}",
            level="INFO",
        )

    def _extract_plate_metadata(self) -> None:
        """Extrai metadados como nÃºmero da placa e data do nome do arquivo."""
        # Regex aprimorada para ser mais flexÃ­vel
        match = re.search(r"(PLACA\s*\d+).*(\d{8})", self.filename, re.IGNORECASE)
        num_placa = match.group(1).replace(" ", "") if match else "Placa Desconhecida"
        data_placa = match.group(2) if match else "Data Desconhecida"

        data_formatada = data_placa
        if data_placa != "Data Desconhecida":
            try:
                data_formatada = datetime.strptime(data_placa, "%Y%m%d").strftime(
                    "%d/%m/%Y"
                )
            except ValueError:
                registrar_log(
                    "PlateAnalysisProcessor",
                    f"Formato de data invÃ¡lido no nome do arquivo: {data_placa}",
                    level="WARNING",
                )

        self.analysis_info["NÃºmero da Placa"] = num_placa
        self.analysis_info["Data"] = data_formatada
        self.analysis_info["Status da Corrida"] = "Corrida vÃ¡lida"
        self.analysis_info["Amostras InvÃ¡lidas"] = 0
        registrar_log(
            "PlateAnalysisProcessor",
            f"Metadados da placa extraÃ­dos: {num_placa}, {data_formatada}",
            level="INFO",
        )

    def _analyze_well_pair(self, well1: str, well2: str) -> dict:
        """Analisa um par de poÃ§os usando dados de extraÃ§Ã£o."""
        subset = self.df_raw_data[self.df_raw_data["Well"].isin([well1, well2])].copy()

        # Acesso robusto ao nome da amostra
        sample_name = self.extraction_data.get(well1, "Desconhecido")
        sample_upper = str(sample_name).upper()

        # AnÃ¡lise do controle interno (RP)
        rp_subset = subset[subset["Target"] == "RP"]
        rp_cts = (
            rp_subset["CT"].dropna()
            if "CT" in rp_subset.columns
            else pd.Series(dtype=float)
        )
        rp_valido = any(CT_RP_MIN <= ct <= CT_RP_MAX for ct in rp_cts)

        # Determina se Ã© um controle
        is_control = any(
            id in sample_upper
            for id in CONTROL_NEGATIVE_IDENTIFIERS + CONTROL_POSITIVE_IDENTIFIERS
        )

        # ValidaÃ§Ã£o da amostra
        status_validacao = "VÃ¡lido"
        if not is_control and not rp_valido:
            status_validacao = "InvÃ¡lido"
        if is_control and not rp_valido:
            status_validacao = "InvÃ¡lido"
            self.analysis_info["Status da Corrida"] = "Corrida invÃ¡lida"

        # Coleta de resultados para cada alvo
        ct_str_por_alvo = {alvo: "â€”" for alvo in TARGET_LIST}
        resultado_por_alvo = {alvo: "ND" for alvo in TARGET_LIST}
        inconclusivo_flag = False
        alvos_detectados = []

        for alvo in TARGET_LIST:
            alvo_subset = subset[subset["Target"] == alvo]
            ct_alvo = (
                alvo_subset["CT"].dropna()
                if "CT" in alvo_subset.columns
                else pd.Series(dtype=float)
            )

            # Encontra o primeiro valor detectÃ¡vel ou inconclusivo
            ct_val = next((ct for ct in ct_alvo if not pd.isna(ct)), None)

            if ct_val is not None:
                if CT_DETECTAVEL_MIN <= ct_val <= CT_DETECTAVEL_MAX:
                    resultado_por_alvo[alvo] = "DetectÃ¡vel"
                    alvos_detectados.append(alvo)
                    ct_str_por_alvo[alvo] = f"{ct_val:.2f}".replace(".", ",")
                elif CT_INCONCLUSIVO_MIN <= ct_val <= CT_INCONCLUSIVO_MAX:
                    resultado_por_alvo[alvo] = "Inconclusivo"
                    inconclusivo_flag = True
                    ct_str_por_alvo[alvo] = f"{ct_val:.2f}".replace(".", ",")
                else:
                    ct_str_por_alvo[alvo] = f"{ct_val:.2f}".replace(".", ",")

        selecionado = status_validacao == "VÃ¡lido" and not inconclusivo_flag

        # Se for invÃ¡lido, nÃ£o deve ser selecionado
        if status_validacao == "InvÃ¡lido":
            selecionado = False

        # Contagem de amostras invÃ¡lidas
        if not selecionado and status_validacao == "InvÃ¡lido":
            self.analysis_info["Amostras InvÃ¡lidas"] += 1

        return {
            "Selecionado": selecionado,
            "Sample": sample_name,
            "PoÃ§os": f"{well1}+{well2}",
            "RP (CT)": (
                ", ".join([f"{ct:.2f}".replace(".", ",") for ct in rp_cts])
                if not rp_cts.empty
                else "â€”"
            ),
            "ValidaÃ§Ã£o": status_validacao,
            "Alvos Detectados": ", ".join(alvos_detectados)
            or "Nenhum Alvo DetectÃ¡vel",
            **{f"CT({alvo})": ct_str_por_alvo[alvo] for alvo in TARGET_LIST},
            **{f"Resultado({alvo})": resultado_por_alvo[alvo] for alvo in TARGET_LIST},
        }

    def analyze_plate(self) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Executa a anÃ¡lise completa da placa, processando cada par de poÃ§os."""
        registrar_log(
            "PlateAnalysisProcessor", "Iniciando anÃ¡lise da placa.", level="INFO"
        )
        self._extract_plate_metadata()
        resultados = []
        well_pairs = _generate_well_pairs()

        for well1, well2 in well_pairs:
            # Verifica se pelo menos um dos poÃ§os existe nos dados brutos
            if not self.df_raw_data["Well"].isin([well1, well2]).any():
                registrar_log(
                    "PlateAnalysisProcessor",
                    f"PoÃ§os {well1}+{well2} nÃ£o encontrados nos dados brutos. Pulando.",
                    level="DEBUG",
                )
                continue

            # Garante que os poÃ§os nÃ£o sÃ£o vazios na extraÃ§Ã£o (seja por um arquivo .txt vazio)
            sample_name = self.extraction_data.get(well1, "")
            if not sample_name:
                registrar_log(
                    "PlateAnalysisProcessor",
                    f"Amostra nÃ£o encontrada para o poÃ§o {well1}. Pulando.",
                    level="DEBUG",
                )
                continue

            resultado = self._analyze_well_pair(well1, well2)
            resultados.append(resultado)

        self.df_processed_results = pd.DataFrame(resultados)
        registrar_log(
            "PlateAnalysisProcessor",
            f"AnÃ¡lise da placa concluÃ­da. {len(resultados)} pares de poÃ§os processados.",
            level="INFO",
        )
        return self.df_processed_results, self.analysis_info


def count_detectable_samples(df_processed_results: pd.DataFrame) -> Dict[str, int]:
    """Conta o nÃºmero de amostras detectÃ¡veis para cada alvo em resultados vÃ¡lidos."""
    counts = {col_csv: 0 for col_csv in TARGET_RESULT_TO_CSV_COLUMN_MAPPING.values()}

    df_validos = df_processed_results[df_processed_results["Selecionado"] == True]

    for _, row in df_validos.iterrows():
        for internal_col, csv_col in TARGET_RESULT_TO_CSV_COLUMN_MAPPING.items():
            if row.get(internal_col, "") == "DetectÃ¡vel":
                counts[csv_col] += 1
    registrar_log(
        "RelatÃ³rio AnÃ¡lise",
        "Contagem de amostras detectÃ¡veis realizada.",
        level="INFO",
    )
    return counts


def display_analysis_report(
    analysis_info: Dict[str, Any], detectable_counts: Dict[str, int]
) -> None:
    """Exibe um relatÃ³rio de anÃ¡lise em uma caixa de mensagem."""
    report = (
        f"Placa: {analysis_info.get('NÃºmero da Placa', 'N/A')}\n"
        f"Data: {analysis_info.get('Data', 'N/A')}\n"
        f"Status da Corrida: {analysis_info.get('Status da Corrida', 'N/A')}\n"
        f"Amostras InvÃ¡lidas: {analysis_info.get('Amostras InvÃ¡lidas', 0)}\n\n"
        f"Contagem de DetectÃ¡veis (amostras vÃ¡lidas):\n"
    )
    for csv_col in sorted(
        detectable_counts.keys(), key=lambda c: HUMAN_READABLE_TARGET_NAMES.get(c, c)
    ):
        human_name = HUMAN_READABLE_TARGET_NAMES.get(csv_col, csv_col)
        report += f"{human_name}: {detectable_counts[csv_col]} detectÃ¡veis\n"

    messagebox.showinfo("RelatÃ³rio de AnÃ¡lise", report)
    registrar_log(
        "RelatÃ³rio AnÃ¡lise",
        "RelatÃ³rio de anÃ¡lise exibido ao usuÃ¡rio.",
        level="INFO",
    )


def generate_detectable_plot(detectable_counts: Dict[str, int]) -> None:
    """Gera e exibe um grÃ¡fico de barras das amostras detectÃ¡veis."""
    if not detectable_counts or all(v == 0 for v in detectable_counts.values()):
        messagebox.showinfo(
            "GrÃ¡fico de DetecÃ§Ã£o", "Nenhum alvo detectÃ¡vel para gerar o grÃ¡fico."
        )
        registrar_log(
            "GrÃ¡fico DetecÃ§Ã£o",
            "Nenhum alvo detectÃ¡vel para gerar o grÃ¡fico.",
            level="INFO",
        )
        return

    labels = [
        HUMAN_READABLE_TARGET_NAMES.get(k, k)
        for k, v in detectable_counts.items()
        if v > 0
    ]
    values = [v for v in detectable_counts.values() if v > 0]

    plt.figure(figsize=(10, 5))
    plt.bar(labels, values, color="skyblue")
    plt.title("NÃºmero de Amostras DetectÃ¡veis por Agravo")
    plt.xlabel("Agravo")
    plt.ylabel("Quantidade")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()
    registrar_log(
        "GrÃ¡fico DetecÃ§Ã£o",
        "GrÃ¡fico de amostras detectÃ¡veis gerado e exibido.",
        level="INFO",
    )


def generate_plate_map(df_processed_results: pd.DataFrame) -> None:
    """Gera e exibe um mapa visual da placa de PCR com os resultados."""
    plt.close("all")
    rows = "ABCDEFGH"
    cols = range(1, 13)
    fig, ax = plt.subplots(figsize=(16, 10))

    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.set_aspect("equal")
    ax.invert_yaxis()
    ax.set_xticks([i + 0.5 for i in range(12)])
    ax.set_xticklabels([str(c) for c in cols])
    ax.set_yticks([i + 0.5 for i in range(8)])
    ax.set_yticklabels(list(rows))
    ax.tick_params(axis="both", which="both", length=0)
    ax.grid(True, color="gray", linestyle="-", linewidth=0.5)
    ax.set_title("Mapa de Resultados da Placa de PCR", fontsize=16)

    # Adiciona rÃ³tulos de coluna e linha fora do grid
    for c in cols:
        ax.text(
            c - 0.5, -0.7, str(c), ha="center", va="center", fontsize=10, weight="bold"
        )
    for i, r in enumerate(rows):
        ax.text(-0.7, i + 0.5, r, ha="center", va="center", fontsize=10, weight="bold")

    for _, row in df_processed_results.iterrows():
        well1 = row["PoÃ§os"].split("+")[0]
        row_char = well1[0]
        col_num = int(well1[1:])
        row_idx = rows.index(row_char)
        col_idx = col_num - 1

        # Determina a cor do poÃ§o com base no status
        facecolor = COLOR_UNDEFINED
        if row.get("Selecionado") == True:
            facecolor = COLOR_VALID_SELECTED
        elif row.get("ValidaÃ§Ã£o") == "InvÃ¡lido":
            facecolor = COLOR_INVALID
        elif any("Inconclusivo" in row.get(f"Resultado({t})", "") for t in TARGET_LIST):
            facecolor = COLOR_INCONCLUSIVE

        rect = Rectangle(
            (col_idx, row_idx),
            2,
            1,
            facecolor=facecolor,
            edgecolor="black",
            linewidth=0.8,
            alpha=0.8,
        )
        ax.add_patch(rect)

        # Adiciona textos dentro do poÃ§o
        texts = []
        texts.append(
            ("âœ“" if row.get("Selecionado") == True else "[ ]") + f" {row['Sample']}"
        )
        texts.append(f"RP: {row['RP (CT)']}")

        detected_targets = []
        for t in TARGET_LIST:
            res = row.get(f"Resultado({t})", "ND")
            ct = row.get(f"CT({t})", "â€”")
            if res == "DetectÃ¡vel":
                detected_targets.append(f"{t}: {ct} (D)")
            elif res == "Inconclusivo":
                detected_targets.append(f"{t}: {ct} (I)")

        texts.append("\n".join(detected_targets) if detected_targets else "ND")

        validation_status = row.get("ValidaÃ§Ã£o", "")
        if validation_status == "VÃ¡lido" and row.get("Selecionado") != True:
            validation_status = "VÃ¡lido (NÃ£o Selecionado)"

        texts.append(f"Status: {validation_status}")

        ax.text(
            col_idx + 1,
            row_idx + 0.5,
            "\n".join(texts),
            ha="center",
            va="center",
            fontsize=7,
            color="black",
            bbox=dict(facecolor="white", alpha=0.0, edgecolor="none"),
        )

    plt.tight_layout()
    plt.show()
    plt.close("all")
    registrar_log(
        "GrÃ¡fico DetecÃ§Ã£o", "Mapa da placa gerado e exibido.", level="INFO"
    )


def export_analysis_to_csv(df_processed_results: pd.DataFrame, lote_kit: str) -> None:
    """Exporta os resultados processados para um arquivo CSV no formato GAL."""
    registrar_log(
        "ExportaÃ§Ã£o CSV",
        "Iniciando exportaÃ§Ã£o de resultados para CSV (funÃ§Ã£o interna).",
        level="INFO",
    )
    lines_to_export = []
    processing_end_date = datetime.now().strftime("%d/%m/%Y")
    log_file_path = os.path.join(BASE_DIR, "logs", "resultados_por_amostra.txt")
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    detectable_counts = {
        col_csv: 0 for col_csv in TARGET_RESULT_TO_CSV_COLUMN_MAPPING.values()
    }

    df_selecionados = df_processed_results[df_processed_results["Selecionado"] == True]
    if df_selecionados.empty:
        messagebox.showwarning(
            "Nenhuma Amostra", "Nenhuma amostra vÃ¡lida para exportaÃ§Ã£o."
        )
        registrar_log(
            "ExportaÃ§Ã£o CSV",
            "Nenhuma amostra vÃ¡lida para exportaÃ§Ã£o.",
            level="WARNING",
        )
        return

    try:
        with open(log_file_path, "w", encoding="utf-8") as log_file:
            for _, row in df_selecionados.iterrows():
                csv_line = {col_name: "" for col_name in CSV_COLUMNS_MODEL}
                csv_line["codigoAmostra"] = row["Sample"]
                csv_line["registroInterno"] = row["Sample"]
                csv_line["loteKit"] = lote_kit
                csv_line["dataProcessamentoFim"] = processing_end_date

                for k, v in DEFAULT_CSV_VALUES.items():
                    csv_line[k] = v

                for (
                    internal_col,
                    csv_col,
                ) in TARGET_RESULT_TO_CSV_COLUMN_MAPPING.items():
                    internal_result = row.get(internal_col, "")
                    mapped_value = RESULT_MAPPING_TO_CSV.get(internal_result, "")
                    csv_line[csv_col] = mapped_value

                    if mapped_value == "1":
                        detectable_counts[csv_col] += 1

                for col in CSV_COLUMNS_MODEL:
                    if col not in csv_line:
                        csv_line[col] = ""

                lines_to_export.append(csv_line)

                # Log detalhado
                log_file.write(f"Amostra {csv_line['codigoAmostra']}:\n")
                for col in CSV_COLUMNS_MODEL:
                    log_file.write(f"  {col}: {csv_line.get(col, '')}\n")
                log_file.write("\n")

    except Exception as e:
        registrar_log(
            "ExportaÃ§Ã£o CSV",
            f"Erro ao preparar dados para exportaÃ§Ã£o ou escrever log: {e}",
            level="ERROR",
        )
        messagebox.showerror("Erro", f"Falha ao preparar dados para exportaÃ§Ã£o: {e}")
        return

    df_export = pd.DataFrame(lines_to_export, columns=CSV_COLUMNS_MODEL)

    output_filepath = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        title="Salvar CSV no Formato GAL",
    )

    if output_filepath:
        try:
            df_export.to_csv(output_filepath, sep=";", index=False, encoding="utf-8")
            registrar_log(
                "ExportaÃ§Ã£o CSV", f"Arquivo salvo em: {output_filepath}", level="INFO"
            )

            msg = f"Arquivo salvo em: {output_filepath}\nLog salvo em: {log_file_path}\n\nContagem de DetectÃ¡veis:\n"
            for col_csv in sorted(
                detectable_counts.keys(),
                key=lambda c: HUMAN_READABLE_TARGET_NAMES.get(c, c),
            ):
                human = HUMAN_READABLE_TARGET_NAMES.get(col_csv, col_csv)
                msg += f"{human}: {detectable_counts[col_csv]} detectÃ¡veis\n"

            messagebox.showinfo("ExportaÃ§Ã£o ConcluÃ­da", msg)
            generate_detectable_plot(detectable_counts)

        except Exception as e:
            registrar_log(
                "Erro ExportaÃ§Ã£o", f"Falha ao salvar CSV: {e}", level="ERROR"
            )
            messagebox.showerror("Erro", f"Falha ao salvar CSV: {e}")
    else:
        messagebox.showwarning("Cancelado", "ExportaÃ§Ã£o cancelada pelo usuÃ¡rio.")
        registrar_log(
            "ExportaÃ§Ã£o CSV", "ExportaÃ§Ã£o cancelada pelo usuÃ¡rio.", level="INFO"
        )

    plt.close("all")


class AnalysisWindow(AfterManagerMixin, ctk.CTkToplevel):
    """Janela Toplevel para realizar a anÃ¡lise de dados de placa de PCR."""

    def __init__(self, master, dados_extracao=None):
        super().__init__(master=master)
        self.title("AnÃ¡lise VR1e2 Biomanguinhos 7500")
        self.geometry("1024x768")
        self.dados_extracao = dados_extracao or {}
        self.protocol("WM_DELETE_WINDOW", self._safe_close)
        self.df_results = None
        self.analysis_summary = None
        registrar_log(
            "AnalysisWindow", "Janela de anÃ¡lise inicializada.", level="INFO"
        )
        self._init_analysis()

    def _init_analysis(self):
        """Inicia o fluxo de anÃ¡lise, solicitando o arquivo de dados da placa."""
        file_path = filedialog.askopenfilename(
            parent=self,
            title="Selecione o Arquivo de Dados da Placa",
            filetypes=[
                ("Planilhas Excel", "*.xls;*.xlsx;*.xlsm"),
                ("Arquivos CSV", "*.csv"),
            ],
        )
        if not file_path:
            registrar_log(
                "AnÃ¡lise Cancelada",
                "Nenhum arquivo de dados da placa selecionado.",
                level="INFO",
            )
            self._safe_close()
            return

        try:
            df_raw = load_and_preprocess_data(file_path)
            file_name = os.path.basename(file_path)
            processor = PlateAnalysisProcessor(
                df_raw, file_name, extraction_data=self.dados_extracao
            )
            self.df_results, self.analysis_summary = processor.analyze_plate()

            # Garante que temos resultados vÃ¡lidos antes de continuar
            if self.df_results is None or self.df_results.empty:
                messagebox.showwarning(
                    "Aviso", "A anÃ¡lise nÃ£o retornou resultados vÃ¡lidos."
                )
                self._safe_close()
                return

            detectable_counts = count_detectable_samples(self.df_results)
            display_analysis_report(self.analysis_summary, detectable_counts)

            from ..utils.gui_utils import TabelaComSelecaoSimulada

            self.table_window = TabelaComSelecaoSimulada(
                self,
                self.df_results,
                self.analysis_summary["Status da Corrida"],
                self.analysis_summary["NÃºmero da Placa"],
                self.analysis_summary["Data"],
                agravos=TARGET_LIST,
            )
            self.table_window.grab_set()
            self.wait_window(self.table_window)

            # ApÃ³s a tabela ser fechada, verifica se a janela principal ainda existe
            if not self.winfo_exists():
                return

            # Pega o df atualizado com as seleÃ§Ãµes do usuÃ¡rio
            self.df_results = self.table_window.df_atualizado

            generate_plate_map(self.df_results)
            salvar_historico_processamento(
                "Analista",
                "VR1e2 Biomanguinhos 7500",
                self.analysis_summary["Status da Corrida"],
                f"Placa: {self.analysis_summary['NÃºmero da Placa']}",
            )
            registrar_log(
                "AnalysisWindow",
                "AnÃ¡lise concluÃ­da e histÃ³rico salvo.",
                level="INFO",
            )

        except Exception as e:
            registrar_log(
                "Erro AnÃ¡lise", f"Erro durante a anÃ¡lise da placa: {e}", level="ERROR"
            )
            messagebox.showerror("Erro", f"Erro durante a anÃ¡lise: {e}", parent=self)
            self._safe_close()
        finally:
            plt.close("all")

    def _safe_close(self):
        """Fecha a janela de forma segura, cancelando todos os recursos."""
        try:
            self.dispose()
            self.grab_release()
            self.update_idletasks()
            if self.winfo_exists():
                self.destroy()
            registrar_log(
                "Fechamento", "Janela de anÃ¡lise fechada com seguranÃ§a", level="INFO"
            )
        except Exception as e:
            registrar_log(
                "Erro Fechamento", f"Erro crÃ­tico ao fechar janela: {e}", level="ERROR"
            )


def abrir_analise(master, dados_extracao=None):
    """FunÃ§Ã£o exposta para criar a janela de anÃ¡lise."""
    registrar_log(
        "AnÃ¡lise Integrada", "Chamada para abrir janela de anÃ¡lise.", level="INFO"
    )
    return AnalysisWindow(master=master, dados_extracao=dados_extracao)


def analisar_placa_vr1e2_7500(
    master_app_root: ctk.CTk, dados_extracao: dict, parte_placa: str
) -> pd.DataFrame:
    """FunÃ§Ã£o de anÃ¡lise para VR1e2 Biomanguinhos 7500, integrada ao sistema principal."""
    try:
        registrar_log(
            "AnÃ¡lise Integrada",
            "Iniciando anÃ¡lise com dados de extraÃ§Ã£o",
            level="INFO",
        )

        janela_analise = abrir_analise(
            master=master_app_root, dados_extracao=dados_extracao
        )
        janela_analise.grab_set()
        master_app_root.wait_window(janela_analise)

        if (
            janela_analise.df_results is not None
            and not janela_analise.df_results.empty
        ):
            registrar_log(
                "AnÃ¡lise Integrada", "AnÃ¡lise concluÃ­da com sucesso", level="INFO"
            )
            return janela_analise.df_results
        else:
            registrar_log(
                "AnÃ¡lise Integrada",
                "AnÃ¡lise retornou DataFrame vazio ou None",
                level="WARNING",
            )
            return pd.DataFrame()
    except Exception as e:
        registrar_log(
            "Erro Interface", f"Falha na interface de anÃ¡lise: {str(e)}", level="ERROR"
        )
        messagebox.showerror("Erro", f"Falha na integraÃ§Ã£o da anÃ¡lise: {str(e)}")
        return pd.DataFrame()
    finally:
        plt.close("all")


# ---------- Entrada para execuÃ§Ã£o autÃ´noma ----------
if __name__ == "__main__":
    # Define o diretÃ³rio base para que os imports relativos funcionem
    os.chdir(BASE_DIR)
    registrar_log(
        "ExecuÃ§Ã£o AutÃ´noma",
        "Iniciando execuÃ§Ã£o autÃ´noma do mÃ³dulo de anÃ¡lise.",
        level="INFO",
    )

    # Se rodar isoladamente, cria uma root para mostrar interface
    root_app = ctk.CTk()
    root_app.withdraw()

    janela = abrir_analise(master=root_app)
    # A janela de anÃ¡lise irÃ¡ lidar com o seu prÃ³prio mainloop

    plt.close("all")
    if root_app.winfo_exists():
        root_app.destroy()
    registrar_log(
        "ExecuÃ§Ã£o AutÃ´noma",
        "ExecuÃ§Ã£o autÃ´noma do mÃ³dulo de anÃ¡lise finalizada.",
        level="INFO",
    )

# FileName: /Integragal/utils/io_utils.py
import os
from typing import Optional

import pandas as pd

from utils.logger import registrar_log  # Importa o logger centralizado


def detectar_separador_csv(filepath: str) -> str:
    """
    Tenta detectar o separador de um arquivo CSV lendo as primeiras linhas.
    Prioriza ponto e vírgula (;) sobre vírgula (,).
    """
    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            for _ in range(5):  # Lê as primeiras 5 linhas para análise
                linha = f.readline()
                if ";" in linha and "," not in linha:  # Se só tem ponto e vírgula
                    registrar_log(
                        "IO Utils",
                        f"Separador detectado para '{os.path.basename(filepath)}': ';'",
                        level="DEBUG",
                    )
                    return ";"
                if "," in linha and ";" not in linha:  # Se só tem vírgula
                    registrar_log(
                        "IO Utils",
                        f"Separador detectado para '{os.path.basename(filepath)}': ','",
                        level="DEBUG",
                    )
                    return ","
                if (
                    ";" in linha and "," in linha
                ):  # Se tem ambos, prioriza o que aparece mais
                    if linha.count(";") > linha.count(","):
                        registrar_log(
                            "IO Utils",
                            f"Separador detectado para '{os.path.basename(filepath)}': ';'",
                            level="DEBUG",
                        )
                        return ";"
                    else:
                        registrar_log(
                            "IO Utils",
                            f"Separador detectado para '{os.path.basename(filepath)}': ','",
                            level="DEBUG",
                        )
                        return ","
        registrar_log(
            "IO Utils",
            f"Separador padrão ',' usado para '{os.path.basename(filepath)}' (não detectado claramente).",
            level="WARNING",
        )
        return ","  # Padrão se não for claramente detectado
    except Exception as e:
        registrar_log(
            "IO Utils",
            f"Erro ao detectar separador para '{os.path.basename(filepath)}': {e}. Usando padrão ','.",
            level="ERROR",
        )
        return ","


def detectar_linha_cabecalho(filepath: str, sep: str = ",") -> int:
    """
    Tenta detectar a linha de cabeçalho em um arquivo CSV ou Excel,
    procurando por palavras-chave comuns como 'Well', 'Sample', 'Target'.
    Retorna o índice da linha (0-based).
    """
    try:
        # Para CSV
        if filepath.lower().endswith(".csv"):
            with open(filepath, "r", encoding="utf-8-sig") as f:
                for idx, linha in enumerate(f):
                    # Verifica se a linha contém as palavras-chave comuns de cabeçalho
                    if all(
                        col in linha.lower() for col in ["well", "sample", "target"]
                    ):
                        registrar_log(
                            "IO Utils",
                            f"Cabeçalho detectado em CSV '{os.path.basename(filepath)}' na linha {idx}.",
                            level="DEBUG",
                        )
                        return idx
                    if (
                        idx > 50
                    ):  # Limita a busca para evitar ler arquivos muito grandes desnecessariamente
                        break
            registrar_log(
                "IO Utils",
                f"Cabeçalho não detectado em CSV '{os.path.basename(filepath)}'. Usando linha 0.",
                level="WARNING",
            )
            return 0  # Padrão se não encontrar

        # Para Excel (tentativa de leitura para encontrar sheet 'Results' e cabeçalho)
        elif filepath.lower().endswith((".xls", ".xlsx")):
            # Tenta ler a sheet 'Results' e procurar o cabeçalho
            for skip_rows in range(50):  # Tenta pular até 50 linhas
                try:
                    temp_df = pd.read_excel(
                        filepath,
                        sheet_name="Results",
                        skiprows=skip_rows,
                        engine="openpyxl",
                    )
                    temp_df.columns = [str(col).strip() for col in temp_df.columns]
                    if (
                        any("Well" in col for col in temp_df.columns)
                        and any("Sample" in col for col in temp_df.columns)
                        and any("Target" in col for col in temp_df.columns)
                    ):
                        registrar_log(
                            "IO Utils",
                            f"Cabeçalho detectado em Excel '{os.path.basename(filepath)}' na linha {skip_rows} (skiprows).",
                            level="DEBUG",
                        )
                        return skip_rows
                except Exception:
                    continue  # Tenta a próxima skiprows
            registrar_log(
                "IO Utils",
                f"Cabeçalho não detectado em Excel '{os.path.basename(filepath)}'. Usando linha 0.",
                level="WARNING",
            )
            return 0  # Padrão se não encontrar

        registrar_log(
            "IO Utils",
            f"Tipo de arquivo desconhecido para detecção de cabeçalho: '{os.path.basename(filepath)}'. Usando linha 0.",
            level="WARNING",
        )
        return 0
    except Exception as e:
        registrar_log(
            "IO Utils",
            f"Erro ao detectar linha de cabeçalho para '{os.path.basename(filepath)}': {e}. Usando linha 0.",
            level="ERROR",
        )
        return 0


def read_data_with_auto_detection(filepath: str) -> Optional[pd.DataFrame]:
    """
    Lê um arquivo de dados (CSV ou Excel) com detecção automática de formato,
    separador (para CSV) e linha de cabeçalho.
    Retorna um DataFrame do pandas ou None em caso de falha.
    """
    if not os.path.exists(filepath):
        registrar_log("IO Utils", f"Arquivo não encontrado: {filepath}", level="ERROR")
        return None

    ext = os.path.splitext(filepath)[-1].lower()
    df = None

    if ext in [".xls", ".xlsx"]:
        registrar_log(
            "IO Utils",
            f"Tentando ler arquivo Excel: {os.path.basename(filepath)}",
            level="INFO",
        )
        try:
            # Tenta detectar a linha de cabeçalho para Excel
            skip_rows = detectar_linha_cabecalho(filepath)
            df = pd.read_excel(
                filepath, sheet_name="Results", skiprows=skip_rows, engine="openpyxl"
            )
            df.columns = [
                str(col).strip() for col in df.columns
            ]  # Limpa nomes das colunas
            registrar_log(
                "IO Utils",
                f"Arquivo Excel '{os.path.basename(filepath)}' lido com sucesso.",
                level="INFO",
            )
        except Exception as e:
            registrar_log(
                "IO Utils",
                f"Falha ao ler arquivo Excel '{os.path.basename(filepath)}': {e}",
                level="ERROR",
            )
            return None

    elif ext == ".csv":
        registrar_log(
            "IO Utils",
            f"Tentando ler arquivo CSV: {os.path.basename(filepath)}",
            level="INFO",
        )
        try:
            sep = detectar_separador_csv(filepath)
            skip_rows = detectar_linha_cabecalho(filepath, sep=sep)

            # Tenta ler com múltiplas codificações
            encodings_to_try = [
                "utf-8-sig",
                "utf-8",
                "latin-1",
                "cp1252",
                "windows-1252",
            ]
            last_exception = None
            for enc in encodings_to_try:
                try:
                    df = pd.read_csv(
                        filepath, encoding=enc, sep=sep, skiprows=skip_rows
                    )
                    df.columns = [
                        str(col).strip() for col in df.columns
                    ]  # Limpa nomes das colunas
                    registrar_log(
                        "IO Utils",
                        f"Arquivo CSV '{os.path.basename(filepath)}' lido com sucesso com codificação '{enc}'.",
                        level="INFO",
                    )
                    break  # Sai do loop se a leitura for bem-sucedida
                except UnicodeDecodeError as e:
                    last_exception = e
                    registrar_log(
                        "IO Utils",
                        f"Falha na leitura CSV com codificação '{enc}': {e}",
                        level="DEBUG",
                    )
                except Exception as e:
                    last_exception = e
                    registrar_log(
                        "IO Utils",
                        f"Erro inesperado na leitura CSV com codificação '{enc}': {e}",
                        level="ERROR",
                    )

            if df is None:  # Se todas as tentativas falharam
                registrar_log(
                    "IO Utils",
                    f"Todas as tentativas de leitura CSV para '{os.path.basename(filepath)}' falharam. Último erro: {last_exception}",
                    level="ERROR",
                )
                return None

        except Exception as e:
            registrar_log(
                "IO Utils",
                f"Falha ao ler arquivo CSV '{os.path.basename(filepath)}': {e}",
                level="ERROR",
            )
            return None
    else:
        registrar_log(
            "IO Utils",
            f"Tipo de arquivo não suportado para leitura: {ext}",
            level="ERROR",
        )
        return None

    # Padroniza nomes de colunas comuns após a leitura
    if df is not None:
        df.columns = [
            (
                col.replace("CÑ‚", "CT").replace("Cq", "CT")
                if isinstance(col, str)
                else col
            )
            for col in df.columns
        ]
        df.columns = [
            (
                col.replace("Target Name", "Target").replace("Sample Name", "Sample")
                if isinstance(col, str)
                else col
            )
            for col in df.columns
        ]
        # Reaplica uma normalizacao mais robusta dos nomes de colunas
        try:
            import unicodedata as _ud

            def _norm_col(col):
                if not isinstance(col, str):
                    return col
                s = _ud.normalize("NFKD", col).encode("ASCII", "ignore").decode("ASCII")
                s = s.strip()
                if s.lower() in {"cq", "ct", "cq mean", "cqmean", "ct mean", "ctmean"}:
                    s = "CT"
                s = s.replace("Target Name", "Target").replace("Sample Name", "Sample")
                return s

            df.columns = [_norm_col(c) for c in df.columns]
        except Exception:
            pass

        # Converte coluna 'CT' para float de forma segura, se existir
        if "CT" in df.columns:
            df["CT"] = df["CT"].apply(
                lambda x: (
                    round(float(str(x).replace(",", ".").strip()), 2)
                    if pd.notna(x)
                    and str(x).replace(",", ".").strip().replace(".", "", 1).isdigit()
                    else pd.NA
                )
            )
            registrar_log(
                "IO Utils", "Coluna 'CT' convertida para float.", level="DEBUG"
            )

    return df

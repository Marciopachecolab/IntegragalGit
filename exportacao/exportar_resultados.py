# FileName: /Integragal/exportacao/exportar_resultados.py
import os
from datetime import datetime
from tkinter import filedialog, messagebox

import matplotlib.pyplot as plt
import pandas as pd

from utils.logger import registrar_log  # Importa o logger centralizado


def exportar_resultados_gal(
    df_processado: pd.DataFrame,
    lote_kit: str,
    mapeamento_alvo: dict,
    mapeamento_saida: dict,
    colunas_modelo: list,
    colunas_humanas: dict = None,
) -> None:
    """
    Exporta os resultados processados para um arquivo CSV no formato GAL.
    ParÃ¢metros:
        df_processado: DataFrame com os resultados processados.
        lote_kit: CÃ³digo do lote do kit utilizado.
        mapeamento_alvo: DicionÃ¡rio mapeando nomes de colunas de resultado internos para colunas do CSV.
        mapeamento_saida: DicionÃ¡rio mapeando valores de resultado (e.g. 'DetectÃ¡vel', 'ND') para cÃ³digos CSV ('1','2','3').
        colunas_modelo: Lista contendo o modelo de colunas do CSV de saÃ­da (formato GAL).
        colunas_humanas: (Opcional) DicionÃ¡rio para mapear nomes de colunas CSV para nomes legÃ­veis (usado no grÃ¡fico).
    """
    # VerificaÃ§Ãµes iniciais de validade dos parÃ¢metros
    if df_processado is None or not isinstance(df_processado, pd.DataFrame):
        registrar_log(
            "Erro de ExportaÃ§Ã£o",
            "DataFrame de resultados invÃ¡lido ou nÃ£o fornecido.",
            level="ERROR",
        )
        messagebox.showerror(
            "Erro de ExportaÃ§Ã£o",
            "DataFrame de resultados invÃ¡lido ou nÃ£o fornecido.",
        )
        return
    if mapeamento_alvo is None or not isinstance(mapeamento_alvo, dict):
        registrar_log(
            "Erro de ExportaÃ§Ã£o",
            "Mapeamento de alvo invÃ¡lido ou nÃ£o fornecido.",
            level="ERROR",
        )
        messagebox.showerror(
            "Erro de ExportaÃ§Ã£o", "Mapeamento de alvo invÃ¡lido ou nÃ£o fornecido."
        )
        return
    if mapeamento_saida is None or not isinstance(mapeamento_saida, dict):
        registrar_log(
            "Erro de ExportaÃ§Ã£o",
            "Mapeamento de saÃ­da invÃ¡lido ou nÃ£o fornecido.",
            level="ERROR",
        )
        messagebox.showerror(
            "Erro de ExportaÃ§Ã£o", "Mapeamento de saÃ­da invÃ¡lido ou nÃ£o fornecido."
        )
        return
    if colunas_modelo is None or not isinstance(colunas_modelo, (list, tuple)):
        registrar_log(
            "Erro de ExportaÃ§Ã£o",
            "Modelo de colunas invÃ¡lido ou nÃ£o fornecido.",
            level="ERROR",
        )
        messagebox.showerror(
            "Erro de ExportaÃ§Ã£o", "Modelo de colunas invÃ¡lido ou nÃ£o fornecido."
        )
        return

    # Verificar se hÃ¡ coluna 'Selecionado' e coluna 'Sample' no DataFrame
    if "Selecionado" not in df_processado.columns:
        registrar_log(
            "Erro de ExportaÃ§Ã£o",
            "Coluna 'Selecionado' nÃ£o encontrada no DataFrame. Nenhuma amostra serÃ¡ exportada.",
            level="WARNING",
        )
        messagebox.showwarning(
            "Coluna Ausente",
            "A coluna 'Selecionado' nÃ£o foi encontrada nos resultados. Nenhuma amostra serÃ¡ exportada.",
        )
        return
    if "Sample" not in df_processado.columns:
        registrar_log(
            "Erro de ExportaÃ§Ã£o",
            "Coluna 'Sample' nÃ£o encontrada no DataFrame.",
            level="ERROR",
        )
        messagebox.showerror(
            "Erro de ExportaÃ§Ã£o",
            "NÃ£o foi possÃ­vel encontrar a coluna 'Sample' no DataFrame de resultados.",
        )
        return

    # PreparaÃ§Ã£o de variÃ¡veis para exportaÃ§Ã£o
    processing_end_date = datetime.now().strftime("%d/%m/%Y")
    # O log de resultados por amostra pode ser salvo em um subdiretÃ³rio de logs
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)  # Garante que o diretÃ³rio de logs exista
    log_file_path = os.path.join(log_dir, "resultados_por_amostra.txt")

    # Inicializa contagem de detectÃ¡veis para cada coluna de destino do CSV
    detectable_counts_for_plot = {col_csv: 0 for col_csv in mapeamento_alvo.values()}

    lines_to_export = []
    try:
        with open(log_file_path, "w", encoding="utf-8") as log_file:
            # Itera sobre cada linha do DataFrame processado
            for _, row in df_processado.iterrows():
                try:
                    # Verifica se a amostra estÃ¡ selecionada (marca 'âœ“' na coluna 'Selecionado')
                    # ou se a coluna 'Selecionado' Ã© booleana e True
                    is_selected = row.get("Selecionado", False)
                    if isinstance(is_selected, str):
                        is_selected = is_selected == "âœ“"

                    if not is_selected:
                        continue

                    # Prepara dicionÃ¡rio para a linha de CSV, iniciando com colunas modelo em branco
                    csv_line = {col_name: "" for col_name in colunas_modelo}

                    # Preencher dados bÃ¡sicos, se estas colunas estiverem presentes no modelo
                    if "codigoAmostra" in colunas_modelo:
                        csv_line["codigoAmostra"] = row["Sample"]
                    if "registroInterno" in colunas_modelo:
                        csv_line["registroInterno"] = row["Sample"]
                    if "loteKit" in colunas_modelo:
                        csv_line["loteKit"] = lote_kit
                    if "dataProcessamentoFim" in colunas_modelo:
                        csv_line["dataProcessamentoFim"] = processing_end_date

                    # Mapear resultados para colunas do CSV conforme o mapeamento fornecido
                    for internal_col, csv_col in mapeamento_alvo.items():
                        if csv_col not in colunas_modelo:
                            continue
                        internal_result = row.get(internal_col, "")
                        mapped_value = mapeamento_saida.get(internal_result, "")
                        csv_line[csv_col] = mapped_value
                        if mapped_value == "1":
                            detectable_counts_for_plot[csv_col] = (
                                detectable_counts_for_plot.get(csv_col, 0) + 1
                            )

                    # Adicionar valores padrÃ£o se as colunas existirem no modelo e nÃ£o foram preenchidas
                    for k, v in {
                        "paciente": "",
                        "exame": "VRSRT",
                        "metodo": "RTTR",
                        "kit": "427",
                        "painel": "1",
                        "resultado": "",
                    }.items():
                        if k in colunas_modelo and not csv_line.get(k):
                            csv_line[k] = v

                    # Adicionar a linha pronta na lista de exportaÃ§Ã£o
                    lines_to_export.append(csv_line)

                    # Registrar detalhes da linha no log
                    log_file.write(f"Amostra {csv_line.get('codigoAmostra','')}:\n")
                    for key in colunas_modelo:
                        log_file.write(f"  {key}: {csv_line.get(key, '')}\n")
                    log_file.write("\n")

                except Exception as e_row:
                    # Se ocorrer erro em alguma linha, registra no log e continua
                    amostra_id = row.get("Sample", "")
                    registrar_log(
                        "Erro na ExportaÃ§Ã£o",
                        f"Amostra {amostra_id} nÃ£o exportada: {e_row}",
                        level="ERROR",
                    )
                    continue

    except Exception as e_file:
        registrar_log(
            "Erro na ExportaÃ§Ã£o", f"Falha ao criar log: {e_file}", level="ERROR"
        )
        messagebox.showerror(
            "Erro de ExportaÃ§Ã£o",
            f"Ocorreu um erro ao criar o log de exportaÃ§Ã£o: {e_file}",
        )
        return

    # Verifica se hÃ¡ alguma amostra vÃ¡lida para exportar
    if not lines_to_export:
        messagebox.showwarning(
            "Nenhuma Amostra",
            "Nenhuma amostra vÃ¡lida ('Selecionado' com 'âœ“') para exportaÃ§Ã£o.",
        )
        return

    # Criar DataFrame final com as linhas exportadas
    df_final_csv = pd.DataFrame(lines_to_export, columns=colunas_modelo)

    # Solicita local para salvar o arquivo CSV
    output_filepath = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        title="Salvar CSV no Formato GAL",
    )

    if output_filepath:
        try:
            # Salvar CSV com codificaÃ§Ã£o UTF-8 e separador ponto-e-vÃ­rgula
            df_final_csv.to_csv(output_filepath, sep=";", index=False, encoding="utf-8")
            registrar_log(
                "ExportaÃ§Ã£o CSV ConcluÃ­da", f"Arquivo salvo em: {output_filepath}"
            )

            # Construir mensagem de resumo com contagem de detectÃ¡veis por agravo
            msg_to_user = (
                f"Arquivo salvo em: {output_filepath}\n"
                f"Log salvo em: {log_file_path}\n\n"
                "Contagem de DetectÃ¡veis (apenas amostras VÃLIDAS):\n"
            )
            # Ordena alvos para apresentaÃ§Ã£o (pelo nome humano, se disponÃ­vel)
            sorted_targets = sorted(
                detectable_counts_for_plot.keys(),
                key=lambda k: colunas_humanas.get(k, k) if colunas_humanas else k,
            )
            for csv_col_name in sorted_targets:
                human_name = (
                    colunas_humanas.get(csv_col_name, csv_col_name)
                    if colunas_humanas
                    else csv_col_name
                )
                count_val = detectable_counts_for_plot.get(csv_col_name, 0)
                msg_to_user += f"{human_name}: {count_val} detectÃ¡veis\n"

            messagebox.showinfo("ExportaÃ§Ã£o ConcluÃ­da", msg_to_user)
            # Gerar grÃ¡fico de barras para detectÃ¡veis
            _gerar_grafico_detectaveis(detectable_counts_for_plot, colunas_humanas)

        except Exception as e_save:
            registrar_log("Erro na ExportaÃ§Ã£o CSV", str(e_save), level="ERROR")
            messagebox.showerror(
                "Erro de ExportaÃ§Ã£o",
                f"Ocorreu um erro ao salvar o arquivo CSV: {e_save}",
            )
    else:
        # UsuÃ¡rio cancelou a operaÃ§Ã£o de salvar
        messagebox.showwarning("Cancelado", "ExportaÃ§Ã£o cancelada pelo usuÃ¡rio.")


def _gerar_grafico_detectaveis(
    detectable_counts: dict, colunas_humanas: dict = None
) -> None:
    """
    Gera um grÃ¡fico de barras simples mostrando a quantidade de amostras detectÃ¡veis por agravo.
    ParÃ¢metros:
        detectable_counts: DicionÃ¡rio de contagem de amostras detectÃ¡veis por coluna do CSV.
        colunas_humanas: (Opcional) Mapeamento de nomes de coluna para nomes legÃ­veis.
    """
    if not detectable_counts or all(v == 0 for v in detectable_counts.values()):
        registrar_log(
            "GrÃ¡fico de DetecÃ§Ã£o",
            "Nenhum alvo detectÃ¡vel para gerar o grÃ¡fico.",
            level="INFO",
        )
        messagebox.showinfo(
            "GrÃ¡fico de DetecÃ§Ã£o", "Nenhum alvo detectÃ¡vel para gerar o grÃ¡fico."
        )
        return

    # Filtra apenas alvos com contagem maior que zero
    plot_data = {k: v for k, v in detectable_counts.items() if v > 0}
    plot_labels = [
        colunas_humanas.get(k, k) if colunas_humanas else k for k in plot_data.keys()
    ]
    plot_values = list(plot_data.values())

    plt.figure(figsize=(10, 5))
    plt.bar(plot_labels, plot_values, color="skyblue")
    plt.title("NÃºmero de Amostras DetectÃ¡veis por Agravo")
    plt.xlabel("Agravo")
    plt.ylabel("Quantidade")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()
    registrar_log(
        "GrÃ¡fico de DetecÃ§Ã£o", "GrÃ¡fico de detectÃ¡veis gerado.", level="INFO"
    )

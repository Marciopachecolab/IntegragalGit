# FileName: /Integragal/exportacao/exportar_resultados.py
import os
from datetime import datetime
from tkinter import filedialog, messagebox

import matplotlib.pyplot as plt
import pandas as pd

from services.exam_registry import get_exam_cfg
from utils.logger import registrar_log  # Importa o logger centralizado


def exportar_resultados_gal(
    df_processado: pd.DataFrame,
    lote_kit: str,
    mapeamento_alvo: dict,
    mapeamento_saida: dict,
    colunas_modelo: list,
    colunas_humanas: dict = None,
    exam_cfg: any = None,
    exame: str = None,
) -> None:
    """
    Exporta os resultados processados para um arquivo CSV no formato GAL.
    Parâmetros:
        df_processado: DataFrame com os resultados processados.
        lote_kit: Código do lote do kit utilizado.
        mapeamento_alvo: Dicionário mapeando nomes de colunas de resultado internos para colunas do CSV.
        mapeamento_saida: Dicionário mapeando valores de resultado (e.g. 'Detectável', 'ND') para códigos CSV ('1','2','3').
        colunas_modelo: Lista contendo o modelo de colunas do CSV de saída (formato GAL).
        colunas_humanas: (Opcional) Dicionário para mapear nomes de colunas CSV para nomes legíveis (usado no gráfico).
        exam_cfg: (Opcional) Config do exame (ExamConfig) para validações de controles
        exame: (Opcional) Nome do exame (para buscar config se exam_cfg não fornecido)
    """
    # Carrega config do exame se não fornecida
    if not exam_cfg and exame:
        try:
            exam_cfg = get_exam_cfg(exame)
        except Exception:
            exam_cfg = None
    
    # Extrai controles do registry se disponível
    controles_cn_cp = []
    if exam_cfg:
        try:
            controles = exam_cfg.controles or {}
            controles_cn_cp = [str(c).upper() for c in controles.keys()]
        except Exception:
            controles_cn_cp = []
    
    # Verificações iniciais de validade dos parâmetros
    if df_processado is None or not isinstance(df_processado, pd.DataFrame):
        registrar_log(
            "Erro de Exportação",
            "DataFrame de resultados inválido ou não fornecido.",
            level="ERROR",
        )
        messagebox.showerror(
            "Erro de Exportação",
            "DataFrame de resultados inválido ou não fornecido.",
        )
        return
    if mapeamento_alvo is None or not isinstance(mapeamento_alvo, dict):
        registrar_log(
            "Erro de Exportação",
            "Mapeamento de alvo inválido ou não fornecido.",
            level="ERROR",
        )
        messagebox.showerror(
            "Erro de Exportação", "Mapeamento de alvo inválido ou não fornecido."
        )
        return
    if mapeamento_saida is None or not isinstance(mapeamento_saida, dict):
        registrar_log(
            "Erro de Exportação",
            "Mapeamento de saída inválido ou não fornecido.",
            level="ERROR",
        )
        messagebox.showerror(
            "Erro de Exportação", "Mapeamento de saída inválido ou não fornecido."
        )
        return
    if colunas_modelo is None or not isinstance(colunas_modelo, (list, tuple)):
        registrar_log(
            "Erro de Exportação",
            "Modelo de colunas inválido ou não fornecido.",
            level="ERROR",
        )
        messagebox.showerror(
            "Erro de Exportação", "Modelo de colunas inválido ou não fornecido."
        )
        return

    # Verificar se há coluna 'Selecionado' e coluna 'Sample' no DataFrame
    if "Selecionado" not in df_processado.columns:
        registrar_log(
            "Erro de Exportação",
            "Coluna 'Selecionado' não encontrada no DataFrame. Nenhuma amostra será exportada.",
            level="WARNING",
        )
        messagebox.showwarning(
            "Coluna Ausente",
            "A coluna 'Selecionado' não foi encontrada nos resultados. Nenhuma amostra será exportada.",
        )
        return
    if "Sample" not in df_processado.columns:
        registrar_log(
            "Erro de Exportação",
            "Coluna 'Sample' não encontrada no DataFrame.",
            level="ERROR",
        )
        messagebox.showerror(
            "Erro de Exportação",
            "Não foi possível encontrar a coluna 'Sample' no DataFrame de resultados.",
        )
        return

    # Preparação de variáveis para exportação
    processing_end_date = datetime.now().strftime("%d/%m/%Y")
    # O log de resultados por amostra pode ser salvo em um subdiretório de logs
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)  # Garante que o diretório de logs exista
    log_file_path = os.path.join(log_dir, "resultados_por_amostra.txt")

    # Inicializa contagem de detectáveis para cada coluna de destino do CSV
    detectable_counts_for_plot = {col_csv: 0 for col_csv in mapeamento_alvo.values()}

    lines_to_export = []
    try:
        with open(log_file_path, "w", encoding="utf-8") as log_file:
            # Itera sobre cada linha do DataFrame processado
            for _, row in df_processado.iterrows():
                try:
                    # Verifica se a amostra está selecionada (marca '✓' na coluna 'Selecionado')
                    # ou se a coluna 'Selecionado' é booleana e True
                    is_selected = row.get("Selecionado", False)
                    if isinstance(is_selected, str):
                        is_selected = is_selected == "✓"

                    if not is_selected:
                        continue
                    
                    # Filtra CN/CP (controles) automaticamente baseado em registry ou hardcoded
                    sample = str(row.get("Sample", "")).upper()
                    codigo = str(row.get("Codigo", "")).upper() if "Codigo" in row else ""
                    
                    # Detecta controles (CN/CP) automaticamente
                    is_control = False
                    for cc in controles_cn_cp:
                        if cc in sample or cc in codigo:
                            is_control = True
                            break
                    
                    # Se não houver config de controles no registry, usa heurística padrão
                    if not is_control:
                        if ("CN" in sample or "CN" in codigo or 
                            "CP" in sample or "CP" in codigo or
                            "NEGATIVO" in sample or "POSITIVO" in codigo):
                            is_control = True
                    
                    # Pula controles (não exporta)
                    if is_control:
                        log_file.write(f"Skipped control: {sample} ({codigo})\n")
                        continue

                    # Prepara dicionário para a linha de CSV, iniciando com colunas modelo em branco
                    csv_line = {col_name: "" for col_name in colunas_modelo}

                    # Preencher dados básicos, se estas colunas estiverem presentes no modelo
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

                    # Adicionar valores padrão se as colunas existirem no modelo e não foram preenchidas
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

                    # Adicionar a linha pronta na lista de exportação
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
                        "Erro na Exportação",
                        f"Amostra {amostra_id} não exportada: {e_row}",
                        level="ERROR",
                    )
                    continue

    except Exception as e_file:
        registrar_log(
            "Erro na Exportação", f"Falha ao criar log: {e_file}", level="ERROR"
        )
        messagebox.showerror(
            "Erro de Exportação",
            f"Ocorreu um erro ao criar o log de exportação: {e_file}",
        )
        return

    # Verifica se há alguma amostra válida para exportar
    if not lines_to_export:
        messagebox.showwarning(
            "Nenhuma Amostra",
            "Nenhuma amostra válida ('Selecionado' com '✓') para exportação.",
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
            # Salvar CSV com codificação UTF-8 e separador ponto-e-vírgula
            df_final_csv.to_csv(output_filepath, sep=";", index=False, encoding="utf-8")
            registrar_log(
                "Exportação CSV Concluída", f"Arquivo salvo em: {output_filepath}"
            )

            # Construir mensagem de resumo com contagem de detectáveis por agravo
            msg_to_user = (
                f"Arquivo salvo em: {output_filepath}\n"
                f"Log salvo em: {log_file_path}\n\n"
                "Contagem de Detectáveis (apenas amostras VÁLIDAS):\n"
            )
            # Ordena alvos para apresentação (pelo nome humano, se disponível)
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
                msg_to_user += f"{human_name}: {count_val} detectáveis\n"

            messagebox.showinfo("Exportação Concluída", msg_to_user)
            # Gerar gráfico de barras para detectáveis
            _gerar_grafico_detectaveis(detectable_counts_for_plot, colunas_humanas)

        except Exception as e_save:
            registrar_log("Erro na Exportação CSV", str(e_save), level="ERROR")
            messagebox.showerror(
                "Erro de Exportação",
                f"Ocorreu um erro ao salvar o arquivo CSV: {e_save}",
            )
    else:
        # Usuário cancelou a operação de salvar
        messagebox.showwarning("Cancelado", "Exportação cancelada pelo usuário.")


def _gerar_grafico_detectaveis(
    detectable_counts: dict, colunas_humanas: dict = None
) -> None:
    """
    Gera um gráfico de barras simples mostrando a quantidade de amostras detectáveis por agravo.
    Parâmetros:
        detectable_counts: Dicionário de contagem de amostras detectáveis por coluna do CSV.
        colunas_humanas: (Opcional) Mapeamento de nomes de coluna para nomes legíveis.
    """
    if not detectable_counts or all(v == 0 for v in detectable_counts.values()):
        registrar_log(
            "Gráfico de Detecção",
            "Nenhum alvo detectável para gerar o gráfico.",
            level="INFO",
        )
        messagebox.showinfo(
            "Gráfico de Detecção", "Nenhum alvo detectável para gerar o gráfico."
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
    plt.title("Número de Amostras Detectáveis por Agravo")
    plt.xlabel("Agravo")
    plt.ylabel("Quantidade")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()
    registrar_log(
        "Gráfico de Detecção", "Gráfico de detectáveis gerado.", level="INFO"
    )

# FileName: /Integragal/relatorios/gerar_relatorios.py

import os

from tkinter import filedialog, messagebox



import matplotlib.pyplot as plt

import pandas as pd



from utils.logger import registrar_log  # Importa o logger centralizado





def gerar_relatorio_csv():

    """

    Permite ao usuário selecionar um arquivo CSV de resultados e salvá-lo

    em um novo local, garantindo a codificação e o separador.

    """

    arquivo = filedialog.askopenfilename(

        title="Selecione o CSV de resultados", filetypes=[("CSV", "*.csv")]

    )

    if not arquivo:

        registrar_log(

            "Gerar Relatório CSV", "Seleção de arquivo CSV cancelada.", level="INFO"

        )

        return



    try:

        # Tenta ler com utf-8-sig e ponto e vírgula, que é o padrão de exportação do sistema

        df = pd.read_csv(arquivo, delimiter=";", encoding="utf-8-sig")

        registrar_log(

            "Gerar Relatório CSV",

            f"Arquivo CSV '{os.path.basename(arquivo)}' lido com sucesso.",

            level="INFO",

        )

    except Exception as e:

        registrar_log(

            "Gerar Relatório CSV",

            f"Erro ao ler o arquivo CSV '{os.path.basename(arquivo)}': {e}",

            level="ERROR",

        )

        messagebox.showerror(

            "Erro de Leitura",

            f"Não foi possível ler o arquivo CSV:\n{e}\nVerifique o formato e a codificação.",

        )

        return



    caminho_saida = filedialog.asksaveasfilename(

        defaultextension=".csv",

        filetypes=[("CSV", "*.csv")],

        title="Salvar Relatório CSV Como",

    )



    if caminho_saida:

        try:

            df.to_csv(caminho_saida, sep=";", index=False, encoding="utf-8-sig")

            registrar_log(

                "Gerar Relatório CSV",

                f"Relatório salvo em: {caminho_saida}",

                level="INFO",

            )

            messagebox.showinfo(

                "Relatório", f"✅ Relatório CSV salvo em: {caminho_saida}"

            )

        except Exception as e:

            registrar_log(

                "Gerar Relatório CSV",

                f"Erro ao salvar o relatório CSV em '{caminho_saida}': {e}",

                level="ERROR",

            )

            messagebox.showerror(

                "Erro ao Salvar", f"Não foi possível salvar o relatório CSV:\n{e}"

            )

    else:

        registrar_log(

            "Gerar Relatório CSV",

            "Salvamento do relatório CSV cancelado pelo usuário.",

            level="INFO",

        )





def gerar_grafico():

    """

    Permite ao usuário selecionar um arquivo CSV de resultados e gera um

    gráfico de barras da quantidade de amostras detectáveis por agravo.

    """

    arquivo = filedialog.askopenfilename(

        title="Selecione o CSV de resultados para o gráfico",

        filetypes=[("CSV", "*.csv")],

    )

    if not arquivo:

        registrar_log(

            "Gerar Gráfico",

            "Seleção de arquivo CSV para gráfico cancelada.",

            level="INFO",

        )

        return



    try:

        # Tenta ler com utf-8-sig e ponto e vírgula

        df = pd.read_csv(arquivo, delimiter=";", encoding="utf-8-sig")

        registrar_log(

            "Gerar Gráfico",

            f"Arquivo CSV '{os.path.basename(arquivo)}' lido para gráfico com sucesso.",

            level="INFO",

        )

    except Exception as e:

        registrar_log(

            "Gerar Gráfico",

            f"Erro ao ler o arquivo CSV para gráfico '{os.path.basename(arquivo)}': {e}",

            level="ERROR",

        )

        messagebox.showerror(

            "Erro de Leitura",

            f"Não foi possível ler o arquivo CSV para gerar o gráfico:\n{e}\nVerifique o formato e a codificação.",

        )

        return



    # Identifica colunas de agravos. Assume que colunas não-meta são agravos.

    # Pode ser necessário um mapeamento mais explícito se houver muitas colunas não-agravo.

    # Para o contexto do sistema, as colunas de resultado são '1', '2', '3' (Detectável, ND, Inconclusivo)

    # Então, 'Detectável' é representado por '1'.

    colunas_meta = [

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

    ]



    # Filtra colunas que são potenciais agravos (não estão nas colunas meta e contêm valores de resultado)

    colunas_agravos = [

        col

        for col in df.columns

        if col not in colunas_meta and df[col].isin(["1", "2", "3"]).any()

    ]



    if not colunas_agravos:

        registrar_log(

            "Gerar Gráfico",

            "Nenhuma coluna de agravo detectável encontrada no CSV para gerar o gráfico.",

            level="WARNING",

        )

        messagebox.showinfo(

            "Gráfico de Detecção",

            "Nenhuma coluna de agravo detectável encontrada no arquivo para gerar o gráfico.",

        )

        return



    # Contagem de 'Detectável' (valor '1') para cada agravo

    contagem = {agravo: (df[agravo] == "1").sum() for agravo in colunas_agravos}



    # Filtra agravos com contagem zero para não aparecerem no gráfico

    plot_data = {k: v for k, v in contagem.items() if v > 0}



    if not plot_data:

        registrar_log(

            "Gerar Gráfico",

            "Nenhum alvo detectável com contagem maior que zero para gerar o gráfico.",

            level="INFO",

        )

        messagebox.showinfo(

            "Gráfico de Detecção",

            "Nenhum alvo detectável com contagem maior que zero para gerar o gráfico.",

        )

        return



    labels = list(plot_data.keys())

    values = list(plot_data.values())



    plt.figure(figsize=(10, 6))

    plt.bar(labels, values, color="skyblue")

    plt.title("Quantidade de Amostras Detectáveis por Agravo")

    plt.xlabel("Agravo")

    plt.ylabel("Quantidade")

    plt.xticks(

        rotation=45, ha="right"

    )  # Rotação para melhor visualização de nomes longos

    plt.tight_layout()  # Ajusta o layout para evitar sobreposição

    plt.show()



    registrar_log(

        "Gerar Gráfico", f"Gráfico gerado para arquivo: {arquivo}", level="INFO"

    )





def abrir_menu_relatorios(parent):

    """

    Abre uma pequena janela para o usuário escolher o tipo de relatório.



    Esta função é chamada a partir do MenuHandler e utiliza as funções

    utilitárias definidas neste módulo:

    - gerar_relatorio_csv

    - gerar_grafico

    """

    try:

        import customtkinter as ctk

    except Exception:

        messagebox.showerror(

            "Erro",

            "customtkinter não está disponível para abrir o módulo de relatórios.",

            parent=parent,

        )

        return



    win = ctk.CTkToplevel(parent)

    win.title("Relatórios do Sistema")

    win.geometry("420x220")

    win.grab_set()



    frame = ctk.CTkFrame(win)

    frame.pack(expand=True, fill="both", padx=20, pady=20)



    label = ctk.CTkLabel(

        frame,

        text="Selecione a ação desejada para relatórios:",

        anchor="w",

    )

    label.pack(fill="x", pady=(0, 10))



    def _run_csv():

        win.withdraw()

        try:

            gerar_relatorio_csv()

        finally:

            win.destroy()



    def _run_grafico():

        win.withdraw()

        try:

            gerar_grafico()

        finally:

            win.destroy()



    btn_csv = ctk.CTkButton(

        frame,

        text="Exportar relatório CSV a partir de arquivo",

        command=_run_csv,

    )

    btn_csv.pack(fill="x", pady=5)



    btn_graf = ctk.CTkButton(

        frame,

        text="Gerar gráfico de amostras detectáveis por agravo",

        command=_run_grafico,

    )

    btn_graf.pack(fill="x", pady=5)



    btn_fechar = ctk.CTkButton(

        frame,

        text="Fechar",

        command=win.destroy,

    )

    btn_fechar.pack(fill="x", pady=(15, 0))


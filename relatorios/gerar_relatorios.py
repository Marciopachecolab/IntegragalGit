# FileName: /Integragal/relatorios/gerar_relatorios.py
import os
from tkinter import filedialog, messagebox

import matplotlib.pyplot as plt
import pandas as pd

from utils.logger import registrar_log  # Importa o logger centralizado


def gerar_relatorio_csv():
    """
    Permite ao usuÃ¡rio selecionar um arquivo CSV de resultados e salvÃ¡-lo
    em um novo local, garantindo a codificaÃ§Ã£o e o separador.
    """
    arquivo = filedialog.askopenfilename(
        title="Selecione o CSV de resultados", filetypes=[("CSV", "*.csv")]
    )
    if not arquivo:
        registrar_log(
            "Gerar RelatÃ³rio CSV", "SeleÃ§Ã£o de arquivo CSV cancelada.", level="INFO"
        )
        return

    try:
        # Tenta ler com utf-8-sig e ponto e vÃ­rgula, que Ã© o padrÃ£o de exportaÃ§Ã£o do sistema
        df = pd.read_csv(arquivo, delimiter=";", encoding="utf-8-sig")
        registrar_log(
            "Gerar RelatÃ³rio CSV",
            f"Arquivo CSV '{os.path.basename(arquivo)}' lido com sucesso.",
            level="INFO",
        )
    except Exception as e:
        registrar_log(
            "Gerar RelatÃ³rio CSV",
            f"Erro ao ler o arquivo CSV '{os.path.basename(arquivo)}': {e}",
            level="ERROR",
        )
        messagebox.showerror(
            "Erro de Leitura",
            f"NÃ£o foi possÃ­vel ler o arquivo CSV:\n{e}\nVerifique o formato e a codificaÃ§Ã£o.",
        )
        return

    caminho_saida = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV", "*.csv")],
        title="Salvar RelatÃ³rio CSV Como",
    )

    if caminho_saida:
        try:
            df.to_csv(caminho_saida, sep=";", index=False, encoding="utf-8-sig")
            registrar_log(
                "Gerar RelatÃ³rio CSV",
                f"RelatÃ³rio salvo em: {caminho_saida}",
                level="INFO",
            )
            messagebox.showinfo(
                "RelatÃ³rio", f"âœ”ï¸ RelatÃ³rio CSV salvo em: {caminho_saida}"
            )
        except Exception as e:
            registrar_log(
                "Gerar RelatÃ³rio CSV",
                f"Erro ao salvar o relatÃ³rio CSV em '{caminho_saida}': {e}",
                level="ERROR",
            )
            messagebox.showerror(
                "Erro ao Salvar", f"NÃ£o foi possÃ­vel salvar o relatÃ³rio CSV:\n{e}"
            )
    else:
        registrar_log(
            "Gerar RelatÃ³rio CSV",
            "Salvamento do relatÃ³rio CSV cancelado pelo usuÃ¡rio.",
            level="INFO",
        )


def gerar_grafico():
    """
    Permite ao usuÃ¡rio selecionar um arquivo CSV de resultados e gera um
    grÃ¡fico de barras da quantidade de amostras detectÃ¡veis por agravo.
    """
    arquivo = filedialog.askopenfilename(
        title="Selecione o CSV de resultados para o grÃ¡fico",
        filetypes=[("CSV", "*.csv")],
    )
    if not arquivo:
        registrar_log(
            "Gerar GrÃ¡fico",
            "SeleÃ§Ã£o de arquivo CSV para grÃ¡fico cancelada.",
            level="INFO",
        )
        return

    try:
        # Tenta ler com utf-8-sig e ponto e vÃ­rgula
        df = pd.read_csv(arquivo, delimiter=";", encoding="utf-8-sig")
        registrar_log(
            "Gerar GrÃ¡fico",
            f"Arquivo CSV '{os.path.basename(arquivo)}' lido para grÃ¡fico com sucesso.",
            level="INFO",
        )
    except Exception as e:
        registrar_log(
            "Gerar GrÃ¡fico",
            f"Erro ao ler o arquivo CSV para grÃ¡fico '{os.path.basename(arquivo)}': {e}",
            level="ERROR",
        )
        messagebox.showerror(
            "Erro de Leitura",
            f"NÃ£o foi possÃ­vel ler o arquivo CSV para gerar o grÃ¡fico:\n{e}\nVerifique o formato e a codificaÃ§Ã£o.",
        )
        return

    # Identifica colunas de agravos. Assume que colunas nÃ£o-meta sÃ£o agravos.
    # Pode ser necessÃ¡rio um mapeamento mais explÃ­cito se houver muitas colunas nÃ£o-agravo.
    # Para o contexto do sistema, as colunas de resultado sÃ£o '1', '2', '3' (DetectÃ¡vel, ND, Inconclusivo)
    # EntÃ£o, 'DetectÃ¡vel' Ã© representado por '1'.
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

    # Filtra colunas que sÃ£o potenciais agravos (nÃ£o estÃ£o nas colunas meta e contÃªm valores de resultado)
    colunas_agravos = [
        col
        for col in df.columns
        if col not in colunas_meta and df[col].isin(["1", "2", "3"]).any()
    ]

    if not colunas_agravos:
        registrar_log(
            "Gerar GrÃ¡fico",
            "Nenhuma coluna de agravo detectÃ¡vel encontrada no CSV para gerar o grÃ¡fico.",
            level="WARNING",
        )
        messagebox.showinfo(
            "GrÃ¡fico de DetecÃ§Ã£o",
            "Nenhuma coluna de agravo detectÃ¡vel encontrada no arquivo para gerar o grÃ¡fico.",
        )
        return

    # Contagem de 'DetectÃ¡vel' (valor '1') para cada agravo
    contagem = {agravo: (df[agravo] == "1").sum() for agravo in colunas_agravos}

    # Filtra agravos com contagem zero para nÃ£o aparecerem no grÃ¡fico
    plot_data = {k: v for k, v in contagem.items() if v > 0}

    if not plot_data:
        registrar_log(
            "Gerar GrÃ¡fico",
            "Nenhum alvo detectÃ¡vel com contagem maior que zero para gerar o grÃ¡fico.",
            level="INFO",
        )
        messagebox.showinfo(
            "GrÃ¡fico de DetecÃ§Ã£o",
            "Nenhum alvo detectÃ¡vel com contagem maior que zero para gerar o grÃ¡fico.",
        )
        return

    labels = list(plot_data.keys())
    values = list(plot_data.values())

    plt.figure(figsize=(10, 6))
    plt.bar(labels, values, color="skyblue")
    plt.title("Quantidade de Amostras DetectÃ¡veis por Agravo")
    plt.xlabel("Agravo")
    plt.ylabel("Quantidade")
    plt.xticks(
        rotation=45, ha="right"
    )  # RotaÃ§Ã£o para melhor visualizaÃ§Ã£o de nomes longos
    plt.tight_layout()  # Ajusta o layout para evitar sobreposiÃ§Ã£o
    plt.show()

    registrar_log(
        "Gerar GrÃ¡fico", f"GrÃ¡fico gerado para arquivo: {arquivo}", level="INFO"
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

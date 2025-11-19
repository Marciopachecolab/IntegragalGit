import os
import sys
from typing import List, Optional

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from utils.after_mixin import AfterManagerMixin
from utils.logger import registrar_log
from db.db_utils import salvar_historico_processamento


def _norm_res_label(val: str) -> str:
    try:
        s = str(val).strip().lower()
    except Exception:
        return ''
    s = (s
         .replace('detectável', 'detectavel')
         .replace('não', 'nao')
         .replace('inválido', 'invalido'))
    if s in {'detectavel', 'detectado'}:
        return 'detectavel'
    if s in {'nao detectavel', 'nao detectado'}:
        return 'nao_detectavel'
    if s in {'invalido'}:
        return 'invalido'
    return s


class TabelaComSelecaoSimulada(AfterManagerMixin, ctk.CTkToplevel):
    """Interface para exibir resultados em tabela com seleção simulada."""

    def __init__(self, root, dataframe, status_corrida, num_placa, data_placa_formatada, agravos, usuario_logado: str = "Desconhecido"):
        super().__init__(master=root)
        self.title("RT-PCR - Análise com Seleção Simulada")
        self.state('zoomed')

        self.df = dataframe.copy()
        # Seleciona por padrão todas exceto inválidas
        if 'Selecionado' not in self.df.columns:
            result_cols = [c for c in self.df.columns if str(c).startswith('Resultado_')]
            selecoes = []
            for _, r in self.df.iterrows():
                inval = any(_norm_res_label(r.get(c, '')) == 'invalido' for c in result_cols)
                selecoes.append(False if inval else True)
            self.df.insert(0, 'Selecionado', selecoes)

        self.status_corrida = status_corrida
        self.num_placa = num_placa
        self.data_placa_formatada = data_placa_formatada
        self.agravos = agravos
        self.usuario_logado = usuario_logado

        self.transient(root)
        self.grab_set()

        self._criar_widgets()
        self._popular_tabela()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _criar_widgets(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # Frame superior para informações e botões
        top_frame = ctk.CTkFrame(main_frame)
        top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        top_frame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(top_frame, text=f"Placa: {self.num_placa}", font=("", 12, "bold")).grid(row=0, column=0, padx=10)
        ctk.CTkLabel(top_frame, text=f"Data: {self.data_placa_formatada}", font=("", 12, "bold")).grid(row=0, column=1, padx=10)
        ctk.CTkLabel(top_frame, text=f"Status da Corrida: {self.status_corrida}", font=("", 12, "bold")).grid(row=0, column=2, padx=10)

        # Botões de ação
        btn_relatorio = ctk.CTkButton(top_frame, text="Relatório Estatístico", command=self._mostrar_relatorio)
        btn_relatorio.grid(row=0, column=4, padx=5)

        btn_grafico = ctk.CTkButton(top_frame, text="Gráfico de Detecção", command=self._gerar_grafico_detectaveis)
        btn_grafico.grid(row=0, column=5, padx=5)

        btn_salvar = ctk.CTkButton(top_frame, text="Salvar Selecionados no Histórico", command=self._salvar_selecionados)
        btn_salvar.grid(row=0, column=6, padx=10)

        # Frame da Tabela
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(table_frame, columns=list(self.df.columns), show="headings")

        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        hsb.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<Double-1>", self._on_double_click)

    def _popular_tabela(self):
        for col in self.df.columns:
            self.tree.heading(col, text=col, command=lambda _col=col: self._ordenar_coluna(_col, False))
            self.tree.column(col, width=100, anchor="center")

        for index, row in self.df.iterrows():
            row_values = list(row)
            if isinstance(row_values[0], bool):
                row_values[0] = "V" if row_values[0] else ""
            self.tree.insert("", "end", values=row_values, iid=str(index))

    def _on_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return

        index = int(item_id)
        # Bloqueia alteração de seleção em amostras de controlo
        amostra = self.df.loc[index, 'Amostra']
        if any(ctrl in str(amostra).upper() for ctrl in ['CN', 'CP', 'NEG', 'POS']):
            messagebox.showwarning("Ação Bloqueada", "Não é permitido alterar a seleção de amostras de controlo.", parent=self)
            return

        # Impede selecionar amostras Inválidas
        result_cols = [c for c in self.df.columns if str(c).startswith('Resultado_')]
        if any(_norm_res_label(self.df.loc[index, c]) == 'invalido' for c in result_cols if c in self.df.columns):
            messagebox.showwarning("Ação Bloqueada", "Amostras inválidas não podem ser selecionadas.", parent=self)
            return

        # Alterna o valor
        current_value = self.df.loc[index, 'Selecionado']
        self.df.loc[index, 'Selecionado'] = not current_value

        new_symbol = "V" if not current_value else ""
        self.tree.item(item_id, values=[new_symbol] + list(self.df.iloc[index, 1:]))

    def _ordenar_coluna(self, col, reverse):
        # Implementação de ordenação opcional
        pass

    def _salvar_selecionados(self):
        # Reforça invariância: desmarca inválidas antes de salvar
        result_cols = [c for c in self.df.columns if str(c).startswith('Resultado_')]
        invalid_mask = self.df.apply(lambda r: any(_norm_res_label(r.get(c, '')) == 'invalido' for c in result_cols), axis=1)
        if invalid_mask.any():
            self.df.loc[invalid_mask, 'Selecionado'] = False

        df_selecionados = self.df[self.df['Selecionado'] == True]
        total_selecionados = len(df_selecionados)
        if total_selecionados == 0:
            messagebox.showinfo("Informação", "Nenhuma amostra selecionada para salvar.", parent=self)
            return

        try:
            detalhes = f"Placa: {self.num_placa}; {total_selecionados} amostras salvas."
            salvar_historico_processamento(self.usuario_logado, "Análise Manual", "Concluído", detalhes)
            messagebox.showinfo("Sucesso", f"{total_selecionados} amostras selecionadas foram salvas no histórico.", parent=self)
            registrar_log("Salvar Histórico", f"{total_selecionados} amostras salvas pelo utilizador {self.usuario_logado}.", "INFO")
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o histórico no banco de dados.\n\nErro: {e}", parent=self)
            registrar_log("Salvar Histórico", f"Falha ao salvar histórico: {e}", "ERROR")

    def _mostrar_relatorio(self):
        df_selecionados = self.df[self.df['Selecionado'] == True]
        total_amostras = len(df_selecionados)
        if total_amostras == 0:
            messagebox.showinfo("Relatório", "Nenhuma amostra selecionada.", parent=self)
            return

        report_text = f"Total de Amostras Selecionadas: {total_amostras}\n"
        report_text += "--------------------------------------\n"

        for agravo in self.agravos:
            col_resultado = f"Resultado_{agravo.replace(' ', '')}"
            if col_resultado in df_selecionados.columns:
                vals = df_selecionados[col_resultado].astype(str).str.strip().str.lower()
                detectaveis = vals.isin(['detectável', 'detectavel', 'detectado']).sum()
                nao_detectaveis = vals.isin(['não detectável', 'nao detectavel', 'nao detectado']).sum()
                invalidos = total_amostras - (detectaveis + nao_detectaveis)
                report_text += f"\nAgravo: {agravo}\n"
                report_text += f"  - Detectáveis: {detectaveis}\n"
                report_text += f"  - Não Detectáveis: {nao_detectaveis}\n"
                report_text += f"  - Inválidos/Outros: {invalidos}\n"

        messagebox.showinfo("Relatório Estatístico", report_text, parent=self)

    def _gerar_grafico_detectaveis(self):
        contagem = {}
        for agravo in self.agravos:
            col_resultado = 'Resultado_' + agravo.replace(' ', '')
            if col_resultado in self.df.columns:
                vals = self.df[col_resultado].astype(str).str.strip().str.lower()
                contagem[agravo] = int(vals.isin(['detectável', 'detectavel', 'detectado']).sum())
        plot_data = {k: v for k, v in contagem.items() if v > 0}
        if not plot_data:
            messagebox.showinfo('Gráfico de Detecção', 'Nenhum alvo detectável para gerar o gráfico.', parent=self)
            return
        plt.figure(figsize=(10, 6))
        plt.bar(plot_data.keys(), plot_data.values(), color='skyblue')
        plt.title('Distribuição de Agravos Detectáveis')
        plt.xlabel('Agravos')
        plt.ylabel('Amostras Detectáveis')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()

    def _on_close(self):
        self.dispose()
        self.grab_release()
        if self.winfo_exists():
            self.destroy()


class CTkSelectionDialog(ctk.CTkToplevel):
    def __init__(self, master, title: str, text: str, values: List[str]):
        super().__init__(master)
        self.title(title)
        self.geometry("400x180")

        self._values = values
        self._selection: Optional[str] = None

        self.transient(master)
        self.grab_set()
        self._create_widgets(text)

    def _create_widgets(self, text: str):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(main_frame, text=text).pack(anchor="w")

        self.combobox = ctk.CTkComboBox(main_frame, values=self._values)
        self.combobox.pack(fill="x", pady=(5, 20))
        if self._values:
            self.combobox.set(self._values[0])

        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        ok_button = ctk.CTkButton(button_frame, text="OK", command=self._on_ok)
        ok_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        cancel_button = ctk.CTkButton(button_frame, text="Cancelar", command=self._on_cancel, fg_color="gray")
        cancel_button.grid(row=0, column=1, padx=(5, 0), sticky="ew")

    def _on_ok(self):
        self._selection = self.combobox.get()
        self.destroy()

    def _on_cancel(self):
        self._selection = None
        self.destroy()

    def get_selection(self) -> Optional[str]:
        self.wait_window()
        return self._selection


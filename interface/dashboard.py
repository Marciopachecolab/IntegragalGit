"""
Dashboard Principal - IntegaGal
Fase 3.1 - Interface Gráfica
"""

import customtkinter as ctk
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime, timedelta
from pathlib import Path
import os

from .estilos import CORES, FONTES, STATUS_CORES, GRAFICO_CORES
from .componentes import criar_card_estatistica


class Dashboard(ctk.CTk):
    """
    Dashboard Principal do IntegaGal
    Exibe resumo de análises, gráficos e tabela de resultados recentes
    """
    
    def __init__(self):
        super().__init__()
        
        # Configurações da janela
        self.title("IntegaGal - Dashboard de Análises")
        self.geometry("1400x900")
        
        # Configurar tema
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Dados
        self.df_historico = None
        self.cards = {}
        
        # Criar interface
        self._criar_interface()
        
        # Carregar dados
        self.carregar_dados()
    
    def _criar_interface(self):
        """Cria toda a interface do dashboard"""
        # Configurar grid principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        self._criar_header()
        
        # Container principal com scroll
        self.main_container = ctk.CTkScrollableFrame(
            self,
            fg_color=CORES['fundo'],
            corner_radius=0
        )
        self.main_container.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Seções do dashboard
        self._criar_secao_cards()
        self._criar_secao_grafico()
        self._criar_secao_tabela()
    
    def _criar_header(self):
        """Cria header com logo e navegação"""
        header = ctk.CTkFrame(
            self,
            fg_color=CORES['primaria'],
            corner_radius=0,
            height=70
        )
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)
        
        # Logo e título
        frame_logo = ctk.CTkFrame(header, fg_color="transparent")
        frame_logo.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        label_icone = ctk.CTkLabel(
            frame_logo,
            text="🧬",
            font=("Arial", 32),
            text_color=CORES['branco']
        )
        label_icone.pack(side="left", padx=(0, 10))
        
        label_titulo = ctk.CTkLabel(
            frame_logo,
            text="IntegaGal",
            font=FONTES['titulo_grande'],
            text_color=CORES['branco']
        )
        label_titulo.pack(side="left")
        
        # Botões de navegação
        frame_nav = ctk.CTkFrame(header, fg_color="transparent")
        frame_nav.grid(row=0, column=1, padx=20, pady=10, sticky="e")
        
        btn_dashboard = ctk.CTkButton(
            frame_nav,
            text="Dashboard",
            fg_color=CORES['branco'],
            text_color=CORES['primaria'],
            hover_color=CORES['fundo'],
            corner_radius=5,
            width=120
        )
        btn_dashboard.pack(side="left", padx=5)
        
        btn_historico = ctk.CTkButton(
            frame_nav,
            text="Histórico",
            fg_color="transparent",
            text_color=CORES['branco'],
            hover_color=CORES['primaria_escuro'],
            border_width=2,
            border_color=CORES['branco'],
            corner_radius=5,
            width=120
        )
        btn_historico.pack(side="left", padx=5)
        
        btn_configuracoes = ctk.CTkButton(
            frame_nav,
            text="⚙️ Configurações",
            fg_color="transparent",
            text_color=CORES['branco'],
            hover_color=CORES['primaria_escuro'],
            border_width=2,
            border_color=CORES['branco'],
            corner_radius=5,
            width=140
        )
        btn_configuracoes.pack(side="left", padx=5)
    
    def _criar_secao_cards(self):
        """Cria seção de cards de resumo"""
        # Container dos cards
        frame_cards = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent"
        )
        frame_cards.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        frame_cards.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Criar 4 cards
        self.cards['total'] = criar_card_estatistica(
            frame_cards,
            titulo="Total de Análises",
            valor="0",
            tipo="info"
        )
        self.cards['total'].grid(row=0, column=0, sticky="ew", padx=10)
        
        self.cards['validas'] = criar_card_estatistica(
            frame_cards,
            titulo="Análises Válidas",
            valor="0",
            tipo="sucesso"
        )
        self.cards['validas'].grid(row=0, column=1, sticky="ew", padx=10)
        
        self.cards['alertas'] = criar_card_estatistica(
            frame_cards,
            titulo="Alertas Pendentes",
            valor="0",
            tipo="aviso"
        )
        self.cards['alertas'].grid(row=0, column=2, sticky="ew", padx=10)
        
        self.cards['ultima'] = criar_card_estatistica(
            frame_cards,
            titulo="Última Análise",
            valor="--:--",
            tipo="info"
        )
        self.cards['ultima'].grid(row=0, column=3, sticky="ew", padx=10)
    
    def _criar_secao_grafico(self):
        """Cria seção com gráfico de tendências"""
        # Container do gráfico
        frame_grafico = ctk.CTkFrame(
            self.main_container,
            fg_color=CORES['fundo_card'],
            corner_radius=10,
            border_width=1,
            border_color=CORES['borda']
        )
        frame_grafico.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        frame_grafico.grid_columnconfigure(0, weight=1)
        
        # Título
        label_titulo = ctk.CTkLabel(
            frame_grafico,
            text="📊 Análises por Dia (Últimos 30 dias)",
            font=FONTES['subtitulo'],
            text_color=CORES['texto']
        )
        label_titulo.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 10))
        
        # Frame para o gráfico matplotlib
        self.frame_canvas_grafico = ctk.CTkFrame(
            frame_grafico,
            fg_color=CORES['branco']
        )
        self.frame_canvas_grafico.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        # Placeholder - será preenchido em carregar_dados()
        self.canvas_grafico = None
    
    def _criar_secao_tabela(self):
        """Cria seção com tabela de análises recentes"""
        # Container da tabela
        frame_tabela = ctk.CTkFrame(
            self.main_container,
            fg_color=CORES['fundo_card'],
            corner_radius=10,
            border_width=1,
            border_color=CORES['borda']
        )
        frame_tabela.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        frame_tabela.grid_columnconfigure(0, weight=1)
        
        # Título
        label_titulo = ctk.CTkLabel(
            frame_tabela,
            text="📋 Análises Recentes",
            font=FONTES['subtitulo'],
            text_color=CORES['texto']
        )
        label_titulo.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 10))
        
        # Frame para a tabela
        frame_tree = ctk.CTkFrame(
            frame_tabela,
            fg_color=CORES['branco']
        )
        frame_tree.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
        frame_tree.grid_columnconfigure(0, weight=1)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tree, orient="vertical")
        
        # Treeview (tabela)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=CORES['branco'],
            foreground=CORES['texto'],
            rowheight=30,
            fieldbackground=CORES['branco'],
            font=FONTES['corpo']
        )
        style.configure(
            "Treeview.Heading",
            font=FONTES['corpo_bold'],
            background=CORES['fundo'],
            foreground=CORES['texto']
        )
        style.map('Treeview', background=[('selected', CORES['primaria_claro'])])
        
        self.tree = ttk.Treeview(
            frame_tree,
            columns=("data_hora", "exame", "equipamento", "status"),
            show="headings",
            yscrollcommand=scrollbar.set,
            height=10
        )
        
        # Configurar colunas
        self.tree.heading("data_hora", text="Data/Hora")
        self.tree.heading("exame", text="Exame")
        self.tree.heading("equipamento", text="Equipamento")
        self.tree.heading("status", text="Status")
        
        self.tree.column("data_hora", width=150, anchor="w")
        self.tree.column("exame", width=250, anchor="w")
        self.tree.column("equipamento", width=200, anchor="w")
        self.tree.column("status", width=120, anchor="center")
        
        scrollbar.config(command=self.tree.yview)
        
        self.tree.grid(row=0, column=0, sticky="ew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Bind para duplo clique (futura navegação para detalhes)
        self.tree.bind("<Double-1>", self._on_item_double_click)
    
    def carregar_dados(self):
        """Carrega dados do histórico de análises"""
        try:
            # Tentar carregar histórico
            caminho_historico = Path("logs/historico_analises.csv")
            
            if caminho_historico.exists():
                self.df_historico = pd.read_csv(caminho_historico)
                self._atualizar_interface_com_dados()
            else:
                # Criar dados de exemplo
                self._criar_dados_exemplo()
                self._atualizar_interface_com_dados()
        
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            self._criar_dados_exemplo()
            self._atualizar_interface_com_dados()
    
    def _criar_dados_exemplo(self):
        """Cria dados de exemplo para demonstração"""
        # Dados fictícios para demonstração
        dados = []
        equipamentos = ["ABI 7500", "Biomanguinhos", "QuantStudio"]
        exames = ["VR1e2 Biomanguinhos", "Dengue PCR", "Zika RT-PCR", "Chikungunya"]
        status = ["valida", "valida", "invalida", "aviso"]
        
        for i in range(30):
            data = datetime.now() - timedelta(days=29-i)
            dados.append({
                'data_hora': data.strftime("%Y-%m-%d %H:%M:%S"),
                'exame': exames[i % len(exames)],
                'equipamento': equipamentos[i % len(equipamentos)],
                'status': status[i % len(status)],
                'analista': 'Usuario Teste'
            })
        
        self.df_historico = pd.DataFrame(dados)
    
    def _atualizar_interface_com_dados(self):
        """Atualiza toda a interface com os dados carregados"""
        if self.df_historico is None or len(self.df_historico) == 0:
            return
        
        # Atualizar cards
        self._atualizar_cards()
        
        # Atualizar gráfico
        self._atualizar_grafico()
        
        # Atualizar tabela
        self._atualizar_tabela()
    
    def _atualizar_cards(self):
        """Atualiza valores dos cards de resumo"""
        if self.df_historico is None:
            return
        
        # Total
        total = len(self.df_historico)
        self.cards['total'].atualizar_valor(str(total))
        
        # Válidas
        validas = len(self.df_historico[self.df_historico['status'] == 'valida'])
        self.cards['validas'].atualizar_valor(str(validas))
        
        # Alertas (avisos + inválidas)
        alertas = len(self.df_historico[self.df_historico['status'].isin(['aviso', 'invalida'])])
        self.cards['alertas'].atualizar_valor(str(alertas))
        
        # Última análise
        if len(self.df_historico) > 0:
            ultima = pd.to_datetime(self.df_historico['data_hora']).max()
            self.cards['ultima'].atualizar_valor(ultima.strftime("%H:%M"))
    
    def _atualizar_grafico(self):
        """Atualiza gráfico de tendências"""
        if self.df_historico is None or len(self.df_historico) == 0:
            return
        
        # Limpar gráfico anterior
        if self.canvas_grafico:
            self.canvas_grafico.get_tk_widget().destroy()
        
        # Preparar dados
        df = self.df_historico.copy()
        df['data'] = pd.to_datetime(df['data_hora']).dt.date
        
        # Agrupar por data
        df_agrupado = df.groupby('data').size().reset_index(name='count')
        
        # Criar figura matplotlib
        fig = Figure(figsize=(12, 4), dpi=100, facecolor=CORES['branco'])
        ax = fig.add_subplot(111)
        
        # Plotar linha
        ax.plot(
            df_agrupado['data'],
            df_agrupado['count'],
            color=CORES['primaria'],
            linewidth=2,
            marker='o',
            markersize=6,
            markerfacecolor=CORES['primaria'],
            markeredgecolor=CORES['branco'],
            markeredgewidth=2
        )
        
        # Estilo
        ax.set_xlabel('Data', fontsize=10)
        ax.set_ylabel('Quantidade', fontsize=10)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_facecolor(CORES['branco'])
        
        # Rotacionar labels do eixo x
        fig.autofmt_xdate()
        
        # Ajustar layout
        fig.tight_layout()
        
        # Criar canvas tkinter
        self.canvas_grafico = FigureCanvasTkAgg(fig, master=self.frame_canvas_grafico)
        self.canvas_grafico.draw()
        self.canvas_grafico.get_tk_widget().pack(fill="both", expand=True)
    
    def _atualizar_tabela(self):
        """Atualiza tabela de análises recentes"""
        if self.df_historico is None:
            return
        
        # Limpar tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Pegar últimas 20 análises
        df_recentes = self.df_historico.tail(20).sort_values('data_hora', ascending=False)
        
        # Adicionar linhas
        for _, row in df_recentes.iterrows():
            # Formatar data/hora
            dt = pd.to_datetime(row['data_hora'])
            data_hora_fmt = dt.strftime("%d/%m/%Y %H:%M")
            
            # Formatar status
            status_map = {
                'valida': '✅ Válida',
                'invalida': '❌ Inválida',
                'aviso': '⚠️ Aviso'
            }
            status_fmt = status_map.get(row['status'], row['status'])
            
            # Inserir na tabela
            self.tree.insert(
                "",
                "end",
                values=(
                    data_hora_fmt,
                    row['exame'],
                    row['equipamento'],
                    status_fmt
                )
            )
    
    def _on_item_double_click(self, event):
        """Handler para duplo clique na tabela"""
        item = self.tree.selection()
        if item:
            # Futuramente: abrir visualizador de detalhes
            valores = self.tree.item(item[0])['values']
            print(f"Duplo clique em: {valores}")
    
    def atualizar_dados(self):
        """Recarrega dados e atualiza interface"""
        self.carregar_dados()


def main():
    """Função principal para executar o dashboard"""
    app = Dashboard()
    app.mainloop()


if __name__ == '__main__':
    main()

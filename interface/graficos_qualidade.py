"""
Gráficos de Qualidade e Estatísticas - IntegaGal
Fase 3.3 - Interface Gráfica
"""

import customtkinter as ctk
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from .estilos import CORES, FONTES, GRAFICO_CORES


class GraficosQualidade(ctk.CTkToplevel):
    """
    Janela de visualização de gráficos de qualidade e estatísticas
    Exibe análises estatísticas, tendências e distribuições
    """
    
    def __init__(self, master, dados_historico: Optional[pd.DataFrame] = None):
        """
        Inicializa janela de gráficos de qualidade
        
        Args:
            master: Janela pai
            dados_historico: DataFrame com histórico de análises
        """
        super().__init__(master)
        
        self.df = dados_historico if dados_historico is not None else self._gerar_dados_exemplo()
        
        # Configurações da janela
        self.title("Gráficos de Qualidade e Estatísticas")
        self.geometry("1400x900")
        
        # Configurar grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Criar interface
        self._criar_header()
        self._criar_conteudo()
        
        # Focar na janela
        self.focus()
    
    def _criar_header(self):
        """Cria header com título e controles"""
        header = ctk.CTkFrame(
            self,
            fg_color=CORES['primaria'],
            corner_radius=0,
            height=80
        )
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)
        header.grid_propagate(False)
        
        # Ícone e título
        label_icone = ctk.CTkLabel(
            header,
            text="📊",
            font=("Arial", 36),
            text_color=CORES['branco']
        )
        label_icone.grid(row=0, column=0, padx=(30, 15), pady=20)
        
        label_titulo = ctk.CTkLabel(
            header,
            text="Gráficos de Qualidade e Estatísticas",
            font=FONTES['titulo_grande'],
            text_color=CORES['branco']
        )
        label_titulo.grid(row=0, column=1, sticky="w", pady=20)
        
        # Informações do período
        if not self.df.empty:
            data_min = self.df['data_hora'].min()
            data_max = self.df['data_hora'].max()
            total_analises = len(self.df)
            
            info_text = f"📅 {data_min} a {data_max} | 🔬 {total_analises} análises"
            
            label_info = ctk.CTkLabel(
                header,
                text=info_text,
                font=FONTES['corpo'],
                text_color=CORES['branco']
            )
            label_info.grid(row=0, column=2, padx=20)
        
        # Botão fechar
        btn_fechar = ctk.CTkButton(
            header,
            text="✕",
            command=self.destroy,
            fg_color="transparent",
            hover_color=CORES['primaria_escuro'],
            width=40,
            height=40,
            font=("Arial", 20, "bold"),
            corner_radius=5
        )
        btn_fechar.grid(row=0, column=3, padx=(10, 30))
    
    def _criar_conteudo(self):
        """Cria conteúdo principal com gráficos"""
        # Container com scroll
        container = ctk.CTkScrollableFrame(
            self,
            fg_color=CORES['fundo'],
            corner_radius=0
        )
        container.grid(row=1, column=0, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        
        # Seções
        self._criar_secao_estatisticas(container)
        self._criar_secao_distribuicao_ct(container)
        self._criar_secao_tendencia_temporal(container)
        self._criar_secao_taxa_sucesso(container)
        self._criar_secao_analise_equipamentos(container)
        self._criar_secao_acoes(container)
    
    def _criar_secao_estatisticas(self, parent):
        """Cria seção de estatísticas descritivas"""
        frame = self._criar_frame_secao(
            parent,
            titulo="📈 Estatísticas Gerais",
            row=0
        )
        
        if self.df.empty:
            self._criar_mensagem_vazio(frame, "Sem dados para análise estatística")
            return
        
        # Container de cards
        cards_container = ctk.CTkFrame(frame, fg_color="transparent")
        cards_container.pack(fill="x", padx=20, pady=(0, 15))
        cards_container.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Calcular estatísticas
        total_analises = len(self.df)
        analises_validas = len(self.df[self.df['status'] == 'Válida'])
        taxa_sucesso = (analises_validas / total_analises * 100) if total_analises > 0 else 0
        
        # Equipamento mais usado
        equipamento_mais_usado = self.df['equipamento'].mode()[0] if not self.df.empty else "N/A"
        
        # Exame mais frequente
        exame_mais_freq = self.df['exame'].mode()[0] if not self.df.empty else "N/A"
        
        # Criar cards
        stats = [
            ("📊", str(total_analises), "Total de Análises", CORES['primaria']),
            ("✅", f"{taxa_sucesso:.1f}%", "Taxa de Sucesso", CORES['sucesso']),
            ("🔧", equipamento_mais_usado, "Equipamento + Usado", CORES['secundaria']),
            ("🔬", exame_mais_freq, "Exame + Frequente", CORES['info'])
        ]
        
        for col, (emoji, valor, titulo, cor) in enumerate(stats):
            self._criar_card_estatistica(cards_container, emoji, valor, titulo, cor, col)
    
    def _criar_card_estatistica(self, parent, emoji: str, valor: str, titulo: str, cor: str, col: int):
        """Cria card de estatística"""
        card = ctk.CTkFrame(
            parent,
            fg_color=CORES['branco'],
            corner_radius=10,
            border_width=2,
            border_color=cor
        )
        card.grid(row=0, column=col, padx=10, pady=10, sticky="ew")
        
        # Emoji
        label_emoji = ctk.CTkLabel(
            card,
            text=emoji,
            font=("Arial", 32),
            text_color=cor
        )
        label_emoji.pack(pady=(15, 5))
        
        # Valor
        label_valor = ctk.CTkLabel(
            card,
            text=valor,
            font=FONTES['titulo'],
            text_color=cor
        )
        label_valor.pack(pady=5)
        
        # Título
        label_titulo = ctk.CTkLabel(
            card,
            text=titulo,
            font=FONTES['corpo'],
            text_color=CORES['texto_secundario']
        )
        label_titulo.pack(pady=(0, 15))
    
    def _criar_secao_distribuicao_ct(self, parent):
        """Cria seção com gráfico de distribuição de valores CT"""
        frame = self._criar_frame_secao(
            parent,
            titulo="📊 Distribuição de Valores CT",
            row=1
        )
        
        if self.df.empty:
            self._criar_mensagem_vazio(frame, "Sem dados para gráfico de distribuição")
            return
        
        # Frame para gráfico
        frame_canvas = ctk.CTkFrame(frame, fg_color=CORES['branco'])
        frame_canvas.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Criar figura
        fig = Figure(figsize=(12, 5), dpi=100, facecolor=CORES['branco'])
        
        # Subplot 1: Histograma
        ax1 = fig.add_subplot(121)
        
        # Gerar dados CT fictícios (em produção, virão do banco)
        ct_values = np.random.normal(25, 5, 1000)
        ct_values = ct_values[ct_values > 0]  # Apenas valores positivos
        
        ax1.hist(ct_values, bins=30, color=GRAFICO_CORES[0], edgecolor='white', alpha=0.8)
        ax1.axvline(x=30, color=CORES['erro'], linestyle='--', linewidth=2, label='Threshold (30)')
        ax1.set_xlabel('Valor CT', fontsize=10)
        ax1.set_ylabel('Frequência', fontsize=10)
        ax1.set_title('Distribuição de Valores CT', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.legend()
        ax1.set_facecolor(CORES['branco'])
        
        # Subplot 2: Boxplot
        ax2 = fig.add_subplot(122)
        
        # Simular dados por exame
        exames = ['DEN1', 'DEN2', 'DEN3', 'DEN4', 'ZIKA']
        ct_por_exame = [np.random.normal(20 + i*2, 4, 200) for i in range(len(exames))]
        
        bp = ax2.boxplot(ct_por_exame, labels=exames, patch_artist=True,
                         medianprops=dict(color='red', linewidth=2),
                         boxprops=dict(facecolor=GRAFICO_CORES[1], alpha=0.8))
        
        ax2.axhline(y=30, color=CORES['erro'], linestyle='--', linewidth=2, label='Threshold')
        ax2.set_ylabel('Valor CT', fontsize=10)
        ax2.set_xlabel('Alvos', fontsize=10)
        ax2.set_title('Distribuição CT por Alvo', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y', linestyle='--')
        ax2.legend()
        ax2.set_facecolor(CORES['branco'])
        
        fig.tight_layout()
        
        # Canvas
        canvas = FigureCanvasTkAgg(fig, master=frame_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def _criar_secao_tendencia_temporal(self, parent):
        """Cria seção com gráfico de tendência temporal"""
        frame = self._criar_frame_secao(
            parent,
            titulo="📈 Tendência Temporal de Análises",
            row=2
        )
        
        if self.df.empty:
            self._criar_mensagem_vazio(frame, "Sem dados para gráfico de tendência")
            return
        
        # Frame para gráfico
        frame_canvas = ctk.CTkFrame(frame, fg_color=CORES['branco'])
        frame_canvas.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Criar figura
        fig = Figure(figsize=(12, 5), dpi=100, facecolor=CORES['branco'])
        ax = fig.add_subplot(111)
        
        # Gerar dados de tendência (30 dias)
        hoje = datetime.now()
        datas = [hoje - timedelta(days=x) for x in range(30, 0, -1)]
        datas_str = [d.strftime('%d/%m') for d in datas]
        
        # Simular análises por dia
        validas = np.random.randint(15, 35, 30)
        invalidas = np.random.randint(2, 8, 30)
        avisos = np.random.randint(3, 10, 30)
        
        # Gráfico de área empilhada
        ax.fill_between(range(30), 0, validas, color=CORES['sucesso'], alpha=0.7, label='Válidas')
        ax.fill_between(range(30), validas, validas + avisos, color=CORES['aviso'], alpha=0.7, label='Avisos')
        ax.fill_between(range(30), validas + avisos, validas + avisos + invalidas, 
                       color=CORES['erro'], alpha=0.7, label='Inválidas')
        
        # Linha de total
        total = validas + avisos + invalidas
        ax.plot(range(30), total, color=CORES['primaria'], linewidth=2, marker='o', 
               markersize=4, label='Total')
        
        # Configurações
        ax.set_xlabel('Data', fontsize=10)
        ax.set_ylabel('Número de Análises', fontsize=10)
        ax.set_title('Evolução de Análises nos Últimos 30 Dias', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(loc='upper left')
        ax.set_facecolor(CORES['branco'])
        
        # Labels do eixo X (mostrar apenas alguns)
        indices_mostrar = list(range(0, 30, 5))
        ax.set_xticks(indices_mostrar)
        ax.set_xticklabels([datas_str[i] for i in indices_mostrar], rotation=45)
        
        fig.tight_layout()
        
        # Canvas
        canvas = FigureCanvasTkAgg(fig, master=frame_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def _criar_secao_taxa_sucesso(self, parent):
        """Cria seção com gráfico de taxa de sucesso"""
        frame = self._criar_frame_secao(
            parent,
            titulo="✅ Taxa de Sucesso por Exame",
            row=3
        )
        
        if self.df.empty:
            self._criar_mensagem_vazio(frame, "Sem dados para taxa de sucesso")
            return
        
        # Frame para gráfico
        frame_canvas = ctk.CTkFrame(frame, fg_color=CORES['branco'])
        frame_canvas.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Criar figura
        fig = Figure(figsize=(12, 5), dpi=100, facecolor=CORES['branco'])
        
        # Subplot 1: Barras horizontais de taxa de sucesso
        ax1 = fig.add_subplot(121)
        
        exames = ['VR1e2\nBiomanguinhos', 'Dengue\nQuadruplex', 'Zika\nDetecção', 
                 'Chikungunya\nPCR', 'Influenza\nMultiplex']
        taxas = [95.5, 92.3, 88.7, 90.1, 93.8]
        
        colors = [CORES['sucesso'] if t >= 90 else CORES['aviso'] for t in taxas]
        bars = ax1.barh(exames, taxas, color=colors, edgecolor='white', linewidth=2)
        
        # Adicionar valores nas barras
        for i, (bar, taxa) in enumerate(zip(bars, taxas)):
            ax1.text(taxa + 1, i, f'{taxa:.1f}%', va='center', fontweight='bold', fontsize=10)
        
        ax1.set_xlabel('Taxa de Sucesso (%)', fontsize=10)
        ax1.set_title('Taxa de Sucesso por Tipo de Exame', fontsize=12, fontweight='bold')
        ax1.set_xlim(0, 110)
        ax1.axvline(x=90, color=CORES['texto_secundario'], linestyle='--', linewidth=1, alpha=0.5)
        ax1.grid(True, alpha=0.3, axis='x', linestyle='--')
        ax1.set_facecolor(CORES['branco'])
        
        # Subplot 2: Pizza de status
        ax2 = fig.add_subplot(122)
        
        status = ['Válidas', 'Avisos', 'Inválidas']
        valores = [850, 120, 30]
        cores_pizza = [CORES['sucesso'], CORES['aviso'], CORES['erro']]
        
        wedges, texts, autotexts = ax2.pie(valores, labels=status, autopct='%1.1f%%',
                                           colors=cores_pizza, startangle=90,
                                           textprops={'fontsize': 10, 'fontweight': 'bold'})
        
        # Estilo dos textos
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(11)
            autotext.set_fontweight('bold')
        
        ax2.set_title('Distribuição Geral de Status', fontsize=12, fontweight='bold')
        
        fig.tight_layout()
        
        # Canvas
        canvas = FigureCanvasTkAgg(fig, master=frame_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def _criar_secao_analise_equipamentos(self, parent):
        """Cria seção com análise por equipamento"""
        frame = self._criar_frame_secao(
            parent,
            titulo="🔧 Análise por Equipamento",
            row=4
        )
        
        if self.df.empty:
            self._criar_mensagem_vazio(frame, "Sem dados para análise de equipamentos")
            return
        
        # Frame para gráfico
        frame_canvas = ctk.CTkFrame(frame, fg_color=CORES['branco'])
        frame_canvas.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Criar figura
        fig = Figure(figsize=(12, 5), dpi=100, facecolor=CORES['branco'])
        ax = fig.add_subplot(111)
        
        # Dados por equipamento
        equipamentos = ['ABI 7500', 'QuantStudio 5', 'CFX96', 'LightCycler']
        x = np.arange(len(equipamentos))
        
        validas = [280, 245, 190, 135]
        avisos = [35, 28, 42, 15]
        invalidas = [8, 12, 15, 5]
        
        width = 0.25
        
        # Barras agrupadas
        bars1 = ax.bar(x - width, validas, width, label='Válidas', color=CORES['sucesso'], edgecolor='white')
        bars2 = ax.bar(x, avisos, width, label='Avisos', color=CORES['aviso'], edgecolor='white')
        bars3 = ax.bar(x + width, invalidas, width, label='Inválidas', color=CORES['erro'], edgecolor='white')
        
        # Adicionar valores nas barras
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height)}',
                           ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax.set_xlabel('Equipamento', fontsize=10)
        ax.set_ylabel('Número de Análises', fontsize=10)
        ax.set_title('Desempenho por Equipamento', fontsize=12, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(equipamentos)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y', linestyle='--')
        ax.set_facecolor(CORES['branco'])
        
        fig.tight_layout()
        
        # Canvas
        canvas = FigureCanvasTkAgg(fig, master=frame_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def _criar_frame_secao(self, parent, titulo: str, row: int) -> ctk.CTkFrame:
        """Helper para criar frame de seção"""
        frame = ctk.CTkFrame(
            parent,
            fg_color=CORES['fundo_card'],
            corner_radius=10,
            border_width=1,
            border_color=CORES['borda']
        )
        frame.grid(row=row, column=0, sticky="ew", padx=20, pady=(0, 20))
        frame.grid_columnconfigure(0, weight=1)
        
        # Título
        label_titulo = ctk.CTkLabel(
            frame,
            text=titulo,
            font=FONTES['subtitulo'],
            text_color=CORES['texto']
        )
        label_titulo.pack(anchor="w", padx=20, pady=(15, 10))
        
        return frame
    
    def _criar_mensagem_vazio(self, parent, mensagem: str):
        """Cria mensagem de container vazio"""
        label = ctk.CTkLabel(
            parent,
            text=mensagem,
            font=FONTES['corpo'],
            text_color=CORES['texto_secundario']
        )
        label.pack(padx=20, pady=20)
    
    def _criar_secao_acoes(self, parent):
        """Cria seção de ações de exportação"""
        frame = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )
        frame.grid(row=5, column=0, sticky="ew", padx=20, pady=20)
        frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Botões de exportação
        btn_exportar_excel = ctk.CTkButton(
            frame,
            text="📊 Exportar Histórico (Excel)",
            command=lambda: self._exportar_historico_excel(),
            fg_color=CORES['secundaria'],
            hover_color=CORES['secundaria_hover'],
            height=40,
            font=FONTES['corpo_bold']
        )
        btn_exportar_excel.grid(row=0, column=0, padx=10)
        
        btn_exportar_csv = ctk.CTkButton(
            frame,
            text="📄 Exportar Histórico (CSV)",
            command=lambda: self._exportar_historico_csv(),
            fg_color=CORES['info'],
            hover_color=CORES['info'],
            height=40,
            font=FONTES['corpo_bold']
        )
        btn_exportar_csv.grid(row=0, column=1, padx=10)
        
        btn_fechar = ctk.CTkButton(
            frame,
            text="✕ Fechar",
            command=self.destroy,
            fg_color=CORES['texto_secundario'],
            hover_color=CORES['texto'],
            height=40,
            font=FONTES['corpo_bold']
        )
        btn_fechar.grid(row=0, column=2, padx=10)
    
    def _exportar_historico_excel(self):
        """Exporta histórico para Excel"""
        try:
            from .exportacao_relatorios import ExportadorRelatorios
            import tkinter.messagebox as messagebox
            
            exportador = ExportadorRelatorios()
            caminho = exportador.exportar_historico_excel(self.df)
            messagebox.showinfo("Sucesso", f"Excel gerado com sucesso!\\n\\nLocal: {caminho}")
            print(f"✅ Excel exportado: {caminho}")
        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Erro", f"Erro ao exportar Excel:\\n{e}")
            print(f"❌ Erro ao exportar Excel: {e}")
    
    def _exportar_historico_csv(self):
        """Exporta histórico para CSV"""
        try:
            from .exportacao_relatorios import ExportadorRelatorios
            import tkinter.messagebox as messagebox
            
            exportador = ExportadorRelatorios()
            caminho = exportador.exportar_historico_csv(self.df)
            messagebox.showinfo("Sucesso", f"CSV gerado com sucesso!\\n\\nLocal: {caminho}")
            print(f"✅ CSV exportado: {caminho}")
        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Erro", f"Erro ao exportar CSV:\\n{e}")
            print(f"❌ Erro ao exportar CSV: {e}")
    
    def _gerar_dados_exemplo(self) -> pd.DataFrame:
        """Gera dados de exemplo para demonstração"""
        hoje = datetime.now()
        datas = [hoje - timedelta(days=x) for x in range(90)]
        
        dados = []
        exames = ['VR1e2 Biomanguinhos 7500', 'Dengue Quadruplex', 'Zika Detecção']
        equipamentos = ['ABI 7500', 'QuantStudio 5', 'CFX96']
        status_opcoes = ['Válida', 'Válida', 'Válida', 'Válida', 'Aviso', 'Inválida']
        
        for data in datas:
            n_analises = np.random.randint(8, 15)
            for _ in range(n_analises):
                dados.append({
                    'data_hora': data.strftime('%d/%m/%Y %H:%M:%S'),
                    'exame': np.random.choice(exames),
                    'equipamento': np.random.choice(equipamentos),
                    'status': np.random.choice(status_opcoes)
                })
        
        return pd.DataFrame(dados)


# Teste standalone
if __name__ == '__main__':
    import customtkinter as ctk
    
    app = ctk.CTk()
    app.withdraw()
    
    graficos = GraficosQualidade(app)
    
    app.mainloop()

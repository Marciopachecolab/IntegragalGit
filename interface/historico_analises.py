"""
Histórico de Análises - IntegaGal
Fase 3.5 - Interface Gráfica

Módulo para busca, filtro e visualização de histórico de análises
"""

import customtkinter as ctk
from tkinter import ttk
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from .estilos import CORES, FONTES, STATUS_CORES


class HistoricoAnalises(ctk.CTkToplevel):
    """
    Janela de histórico de análises com busca e filtros
    """
    
    def __init__(self, master, dados_historico: Optional[pd.DataFrame] = None):
        """
        Inicializa janela de histórico
        
        Args:
            master: Janela pai
            dados_historico: DataFrame com histórico de análises
        """
        super().__init__(master)
        
        self.df_original = dados_historico if dados_historico is not None else self._gerar_dados_exemplo()
        self.df_filtrado = self.df_original.copy()
        
        # Configurações da janela
        self.title("Histórico de Análises")
        self.geometry("1400x800")
        
        # Configurar grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Criar interface
        self._criar_header()
        self._criar_filtros()
        self._criar_tabela()
        self._criar_rodape()
        
        # Atualizar tabela inicial
        self._atualizar_tabela()
        
        # Focar na janela
        self.focus()
    
    def _criar_header(self):
        """Cria header com título"""
        header = ctk.CTkFrame(
            self,
            fg_color=CORES['primaria'],
            corner_radius=0,
            height=70
        )
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)
        header.grid_propagate(False)
        
        # Ícone e título
        label_icone = ctk.CTkLabel(
            header,
            text="📜",
            font=("Arial", 32),
            text_color=CORES['branco']
        )
        label_icone.grid(row=0, column=0, padx=(30, 15), pady=15)
        
        label_titulo = ctk.CTkLabel(
            header,
            text="Histórico de Análises",
            font=FONTES['titulo_grande'],
            text_color=CORES['branco']
        )
        label_titulo.grid(row=0, column=1, sticky="w", pady=15)
        
        # Contador de registros
        self.label_contador = ctk.CTkLabel(
            header,
            text=f"📊 {len(self.df_original)} registros",
            font=FONTES['corpo'],
            text_color=CORES['branco']
        )
        self.label_contador.grid(row=0, column=2, padx=20)
        
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
    
    def dispose(self):
        """Cancela todos os callbacks agendados."""
        for aid in self._after_ids:
            try:
                self.after_cancel(aid)
            except Exception:
                pass
        self._after_ids.clear()
    
    def schedule(self, delay_ms: int, callback, *args, **kwargs):
        """Agendar callback e registrar para cancelamento posterior."""
        aid = self.after(delay_ms, callback, *args, **kwargs)
        self._after_ids.add(aid)
        return aid
    
    def _on_close(self):
        """Fecha a janela com segurança."""
        try:
            # Cancelar callbacks pendentes
            self.dispose()
            
            # Destruir janela
            if self.winfo_exists():
                self.destroy()
        except Exception:
            pass
    
    def _criar_filtros(self):
        """Cria seção de filtros"""
        frame_filtros = ctk.CTkFrame(
            self,
            fg_color=CORES['fundo_card'],
            corner_radius=10,
            border_width=1,
            border_color=CORES['borda']
        )
        frame_filtros.grid(row=1, column=0, sticky="ew", padx=20, pady=(20, 10))
        frame_filtros.grid_columnconfigure(1, weight=1)
        
        # Label
        label_filtros = ctk.CTkLabel(
            frame_filtros,
            text="🔍 Filtros",
            font=FONTES['subtitulo'],
            text_color=CORES['texto']
        )
        label_filtros.grid(row=0, column=0, columnspan=6, sticky="w", padx=20, pady=(15, 10))
        
        # Linha 1: Busca por texto
        label_busca = ctk.CTkLabel(
            frame_filtros,
            text="Buscar:",
            font=FONTES['corpo'],
            text_color=CORES['texto']
        )
        label_busca.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="w")
        
        self.entry_busca = ctk.CTkEntry(
            frame_filtros,
            placeholder_text="Digite nome do exame, equipamento...",
            width=300,
            height=35
        )
        self.entry_busca.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.entry_busca.bind("<KeyRelease>", lambda e: self._aplicar_filtros())
        
        # Período
        label_periodo = ctk.CTkLabel(
            frame_filtros,
            text="Período:",
            font=FONTES['corpo'],
            text_color=CORES['texto']
        )
        label_periodo.grid(row=1, column=2, padx=(20, 10), pady=10, sticky="w")
        
        self.combo_periodo = ctk.CTkComboBox(
            frame_filtros,
            values=["Todos", "Hoje", "Última semana", "Último mês", "Último ano"],
            width=150,
            height=35,
            command=lambda _: self._aplicar_filtros()
        )
        self.combo_periodo.set("Todos")
        self.combo_periodo.grid(row=1, column=3, padx=10, pady=10)
        
        # Linha 2: Filtros adicionais
        label_equipamento = ctk.CTkLabel(
            frame_filtros,
            text="Equipamento:",
            font=FONTES['corpo'],
            text_color=CORES['texto']
        )
        label_equipamento.grid(row=2, column=0, padx=(20, 10), pady=10, sticky="w")
        
        equipamentos = ["Todos"] + sorted(self.df_original['equipamento'].unique().tolist())
        self.combo_equipamento = ctk.CTkComboBox(
            frame_filtros,
            values=equipamentos,
            width=200,
            height=35,
            command=lambda _: self._aplicar_filtros()
        )
        self.combo_equipamento.set("Todos")
        self.combo_equipamento.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        label_status = ctk.CTkLabel(
            frame_filtros,
            text="Status:",
            font=FONTES['corpo'],
            text_color=CORES['texto']
        )
        label_status.grid(row=2, column=2, padx=(20, 10), pady=10, sticky="w")
        
        self.combo_status = ctk.CTkComboBox(
            frame_filtros,
            values=["Todos", "Válida", "Aviso", "Inválida"],
            width=150,
            height=35,
            command=lambda _: self._aplicar_filtros()
        )
        self.combo_status.set("Todos")
        self.combo_status.grid(row=2, column=3, padx=10, pady=10)
        
        # Botões de ação
        btn_limpar = ctk.CTkButton(
            frame_filtros,
            text="🔄 Limpar Filtros",
            command=self._limpar_filtros,
            fg_color=CORES['texto_secundario'],
            hover_color=CORES['texto'],
            width=140,
            height=35
        )
        btn_limpar.grid(row=2, column=4, padx=10, pady=10)
        
        btn_exportar = ctk.CTkButton(
            frame_filtros,
            text="📊 Exportar",
            command=self._exportar_filtrados,
            fg_color=CORES['secundaria'],
            hover_color=CORES['secundaria_hover'],
            width=120,
            height=35
        )
        btn_exportar.grid(row=2, column=5, padx=(10, 20), pady=10)
    
    def _criar_tabela(self):
        """Cria tabela de resultados"""
        frame_tabela = ctk.CTkFrame(
            self,
            fg_color=CORES['branco'],
            corner_radius=10,
            border_width=1,
            border_color=CORES['borda']
        )
        frame_tabela.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        frame_tabela.grid_columnconfigure(0, weight=1)
        frame_tabela.grid_rowconfigure(0, weight=1)
        
        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "Historico.Treeview",
            background=CORES['branco'],
            foreground=CORES['texto'],
            rowheight=35,
            fieldbackground=CORES['branco'],
            font=FONTES['corpo']
        )
        style.configure(
            "Historico.Treeview.Heading",
            font=FONTES['corpo_bold'],
            background=CORES['primaria'],
            foreground=CORES['branco'],
            relief="flat"
        )
        style.map(
            'Historico.Treeview',
            background=[('selected', CORES['primaria'])],
            foreground=[('selected', CORES['branco'])]
        )
        
        # Scrollbars
        scrollbar_y = ttk.Scrollbar(frame_tabela, orient="vertical")
        scrollbar_x = ttk.Scrollbar(frame_tabela, orient="horizontal")
        
        # Treeview
        self.tree = ttk.Treeview(
            frame_tabela,
            columns=("data_hora", "exame", "equipamento", "status"),
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            style="Historico.Treeview"
        )
        
        # Configurar colunas
        self.tree.heading("data_hora", text="Data/Hora", command=lambda: self._ordenar_coluna("data_hora"))
        self.tree.heading("exame", text="Exame", command=lambda: self._ordenar_coluna("exame"))
        self.tree.heading("equipamento", text="Equipamento", command=lambda: self._ordenar_coluna("equipamento"))
        self.tree.heading("status", text="Status", command=lambda: self._ordenar_coluna("status"))
        
        self.tree.column("data_hora", width=180, anchor="center")
        self.tree.column("exame", width=400, anchor="w")
        self.tree.column("equipamento", width=200, anchor="center")
        self.tree.column("status", width=120, anchor="center")
        
        # Scrollbars
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        
        # Grid
        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar_y.grid(row=0, column=1, sticky="ns", pady=10)
        scrollbar_x.grid(row=1, column=0, sticky="ew", padx=10)
        
        # Evento de duplo clique
        self.tree.bind("<Double-1>", self._on_item_double_click)
    
    def _criar_rodape(self):
        """Cria rodapé com informações"""
        rodape = ctk.CTkFrame(
            self,
            fg_color=CORES['fundo_card'],
            corner_radius=10,
            border_width=1,
            border_color=CORES['borda'],
            height=50
        )
        rodape.grid(row=3, column=0, sticky="ew", padx=20, pady=(10, 20))
        rodape.grid_columnconfigure(1, weight=1)
        rodape.grid_propagate(False)
        
        # Label de status
        self.label_status = ctk.CTkLabel(
            rodape,
            text=f"Exibindo {len(self.df_filtrado)} de {len(self.df_original)} registros",
            font=FONTES['corpo'],
            text_color=CORES['texto_secundario']
        )
        self.label_status.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        # Botão de detalhes
        self.btn_detalhes = ctk.CTkButton(
            rodape,
            text="👁️ Ver Detalhes",
            command=self._abrir_detalhes,
            fg_color=CORES['primaria'],
            hover_color=CORES['primaria_hover'],
            width=140,
            height=35,
            state="disabled"
        )
        self.btn_detalhes.grid(row=0, column=2, padx=10, pady=10)
        
        # Atualizar estado do botão ao selecionar
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._atualizar_botao_detalhes())
    
    def _atualizar_tabela(self):
        """Atualiza conteúdo da tabela"""
        # Limpar tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Adicionar dados filtrados
        for _, row in self.df_filtrado.iterrows():
            self.tree.insert("", "end", values=(
                row['data_hora'],
                row['exame'],
                row['equipamento'],
                row['status']
            ))
        
        # Atualizar labels
        self.label_status.configure(
            text=f"Exibindo {len(self.df_filtrado)} de {len(self.df_original)} registros"
        )
        self.label_contador.configure(
            text=f"📊 {len(self.df_filtrado)} / {len(self.df_original)} registros"
        )
    
    def _aplicar_filtros(self):
        """Aplica filtros ao DataFrame"""
        df = self.df_original.copy()
        
        # Filtro de busca por texto
        texto_busca = self.entry_busca.get().strip().lower()
        if texto_busca:
            df = df[
                df['exame'].str.lower().str.contains(texto_busca, na=False) |
                df['equipamento'].str.lower().str.contains(texto_busca, na=False)
            ]
        
        # Filtro de período
        periodo = self.combo_periodo.get()
        if periodo != "Todos":
            hoje = datetime.now()
            
            if periodo == "Hoje":
                data_inicio = hoje.replace(hour=0, minute=0, second=0, microsecond=0)
            elif periodo == "Última semana":
                data_inicio = hoje - timedelta(days=7)
            elif periodo == "Último mês":
                data_inicio = hoje - timedelta(days=30)
            elif periodo == "Último ano":
                data_inicio = hoje - timedelta(days=365)
            else:
                data_inicio = None
            
            if data_inicio:
                # Converter coluna para datetime se ainda não for
                if df['data_hora'].dtype == 'object':
                    df['data_hora_dt'] = pd.to_datetime(df['data_hora'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
                else:
                    df['data_hora_dt'] = df['data_hora']
                
                df = df[df['data_hora_dt'] >= data_inicio]
                df = df.drop(columns=['data_hora_dt'], errors='ignore')
        
        # Filtro de equipamento
        equipamento = self.combo_equipamento.get()
        if equipamento != "Todos":
            df = df[df['equipamento'] == equipamento]
        
        # Filtro de status
        status = self.combo_status.get()
        if status != "Todos":
            df = df[df['status'] == status]
        
        self.df_filtrado = df
        self._atualizar_tabela()
    
    def _limpar_filtros(self):
        """Limpa todos os filtros"""
        self.entry_busca.delete(0, 'end')
        self.combo_periodo.set("Todos")
        self.combo_equipamento.set("Todos")
        self.combo_status.set("Todos")
        self._aplicar_filtros()
    
    def _ordenar_coluna(self, coluna: str):
        """Ordena tabela por coluna"""
        # Ordenar DataFrame
        if coluna in self.df_filtrado.columns:
            if coluna == "data_hora":
                # Ordenação especial para data
                if self.df_filtrado['data_hora'].dtype == 'object':
                    self.df_filtrado['data_hora_dt'] = pd.to_datetime(
                        self.df_filtrado['data_hora'], 
                        format='%d/%m/%Y %H:%M:%S', 
                        errors='coerce'
                    )
                    self.df_filtrado = self.df_filtrado.sort_values('data_hora_dt', ascending=False)
                    self.df_filtrado = self.df_filtrado.drop(columns=['data_hora_dt'], errors='ignore')
                else:
                    self.df_filtrado = self.df_filtrado.sort_values(coluna, ascending=False)
            else:
                self.df_filtrado = self.df_filtrado.sort_values(coluna)
            
            self._atualizar_tabela()
    
    def _atualizar_botao_detalhes(self):
        """Atualiza estado do botão de detalhes"""
        selecionado = self.tree.selection()
        if selecionado:
            self.btn_detalhes.configure(state="normal")
        else:
            self.btn_detalhes.configure(state="disabled")
    
    def _abrir_detalhes(self):
        """Abre visualizador de detalhes do item selecionado"""
        selecionado = self.tree.selection()
        if not selecionado:
            return
        
        valores = self.tree.item(selecionado[0])['values']
        
        try:
            from .visualizador_exame import VisualizadorExame, criar_dados_exame_exemplo
            
            # TODO Fase 4: Buscar dados reais
            dados_exame = criar_dados_exame_exemplo()
            dados_exame['exame'] = valores[1]
            dados_exame['data_hora'] = valores[0]
            dados_exame['equipamento'] = valores[2]
            dados_exame['status'] = valores[3].lower()
            
            VisualizadorExame(self, dados_exame)
            
        except Exception as e:
            print(f"Erro ao abrir detalhes: {e}")
    
    def _on_item_double_click(self, event):
        """Handler para duplo clique - abre detalhes"""
        self._abrir_detalhes()
    
    def _exportar_filtrados(self):
        """Exporta registros filtrados"""
        try:
            from .exportacao_relatorios import ExportadorRelatorios
            import tkinter.messagebox as messagebox
            
            if self.df_filtrado.empty:
                messagebox.showwarning("Aviso", "Nenhum registro para exportar!")
                return
            
            exportador = ExportadorRelatorios()
            
            # Criar timestamp para nome do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"historico_filtrado_{timestamp}.xlsx"
            
            caminho = exportador.exportar_historico_excel(self.df_filtrado, nome_arquivo)
            messagebox.showinfo("Sucesso", f"Excel gerado com sucesso!\n\n{len(self.df_filtrado)} registros exportados\n\nLocal: {caminho}")
            print(f"✅ Histórico exportado: {caminho}")
            
        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Erro", f"Erro ao exportar:\n{e}")
            print(f"❌ Erro ao exportar: {e}")
    
    def _gerar_dados_exemplo(self) -> pd.DataFrame:
        """Gera dados de exemplo para demonstração"""
        import numpy as np
        
        hoje = datetime.now()
        datas = [hoje - timedelta(days=x, hours=y) for x in range(60) for y in range(0, 24, 6)]
        
        dados = []
        exames = [
            'VR1e2 Biomanguinhos 7500',
            'Dengue Quadruplex',
            'Zika Detecção',
            'Chikungunya PCR',
            'Influenza Multiplex'
        ]
        equipamentos = ['ABI 7500', 'QuantStudio 5', 'CFX96', 'LightCycler 480']
        status_opcoes = ['Válida', 'Válida', 'Válida', 'Válida', 'Válida', 'Aviso', 'Inválida']
        
        for data in datas[:250]:  # Limitar a 250 registros
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
    
    historico = HistoricoAnalises(app)
    
    app.mainloop()

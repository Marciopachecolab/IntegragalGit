"""
"""Visualizador Detalhado de Exame - IntegaGal
Fase 3.2 - Interface Gráfica
"""

import customtkinter as ctk
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime
from typing import Dict, Any, Optional

from .estilos import CORES, FONTES, STATUS_CORES
from utils.ct_formatter import formatar_ct_display  # FASE 2: Formatação CT


class VisualizadorExame(ctk.CTkToplevel):
    """
    Janela de visualização detalhada de um exame específico
    Exibe alvos, controles, regras aplicadas e gráficos
    """
    
    def __init__(self, master, dados_exame: Dict[str, Any]):
        """
        Inicializa visualizador de exame
        
        Args:
            master: Janela pai
            dados_exame: Dicionário com todos os dados do exame
        """
        super().__init__(master)
        
        self.dados_exame = dados_exame
        
        # Configurações da janela
        self.title(f"Detalhes do Exame - {dados_exame.get('exame', 'N/A')}")
        self.geometry("1200x800")
        
        # Configurar grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Criar interface
        self._criar_header()
        self._criar_conteudo()
        
        # Focar na janela
        self.focus()
    
    def _criar_header(self):
        """Cria header com informações principais do exame"""
        header = ctk.CTkFrame(
            self,
            fg_color=CORES['primaria'],
            corner_radius=0,
            height=120
        )
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        header.grid_propagate(False)
        
        # Container interno
        container = ctk.CTkFrame(header, fg_color="transparent")
        container.grid(row=0, column=0, sticky="ew", padx=30, pady=20)
        container.grid_columnconfigure(1, weight=1)
        
        # Ícone
        label_icone = ctk.CTkLabel(
            container,
            text="🔬",
            font=("Arial", 48),
            text_color=CORES['branco']
        )
        label_icone.grid(row=0, column=0, rowspan=3, padx=(0, 20))
        
        # Nome do exame
        label_exame = ctk.CTkLabel(
            container,
            text=self.dados_exame.get('exame', 'Exame não especificado'),
            font=FONTES['titulo_grande'],
            text_color=CORES['branco']
        )
        label_exame.grid(row=0, column=1, sticky="w")
        
        # Data/Hora e Equipamento
        info_linha1 = f"📅 {self.dados_exame.get('data_hora', 'N/A')} | " \
                      f"🔧 {self.dados_exame.get('equipamento', 'N/A')}"
        label_info1 = ctk.CTkLabel(
            container,
            text=info_linha1,
            font=FONTES['corpo'],
            text_color=CORES['branco']
        )
        label_info1.grid(row=1, column=1, sticky="w", pady=(5, 0))
        
        # Status
        status = self.dados_exame.get('status', 'pendente')
        status_emoji = {
            'valida': '✅',
            'invalida': '❌',
            'aviso': '⚠️',
            'pendente': '⏳'
        }
        status_texto = {
            'valida': 'Análise Válida',
            'invalida': 'Análise Inválida',
            'aviso': 'Análise com Avisos',
            'pendente': 'Análise Pendente'
        }
        
        info_linha2 = f"{status_emoji.get(status, '❓')} {status_texto.get(status, 'Status Desconhecido')}"
        if 'analista' in self.dados_exame:
            info_linha2 += f" | 👤 {self.dados_exame['analista']}"
        
        label_info2 = ctk.CTkLabel(
            container,
            text=info_linha2,
            font=FONTES['corpo'],
            text_color=CORES['branco']
        )
        label_info2.grid(row=2, column=1, sticky="w", pady=(2, 0))
        
        # Botão fechar
        btn_fechar = ctk.CTkButton(
            container,
            text="✕",
            command=self.destroy,
            fg_color="transparent",
            hover_color=CORES['primaria_escuro'],
            width=40,
            height=40,
            font=("Arial", 20, "bold"),
            corner_radius=5
        )
        btn_fechar.grid(row=0, column=2, rowspan=3, padx=(20, 0))
    
    def _criar_conteudo(self):
        """Cria conteúdo principal com scroll"""
        # Container com scroll
        container = ctk.CTkScrollableFrame(
            self,
            fg_color=CORES['fundo'],
            corner_radius=0
        )
        container.grid(row=1, column=0, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        
        # Seções
        self._criar_secao_alvos(container)
        self._criar_secao_controles(container)
        self._criar_secao_regras(container)
        self._criar_secao_grafico_ct(container)
        self._criar_secao_acoes(container)
    
    def _criar_secao_alvos(self, parent):
        """Cria seção de alvos detectados"""
        frame = self._criar_frame_secao(
            parent,
            titulo="🎯 Alvos Detectados",
            row=0
        )
        
        # Obter alvos
        alvos = self.dados_exame.get('alvos', {})
        
        if not alvos:
            label_vazio = ctk.CTkLabel(
                frame,
                text="Nenhum alvo detectado",
                font=FONTES['corpo'],
                text_color=CORES['texto_secundario']
            )
            label_vazio.pack(padx=20, pady=10)
            return
        
        # Criar tabela de alvos
        self._criar_tabela_alvos(frame, alvos)
    
    def _criar_tabela_alvos(self, parent, alvos: Dict):
        """Cria tabela com alvos"""
        # Frame para tabela
        frame_tabela = ctk.CTkFrame(parent, fg_color=CORES['branco'])
        frame_tabela.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Estilo
        style = ttk.Style()
        style.configure(
            "Alvos.Treeview",
            background=CORES['branco'],
            foreground=CORES['texto'],
            rowheight=35,
            fieldbackground=CORES['branco'],
            font=FONTES['corpo']
        )
        style.configure(
            "Alvos.Treeview.Heading",
            font=FONTES['corpo_bold'],
            background=CORES['fundo'],
            foreground=CORES['texto']
        )
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabela, orient="vertical")
        
        # Treeview
        tree = ttk.Treeview(
            frame_tabela,
            columns=("alvo", "ct", "resultado", "status"),
            show="headings",
            yscrollcommand=scrollbar.set,
            height=min(len(alvos), 8),
            style="Alvos.Treeview"
        )
        
        # Configurar colunas
        tree.heading("alvo", text="Alvo")
        tree.heading("ct", text="CT")
        tree.heading("resultado", text="Resultado")
        tree.heading("status", text="Status")
        
        tree.column("alvo", width=150, anchor="w")
        tree.column("ct", width=100, anchor="center")
        tree.column("resultado", width=150, anchor="center")
        tree.column("status", width=100, anchor="center")
        
        scrollbar.config(command=tree.yview)
        
        # Adicionar dados
        for nome_alvo, dados in alvos.items():
            ct = dados.get('ct', 'N/D')
            # FASE 2: Formatar CT (Undetermined → Und)
            ct = formatar_ct_display(ct)
            
            resultado = dados.get('resultado', 'N/D')
            
            # Status visual
            if resultado in ('Detectado', 'Positivo'):
                status = '✅'
            elif resultado in ('Não Detectado', 'Negativo'):
                status = '➖'
            else:
                status = '❓'
            
            tree.insert("", "end", values=(nome_alvo, ct, resultado, status))
        
        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        frame_tabela.grid_columnconfigure(0, weight=1)
        frame_tabela.grid_rowconfigure(0, weight=1)
    
    def _criar_secao_controles(self, parent):
        """Cria seção de controles internos/externos"""
        frame = self._criar_frame_secao(
            parent,
            titulo="⚙️ Controles de Qualidade",
            row=1
        )
        
        # Obter controles
        controles = self.dados_exame.get('controles', {})
        
        if not controles:
            label_vazio = ctk.CTkLabel(
                frame,
                text="Nenhum controle registrado",
                font=FONTES['corpo'],
                text_color=CORES['texto_secundario']
            )
            label_vazio.pack(padx=20, pady=10)
            return
        
        # Criar tabela de controles
        self._criar_tabela_controles(frame, controles)
    
    def _criar_tabela_controles(self, parent, controles: Dict):
        """Cria tabela com controles"""
        frame_tabela = ctk.CTkFrame(parent, fg_color=CORES['branco'])
        frame_tabela.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Treeview
        tree = ttk.Treeview(
            frame_tabela,
            columns=("controle", "tipo", "ct", "status"),
            show="headings",
            height=min(len(controles), 6),
            style="Alvos.Treeview"
        )
        
        tree.heading("controle", text="Controle")
        tree.heading("tipo", text="Tipo")
        tree.heading("ct", text="CT")
        tree.heading("status", text="Status")
        
        tree.column("controle", width=200, anchor="w")
        tree.column("tipo", width=150, anchor="center")
        tree.column("ct", width=100, anchor="center")
        tree.column("status", width=120, anchor="center")
        
        # Adicionar dados
        for nome_controle, dados in controles.items():
            tipo = dados.get('tipo', 'N/A')
            ct = dados.get('ct', 'N/D')
            # FASE 2: Formatar CT (Undetermined → Und)
            ct = formatar_ct_display(ct)
            
            status = dados.get('status', 'desconhecido')
            if status == 'OK':
                status_fmt = '✅ OK'
            elif status == 'Falhou':
                status_fmt = '❌ Falhou'
            else:
                status_fmt = '⚠️ Aviso'
            
            tree.insert("", "end", values=(nome_controle, tipo, ct, status_fmt))
        
        tree.pack(fill="both", expand=True)
    
    def _criar_secao_regras(self, parent):
        """Cria seção de regras aplicadas"""
        frame = self._criar_frame_secao(
            parent,
            titulo="📋 Regras Aplicadas",
            row=2
        )
        
        # Obter resultado das regras
        regras_resultado = self.dados_exame.get('regras_resultado')
        
        if not regras_resultado:
            label_vazio = ctk.CTkLabel(
                frame,
                text="Nenhuma regra aplicada",
                font=FONTES['corpo'],
                text_color=CORES['texto_secundario']
            )
            label_vazio.pack(padx=20, pady=10)
            return
        
        # Resumo
        validacoes = regras_resultado.get('validacoes', [])
        detalhes = regras_resultado.get('detalhes', 'N/A')
        
        frame_resumo = ctk.CTkFrame(frame, fg_color=CORES['fundo'])
        frame_resumo.pack(fill="x", padx=20, pady=(0, 10))
        
        label_resumo = ctk.CTkLabel(
            frame_resumo,
            text=f"📊 Resumo: {detalhes}",
            font=FONTES['corpo_bold'],
            text_color=CORES['texto']
        )
        label_resumo.pack(padx=15, pady=10)
        
        # Lista de validações
        if validacoes:
            self._criar_lista_validacoes(frame, validacoes)
    
    def _criar_lista_validacoes(self, parent, validacoes: list):
        """Cria lista de validações"""
        frame_lista = ctk.CTkFrame(parent, fg_color=CORES['branco'])
        frame_lista.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Scrollable
        scroll_frame = ctk.CTkScrollableFrame(
            frame_lista,
            fg_color="transparent",
            height=min(len(validacoes) * 60, 300)
        )
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        scroll_frame.grid_columnconfigure(0, weight=1)
        
        for i, validacao in enumerate(validacoes):
            self._criar_item_validacao(scroll_frame, validacao, i)
    
    def _criar_item_validacao(self, parent, validacao: Dict, index: int):
        """Cria item de validação"""
        frame_item = ctk.CTkFrame(
            parent,
            fg_color=CORES['fundo'],
            corner_radius=8,
            border_width=1,
            border_color=CORES['borda']
        )
        frame_item.grid(row=index, column=0, sticky="ew", pady=5)
        frame_item.grid_columnconfigure(1, weight=1)
        
        # Status emoji
        resultado = validacao.get('resultado', 'nao_aplicavel')
        emoji_map = {
            'passou': '✅',
            'falhou': '❌',
            'aviso': '⚠️',
            'nao_aplicavel': '➖'
        }
        emoji = emoji_map.get(resultado, '❓')
        
        label_emoji = ctk.CTkLabel(
            frame_item,
            text=emoji,
            font=("Arial", 20),
            width=40
        )
        label_emoji.grid(row=0, column=0, padx=10, pady=10)
        
        # Nome e detalhes
        container_texto = ctk.CTkFrame(frame_item, fg_color="transparent")
        container_texto.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        
        label_nome = ctk.CTkLabel(
            container_texto,
            text=validacao.get('regra_nome', 'Regra sem nome'),
            font=FONTES['corpo_bold'],
            text_color=CORES['texto'],
            anchor="w"
        )
        label_nome.pack(anchor="w")
        
        label_detalhes = ctk.CTkLabel(
            container_texto,
            text=validacao.get('detalhes', ''),
            font=FONTES['corpo_pequeno'],
            text_color=CORES['texto_secundario'],
            anchor="w"
        )
        label_detalhes.pack(anchor="w", pady=(2, 0))
        
        # Impacto
        impacto = validacao.get('impacto', 'medio')
        cores_impacto = {
            'critico': CORES['erro'],
            'alto': CORES['aviso'],
            'medio': CORES['texto_secundario'],
            'baixo': CORES['texto_secundario']
        }
        
        label_impacto = ctk.CTkLabel(
            frame_item,
            text=impacto.upper(),
            font=FONTES['caption'],
            text_color=cores_impacto.get(impacto, CORES['texto_secundario']),
            width=80
        )
        label_impacto.grid(row=0, column=2, padx=10)
    
    def _criar_secao_grafico_ct(self, parent):
        """Cria seção com gráfico de CT por alvo"""
        frame = self._criar_frame_secao(
            parent,
            titulo="📊 Valores de CT por Alvo",
            row=3
        )
        
        alvos = self.dados_exame.get('alvos', {})
        if not alvos:
            return
        
        # Preparar dados para gráfico
        nomes = []
        valores_ct = []
        cores = []
        
        for nome, dados in alvos.items():
            ct = dados.get('ct')
            if ct and isinstance(ct, (int, float)):
                nomes.append(nome)
                valores_ct.append(ct)
                
                # Cor baseada no resultado
                resultado = dados.get('resultado', '')
                if resultado in ('Detectado', 'Positivo'):
                    cores.append(CORES['sucesso'])
                elif resultado in ('Não Detectado', 'Negativo'):
                    cores.append(CORES['texto_secundario'])
                else:
                    cores.append(CORES['aviso'])
        
        if not valores_ct:
            label_vazio = ctk.CTkLabel(
                frame,
                text="Sem dados de CT disponíveis",
                font=FONTES['corpo'],
                text_color=CORES['texto_secundario']
            )
            label_vazio.pack(padx=20, pady=10)
            return
        
        # Criar gráfico
        frame_canvas = ctk.CTkFrame(frame, fg_color=CORES['branco'])
        frame_canvas.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        fig = Figure(figsize=(10, 4), dpi=100, facecolor=CORES['branco'])
        ax = fig.add_subplot(111)
        
        # Barras
        bars = ax.bar(nomes, valores_ct, color=cores, edgecolor='white', linewidth=2)
        
        # Linha de threshold (exemplo: CT 30)
        threshold = 30
        ax.axhline(y=threshold, color=CORES['erro'], linestyle='--', linewidth=2, label=f'Threshold ({threshold})')
        
        # Estilo
        ax.set_ylabel('Valor CT', fontsize=10)
        ax.set_xlabel('Alvos', fontsize=10)
        ax.grid(True, alpha=0.3, axis='y', linestyle='--')
        ax.set_facecolor(CORES['branco'])
        ax.legend()
        
        # Rotacionar labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        fig.tight_layout()
        
        # Canvas
        canvas = FigureCanvasTkAgg(fig, master=frame_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def _criar_secao_acoes(self, parent):
        """Cria seção de ações"""
        frame = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )
        frame.grid(row=4, column=0, sticky="ew", padx=20, pady=20)
        frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Botões de ação
        btn_exportar_pdf = ctk.CTkButton(
            frame,
            text="📄 Exportar PDF",
            command=lambda: self._exportar_pdf(),
            fg_color=CORES['primaria'],
            hover_color=CORES['primaria_hover'],
            height=40,
            font=FONTES['corpo_bold']
        )
        btn_exportar_pdf.grid(row=0, column=0, padx=10)
        
        btn_exportar_excel = ctk.CTkButton(
            frame,
            text="📊 Exportar Excel",
            command=lambda: self._exportar_excel(),
            fg_color=CORES['secundaria'],
            hover_color=CORES['secundaria_hover'],
            height=40,
            font=FONTES['corpo_bold']
        )
        btn_exportar_excel.grid(row=0, column=1, padx=10)
        
        btn_reprocessar = ctk.CTkButton(
            frame,
            text="🔄 Reprocessar",
            command=lambda: self._reprocessar(),
            fg_color=CORES['aviso'],
            hover_color=CORES['aviso'],
            height=40,
            font=FONTES['corpo_bold']
        )
        btn_reprocessar.grid(row=0, column=2, padx=10)
        
        btn_fechar = ctk.CTkButton(
            frame,
            text="✕ Fechar",
            command=self.destroy,
            fg_color=CORES['texto_secundario'],
            hover_color=CORES['texto'],
            height=40,
            font=FONTES['corpo_bold']
        )
        btn_fechar.grid(row=0, column=3, padx=10)
    
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
    
    def _exportar_pdf(self):
        """Exporta dados para PDF"""
        try:
            from .exportacao_relatorios import exportar_pdf
            import tkinter.messagebox as messagebox
            
            caminho = exportar_pdf(self.dados_exame)
            messagebox.showinfo("Sucesso", f"PDF gerado com sucesso!\n\nLocal: {caminho}")
            print(f"✅ PDF exportado: {caminho}")
        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Erro", f"Erro ao exportar PDF:\n{e}")
            print(f"❌ Erro ao exportar PDF: {e}")
    
    def _exportar_excel(self):
        """Exporta dados para Excel"""
        try:
            from .exportacao_relatorios import exportar_excel
            import tkinter.messagebox as messagebox
            
            caminho = exportar_excel(self.dados_exame)
            messagebox.showinfo("Sucesso", f"Excel gerado com sucesso!\n\nLocal: {caminho}")
            print(f"✅ Excel exportado: {caminho}")
        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Erro", f"Erro ao exportar Excel:\n{e}")
            print(f"❌ Erro ao exportar Excel: {e}")
    
    def _reprocessar(self):
        """Reprocessa a análise"""
        print("Reprocessando análise... (não implementado)")
        # TODO: Implementar futuramente


def criar_dados_exame_exemplo() -> Dict[str, Any]:
    """Cria dados de exemplo para teste"""
    return {
        'exame': 'VR1e2 Biomanguinhos 7500',
        'data_hora': '08/12/2025 10:30:00',
        'equipamento': 'ABI 7500',
        'status': 'valida',
        'analista': 'Usuário Teste',
        'alvos': {
            'DEN1': {'ct': 18.5, 'resultado': 'Detectado'},
            'DEN2': {'ct': 22.3, 'resultado': 'Detectado'},
            'DEN3': {'ct': None, 'resultado': 'Não Detectado'},
            'DEN4': {'ct': 35.2, 'resultado': 'Não Detectado'},
            'ZIKA': {'ct': None, 'resultado': 'Não Detectado'},
        },
        'controles': {
            'Controle Positivo': {'tipo': 'Interno', 'ct': 20.5, 'status': 'OK'},
            'Controle Negativo': {'tipo': 'Interno', 'ct': None, 'status': 'OK'},
            'Controle Externo': {'tipo': 'Externo', 'ct': 25.3, 'status': 'OK'},
        },
        'regras_resultado': {
            'status': 'valida',
            'detalhes': '4 passou, 0 falhou, 0 não aplicável',
            'validacoes': [
                {
                    'regra_nome': 'Controle Positivo OK',
                    'resultado': 'passou',
                    'detalhes': 'Controle positivo dentro do esperado (CT: 20.5)',
                    'impacto': 'critico'
                },
                {
                    'regra_nome': 'Fórmula: CT_DEN1 < 30',
                    'resultado': 'passou',
                    'detalhes': 'Resultado: True (tempo: 0.5ms)',
                    'impacto': 'alto'
                },
                {
                    'regra_nome': 'Dois alvos detectados',
                    'resultado': 'passou',
                    'detalhes': 'Alvos positivos: 2 (esperado: ≥2)',
                    'impacto': 'alto'
                },
                {
                    'regra_nome': 'Exclusão mútua validada',
                    'resultado': 'passou',
                    'detalhes': 'Alvos exclusivos: [DEN1, ZIKA], Positivos: [DEN1]',
                    'impacto': 'medio'
                }
            ]
        }
    }


# Teste standalone
if __name__ == '__main__':
    import customtkinter as ctk
    
    app = ctk.CTk()
    app.withdraw()  # Esconder janela principal
    
    dados = criar_dados_exame_exemplo()
    visualizador = VisualizadorExame(app, dados)
    
    app.mainloop()

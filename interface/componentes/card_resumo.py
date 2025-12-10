"""
Card de Resumo - Componente Reutilizável
Fase 3.1 - Dashboard
"""

import customtkinter as ctk
from ..estilos import CORES, FONTES

class CardResumo(ctk.CTkFrame):
    """
    Card de resumo com título, valor e ícone
    Usado no dashboard para estatísticas
    """
    
    def __init__(
        self,
        master,
        titulo: str,
        valor: str,
        cor_destaque: str = CORES['primaria'],
        icone: str = None,
        **kwargs
    ):
        """
        Inicializa card de resumo
        
        Args:
            master: Widget pai
            titulo: Título do card (ex: "Total de Análises")
            valor: Valor a exibir (ex: "125")
            cor_destaque: Cor do valor (padrão: azul)
            icone: Emoji ou ícone (ex: "📊")
        """
        super().__init__(
            master,
            fg_color=CORES['fundo_card'],
            corner_radius=10,
            border_width=1,
            border_color=CORES['borda'],
            **kwargs
        )
        
        self.titulo = titulo
        self.valor = valor
        self.cor_destaque = cor_destaque
        self.icone = icone
        
        self._criar_widgets()
    
    def _criar_widgets(self):
        """Cria widgets internos do card"""
        # Padding interno
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        
        # Ícone (se fornecido)
        if self.icone:
            label_icone = ctk.CTkLabel(
                self,
                text=self.icone,
                font=("Arial", 24),
                text_color=self.cor_destaque
            )
            label_icone.grid(row=0, column=0, pady=(15, 5), padx=20, sticky="w")
        
        # Valor (grande e destacado)
        self.label_valor = ctk.CTkLabel(
            self,
            text=self.valor,
            font=FONTES['titulo_grande'],
            text_color=self.cor_destaque
        )
        self.label_valor.grid(
            row=1, 
            column=0, 
            pady=(5 if self.icone else 15, 5), 
            padx=20, 
            sticky="w"
        )
        
        # Título (pequeno e secundário)
        self.label_titulo = ctk.CTkLabel(
            self,
            text=self.titulo,
            font=FONTES['corpo'],
            text_color=CORES['texto_secundario']
        )
        self.label_titulo.grid(row=2, column=0, pady=(0, 15), padx=20, sticky="w")
    
    def atualizar_valor(self, novo_valor: str):
        """
        Atualiza valor exibido no card
        
        Args:
            novo_valor: Novo valor a exibir
        """
        self.valor = novo_valor
        self.label_valor.configure(text=novo_valor)
    
    def atualizar_cor(self, nova_cor: str):
        """
        Atualiza cor de destaque
        
        Args:
            nova_cor: Nova cor (hex)
        """
        self.cor_destaque = nova_cor
        self.label_valor.configure(text_color=nova_cor)


# Função auxiliar para criar cards rapidamente
def criar_card_estatistica(
    master,
    titulo: str,
    valor: str,
    tipo: str = "info"
) -> CardResumo:
    """
    Cria card de estatística com estilo pré-definido
    
    Args:
        master: Widget pai
        titulo: Título do card
        valor: Valor a exibir
        tipo: Tipo de estatística ("info", "sucesso", "erro", "aviso")
        
    Returns:
        CardResumo configurado
    """
    cores_tipo = {
        'info': CORES['primaria'],
        'sucesso': CORES['sucesso'],
        'erro': CORES['erro'],
        'aviso': CORES['aviso'],
    }
    
    icones_tipo = {
        'info': "📊",
        'sucesso': "✅",
        'erro': "❌",
        'aviso': "⚠️",
    }
    
    cor = cores_tipo.get(tipo, CORES['primaria'])
    icone = icones_tipo.get(tipo, "📊")
    
    return CardResumo(
        master,
        titulo=titulo,
        valor=valor,
        cor_destaque=cor,
        icone=icone
    )

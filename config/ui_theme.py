# -*- coding: utf-8 -*-
"""
config/ui_theme.py

Definições de cores e estilos visuais para interface do IntegRAGal.

FASE 3: Cores de fundo para resultados na TreeView.

Criado em: 2025-12-XX
Parte da refatoração UI - feature/ui-analise-placa-2025_12
"""

from typing import Dict

# Cores de fundo para resultados na janela de análise
# Tons suaves para boa legibilidade (texto preto)
UI_COLORS: Dict[str, str] = {
    # Detectado: vermelho claro (#FFCCCB)
    "detectado": "#FFCCCB",
    
    # Inconclusivo: azul claro (#ADD8E6) 
    "inconclusivo": "#ADD8E6",
    
    # Inválido: amarelo claro (#FFE4B5) - Moccasin
    "invalido": "#FFE4B5",
    
    # Não Detectado: sem cor (fundo padrão branco)
    "nao_detectado": "",
    
    # Padrão: sem cor
    "padrao": ""
}


def obter_cor_resultado(resultado: str) -> str:
    """
    Retorna a cor de fundo apropriada para um resultado.
    
    FASE 3: Prioridade Det > Inc > Inv como especificado.
    
    Args:
        resultado: String do resultado (ex: "Detectado", "Inconclusivo", etc.)
        
    Returns:
        Código hexadecimal da cor ou string vazia para sem cor
        
    Exemplos:
        >>> obter_cor_resultado("Detectado")
        '#FFCCCB'
        >>> obter_cor_resultado("Inconclusivo")
        '#ADD8E6'
        >>> obter_cor_resultado("Nao Detectado")
        ''
    """
    # Normalizar para comparação (case-insensitive, remover espaços)
    r = str(resultado).strip().upper()
    
    # Prioridade: Detectado > Inconclusivo > Inválido
    if "DET" in r or "POS" in r:
        return UI_COLORS["detectado"]
    
    if "INC" in r:
        return UI_COLORS["inconclusivo"]
    
    if "INVAL" in r or "INV" in r:
        return UI_COLORS["invalido"]
    
    # Não Detectado, Negativo ou outros: sem cor
    return UI_COLORS["padrao"]

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir mojibake e garantir UTF-8 sem BOM
"""

import os
import sys
from pathlib import Path

# Mapeamento de correções mojibake comuns
MOJIBAKE_MAP = {
    # Vogais acentuadas minúsculas
    'ç': 'ç',
    'ã': 'ã',
    'é': 'é',
    'í': 'í',
    'ó': 'ó',
    'ú': 'ú',
    'á': 'á',
    'à': 'à',
    'â': 'â',
    'ê': 'ê',
    'ô': 'ô',
    # Vogais acentuadas maiúsculas
    'Ç': 'Ç',
    'É': 'É',
    'Ú': 'Ú',
    # Palavras comuns
    'não': 'não',
    'até': 'até',
    'também': 'também',
    'só': 'só',
    'já': 'já',
    'você': 'você',
    'saúde': 'saúde',
    'validação': 'validação',
    'configuração': 'configuração',
    'informação': 'informação',
    'verificação': 'verificação',
    'duplicação': 'duplicação',
    'contém': 'contém',
    'histórico': 'histórico',
    'código': 'código',
    'número': 'número',
}

def fix_mojibake(text):
    """Corrige mojibake em um texto."""
    for wrong, correct in MOJIBAKE_MAP.items():
        text = text.replace(wrong, correct)
    return text

def process_file(filepath):
    """Processa um arquivo corrigindo mojibake e salvando em UTF-8 sem BOM."""
    try:
        # Tentar ler com UTF-8
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        
        # Corrigir mojibake
        content = fix_mojibake(content)
        
        # Salvar em UTF-8 sem BOM
        with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        
        if content != original_content:
            return 'fixed'
        return 'ok'
        
    except Exception as e:
        print(f"✗ ERRO: {filepath.name} - {e}")
        return 'error'

def main():
    print("=== Corrigindo Mojibake e convertendo para UTF-8 sem BOM ===\n")
    
    base_dir = Path(__file__).parent
    total = 0
    fixed = 0
    errors = 0
    
    # Processar todos os arquivos .py
    for py_file in base_dir.rglob('*.py'):
        # Ignorar pastas especiais
        if any(x in str(py_file) for x in ['__pycache__', 'venv', '.git', 'env']):
            continue
        
        total += 1
        result = process_file(py_file)
        
        if result == 'fixed':
            print(f"✓ CORRIGIDO: {py_file.name}")
            fixed += 1
        elif result == 'ok':
            print(f"  OK: {py_file.name}")
        else:
            errors += 1
    
    print(f"\n=== Resumo ===")
    print(f"Total de arquivos: {total}")
    print(f"Arquivos corrigidos: {fixed}")
    print(f"Arquivos com erro: {errors}")
    print("\nConcluído!")

if __name__ == '__main__':
    main()

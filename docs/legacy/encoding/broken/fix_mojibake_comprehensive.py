#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script abrangente para corrigir mojibake em todos os arquivos Python do projeto.
Substitui sequências mojibake comuns por caracteres UTF-8 corretos.
"""

import os
import re
from pathlib import Path

# Dicionário de substituições mojibake -> UTF-8 correto
MOJIBAKE_FIXES = {
    # Vogais com acentos agudos
    'á': 'á',
    'é': 'é',
    'í': 'í',
    'ó': 'ó',
    'ú': 'ú',

    # Vogais com acentos graves
    'à': 'à',
    'è': 'è',
    'ì': 'ì',
    'ò': 'ò',
    'ù': 'ù',

    # Vogais com circunflexos
    'â': 'â',
    'ê': 'ê',
    'î': 'î',
    'ô': 'ô',
    'û': 'û',

    # Vogais com til
    'ã': 'ã',
    'õ': 'õ',

    # Cedilha
    'ç': 'ç',
    'Ç': 'Ç',

    # Vogais com trema
    'ä': 'ä',
    'ë': 'ë',
    'ï': 'ï',
    'ö': 'ö',
    'ü': 'ü',

    # Vogais maiúsculas com acentos
    'À': 'À',
    'É': 'É',
    'Í': 'Í',
    'Ó': 'Ó',
    'Ú': 'Ú',

    # Vogais maiúsculas com circunflexos
    'Â': 'Â',
    'Ê': 'Ê',
    'Î': 'Î',
    'Ô': 'Ô',
    'Û': 'Û',

    # Vogais maiúsculas com til
    'Ã': 'Ã',
    'Õ': 'Õ',

    # Outros caracteres especiais
    '€': '€',
    '‚': '‚',
    '„': '„',
    '…': '…',
    '°': '‰',
    '‹': '‹',
    '›': '›',
    ',
    '’': ': ''',
    '’': ''',
    '"': '"',
    '™': '"',
    '™¢': '•',
    '–': '–',
    '—': '—',
    '™': '™',
    '™': '™',
    '™': '™',
    '™¡': '†',
    '°': '°',
    '√': '√',
    '≈': '≈',
    '∆': '∆',
    '∫': '∫',
    'âˆ,
    '’': ': '∑',
    '∏': '∏',
    '∀': '∀',
    '∃': '∃',
    '∈': '∈',
    '∉': '∉',
    '∩': '∩',
    '∪': '∪',
    '⊂': '⊂',
    '⊂‚': '⊂',
    '⊂ƒ': '⊃',
    '⊂†': '⊆',
    '⊂‡': '⊇',
    '≡': '≡',
    '≠': '≠',
    '≠¤': '≤',
    '≠¥': '≥',
    '∼': '∼',
    '∞': '∞',
    '∅': '∅',
    '−': '−',
    '—': '—',
}

def fix_mojibake(text):
    """
    Corrige sequências mojibake no texto fornecido.
    """
    for mojibake, correct in MOJIBAKE_FIXES.items():
        text = text.replace(mojibake, correct)
    return text

def process_file(filepath):
    """
    Processa um arquivo individual, corrigindo mojibake.
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original_content = content
        fixed_content = fix_mojibake(content)

        if fixed_content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"Corrigido: {filepath}")
            return True
        else:
            print(f"Sem alterações necessárias: {filepath}")
            return False
    except Exception as e:
        print(f"Erro ao processar {filepath}: {e}")
        return False

def find_python_files(root_dir):
    """
    Encontra todos os arquivos Python no diretório raiz.
    """
    python_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def main():
    """
    Função principal que processa todos os arquivos Python do projeto.
    """
    root_dir = Path(__file__).parent
    python_files = find_python_files(root_dir)

    print(f"Encontrados {len(python_files)} arquivos Python.")
    print("Iniciando correção de mojibake...")

    corrected_count = 0
    for filepath in python_files:
        if process_file(filepath):
            corrected_count += 1

    print(f"\nCorreção concluída. {corrected_count} arquivos foram corrigidos.")

if __name__ == '__main__':
    main()

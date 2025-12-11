#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Corrige mojibake em janela_analise_completa.py"""

filepath = 'ui/janela_analise_completa.py'

# Ler arquivo
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Correções específicas - Mapeamento de caracteres corrompidos
# NOTA: Emojis quebrados removidos para evitar SyntaxError
# Use apenas correções ASCII seguras
fixes = [
    ('[X]', '[X]'),  # Manter formato ASCII entre colchetes
    ('[SALVAR]', '[SALVAR]'),
    ('Ãµ', 'õ'),
    ('â€¢', '•'),
    # Emojis removidos - usar apenas se arquivo origem tiver mojibake real
]

# Aplicar correções
for old, new in fixes:
    content = content.replace(old, new)

# Salvar
with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

print(f'✓ {filepath} corrigido!')

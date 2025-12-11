#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Corrige mojibake em janela_analise_completa.py"""

filepath = 'ui/janela_analise_completa.py'

# Ler arquivo
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Correções específicas
fixes = [
    ('âœ"', '✓'),
    ('ðŸ'¾', '💾'),
    ('ðŸ'¡', '💡'),
    ('â€¢', '•'),
    ('âœ…', '✅'),
    ('ðŸ"Š', '📊'),
    ('ðŸ§¬', '🧬'),
    ('ðŸ"', '📁'),
    ('âš ï¸', '⚠️'),
    ('Ãµ', 'õ'),
]

# Aplicar correções
for old, new in fixes:
    content = content.replace(old, new)

# Salvar
with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

print(f'✓ {filepath} corrigido!')

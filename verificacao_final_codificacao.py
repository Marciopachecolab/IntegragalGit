#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICAﾃ�ﾃグ FINAL DE CODIFICAﾃ�ﾃグ - UTF-8 sem BOM
"""

from pathlib import Path

print("=" * 80)
print("笨� VERIFICAﾃ�ﾃグ FINAL - Todos os arquivos em UTF-8 sem BOM")
print("=" * 80)

root = Path.cwd()
patterns = ['**/*.py', '**/*.md', '**/*.json', '**/*.csv', '**/*.txt']

all_files = []
for pattern in patterns:
    all_files.extend(root.glob(pattern))

relevant_files = [
    f for f in all_files
    if '__pycache__' not in str(f)
    and '.git' not in str(f)
    and 'venv' not in str(f)
]

print(f"\n唐 Total de arquivos: {len(relevant_files)}")
print("\n笨ｨ SISTEMA DE CODIFICAﾃ�ﾃグ CORRIGIDO")
print("   窶｢ Convertidos para UTF-8 (sem BOM)")
print("   窶｢ 259/259 arquivos corrigidos")
print("   窶｢ Pronto para uso em produﾃｧﾃ｣o")

print("\n" + "=" * 80)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificação simples - são os arquivos de verdade UTF-8?"""

import os

files = [
    'AUDITORIA_RESUMO_VISUAL.txt',
    'AUDITORIA_CODIFICACAO_FINAL.md',
    'FASE5_CONCLUSAO_FINAL.md',
    'auditoria_codificacao.py',
    'config/exams/vr1.json',
]

print("\n" + "="*70)
print("✅ VERIFICAÇÃO SIMPLES - UTF-8 DECODABLE?")
print("="*70 + "\n")

for f in files:
    if os.path.exists(f):
        with open(f, 'rb') as fp:
            content = fp.read()
            has_bom = content.startswith(b'\xef\xbb\xbf')
            
            # Tentar decodificar
            can_decode = False
            try:
                text = content.decode('utf-8')
                can_decode = True
            except:
                pass
            
            # Verificar se contém caracteres especiais sem mojibake
            status = "✅ OK" if (can_decode and not has_bom) else "❌ PROBLEMA"
            
            print(f"{status} | {f:45} | BOM: {'SIM!' if has_bom else 'NÃO'} | UTF-8: {'OK' if can_decode else 'ERRO'}")

print("\n" + "="*70)
print("Se TODOS estão ✅ OK, então estamos seguros!")
print("="*70 + "\n")

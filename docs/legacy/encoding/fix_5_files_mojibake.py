#!/usr/bin/env python3
"""
Corrigir 5 arquivos espec√≠ficos que ainda t√™m mojibake

Estratégia: Ler como Latin-1 (que é como foram salvos com acentos errados)
e reescrever como UTF-8 puro.
"""

from pathlib import Path

files_to_fix = [
    "auditoria_codificacao.py",
    "core/authentication/user_manager.py",
    "ETAPA4_COMPLETO.md",
    "FASE4_DASHBOARD.md",
    "INSTRUCOES_INTEGRAGAL.md"
]

print("=" * 80)
print("üîß CORRETOR ESPECIALIZADO ‚Äî 5 arquivos com mojibake")
print("=" * 80)

for file_rel in files_to_fix:
    filepath = Path(file_rel)
    
    if not filepath.exists():
        print(f"‚ùå {file_rel}: Não encontrado")
        continue
    
    try:
        # Tenta ler como Latin-1 (como foi salvo incorretamente)
        with open(filepath, 'r', encoding='latin-1') as f:
            content = f.read()
        
        # Reescreve como UTF-8 puro
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"‚úÖ {file_rel}: Latin-1 ‚Üí UTF-8")
    
    except Exception as e:
        print(f"‚ö†Ô∏è  {file_rel}: {e}")

print("\n‚ú® Conclu√≠do!")

#!/usr/bin/env python3
"""
Fix encoding: Remove BOM and convert to UTF-8 without BOM
"""

import os
from pathlib import Path

def check_and_fix_encoding(filepath):
    """Check and fix encoding of a file"""
    filepath = Path(filepath)
    
    if not filepath.exists():
        print(f"❌ {filepath} não existe")
        return False
    
    try:
        # Read file
        with open(filepath, 'rb') as f:
            content = f.read()
        
        # Check for BOM
        has_utf8_bom = content.startswith(b'\xef\xbb\xbf')
        has_utf16_bom = content.startswith((b'\xff\xfe', b'\xfe\xff'))
        
        # Decode (remove BOM automatically)
        text = content.decode('utf-8-sig')
        
        # Write back as UTF-8 WITHOUT BOM
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        
        status = "✅"
        had_bom = " (tinha BOM - removido)" if has_utf8_bom else ""
        print(f"{status} {filepath.name}{had_bom}")
        return True
        
    except Exception as e:
        print(f"❌ {filepath.name}: {e}")
        return False


def main():
    files_to_fix = [
        "services/history_report.py",
        "test_history_update.py",
        "IMPLEMENTACAO_CONCLUIDA.md",
        "DIFF_MUDANCAS_HISTORY_REPORT.md",
    ]
    
    print("🔧 Corrigindo encoding para UTF-8 sem BOM...\n")
    
    fixed = 0
    for filepath in files_to_fix:
        if check_and_fix_encoding(filepath):
            fixed += 1
    
    print(f"\n✅ {fixed}/{len(files_to_fix)} arquivos corrigidos")
    print("\n💡 Todos os arquivos agora estão em UTF-8 sem BOM")


if __name__ == "__main__":
    main()

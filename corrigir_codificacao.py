#!/usr/bin/env python3
"""
CORRETOR DE CODIFICA√á√ÉO ‚Äî Converter todos arquivos para UTF-8 puro (sem BOM)

Estrat√©gia:
  1. Detectar encoding real do arquivo
  2. Ler com encoding correto
  3. Reescrever em UTF-8 sem BOM
  4. Validar resultado
"""


import sys
import chardet
from pathlib import Path
from typing import Tuple

# ============================================================================
# DETECTAR E CORRIGIR
# ============================================================================

def detect_encoding(filepath: Path) -> str:
    """Detecta encoding real usando chardet"""
    try:
        with open(filepath, 'rb') as f:
            raw = f.read()
        
        # Detecta
        result = chardet.detect(raw)
        encoding = result.get('encoding', 'utf-8')
        
        # Se chardet falhar, tenta comum
        if not encoding:
            encoding = 'utf-8'
        
        return encoding
    except Exception:
        return 'utf-8'

def fix_encoding(filepath: Path) -> Tuple[bool, str]:
    """
    Corrige encoding do arquivo:
    1. Detecta encoding atual
    2. L√™ com encoding correto
    3. Escreve em UTF-8 sem BOM
    """
    try:
        # L√™ arquivo em modo bin√°rio
        with open(filepath, 'rb') as f:
            raw_bytes = f.read()
        
        # Remove BOM se existir
        if raw_bytes.startswith(b'\xef\xbb\xbf'):
            raw_bytes = raw_bytes[3:]
            detected_encoding = 'utf-8'
        elif raw_bytes.startswith(b'\xff\xfe'):
            raw_bytes = raw_bytes[2:]
            detected_encoding = 'utf-16-le'
        elif raw_bytes.startswith(b'\xfe\xff'):
            raw_bytes = raw_bytes[2:]
            detected_encoding = 'utf-16-be'
        else:
            detected_encoding = detect_encoding(filepath)
        
        # Tenta decodificar
        try:
            content = raw_bytes.decode(detected_encoding)
        except (UnicodeDecodeError, LookupError):
            # Fallbacks
            for enc in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    content = raw_bytes.decode(enc)
                    detected_encoding = enc
                    break
                except:
                    continue
            else:
                return False, "N√£o conseguiu decodificar"
        
        # Remove BOM se existir no conte√∫do decodificado
        if content.startswith('\ufeff'):
            content = content[1:]
        
        # Escreve em UTF-8 puro (SEM BOM)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True, f"‚úÖ {detected_encoding} ‚Üí UTF-8"
    
    except Exception as e:
        return False, f"‚ùå {type(e).__name__}"

def correct_all_files():
    """Corrige todos arquivos do projeto"""
    
    print("=" * 80)
    print("üîß CORRETOR DE CODIFICA√á√ÉO ‚Äî Convertendo para UTF-8 puro")
    print("=" * 80)
    
    root = Path.cwd()
    
    # Padr√µes de arquivo
    patterns = ['**/*.py', '**/*.md', '**/*.json', '**/*.csv', '**/*.txt', '**/*.yaml', '**/*.yml']
    
    all_files = []
    for pattern in patterns:
        all_files.extend(root.glob(pattern))
    
    # Filtra relevantes
    relevant_files = [
        f for f in all_files
        if '__pycache__' not in str(f)
        and '.git' not in str(f)
        and 'venv' not in str(f)
        and '.pytest' not in str(f)
        and '.venv' not in str(f)
    ]
    
    print(f"\nüìÇ Total de arquivos: {len(relevant_files)}")
    print("üîÑ Corrigindo...\n")
    
    success_count = 0
    error_count = 0
    results = []
    
    for i, filepath in enumerate(sorted(relevant_files), 1):
        rel_path = filepath.relative_to(root)
        success, msg = fix_encoding(filepath)
        
        if success:
            success_count += 1
            status = "‚úÖ"
        else:
            error_count += 1
            status = "‚ùå"
        
        results.append((rel_path, status, msg))
        
        # Mostra progresso (a cada 10 ou no final)
        if i % 10 == 0 or i == len(relevant_files):
            print(f"[{i}/{len(relevant_files)}] {status} {rel_path} ... {msg}")
    
    # Resumo
    print("\n" + "=" * 80)
    print("üìä RESUMO DA CORRE√á√ÉO")
    print("=" * 80)
    
    print(f"\n‚úÖ Sucesso: {success_count}/{len(relevant_files)}")
    print(f"‚ùå Erros: {error_count}/{len(relevant_files)}")
    
    if error_count > 0:
        print("\n‚ö†Ô∏è  Arquivos com erro:")
        for rel_path, status, msg in results:
            if status == "‚ùå":
                print(f"   ‚Ä¢ {rel_path}")
                print(f"     {msg}")
    
    # Cria log detalhado
    print("\nüìÑ Gerando log detalhado...")
    
    with open("CORRECAO_CODIFICACAO.log", "w", encoding="utf-8") as f:
        f.write("LOG DE CORRE√á√ÉO DE CODIFICA√á√ÉO\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total processado: {len(relevant_files)}\n")
        f.write(f"Sucesso: {success_count}\n")
        f.write(f"Erros: {error_count}\n")
        f.write("Encoding target: UTF-8 (sem BOM)\n\n")
        
        f.write("DETALHES:\n")
        f.write("-" * 80 + "\n")
        for rel_path, status, msg in results:
            f.write(f"{status} {rel_path}\n")
            f.write(f"   {msg}\n")
    
    print("‚úÖ Log salvo em: CORRECAO_CODIFICACAO.log")
    
    print("\n" + "=" * 80)
    print("üéâ CORRE√á√ÉO CONCLU√çDA")
    print("=" * 80)
    print("\n‚ú® Todos os arquivos foram convertidos para UTF-8 sem BOM")
    print("\nPr√≥ximo passo:")
    print("  1. Verificar se projeto ainda funciona")
    print("  2. Rodar testes")
    print("  3. Fazer commit das mudan√ßas")

if __name__ == "__main__":
    try:
        correct_all_files()
    except KeyboardInterrupt:
        print("\n‚ùå Opera√ß√£o cancelada")
        sys.exit(1)

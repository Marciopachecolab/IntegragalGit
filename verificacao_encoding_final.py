#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verifica√ßão Final de Encoding - Garantir UTF-8 sem BOM em todo o projeto
"""

import os
import chardet

def check_file_encoding(filepath):
    """Verifica encoding e BOM de um arquivo"""
    try:
        with open(filepath, 'rb') as f:
            raw = f.read(500)
            result = chardet.detect(raw)
            has_bom = raw.startswith(b'\xef\xbb\xbf')
            return {
                'encoding': result.get('encoding', 'unknown'),
                'confidence': result.get('confidence', 0),
                'has_bom': has_bom,
                'error': None
            }
    except Exception as e:
        return {
            'encoding': 'error',
            'confidence': 0,
            'has_bom': False,
            'error': str(e)
        }

def main():
    print("\n" + "=" * 80)
    print("üîç VERIFICA√áÉO FINAL DE ENCODING UTF-8 SEM BOM")
    print("=" * 80 + "\n")
    
    # Arquivos cr√≠ticos para verificar
    critical_files = [
        'AUDITORIA_RESUMO_VISUAL.txt',
        'config/exams/vr1.json',
        'AUDITORIA_CODIFICACAO_FINAL.md',
        'services/cadastros_diversos.py',
        'FASE6_CONCLUSAO_COMPLETA.md',
        'main.py',
        'FASE5_CONCLUSAO_FINAL.md',
        'auditoria_codificacao.py',
        'corrigir_codificacao.py',
    ]
    
    print("üìã ARQUIVOS CRçTICOS:")
    print("-" * 80)
    
    all_ok = True
    issues = []
    
    for fpath in critical_files:
        if os.path.exists(fpath):
            result = check_file_encoding(fpath)
            
            is_utf8 = result['encoding'] and result['encoding'].lower().startswith('utf')
            has_bom = result['has_bom']
            
            if not is_utf8 or has_bom:
                all_ok = False
                status = "‚ùå ERRO"
                if has_bom:
                    issues.append(f"‚ùå {fpath}: UTF-8 COM BOM (deve remover)")
                elif not is_utf8:
                    issues.append(f"‚ùå {fpath}: Encoding é {result['encoding']} (deve ser UTF-8)")
            else:
                status = "‚úÖ OK"
            
            enc_display = f"{result['encoding']}"
            bom_display = "BOM" if has_bom else "Sem BOM"
            print(f"{status} | {fpath:50} | {enc_display:12} | {bom_display}")
        else:
            print(f"‚ö†Ô∏è  SKIP | {fpath:50} | (arquivo não existe)")
    
    print("\n" + "-" * 80)
    
    # Scan all project files for encoding issues
    print("\nüìä SCAN COMPLETO DO PROJETO (todos os arquivos):")
    print("-" * 80)
    
    root_dir = '.'
    all_files = []
    encoding_summary = {}
    
    # Extens√µes importantes
    important_extensions = ['.py', '.md', '.json', '.csv', '.txt']
    
    for root, dirs, files in os.walk(root_dir):
        # Ignorar diret√≥rios espec√≠ficos
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', '.venv', 'venv', 'node_modules']]
        
        for file in files:
            fpath = os.path.join(root, file)
            
            # Verificar apenas arquivos importantes
            if any(fpath.endswith(ext) for ext in important_extensions):
                result = check_file_encoding(fpath)
                enc = result['encoding'].lower() if result['encoding'] else 'unknown'
                
                # Contar tipos de encoding
                if enc not in encoding_summary:
                    encoding_summary[enc] = {'total': 0, 'with_bom': 0, 'files': []}
                
                encoding_summary[enc]['total'] += 1
                if result['has_bom']:
                    encoding_summary[enc]['with_bom'] += 1
                
                all_files.append({
                    'path': fpath,
                    'encoding': result['encoding'],
                    'has_bom': result['has_bom'],
                    'is_utf8': enc.startswith('utf')
                })
    
    # Exibir resumo
    print(f"\nüìà RESUMO DE ENCODING (Arquivos: {len(all_files)})")
    print("-" * 80)
    for enc_type in sorted(encoding_summary.keys()):
        data = encoding_summary[enc_type]
        bom_indicator = f" ({data['with_bom']} com BOM!)" if data['with_bom'] > 0 else ""
        print(f"  {enc_type:15}: {data['total']:3} arquivos{bom_indicator}")
    
    # Verificar problemas
    utf8_files = [f for f in all_files if f['is_utf8']]
    non_utf8_files = [f for f in all_files if not f['is_utf8']]
    bom_files = [f for f in all_files if f['has_bom']]
    
    print(f"\n‚úÖ UTF-8:        {len(utf8_files)} arquivos")
    print(f"‚ùå Não-UTF-8:    {len(non_utf8_files)} arquivos")
    print(f"‚ö†Ô∏è  Com BOM:      {len(bom_files)} arquivos")
    
    if non_utf8_files:
        print("\n‚ùå ARQUIVOS NÉO-UTF-8 ENCONTRADOS:")
        for f in non_utf8_files[:10]:  # Mostrar primeiros 10
            print(f"   - {f['path']}: {f['encoding']}")
        if len(non_utf8_files) > 10:
            print(f"   ... e {len(non_utf8_files) - 10} mais")
    
    if bom_files:
        print("\n‚ö†Ô∏è  ARQUIVOS COM BOM ENCONTRADOS:")
        for f in bom_files[:10]:
            print(f"   - {f['path']}")
        if len(bom_files) > 10:
            print(f"   ... e {len(bom_files) - 10} mais")
    
    # Conclusão
    print("\n" + "=" * 80)
    if all_ok and len(non_utf8_files) == 0 and len(bom_files) == 0:
        print("‚úÖ ‚úÖ ‚úÖ SUCESSO! TUDO UTF-8 SEM BOM! ‚úÖ ‚úÖ ‚úÖ")
        print("\n‚ú® SEGURO PARA CONTINUAR: Daqui para frente voc√™ pode trabalhar com")
        print("   compatibilidade UTF-8 sem preocupa√ß√µes!")
    else:
        print("‚ö†Ô∏è  PROBLEMAS DETECTADOS - Veja detalhes acima")
    
    print("=" * 80 + "\n")
    
    return 0 if (all_ok and len(non_utf8_files) == 0 and len(bom_files) == 0) else 1

if __name__ == '__main__':
    exit(main())

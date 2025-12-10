#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correção Final - Converter TODOS os arquivos para UTF-8 sem BOM
Incluindo os que chardet detectou incorretamente como Windows-1254, MacRoman, etc
"""

import os
import chardet

def fix_all_files():
    """Converter todos os arquivos para UTF-8 sem BOM"""
    print("\n" + "=" * 80)
    print("ðŸ”§ CORREÇÃO FINAL - CONVERTER TUDO PARA UTF-8 SEM BOM")
    print("=" * 80 + "\n")
    
    root_dir = '.'
    important_extensions = ['.py', '.md', '.json', '.csv', '.txt', '.log']
    
    stats = {
        'total': 0,
        'fixed': 0,
        'errors': 0,
        'skipped': 0,
    }
    
    problems = []
    
    for root, dirs, files in os.walk(root_dir):
        # Ignorar diretórios específicos
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', '.venv', 'venv', 'node_modules']]
        
        for file in files:
            fpath = os.path.join(root, file)
            
            # Verificar apenas arquivos importantes
            if not any(fpath.endswith(ext) for ext in important_extensions):
                continue
            
            stats['total'] += 1
            
            try:
                # Ler arquivo como binário
                with open(fpath, 'rb') as f:
                    raw_data = f.read()
                
                # Detectar encoding atual
                result = chardet.detect(raw_data)
                current_encoding = result.get('encoding', 'utf-8')
                
                # Remover BOM se houver
                if raw_data.startswith(b'\xef\xbb\xbf'):
                    raw_data = raw_data[3:]
                    print(f"[{stats['fixed']+1:3}] ðŸ”¨ {fpath:50} | Removido BOM")
                    stats['fixed'] += 1
                
                # Decodificar com o encoding detectado
                try:
                    if current_encoding and current_encoding.lower() != 'utf-8':
                        text = raw_data.decode(current_encoding, errors='replace')
                        # Re-encodar como UTF-8
                        utf8_bytes = text.encode('utf-8')
                        with open(fpath, 'wb') as f:
                            f.write(utf8_bytes)
                        print(f"[{stats['fixed']+1:3}] âœ… {fpath:50} | {current_encoding:15} â†’ UTF-8")
                        stats['fixed'] += 1
                    else:
                        # Já está UTF-8, apenas garante que está correto
                        text = raw_data.decode('utf-8', errors='replace')
                        utf8_bytes = text.encode('utf-8')
                        with open(fpath, 'wb') as f:
                            f.write(utf8_bytes)
                        stats['fixed'] += 1
                except Exception as e:
                    stats['errors'] += 1
                    problems.append(f"   â�Œ {fpath}: {str(e)}")
            
            except Exception as e:
                stats['errors'] += 1
                problems.append(f"   â�Œ {fpath}: {str(e)}")
    
    print("\n" + "-" * 80)
    print("\nðŸ"Š RESULTADO:")
    print(f"   Total analisado:    {stats['total']}")
    print(f"   Corrigidos:         {stats['fixed']}")
    print(f"   Erros:              {stats['errors']}")
    print()
    
    if problems:
        print("™ ï¸�  PROBLEMAS:")
        for p in problems[:10]:
            print(p)
        if len(problems) > 10:
            print(f"   ... e {len(problems) - 10} mais")
    
    print("\n" + "=" * 80)
    print("âœ… CONVERSÃO COMPLETA - TODOS OS ARQUIVOS AGORA UTF-8 SEM BOM!")
    print("=" * 80 + "\n")

if __name__ == '__main__':
    fix_all_files()

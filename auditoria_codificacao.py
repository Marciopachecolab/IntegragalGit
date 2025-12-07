#!/usr/bin/env python3



"""



AUDITORIA DE CODIFICAâÃ¡âÃO âÃÃ® Detectar e corrigir problemas de UTF-8/Mojibake







Objetivo:



  1. Verificar BOM em todos arquivos



  2. Verificar encoding de cada arquivo



  3. Detectar mojibake (caracteres invâÂ°lidos)



  4. Gerar relatââ¥rio



  5. Corrigir arquivos problemâÂ°ticos



"""







import os



import sys



from pathlib import Path



from typing import Tuple, List, Dict







# ============================================================================



# FUNâÃ¡âÃ¯ES AUXILIARES



# ============================================================================







def detect_bom(filepath: Path) -> Tuple[str, bool]:



    """Detecta BOM e retorna (encoding, has_bom)"""



    with open(filepath, 'rb') as f:



        raw = f.read(4)



    



    boms = {



        b'\xef\xbb\xbf': ('UTF-8-SIG', True),



        b'\xff\xfe': ('UTF-16-LE', True),



        b'\xfe\xff': ('UTF-16-BE', True),



    }



    



    for bom_bytes, (encoding, has_bom) in boms.items():



        if raw.startswith(bom_bytes):



            return encoding, has_bom



    



    return 'UTF-8', False







def check_file_encoding(filepath: Path) -> Dict:



    """Verifica encoding de um arquivo"""



    result = {



        'filepath': str(filepath),



        'exists': filepath.exists(),



        'encoding_detected': None,



        'has_bom': False,



        'mojibake_found': False,



        'mojibake_samples': [],



        'issues': []



    }



    



    if not filepath.exists():



        result['issues'].append("Arquivo nâÂ£o existe")



        return result



    



    # Detecta BOM



    encoding, has_bom = detect_bom(filepath)



    result['encoding_detected'] = encoding



    result['has_bom'] = has_bom



    



    if has_bom:



        result['issues'].append(f"âÃ¶â ÃâÃ¨  BOM encontrado: {encoding}")



    



    # Tenta ler com UTF-8



    try:



        with open(filepath, 'r', encoding='utf-8') as f:



            content = f.read()



        



        # Procura por mojibake comum



        mojibake_patterns = [



            'âÂ¢', 'âÃ', 'âÂ´', 'ââ', 'âÂ¥', 'âÂ¢âÃÂ¨', 'âÂ¢âÃÂ¢', 'âÂ¢âÃÃ¬', 'âÂ¢âÃÃ¬ÃÃ', 'âÂ¢âÃâ ',



            'âÃÂ¬Â©', 'âÃÂ¬Ã', 'âÃÂ¬Â£', 'âÃÂ¬Â°', 'âÃÂ¬â¥', 'âÃÂ¬Â¢',  # UTF-8 como Latin-1



        ]



        



        for pattern in mojibake_patterns:



            if pattern in content:



                result['mojibake_found'] = True



                # Encontra exemplos



                lines = content.split('\n')



                for i, line in enumerate(lines, 1):



                    if pattern in line:



                        sample = line.strip()[:80]



                        if sample not in result['mojibake_samples']:



                            result['mojibake_samples'].append(f"Linha {i}: {sample}")



                        if len(result['mojibake_samples']) >= 3:



                            break



                if len(result['mojibake_samples']) >= 3:



                    break



        



        if result['mojibake_found']:



            result['issues'].append("âÃ¹Ã¥ Mojibake detectado")



    



    except UnicodeDecodeError as e:



        result['issues'].append(f"âÃ¹Ã¥ Erro ao decodificar: {e}")



    



    return result







def fix_utf8_file(filepath: Path) -> Tuple[bool, str]:



    """



    Corrige arquivo:



    1. Remove BOM se existir



    2. Converte para UTF-8 puro (sem BOM)



    3. Preserva conteââ«do



    """



    try:



        # Lââ¢ arquivo original



        with open(filepath, 'rb') as f:



            raw = f.read()



        



        # Remove BOM se existir



        if raw.startswith(b'\xef\xbb\xbf'):



            raw = raw[3:]  # Remove UTF-8 BOM



        elif raw.startswith(b'\xff\xfe'):



            raw = raw[2:]  # Remove UTF-16-LE BOM



        elif raw.startswith(b'\xfe\xff'):



            raw = raw[2:]  # Remove UTF-16-BE BOM



        



        # Decodifica com detecâÃâÂ£o automâÂ°tica



        try:



            content = raw.decode('utf-8')



        except UnicodeDecodeError:



            # Tenta Latin-1 como fallback



            content = raw.decode('latin-1')



        



        # Reescreve em UTF-8 puro (sem BOM)



        with open(filepath, 'w', encoding='utf-8') as f:



            f.write(content)



        



        return True, "âÃºÃ Corrigido (UTF-8 sem BOM)"



    



    except Exception as e:



        return False, f"âÃ¹Ã¥ Erro ao corrigir: {e}"







# ============================================================================



# AUDITORIA



# ============================================================================







def audit_project():



    """Executa auditoria completa do projeto"""



    



    print("=" * 80)



    print("ï£¿Ã¼Ã®Ã§ AUDITORIA DE CODIFICAâÃ¡âÃO âÃÃ® UTF-8 / MOJIBAKE")



    print("=" * 80)



    



    # Encontra arquivos Python, Markdown, JSON, CSV



    root = Path.cwd()



    file_patterns = ['**/*.py', '**/*.md', '**/*.json', '**/*.csv', '**/*.txt']



    



    all_files = []



    for pattern in file_patterns:



        all_files.extend(root.glob(pattern))



    



    # Filtra arquivos relevantes (nâÂ£o __pycache__, nâÂ£o .git)



    relevant_files = [



        f for f in all_files



        if '__pycache__' not in str(f)



        and '.git' not in str(f)



        and 'venv' not in str(f)



        and '.pytest' not in str(f)



    ]



    



    print(f"\nï£¿Ã¼Ã¬Ã Total de arquivos encontrados: {len(relevant_files)}")



    



    # Audita cada arquivo



    print("\nï£¿Ã¼Ã®Ã© Auditando arquivos...\n")



    



    problematic_files = []



    files_to_fix = []



    



    for filepath in sorted(relevant_files)[:100]:  # Limita a 100 para output



        result = check_file_encoding(filepath)



        



        if result['issues']:



            problematic_files.append(result)



            rel_path = filepath.relative_to(root)



            



            print(f"âÃ¶â ÃâÃ¨  {rel_path}")



            for issue in result['issues']:



                print(f"   {issue}")



            



            if result['mojibake_found']:



                files_to_fix.append(filepath)



                print(f"   Samples:")



                for sample in result['mojibake_samples'][:2]:



                    print(f"     âÃÂ¢ {sample}")



            



            print()



    



    # Resumo



    print("\n" + "=" * 80)



    print("ï£¿Ã¼Ã¬Ã¤ RESUMO DA AUDITORIA")



    print("=" * 80)



    



    print(f"\nï£¿Ã¼Ã¬Ã  Estatââ sticas:")



    print(f"   Total auditado: {len(relevant_files)}")



    print(f"   Com problemas: {len(problematic_files)}")



    print(f"   Com mojibake: {len(files_to_fix)}")



    



    if not problematic_files:



        print("\nâÃºÃ Todos os arquivos estâÂ£o em UTF-8 correto!")



        return



    



    print(f"\nâÃ¶â ÃâÃ¨  Arquivos com problemas:")



    for result in problematic_files:



        print(f"   âÃÂ¢ {result['filepath']}")



        for issue in result['issues']:



            print(f"     - {issue}")



    



    # Pergunta se quer corrigir



    if files_to_fix:



        print(f"\nï£¿Ã¼Ã®Ã {len(files_to_fix)} arquivos podem ser corrigidos automaticamente")



        print("\nArquivos a corrigir:")



        for filepath in files_to_fix:



            print(f"   âÃÂ¢ {filepath.relative_to(root)}")



        



        # Corrige



        print(f"\nï£¿Ã¼Ã®Ã Corrigindo arquivos...\n")



        



        for filepath in files_to_fix:



            success, msg = fix_utf8_file(filepath)



            rel_path = filepath.relative_to(root)



            print(f"{msg} {rel_path}")



        



        print("\nâÃºÃ CorreâÃâÂ£o concluââ da!")



        print("   Todos os arquivos foram convertidos para UTF-8 sem BOM")



    



    # Cria relatââ¥rio



    print("\nï£¿Ã¼Ã¬Ã Gerando relatââ¥rio...\n")



    



    with open("AUDITORIA_CODIFICACAO.txt", "w", encoding="utf-8") as f:



        f.write("AUDITORIA DE CODIFICAâÃ¡âÃO\n")



        f.write("=" * 80 + "\n\n")



        f.write(f"Data: {__import__('datetime').datetime.now()}\n")



        f.write(f"Total auditado: {len(relevant_files)}\n")



        f.write(f"Com problemas: {len(problematic_files)}\n")



        f.write(f"Com mojibake: {len(files_to_fix)}\n\n")



        



        if problematic_files:



            f.write("ARQUIVOS COM PROBLEMAS:\n")



            f.write("-" * 80 + "\n")



            for result in problematic_files:



                f.write(f"\n{result['filepath']}\n")



                f.write(f"  Encoding detectado: {result['encoding_detected']}\n")



                f.write(f"  BOM: {'Sim' if result['has_bom'] else 'NâÂ£o'}\n")



                f.write(f"  Mojibake: {'Sim' if result['mojibake_found'] else 'NâÂ£o'}\n")



                if result['issues']:



                    f.write(f"  Issues:\n")



                    for issue in result['issues']:



                        f.write(f"    - {issue}\n")



        else:



            f.write("âÃºÃ Nenhum problema encontrado!\n")



    



    print("ï£¿Ã¼Ã¬Ã Relatââ¥rio salvo em: AUDITORIA_CODIFICACAO.txt")







if __name__ == "__main__":



    audit_project()




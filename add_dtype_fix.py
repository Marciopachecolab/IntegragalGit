#!/usr/bin/env python3
import sys

with open('services/history_report.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_pattern = 'df = pd.read_csv(csv_path_obj, sep=";", encoding="utf-8")\n\n        registros_atualizados = 0'
new_pattern = '''df = pd.read_csv(csv_path_obj, sep=";", encoding="utf-8")
        
        # Converte colunas para string para evitar FutureWarnings de dtype
        for col in ["status_gal", "data_hora_envio", "usuario_envio", "sucesso_envio", "detalhes_envio", "atualizado_em"]:
            if col in df.columns:
                df[col] = df[col].astype(str)
        
        registros_atualizados = 0'''

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    with open('services/history_report.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Conversão de dtype adicionada com sucesso')
else:
    print('⚠️ Padrão exato não encontrado')
    print('Tentando substituição manual...')
    # Procura e substituição mais flexível
    lines = content.split('\n')
    output = []
    added = False
    for i, line in enumerate(lines):
        output.append(line)
        if not added and 'df = pd.read_csv(csv_path_obj' in line and 'encoding="utf-8"' in line:
            # Próximas linhas vazias
            j = i + 1
            while j < len(lines) and lines[j].strip() == '':
                output.append(lines[j])
                j += 1
            # Se a próxima não-vazia é registros_atualizados, insere antes
            if j < len(lines) and 'registros_atualizados' in lines[j]:
                indent = '        '
                output.append(f'{indent}# Converte colunas para string para evitar FutureWarnings de dtype')
                output.append(f'{indent}for col in ["status_gal", "data_hora_envio", "usuario_envio", "sucesso_envio", "detalhes_envio", "atualizado_em"]:')
                output.append(f'{indent}    if col in df.columns:')
                output.append(f'{indent}        df[col] = df[col].astype(str)')
                output.append('')
                added = True
    
    if added:
        with open('services/history_report.py', 'w', encoding='utf-8') as f:
            f.write('\n'.join(output))
        print('✅ Conversão de dtype adicionada via método manual')
    else:
        print('❌ Não foi possível localizar o ponto de inserção')
        sys.exit(1)

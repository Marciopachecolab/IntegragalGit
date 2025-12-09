# -*- coding: utf-8 -*-
"""
Teste dos Equipment Extractors - Fase 1.3
Valida extração de dados de diferentes equipamentos PCR
"""
import sys
import io

# Forçar UTF-8 no output do terminal
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, 'c:/Users/marci/downloads/integragal')

import pandas as pd
from pathlib import Path
from services.equipment_extractors import (
    extrair_dados_equipamento,
    EquipmentConfig,
    ExtratorError
)

print("="*80)
print("TESTE: Equipment Extractors")
print("="*80)

# Diretório de teste
test_dir = Path(r'C:\Users\marci\Downloads\18 JULHO 2025\teste')

# Configurações de teste para cada equipamento
configs_teste = {
    '7500_Extended': {
        'arquivo': '20250718 VR1-VR2 BIOM PLACA 5.xls',
        'config': EquipmentConfig(
            nome='7500_Extended',
            xlsx_estrutura={
                'coluna_well': 0,
                'coluna_sample': 1,
                'coluna_target': 2,
                'coluna_ct': 6,
                'linha_inicio': 9
            }
        ),
        'esperado': {
            'min_linhas': 50,
            'colunas': ['bem', 'amostra', 'alvo', 'ct'],
            'formato_well': 'A01',
            'alvos_exemplos': ['VR1', 'VR2', 'RP']
        }
    },
    'QuantStudio': {
        'arquivo': '20210809 COVID BIO M PLACA 8_Copy_20210809_182622_Results_20210809 202116.xls',
        'config': EquipmentConfig(
            nome='QuantStudio',
            xlsx_estrutura={
                'coluna_well': 0,
                'coluna_sample': 3,
                'coluna_target': 4,
                'coluna_ct': 12,
                'linha_inicio': 25
            }
        ),
        'esperado': {
            'min_linhas': 50,
            'colunas': ['bem', 'amostra', 'alvo', 'ct'],
            'formato_well': 'A01',
            'alvos_exemplos': []  # Verificar quais alvos existem
        }
    },
    'CFX96': {
        'arquivo': 'SC2 20200729-MANAGER.xls',
        'config': EquipmentConfig(
            nome='CFX96',
            xlsx_estrutura={
                'coluna_well': 0,
                'coluna_sample': 4,
                'coluna_target': 2,
                'coluna_ct': 5,
                'linha_inicio': 21
            }
        ),
        'esperado': {
            'min_linhas': 50,
            'colunas': ['bem', 'amostra', 'alvo', 'ct'],
            'formato_well': 'A01',
            'alvos_exemplos': []
        }
    },
    'CFX96_Export': {
        'arquivo': 'exemploseegene.xlsx',
        'config': EquipmentConfig(
            nome='CFX96_Export',
            xlsx_estrutura={
                'coluna_well': 2,
                'coluna_sample': 3,
                'coluna_target': 5,
                'coluna_ct': 6,
                'linha_inicio': 3
            }
        ),
        'esperado': {
            'min_linhas': 50,
            'colunas': ['bem', 'amostra', 'alvo', 'ct'],
            'formato_well': 'A01',
            'alvos_exemplos': ['E gene', 'RdRP/S gene', 'N gene', 'IC']
        }
    }
}

# Executar testes
resultados = []

for equipamento, teste in configs_teste.items():
    print(f"\n{'='*80}")
    print(f"🔬 TESTANDO: {equipamento}")
    print(f"{'='*80}")
    
    arquivo_path = test_dir / teste['arquivo']
    
    if not arquivo_path.exists():
        print(f"   ❌ Arquivo não encontrado: {teste['arquivo']}")
        resultados.append((equipamento, False, "Arquivo não encontrado"))
        continue
    
    print(f"   📂 Arquivo: {teste['arquivo']}")
    print(f"   📊 Config: linha_inicio={teste['config'].xlsx_estrutura['linha_inicio']}")
    print(f"            coluna_well={teste['config'].xlsx_estrutura['coluna_well']}")
    print(f"            coluna_ct={teste['config'].xlsx_estrutura['coluna_ct']}")
    
    try:
        # Extrair dados
        df = extrair_dados_equipamento(str(arquivo_path), teste['config'])
        
        print(f"\n   ✅ EXTRAÇÃO CONCLUÍDA")
        print(f"      Total de linhas: {len(df)}")
        print(f"      Colunas: {list(df.columns)}")
        
        # Validações
        esperado = teste['esperado']
        checks = []
        
        # 1. Verificar colunas
        colunas_ok = list(df.columns) == esperado['colunas']
        checks.append(('Colunas corretas', colunas_ok))
        if colunas_ok:
            print(f"      ✅ Colunas: {list(df.columns)}")
        else:
            print(f"      ❌ Colunas incorretas: {list(df.columns)} vs {esperado['colunas']}")
        
        # 2. Verificar mínimo de linhas
        linhas_ok = len(df) >= esperado['min_linhas']
        checks.append(('Mínimo de linhas', linhas_ok))
        if linhas_ok:
            print(f"      ✅ Linhas: {len(df)} >= {esperado['min_linhas']}")
        else:
            print(f"      ❌ Poucas linhas: {len(df)} < {esperado['min_linhas']}")
        
        # 3. Verificar formato de wells
        wells_sample = df['bem'].head(5).tolist()
        print(f"      📝 Wells amostra: {wells_sample}")
        
        # 4. Verificar alvos
        alvos_unicos = df['alvo'].unique().tolist()
        print(f"      🎯 Alvos encontrados: {alvos_unicos}")
        
        if esperado['alvos_exemplos']:
            alvos_ok = any(alvo in alvos_unicos for alvo in esperado['alvos_exemplos'])
            checks.append(('Alvos esperados', alvos_ok))
            if alvos_ok:
                print(f"      ✅ Alvos esperados presentes")
            else:
                print(f"      ⚠️ Alvos esperados não encontrados: {esperado['alvos_exemplos']}")
        
        # 5. Verificar CTs
        cts_com_valor = df['ct'].notna().sum()
        cts_sem_valor = df['ct'].isna().sum()
        print(f"      📊 CTs: {cts_com_valor} com valor, {cts_sem_valor} sem valor (N/A)")
        
        # Mostrar amostra de dados
        print(f"\n      📋 AMOSTRA DE DADOS (primeiras 3 linhas):")
        for idx, row in df.head(3).iterrows():
            ct_str = f"{row['ct']:.2f}" if pd.notna(row['ct']) else "N/A"
            print(f"         {row['bem']} | {row['amostra'][:20]:20s} | {row['alvo']:15s} | CT: {ct_str}")
        
        # Resultado geral
        todos_ok = all(check[1] for check in checks)
        resultados.append((equipamento, todos_ok, f"{len(df)} linhas extraídas"))
        
        if todos_ok:
            print(f"\n      ✅ TESTE PASSOU")
        else:
            print(f"\n      ⚠️ TESTE PARCIALMENTE OK")
    
    except ExtratorError as e:
        print(f"   ❌ ERRO DE EXTRAÇÃO: {e}")
        resultados.append((equipamento, False, str(e)))
    except Exception as e:
        print(f"   ❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        resultados.append((equipamento, False, f"Erro: {e}"))

# Resumo final
print("\n" + "="*80)
print("RESUMO DOS TESTES")
print("="*80)

for equipamento, passou, detalhes in resultados:
    status = "✅" if passou else "❌"
    print(f"{status} {equipamento:20s} - {detalhes}")

total = len(resultados)
passou_count = sum(1 for _, p, _ in resultados if p)

print("="*80)
print(f"TOTAL: {passou_count}/{total} testes passaram")

if passou_count == total:
    print("✅ TODOS OS EXTRACTORS ESTÃO FUNCIONANDO!")
else:
    print("⚠️ ALGUNS EXTRACTORS FALHARAM - VERIFICAR")

print("="*80)

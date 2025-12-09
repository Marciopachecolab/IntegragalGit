"""
Teste integrado de leitura e normalização de arquivo CFX96_Export com C(t)
"""
import sys
sys.path.insert(0, 'c:/Users/marci/downloads/integragal')

import pandas as pd
from services.equipment_detector import detectar_equipamento, analisar_estrutura_xlsx
from services.universal_engine import _normalize_col_key

arquivo = r'C:\Users\marci\Downloads\18 JULHO 2025\teste\exemploseegene.xlsx'

print("="*80)
print("TESTE INTEGRADO: exemploseegene.xlsx")
print("="*80)

# 1. Detecção de equipamento
print("\n📋 ETAPA 1: Detecção de equipamento")
resultado = detectar_equipamento(arquivo)
print(f"   Equipamento: {resultado['equipamento']}")
print(f"   Confiança: {resultado['confianca']:.1f}%")

# 2. Análise de estrutura
print("\n📋 ETAPA 2: Análise de estrutura")
estrutura = analisar_estrutura_xlsx(arquivo)
print(f"   Headers encontrados: {len(estrutura['headers'])}")
print(f"   Coluna Well: {estrutura.get('coluna_well')}")
print(f"   Coluna Sample: {estrutura.get('coluna_sample')}")
print(f"   Coluna CT: {estrutura.get('coluna_ct')}")

# 3. Verificar headers normalizados
print("\n📋 ETAPA 3: Normalização de headers")
headers_com_ct = []
for idx, h in enumerate(estrutura['headers']):
    normalized = _normalize_col_key(h)
    if 'ct' in normalized or h == 'C(t)':
        headers_com_ct.append((idx, h, normalized))

print(f"   Headers com CT/Cq encontrados: {len(headers_com_ct)}")
for idx, original, normalized in headers_com_ct:
    print(f"      Coluna {idx}: '{original}' -> '{normalized}'")

# 4. Ler arquivo com pandas e verificar normalização de colunas
print("\n📋 ETAPA 4: Leitura com pandas")
df = pd.read_excel(arquivo, header=1)  # Header na linha 2 (índice 1)
print(f"   Total de colunas: {len(df.columns)}")
print(f"   Total de linhas: {len(df)}")

# Simular normalização de aliases como em _convert_df_norm
cols_normalized = {c.lower().replace("(", "").replace(")", ""): c for c in df.columns}
print(f"\n   Aliases normalizados (primeiros 10):")
for i, (key, val) in enumerate(list(cols_normalized.items())[:10]):
    print(f"      '{key}' -> '{val}'")

# Testar lookup de colunas críticas
print("\n📋 ETAPA 5: Lookup de colunas críticas")
lookups = [
    ("well", "coluna de poço"),
    ("name", "coluna de nome/amostra"),
    ("ct", "coluna de CT/Cq"),
    ("e gene", "coluna de alvo E gene"),
]

for key, desc in lookups:
    normalized_key = key.lower().replace("(", "").replace(")", "")
    found = cols_normalized.get(normalized_key)
    status = "✅" if found else "❌"
    print(f"   {status} {desc}: '{found}'")

# 6. Verificar se primeiro C(t) foi detectado
print("\n📋 ETAPA 6: Verificação de primeira coluna C(t)")
coluna_ct_detectada = estrutura.get('coluna_ct')
if coluna_ct_detectada is not None:
    header_detectado = estrutura['headers'][coluna_ct_detectada]
    print(f"   ✅ Primeira coluna C(t) detectada:")
    print(f"      Índice: {coluna_ct_detectada}")
    print(f"      Header: '{header_detectado}'")
    print(f"      Normalizado: '{_normalize_col_key(header_detectado)}'")
else:
    print(f"   ❌ Nenhuma coluna C(t) detectada")

# Resumo
print("\n" + "="*80)
print("RESUMO DO TESTE INTEGRADO")
print("="*80)
checks = [
    (resultado['equipamento'] == 'CFX96_Export', "Equipamento CFX96_Export detectado"),
    (resultado['confianca'] >= 70, "Confiança >= 70%"),
    (estrutura.get('coluna_ct') == 6, "Primeira coluna C(t) é coluna 6"),
    (estrutura.get('coluna_well') == 2, "Coluna Well é coluna 2"),
    (len(headers_com_ct) >= 4, "Múltiplas colunas C(t) encontradas (>=4)"),
    ('ct' in cols_normalized, "Alias 'ct' presente no dicionário"),
]

all_ok = all(check[0] for check in checks)
for passed, desc in checks:
    status = "✅" if passed else "❌"
    print(f"{status} {desc}")

print("="*80)
if all_ok:
    print("✅ TESTE INTEGRADO PASSOU! C(t) COM PARÊNTESES TOTALMENTE SUPORTADO!")
else:
    print("⚠️ ALGUNS CHECKS FALHARAM - VERIFICAR")
print("="*80)

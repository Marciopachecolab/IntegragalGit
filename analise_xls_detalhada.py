"""
Análise detalhada de um arquivo .xls para verificar CT/Cq.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from services.equipment_detector import analisar_estrutura_xlsx

# Arquivo .xls de teste
arquivo = r"C:\Users\marci\Downloads\18 JULHO 2025\teste\20250718 VR1-VR2 BIOM PLACA 5.xls"

print("\n" + "="*80)
print("ANÁLISE DETALHADA DE ARQUIVO .XLS")
print("="*80)

print(f"\n📂 Arquivo: {Path(arquivo).name}")

estrutura = analisar_estrutura_xlsx(arquivo)

print(f"\n📋 ESTRUTURA DETECTADA:")
print(f"   Sheet: '{estrutura['sheet_name']}'")
print(f"   Total colunas: {estrutura['total_colunas']}")
print(f"   Linha início dados: {estrutura['linha_inicio_dados']}")
print(f"   Total linhas dados: {estrutura['total_linhas_dados']}")

print(f"\n📑 HEADERS COMPLETOS ({len(estrutura['headers'])}):")
for i, header in enumerate(estrutura['headers']):
    emoji = ""
    if i == estrutura.get('coluna_well'):
        emoji = "🔵 WELL"
    elif i == estrutura.get('coluna_sample'):
        emoji = "🟢 SAMPLE"
    elif i == estrutura.get('coluna_target'):
        emoji = "🟡 TARGET"
    elif i == estrutura.get('coluna_ct'):
        emoji = "🔴 CT/Cq"
    
    print(f"   [{i:2d}] {header[:50]:<50} {emoji}")

print(f"\n🔍 COLUNAS IDENTIFICADAS:")
print(f"   Well: coluna {estrutura.get('coluna_well')}")
print(f"   Sample: coluna {estrutura.get('coluna_sample')}")
print(f"   Target: coluna {estrutura.get('coluna_target')}")
print(f"   CT/Cq: coluna {estrutura.get('coluna_ct')}")

print(f"\n📝 AMOSTRAS DE WELLS:")
for well in estrutura.get('amostras_wells', [])[:10]:
    print(f"   - {well}")

print(f"\n📄 METADADOS (primeiras 5 linhas):")
for i, linha in enumerate(estrutura.get('conteudo_metadados', [])[:5], 1):
    print(f"   Linha {i}: {linha[:100]}...")

# Verificar variações de CT/Cq
print(f"\n🔬 VERIFICAÇÃO CT/CQ:")
headers_text = " ".join(str(h).lower() for h in estrutura['headers'])

ct_variations = ['ct', 'c т', 'threshold cycle', 'cycle threshold']
cq_variations = ['cq', 'quantification cycle']

print(f"\n   Texto completo dos headers (minúsculo):")
print(f"   {headers_text[:200]}...")

print(f"\n   Variações de CT encontradas:")
for var in ct_variations:
    found = var in headers_text
    print(f"      {'✅' if found else '❌'} '{var}': {'SIM' if found else 'NÃO'}")

print(f"\n   Variações de Cq encontradas:")
for var in cq_variations:
    found = var in headers_text
    print(f"      {'✅' if found else '❌'} '{var}': {'SIM' if found else 'NÃO'}")

print("\n" + "="*80)

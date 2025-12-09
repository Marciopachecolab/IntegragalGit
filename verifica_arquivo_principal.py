"""
Análise do arquivo principal que deve ter Cq.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from services.equipment_detector import analisar_estrutura_xlsx

arquivo = r"C:\Users\marci\Downloads\18 JULHO 2025\20250718 VR1-VR2 BIOM PLACA 5.xlsx"

print("\n" + "="*80)
print("ANÁLISE: 20250718 VR1-VR2 BIOM PLACA 5.xlsx")
print("="*80)

estrutura = analisar_estrutura_xlsx(arquivo)

print(f"\n📋 ESTRUTURA:")
print(f"   Sheet: '{estrutura['sheet_name']}'")
print(f"   Colunas: {estrutura['total_colunas']}")
print(f"   Linha início: {estrutura['linha_inicio_dados']}")
print(f"   Linhas dados: {estrutura['total_linhas_dados']}")

print(f"\n📑 HEADERS COMPLETOS:")
for i, h in enumerate(estrutura['headers'][:20]):
    h_str = str(h)
    h_lower = h_str.lower()
    
    emoji = ""
    if i == estrutura.get('coluna_well'):
        emoji = "🔵 WELL"
    elif i == estrutura.get('coluna_sample'):
        emoji = "🟢 SAMPLE"  
    elif i == estrutura.get('coluna_target'):
        emoji = "🟡 TARGET"
    elif i == estrutura.get('coluna_ct'):
        emoji = "🔴 CT/Cq"
    
    # Destacar CT/Cq
    if 'cq' in h_lower or 'ct' in h_lower or 'c т' in h_lower:
        emoji += " ⭐"
    
    print(f"   [{i:2d}] {h_str[:70]:<70} {emoji}")

print(f"\n🔍 BUSCA POR Cq:")
tem_cq = False
colunas_cq = []

for i, h in enumerate(estrutura['headers']):
    if 'cq' in str(h).lower():
        tem_cq = True
        colunas_cq.append({'idx': i, 'nome': str(h)})
        print(f"   ✅ Coluna {i}: '{h}'")

if not tem_cq:
    print(f"   ❌ Nenhuma coluna com 'Cq' encontrada")
    print(f"\n   Procurando por 'CT' ou 'C т':")
    for i, h in enumerate(estrutura['headers']):
        h_lower = str(h).lower()
        if 'ct' in h_lower or 'c т' in h_lower:
            print(f"   ℹ️ Coluna {i}: '{h}'")

print(f"\n📄 METADADOS:")
for i, linha in enumerate(estrutura['conteudo_metadados'][:5], 1):
    print(f"   {i}: {linha[:100]}...")

print("\n" + "="*80)

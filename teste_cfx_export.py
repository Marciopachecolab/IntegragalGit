from services.equipment_detector import detectar_equipamento, analisar_estrutura_xlsx
from pathlib import Path

arquivo = r'C:\Users\marci\Downloads\18 JULHO 2025\teste\exemploseegene.xlsx'

print("="*80)
print(f"TESTE: {Path(arquivo).name}")
print("="*80)

# Análise da estrutura
print("\n ANÁLISE DE ESTRUTURA:")
estrutura = analisar_estrutura_xlsx(arquivo)
print(f"   Sheet: {estrutura['sheet_name']}")
print(f"   Linha início: {estrutura['linha_inicio_dados']}")
print(f"   Headers: {estrutura['headers'][:8]}")
print(f"   Well: coluna {estrutura.get('coluna_well', 'NÃO DETECTADA')}")
print(f"   Sample: coluna {estrutura.get('coluna_sample', 'NÃO DETECTADA')}")
print(f"   Target: coluna {estrutura.get('coluna_target', 'NÃO DETECTADA')}")
print(f"   CT/Cq: coluna {estrutura.get('coluna_ct', 'NÃO DETECTADA')}")

# Detecção de equipamento
print("\n DETECÇÃO DE EQUIPAMENTO:")
resultado = detectar_equipamento(arquivo)
print(f"   Equipamento: {resultado['equipamento']}")
print(f"   Confiança: {resultado['confianca']:.1f}%")
print(f"\n   Alternativas:")
for alt in resultado['alternativas']:
    print(f"      - {alt['equipamento']}: {alt['confianca']:.1f}%")

# Procurar C(t) nos headers
print("\n VERIFICAÇÃO C(t):")
if 'C(t)' in str(estrutura['headers']):
    print("    C(t) encontrado nos headers!")
    for idx, h in enumerate(estrutura['headers']):
        if 'C(t)' in str(h):
            print(f"      Coluna {idx}: '{h}'")
else:
    print("    C(t) NÃO encontrado nos headers")

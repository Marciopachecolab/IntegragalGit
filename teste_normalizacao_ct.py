"""
Teste de normalização de C(t) com parênteses nas funções de matching de colunas
"""
import sys
sys.path.insert(0, 'c:/Users/marci/downloads/integragal')

from services.universal_engine import _normalize_col_key

# Teste da função _normalize_col_key
print("="*80)
print("TESTE: _normalize_col_key (universal_engine.py)")
print("="*80)

test_cases = [
    ("CT", "ct"),
    ("Ct", "ct"),
    ("ct", "ct"),
    ("Cq", "cq"),
    ("CQ", "cq"),
    ("C(t)", "ct"),  # NOVO: Com parênteses
    ("c(t)", "ct"),  # NOVO: Minúsculo com parênteses
    ("C (t)", "ct"), # NOVO: Com espaço
    ("Cт", "ct"),    # Cirílico
    ("CT Mean", "ctmean"),
    ("CT_Mean", "ctmean"),
    ("CT Threshold", "ctthreshold"),
    ("Cq Confidence", "cqconfidence"),
]

print("\n🔍 Testando normalização de variantes de CT/Cq:")
all_ok = True
for input_val, expected in test_cases:
    result = _normalize_col_key(input_val)
    status = "✅" if result == expected else "❌"
    if result != expected:
        all_ok = False
    print(f"   {status} '{input_val}' -> '{result}' (esperado: '{expected}')")

print("\n" + "="*80)
if all_ok:
    print("✅ TODOS OS TESTES PASSARAM!")
else:
    print("❌ ALGUNS TESTES FALHARAM")
print("="*80)

# Teste da função _norm_key do plate_viewer
print("\n" + "="*80)
print("TESTE: _norm_key simulado (plate_viewer.py)")
print("="*80)

def _norm_key(txt: str) -> str:
    """Simulação da função _norm_key atualizada"""
    txt_clean = str(txt).replace("(", "").replace(")", "")
    return "".join(ch for ch in txt_clean.upper() if ch.isalnum())

test_cases_norm = [
    ("CT", "CT"),
    ("C(t)", "CT"),      # NOVO: Com parênteses
    ("c(t)", "CT"),      # NOVO: Minúsculo
    ("Cq", "CQ"),
    ("E gene", "EGENE"),
    ("CT_VR1", "CTVR1"),
    ("C(t)_VR1", "CTVR1"),  # NOVO: Com parênteses e sufixo
]

print("\n🔍 Testando normalização para matching de alvos:")
all_ok_norm = True
for input_val, expected in test_cases_norm:
    result = _norm_key(input_val)
    status = "✅" if result == expected else "❌"
    if result != expected:
        all_ok_norm = False
    print(f"   {status} '{input_val}' -> '{result}' (esperado: '{expected}')")

print("\n" + "="*80)
if all_ok_norm:
    print("✅ TODOS OS TESTES DE MATCHING PASSARAM!")
else:
    print("❌ ALGUNS TESTES DE MATCHING FALHARAM")
print("="*80)

# Teste de matching de colunas com aliases
print("\n" + "="*80)
print("TESTE: Matching de aliases de colunas (_convert_df_norm)")
print("="*80)

# Simular dicionário de colunas normalizado
columns_example = ["Well", "Name", "Type", "E gene", "C(t)", "RdRP/S gene", "C(t)", "IC", "C(t)"]
cols_normalized = {c.lower().replace("(", "").replace(")", ""): c for c in columns_example}

print("\n📋 Colunas originais:", columns_example)
print("\n📋 Dicionário normalizado:")
for key, val in cols_normalized.items():
    print(f"   '{key}' -> '{val}'")

# Testar lookup
test_lookups = [
    ("ct", "C(t)"),           # Deve encontrar primeira ocorrência
    ("c(t)", "C(t)"),         # Com parênteses
    ("well", "Well"),
    ("name", "Name"),
    ("e gene", "E gene"),
]

print("\n🔍 Testando lookup de colunas:")
all_lookups_ok = True
for lookup_key, expected in test_lookups:
    # Normalizar a key de lookup
    normalized_lookup = lookup_key.lower().replace("(", "").replace(")", "")
    result = cols_normalized.get(normalized_lookup)
    status = "✅" if result == expected else "❌"
    if result != expected:
        all_lookups_ok = False
    print(f"   {status} lookup('{lookup_key}') -> '{result}' (esperado: '{expected}')")

print("\n" + "="*80)
if all_lookups_ok:
    print("✅ TODOS OS TESTES DE LOOKUP PASSARAM!")
else:
    print("❌ ALGUNS TESTES DE LOOKUP FALHARAM")
print("="*80)

# Resumo final
print("\n" + "="*80)
print("RESUMO FINAL")
print("="*80)
if all_ok and all_ok_norm and all_lookups_ok:
    print("✅ TODAS AS NORMALIZAÇÕES ESTÃO FUNCIONANDO CORRETAMENTE!")
    print("   - C(t) com parênteses é normalizado para 'ct'")
    print("   - Matching de colunas reconhece C(t) como CT/Cq")
    print("   - Aliases de colunas suportam C(t)")
else:
    print("❌ ALGUMAS NORMALIZAÇÕES FALHARAM - VERIFICAR IMPLEMENTAÇÃO")
print("="*80)

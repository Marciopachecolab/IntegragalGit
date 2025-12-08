"""
Teste para validar a função normalize_result()
Executar: python test_normalize_result.py
"""

import sys
sys.path.insert(0, r'C:\Users\marci\downloads\integragal')

from services.plate_viewer import normalize_result

print("=" * 70)
print("TESTE DA FUNÇÃO normalize_result()")
print("=" * 70)

# Casos de teste
test_cases = [
    # Formato "ALVO - NÚMERO"
    ("SC2 - 1", "Det", "Formato numérico: 1 = Detectado"),
    ("SC2 - 2", "ND", "Formato numérico: 2 = Não Detectado"),
    ("SC2 - 3", "Inc", "Formato numérico: 3 = Inconclusivo"),
    ("HMPV - 1", "Det", "Formato numérico com outro alvo"),
    
    # Texto completo
    ("Detectado", "Det", "Texto: Detectado"),
    ("Detectável", "Det", "Texto: Detectável"),
    ("Nao Detectado", "ND", "Texto: Nao Detectado (bug anterior!)"),
    ("Não Detectado", "ND", "Texto: Não Detectado"),
    ("Nao Detectavel", "ND", "Texto: Nao Detectavel"),
    ("Não Detectável", "ND", "Texto: Não Detectável"),
    ("Positivo", "Det", "Texto: Positivo"),
    ("Negativo", "ND", "Texto: Negativo"),
    ("Reagente", "Det", "Texto: Reagente"),
    ("Inconclusivo", "Inc", "Texto: Inconclusivo"),
    
    # Números diretos
    ("1", "Det", "Número direto: 1"),
    ("2", "ND", "Número direto: 2"),
    ("3", "Inc", "Número direto: 3"),
    
    # Vazio
    ("", "", "String vazia"),
    (None, "", "None"),
]

print("\nExecutando testes...\n")

passed = 0
failed = 0

for input_val, expected, description in test_cases:
    try:
        result = normalize_result(input_val if input_val is not None else "")
        status = "✅ PASS" if result == expected else "❌ FAIL"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
            
        print(f"{status} | {description}")
        print(f"        Input: '{input_val}' -> Esperado: '{expected}', Obtido: '{result}'")
        
        if result != expected:
            print(f"        ⚠️  ERRO: Esperava '{expected}' mas obteve '{result}'")
        print()
        
    except Exception as e:
        failed += 1
        print(f"❌ ERRO | {description}")
        print(f"        Input: '{input_val}' -> Exceção: {e}")
        print()

print("=" * 70)
print(f"RESUMO: {passed} testes passaram, {failed} falharam")
print("=" * 70)

if failed == 0:
    print("✅ TODOS OS TESTES PASSARAM!")
else:
    print(f"❌ {failed} TESTES FALHARAM!")
    sys.exit(1)

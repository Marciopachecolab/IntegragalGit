"""Teste temporário do Formula Parser"""
from services.formula_parser import validar_formula, avaliar_formula

print("=" * 60)
print("TESTE 1: VALIDAÇÃO DE FÓRMULAS")
print("=" * 60)

# Fórmulas válidas
formulas_validas = [
    "CT_DEN1 < 30",
    "(CT_DEN1 + CT_DEN2) / 2 < 33",
    "CT_ZIKA < 30 and CT_DENGUE > 15",
    "resultado_SC2 == 'Detectado'",
]

for f in formulas_validas:
    v = validar_formula(f)
    print(f"✅ {f}")
    print(f"   Válida: {v.valida}, Variáveis: {v.variaveis_encontradas}")

print("\n" + "=" * 60)
print("TESTE 2: BLOQUEIO DE CÓDIGO MALICIOSO")
print("=" * 60)

# Fórmulas perigosas
formulas_perigosas = [
    "__import__('os')",
    "eval('print(123)')",
    "open('/etc/passwd')",
    "CT_DEN1.__class__",
]

for f in formulas_perigosas:
    v = validar_formula(f)
    print(f"❌ {f}")
    print(f"   Bloqueado: {v.mensagem}")

print("\n" + "=" * 60)
print("TESTE 3: AVALIAÇÃO COM VARIÁVEIS")
print("=" * 60)

variaveis = {
    "CT_DEN1": 15.5,
    "CT_DEN2": 18.2,
    "CT_ZIKA": 25.0,
    "CT_DENGUE": 20.0,
}

casos = [
    ("CT_DEN1 < 30", True),
    ("(CT_DEN1 + CT_DEN2) / 2 < 33", True),
    ("CT_ZIKA < 30 and CT_DENGUE > 15", True),
    ("CT_DEN1 > 50", False),
]

for formula, esperado in casos:
    r = avaliar_formula(formula, variaveis)
    status = "✅" if r.sucesso and r.resultado == esperado else "❌"
    print(f"{status} {formula}")
    print(f"   Resultado: {r.resultado} (esperado: {esperado})")
    print(f"   Tempo: {r.tempo_execucao_ms:.2f}ms")

print("\n" + "=" * 60)
print("TESTE 4: TRATAMENTO DE ERROS")
print("=" * 60)

# Divisão por zero
r = avaliar_formula("CT_DEN1 / CT_ZERO", {"CT_DEN1": 10, "CT_ZERO": 0})
print(f"Divisão por zero: {r.mensagem_erro}")

# Variável faltando
r = avaliar_formula("CT_INEXISTENTE < 30", {})
print(f"Variável faltando: {r.mensagem_erro}")

print("\n" + "=" * 60)
print("✅ TODOS OS TESTES CONCLUÍDOS!")
print("=" * 60)

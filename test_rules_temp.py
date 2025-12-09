"""Teste completo do Rules Engine"""
import sys
sys.path.insert(0, 'c:\\Users\\marci\\downloads\\integragal')

from services.rules_engine import (
    aplicar_regras, 
    aplicar_regra_booleana,
    aplicar_regra_formula,
    aplicar_regra_condicional,
    aplicar_regra_sequencia,
    aplicar_regra_exclusao_mutua
)

print("=" * 60)
print("TESTE 1: REGRA BOOLEANA - DOIS ALVOS POSITIVOS")
print("=" * 60)

resultados = {
    'alvos': {
        'DEN1': {'resultado': 'Detectado', 'ct': 15.5},
        'DEN2': {'resultado': 'Detectado', 'ct': 18.2},
        'ZIKA': {'resultado': 'Não Detectado', 'ct': 40.0},
    }
}

v = aplicar_regra_booleana('requer_dois_alvos', True, resultados)
print(f"✅ {v.regra_nome}: {v.resultado}")
print(f"   Detalhes: {v.detalhes}")
print()

print("=" * 60)
print("TESTE 2: REGRA FÓRMULA - MÉDIA CT")
print("=" * 60)

resultados = {
    'alvos': {
        'DEN1': {'resultado': 'Detectado', 'ct': 15.5},
        'DEN2': {'resultado': 'Detectado', 'ct': 18.2},
    }
}

v = aplicar_regra_formula('(CT_DEN1 + CT_DEN2) / 2 < 20', resultados)
print(f"✅ {v.regra_nome}: {v.resultado}")
print(f"   Detalhes: {v.detalhes}")
print()

print("=" * 60)
print("TESTE 3: REGRA CONDICIONAL - IF-THEN")
print("=" * 60)

resultados = {
    'alvos': {
        'DEN1': {'resultado': 'Detectado', 'ct': 15.5},
        'DEN2': {'resultado': 'Detectado', 'ct': 18.2},
    }
}

regra = {
    'if': 'CT_DEN1 < 30',
    'then': 'CT_DEN2 < 30',
    'descricao': 'Se DEN1 positivo, DEN2 também deve ser',
    'impacto': 'alto'
}

v = aplicar_regra_condicional(regra, resultados)
print(f"✅ {v.regra_nome}: {v.resultado}")
print(f"   Detalhes: {v.detalhes}")
print()

print("=" * 60)
print("TESTE 4: REGRA SEQUÊNCIA - ALVOS OBRIGATÓRIOS")
print("=" * 60)

resultados = {
    'alvos': {
        'DEN1': {'resultado': 'Detectado', 'ct': 15.5},
        'DEN2': {'resultado': 'Detectado', 'ct': 18.2},
        'CONTROLE': {'resultado': 'Válido', 'ct': 25.0},
    }
}

regra = {
    'alvos_obrigatorios': ['DEN1', 'DEN2', 'CONTROLE'],
    'descricao': 'Alvos obrigatórios para Dengue'
}

v = aplicar_regra_sequencia(regra, resultados)
print(f"✅ {v.regra_nome}: {v.resultado}")
print(f"   Detalhes: {v.detalhes}")
print()

print("=" * 60)
print("TESTE 5: REGRA EXCLUSÃO MÚTUA")
print("=" * 60)

# Caso 1: OK - apenas um positivo
resultados = {
    'alvos': {
        'DEN1': {'resultado': 'Detectado', 'ct': 15.5},
        'ZIKA': {'resultado': 'Não Detectado', 'ct': 40.0},
        'CHIK': {'resultado': 'Não Detectado', 'ct': 40.0},
    }
}

regra = {
    'alvos': ['DEN1', 'ZIKA', 'CHIK'],
    'descricao': 'Arboviroses mutuamente exclusivas'
}

v = aplicar_regra_exclusao_mutua(regra, resultados)
print(f"✅ Caso OK: {v.resultado}")
print(f"   Detalhes: {v.detalhes}")

# Caso 2: FALHA - dois positivos
resultados = {
    'alvos': {
        'DEN1': {'resultado': 'Detectado', 'ct': 15.5},
        'ZIKA': {'resultado': 'Detectado', 'ct': 18.0},
        'CHIK': {'resultado': 'Não Detectado', 'ct': 40.0},
    }
}

v = aplicar_regra_exclusao_mutua(regra, resultados)
print(f"❌ Caso FALHA: {v.resultado}")
print(f"   Detalhes: {v.detalhes}")
print()

print("=" * 60)
print("TESTE 6: APLICAÇÃO COMPLETA DE REGRAS")
print("=" * 60)

resultados = {
    'alvos': {
        'DEN1': {'resultado': 'Detectado', 'ct': 15.5},
        'DEN2': {'resultado': 'Detectado', 'ct': 18.2},
        'CONTROLE': {'resultado': 'Válido', 'ct': 25.0},
    },
    'controles': {
        'IC': {'ct': 28.0, 'status': 'OK'},
    }
}

regras = {
    'requer_dois_alvos': True,
    'formulas': [
        '(CT_DEN1 + CT_DEN2) / 2 < 33',
        'CT_DEN1 < 30',
        'CT_DEN2 < 30',
    ],
    'condicoes': [
        {
            'if': 'CT_DEN1 < 30',
            'then': 'CT_DEN2 < 30',
            'descricao': 'DEN1 positivo implica DEN2 positivo',
            'impacto': 'alto'
        }
    ],
    'sequencia': {
        'alvos_obrigatorios': ['DEN1', 'DEN2', 'CONTROLE'],
        'descricao': 'Alvos obrigatórios'
    }
}

resultado = aplicar_regras(regras, resultados)
print(f"Status Final: {resultado.status}")
print(f"Tempo: {resultado.tempo_execucao_ms:.2f}ms")
print(f"Resumo: {resultado.detalhes}")
print(f"\nValidações ({len(resultado.validacoes)}):")
for v in resultado.validacoes:
    status_icon = "✅" if v.resultado == "passou" else "❌" if v.resultado == "falhou" else "⚠️"
    print(f"  {status_icon} {v.regra_nome}: {v.resultado}")
    print(f"     {v.detalhes}")

if resultado.mensagens_erro:
    print(f"\nErros: {resultado.mensagens_erro}")
if resultado.mensagens_aviso:
    print(f"\nAvisos: {resultado.mensagens_aviso}")

print()
print("=" * 60)
print("✅ TODOS OS TESTES CONCLUÍDOS!")
print("=" * 60)

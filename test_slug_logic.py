#!/usr/bin/env python
"""Test: Verificar naming convention para novo exame"""

def _norm_exame(nome: str) -> str:
    """Normalização do registry"""
    return str(nome).strip().lower()

# Teste 1: Nome "Teste COVID-19"
nome = "Teste COVID-19"
key_norm = _norm_exame(nome)
print(f"Nome: '{nome}'")
print(f"Key normalizada: '{key_norm}'")
print(f"Slug desejado: 'teste_covid19'")
print()

# O problema:
# - registry usa key = _norm_exame(nome_exame) como chave no dict
# - _norm_exame("Teste COVID-19") = "teste covid-19"
# - slug do JSON é "teste_covid19" (diferente!)
# - Quando carrega JSON, tenta achar por slug, mas a chave é "teste covid-19"

# SOLUÇÃO: Na hora de salvar, deve-se gerar slug de forma
# que SEMPRE corresponda ao _norm_exame(nome_exame)

# Reformulado:
nome = "Teste COVID-19"
key_norm = _norm_exame(nome)
slug_correct = key_norm.replace(" ", "_")

print(f"Nome: '{nome}'")
print(f"Key normalizada (_norm_exame): '{key_norm}'")
print(f"Slug correto (replace space): '{slug_correct}'")
print(f"Quando registry carrega o JSON:")
print(f"  - key = _norm_exame(nome_exame) = '{_norm_exame(nome)}'")
print(f"  - slug no JSON = '{slug_correct}'")
print(f"  - Correspondem? {_norm_exame(nome) == slug_correct}")

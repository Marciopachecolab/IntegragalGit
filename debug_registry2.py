#!/usr/bin/env python
"""Debug: Verificar exatamente o que o registry está carregando"""

from services.cadastros_diversos import RegistryExamEditor
from services.exam_registry import registry, _norm_exame

editor = RegistryExamEditor()

# Limpar registry
registry.exams.clear()
registry.load()

print("Exames carregados do registry:")
for key, cfg in registry.exams.items():
    print(f"  key='{key}' → nome_exame='{cfg.nome_exame}' slug='{cfg.slug}'")

print("\n" + "=" * 70)
print("Tentando achar 'teste covid-19'...")
nome_teste = "Teste COVID-19"
key_teste = _norm_exame(nome_teste)
print(f"nome: '{nome_teste}' → _norm_exame: '{key_teste}'")
print(f"Registry tem essa chave? {key_teste in registry.exams}")

if key_teste in registry.exams:
    cfg = registry.exams[key_teste]
    print(f"✓ Encontrado: {cfg.nome_exame} (slug: {cfg.slug})")
else:
    print(f"✗ NÃO encontrado!")
    print(f"Chaves disponíveis: {list(registry.exams.keys())}")

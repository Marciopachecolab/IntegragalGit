#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para validar interface de ExamRegistry antes de rodar testes FASE 7
"""

from services.exam_registry import ExamRegistry

print("\n" + "="*80)
print("VALIDAÇÃO DE INTERFACE - ExamRegistry")
print("="*80 + "\n")

# Carregar registry
print("1️⃣  Carregando registry...")
registry = ExamRegistry()
registry.load()

print("✅ Registry carregado\n")

# Listar exames
print("2️⃣  Listando exames...")
exams_keys = list(registry.exams.keys())
print(f"   Total: {len(exams_keys)} exames")
for key in exams_keys[:10]:  # Mostrar primeiros 10
    cfg = registry.exams[key]
    print(f"   • {key} → {cfg.nome_exame if hasattr(cfg, 'nome_exame') else 'N/A'}")

if len(exams_keys) > 10:
    print(f"   ... e {len(exams_keys) - 10} mais")

print()

# Tentar acessar um exame
print("3️⃣  Testando acesso a um exame...")
test_slugs = [
    "vr1e2-biomanguinhos-7500",
    "VR1e2 Biomanguinhos 7500",
    "zdc-biomanguinhos-7500",
    "ZDC Biomanguinhos 7500",
]

for slug in test_slugs:
    cfg = registry.get(slug)
    if cfg:
        print(f"   ✅ {slug} encontrado!")
        print(f"      - nome_exame: {cfg.nome_exame}")
        print(f"      - tipo_placa_analitica: {cfg.tipo_placa_analitica}")
        print(f"      - panel_tests_id: {cfg.panel_tests_id}")
        break
else:
    print("   ⚠️  Nenhum dos slugs testados funcionou")
    print("   Keys disponíveis:")
    for key in exams_keys:
        print(f"      • {key}")

print()

# Validar estrutura de ExamConfig
print("4️⃣  Validando campos de ExamConfig...")
if exams_keys:
    cfg_sample = registry.exams[exams_keys[0]]
    fields = [f for f in dir(cfg_sample) if not f.startswith('_')]
    important_fields = ['nome_exame', 'slug', 'panel_tests_id', 'alvos', 'faixas_ct', 'rps']
    
    for field in important_fields:
        has_field = hasattr(cfg_sample, field)
        value = getattr(cfg_sample, field, 'N/A') if has_field else 'N/A'
        status = "✅" if has_field else "❌"
        print(f"   {status} {field}: {value}")

print("\n" + "="*80)
print("✅ VALIDAÇÃO CONCLUÍDA")
print("="*80 + "\n")

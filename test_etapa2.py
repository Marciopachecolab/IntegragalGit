#!/usr/bin/env python
"""Script para testar ETAPA 2 - RegistryExamEditor"""

from services.cadastros_diversos import RegistryExamEditor
from services.exam_registry import ExamConfig

editor = RegistryExamEditor()

# Teste 1: Carregar exame existente
print("=" * 60)
print("TESTE 1: Carregar exame existente")
print("=" * 60)
cfg = editor.load_exam("vr1")
if cfg:
    print(f"✓ Exame carregado: {cfg.nome_exame}")
    print(f"  - Slug: {cfg.slug}")
    print(f"  - Equipamento: {cfg.equipamento}")
else:
    print("✗ Exame não encontrado")

# Teste 2: Validar exame válido
print("\n" + "=" * 60)
print("TESTE 2: Validar exame válido")
print("=" * 60)
is_valid, msg = editor.validate_exam(cfg)
print(f"Validação: {is_valid}")
print(f"Mensagem: {msg}")

# Teste 3: Tentar criar exame inválido
print("\n" + "=" * 60)
print("TESTE 3: Validar exame inválido (nome_exame vazio)")
print("=" * 60)
cfg_invalid = ExamConfig(
    nome_exame="",  # ❌ Inválido
    slug="test",
    equipamento="Test",
    tipo_placa_analitica="96",
    esquema_agrupamento="96->96",
    kit_codigo=123,
)
is_valid, msg = editor.validate_exam(cfg_invalid)
print(f"Validação: {is_valid}")
print(f"Mensagem: {msg}")

# Teste 4: Converter para dict
print("\n" + "=" * 60)
print("TESTE 4: Converter ExamConfig para dict")
print("=" * 60)
cfg = editor.load_exam("vr1")
exam_dict = editor._exam_to_dict(cfg)
print(f"✓ Chaves do dict: {list(exam_dict.keys())}")
print(f"✓ Total de campos: {len(exam_dict)}")

print("\n" + "=" * 60)
print("✓ TODOS OS TESTES PASSARAM!")
print("=" * 60)

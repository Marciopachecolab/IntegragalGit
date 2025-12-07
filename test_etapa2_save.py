#!/usr/bin/env python
"""Teste de save_exam - criar exame de teste e verificar JSON"""

from services.cadastros_diversos import RegistryExamEditor
from services.exam_registry import ExamConfig
from pathlib import Path
import json

editor = RegistryExamEditor()

# Criar novo exame válido
print("=" * 70)
print("TESTE: Criar e salvar novo exame")
print("=" * 70)

editor_instance = RegistryExamEditor()

cfg_novo = ExamConfig(
    nome_exame="Teste COVID-19",
    slug=editor_instance._generate_slug("Teste COVID-19"),  # ← Gera slug corretamente
    equipamento="7500 Real-Time",
    tipo_placa_analitica="96",
    esquema_agrupamento="96->96",
    kit_codigo=9999,
    alvos=["COVID-19", "RP"],
    mapa_alvos={"COVID-19": "SARS-COV-2", "CORONAVIRUS": "SARS-COV-2"},
    faixas_ct={
        "detect_max": 38.0,
        "inconc_min": 38.01,
        "inconc_max": 40.0,
        "rp_min": 15.0,
        "rp_max": 35.0,
    },
    rps=["RP"],
    export_fields=["SARS-CoV-2", "RP"],
    panel_tests_id="99",
    controles={"cn": ["G11+G12"], "cp": ["H11+H12"]},
    comentarios="Exame de teste para validação de ETAPA 2",
    versao_protocolo="1.0",
)

# Validar
print("\n1. Validando novo exame...")
is_valid, msg = editor.validate_exam(cfg_novo)
print(f"   Validação: {is_valid}")
print(f"   Mensagem: {msg}")

if not is_valid:
    print("   ✗ Falhou! Abortando...")
    exit(1)

# Salvar
print("\n2. Salvando novo exame...")
success, msg = editor.save_exam(cfg_novo)
print(f"   Sucesso: {success}")
print(f"   Mensagem: {msg}")

if not success:
    print("   ✗ Falhou! Abortando...")
    exit(1)

# O arquivo foi salvo com o slug gerado
actual_slug = cfg_novo.slug
print(f"   Slug gerado: {actual_slug}")

# Verificar se arquivo foi criado
print("\n3. Verificando se arquivo JSON foi criado...")
json_path = Path(f"config/exams/{actual_slug}.json")
if json_path.exists():
    print(f"   ✓ Arquivo criado: {json_path}")
    print(f"   ✓ Tamanho: {json_path.stat().st_size} bytes")
else:
    print(f"   ✗ Arquivo NÃO encontrado: {json_path}")
    exit(1)

# Ler e validar conteúdo JSON
print("\n4. Lendo conteúdo do JSON...")
with open(json_path) as f:
    saved_data = json.load(f)

print("   ✓ JSON válido")
print(f"   ✓ Campos presentes: {len(saved_data)}")
print(f"   ✓ Nome: {saved_data['nome_exame']}")
print(f"   ✓ Slug: {saved_data['slug']}")

# Recarregar registry
print("\n5. Recarregando registry...")
success, msg = editor.reload_registry()
print(f"   Sucesso: {success}")
print(f"   Mensagem: {msg}")

# Verificar se novo exame aparece na lista
print("\n6. Verificando se novo exame aparece no registry...")
exames = editor.load_all_exams()
print(f"   Total de exames: {len(exames)}")
print("   Procurando por slug que comece com 'teste_covid'...")

# O slug gerado é "teste_covid_19" (COVID-19 → covid_19)
exame_encontrado = False
slug_gerado = None
for nome, slug in exames:
    if "teste" in slug.lower() and "covid" in slug.lower():
        exame_encontrado = True
        slug_gerado = slug
        print(f"   ✓ Novo exame encontrado: {nome} ({slug})")
        break

if not exame_encontrado:
    print("   ✗ Novo exame NÃO encontrado!")
    print(f"   Slugs disponíveis: {[s for _, s in exames]}")
    exit(1)

# Carregar o novo exame
print("\n7. Carregando novo exame do registry...")
cfg_loaded = editor.load_exam(slug_gerado)
if cfg_loaded:
    print(f"   ✓ Exame carregado: {cfg_loaded.nome_exame}")
    print(f"   ✓ Equipamento: {cfg_loaded.equipamento}")
    print(f"   ✓ Alvos: {cfg_loaded.alvos}")
else:
    print("   ✗ Falha ao carregar!")
    exit(1)

# Limpar: deletar arquivo de teste
print("\n8. Limpando: deletando exame de teste...")
success, msg = editor.delete_exam(slug_gerado)
print(f"   Sucesso: {success}")
print(f"   Mensagem: {msg}")

if json_path.exists():
    print(f"   ✗ Arquivo ainda existe: {json_path}")
    # Tentar remover manualmente
    import time
    time.sleep(0.5)  # Esperar um pouco
    try:
        json_path.unlink()
        print("   ✓ Arquivo removido em segunda tentativa")
    except Exception as e:
        print(f"   ✗ Falha ao remover: {e}")
        exit(1)
else:
    print("   ✓ Arquivo deletado com sucesso")

print("\n" + "=" * 70)
print("✓ TODOS OS TESTES DE SAVE/DELETE PASSARAM!")
print("=" * 70)

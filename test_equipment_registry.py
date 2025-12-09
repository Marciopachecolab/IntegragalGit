"""
Teste do Equipment Registry
"""

import sys
from pathlib import Path
sys.path.insert(0, '.')

from services.equipment_registry import EquipmentRegistry, get_registry, EquipmentConfig

print("="*80)
print("TESTE - EQUIPMENT REGISTRY")
print("="*80)

# Criar registry
registry = EquipmentRegistry()
print("\n1. Carregando registry...")
registry.load()

# Listar todos
print("\n2. Equipamentos registrados:")
print("-"*80)
equipamentos = registry.listar_todos()
print(f"Total: {len(equipamentos)} equipamentos\n")

for eq in equipamentos:
    print(f"📟 {eq.nome}")
    print(f"   Modelo: {eq.modelo}")
    print(f"   Fabricante: {eq.fabricante}")
    print(f"   Tipo de placa: {eq.tipo_placa}")
    print(f"   Extrator: {eq.extrator_nome}")
    print(f"   Estrutura XLSX:")
    print(f"      - Well: coluna {eq.xlsx_estrutura['coluna_well']}")
    print(f"      - Target: coluna {eq.xlsx_estrutura['coluna_target']}")
    print(f"      - CT: coluna {eq.xlsx_estrutura['coluna_ct']}")
    print(f"      - Linha início: {eq.xlsx_estrutura['linha_inicio']}")
    print()

# Testar get
print("\n3. Testando get():")
print("-"*80)
testes = ['7500', 'CFX96', 'Biomanguinhos_VR', 'QuantStudio', 'NAO_EXISTE']

for nome in testes:
    config = registry.get(nome)
    if config:
        print(f"✅ {nome}: {config.modelo}")
    else:
        print(f"❌ {nome}: Não encontrado")

# Testar normalização de chave
print("\n4. Testando normalização de chaves:")
print("-"*80)
testes_norm = [
    ('biomanguinhos_vr', 'Biomanguinhos_VR'),
    ('BIOMANGUINHOS_VR', 'Biomanguinhos_VR'),
    ('Biomanguinhos VR', 'Biomanguinhos_VR'),
    ('quantstudio', 'QuantStudio'),
    ('7500', '7500')
]

for entrada, esperado in testes_norm:
    config = registry.get(entrada)
    resultado = "✅" if config and config.nome == esperado else "❌"
    print(f"{resultado} '{entrada}' -> {config.nome if config else 'None'} (esperado: {esperado})")

# Testar registro de novo equipamento
print("\n5. Testando registrar_novo():")
print("-"*80)

novo_config = EquipmentConfig(
    nome="Teste_Custom",
    modelo="Custom PCR 1000",
    fabricante="Empresa Teste",
    tipo_placa="96",
    xlsx_estrutura={
        "coluna_well": 0,
        "coluna_target": 1,
        "coluna_ct": 2,
        "linha_inicio": 5
    },
    extrator_nome="extrair_custom"
)

registry.registrar_novo(novo_config)
print("✅ Equipamento registrado")

# Verificar se foi registrado
config_teste = registry.get("Teste_Custom")
if config_teste:
    print(f"✅ Recuperado: {config_teste.nome} - {config_teste.modelo}")
else:
    print("❌ Falha ao recuperar")

# Testar singleton
print("\n6. Testando singleton get_registry():")
print("-"*80)
registry2 = get_registry()
print(f"✅ Total equipamentos: {len(registry2.listar_todos())}")
print(f"✅ Mesmo objeto: {registry2 is get_registry()}")

print("\n" + "="*80)
print("✅ Testes concluídos!")
print("="*80)

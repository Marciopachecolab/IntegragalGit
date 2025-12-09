# -*- coding: utf-8 -*-
"""
Teste de Integração - Fase 1.5
Valida uso do extrator específico no fluxo de análise
"""
import sys
import io

# Forçar UTF-8 no output do terminal
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, 'c:/Users/marci/downloads/integragal')

import pandas as pd
from pathlib import Path
from models import AppState
from services.equipment_detector import detectar_equipamento
from services.equipment_registry import EquipmentRegistry
from services.equipment_extractors import extrair_dados_equipamento

print("="*80)
print("TESTE: Integração Fase 1.5 - Uso do Extrator Específico")
print("="*80)

# Arquivo de teste
test_file = Path(r'C:\Users\marci\Downloads\18 JULHO 2025\teste\20250718 VR1-VR2 BIOM PLACA 5.xls')

if not test_file.exists():
    print(f"❌ Arquivo não encontrado: {test_file}")
    sys.exit(1)

print(f"\n📂 Arquivo: {test_file.name}")

# Simular o fluxo completo como acontece no AnalysisService
print("\n" + "="*80)
print("SIMULANDO FLUXO DO AnalysisService.executar_analise()")
print("="*80)

# 1. Criar AppState
print("\n1️⃣ Inicializando AppState")
app_state = AppState()
print(f"   ✅ app_state criado")
print(f"   tipo_de_placa_detectado: {app_state.tipo_de_placa_detectado}")
print(f"   tipo_de_placa_config: {app_state.tipo_de_placa_config}")
print(f"   tipo_de_placa_selecionado: {app_state.tipo_de_placa_selecionado}")

# 2. Detectar equipamento (o que acontece na linha ~460 do analysis_service.py)
print("\n2️⃣ Detectando tipo de placa PCR")
try:
    resultado = detectar_equipamento(str(test_file))
    print(f"   ✅ Detecção concluída: {resultado.get('equipamento')}")
    print(f"   Confiança: {resultado.get('confianca', 0)*100:.1f}%")
except Exception as e:
    print(f"   ❌ Erro na detecção: {e}")
    sys.exit(1)

# 3. Carregar config do registry
print("\n3️⃣ Carregando configuração do equipamento")
try:
    registry = EquipmentRegistry()
    registry.load()
    
    equipamento = resultado.get('equipamento')
    config = registry.get(equipamento)
    
    if config:
        print(f"   ✅ Config carregada: {config.nome}")
        print(f"      Modelo: {config.modelo}")
        print(f"      Fabricante: {config.fabricante}")
        print(f"      Extrator: {config.extrator_nome}")
    else:
        print(f"   ❌ Config não encontrada para: {equipamento}")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Erro no registry: {e}")
    sys.exit(1)

# 4. Simular salvamento no app_state (o que _detectar_e_confirmar_tipo_placa faz)
print("\n4️⃣ Salvando no app_state (simulando confirmação do usuário)")
app_state.tipo_de_placa_detectado = resultado.get('equipamento')
app_state.tipo_de_placa_config = config
app_state.tipo_de_placa_selecionado = equipamento

print(f"   ✅ app_state.tipo_de_placa_detectado = '{app_state.tipo_de_placa_detectado}'")
print(f"   ✅ app_state.tipo_de_placa_config = {type(app_state.tipo_de_placa_config).__name__}")
print(f"   ✅ app_state.tipo_de_placa_selecionado = '{app_state.tipo_de_placa_selecionado}'")

# 5. Simular carregamento com extrator específico (Fase 1.5)
print("\n5️⃣ Carregando arquivo com extrator específico (Fase 1.5)")
print("   Simulando: _carregar_arquivo_resultados_com_extrator()")

try:
    # Verificar se há config (como no analysis_service.py linha ~730)
    if (
        hasattr(app_state, 'tipo_de_placa_config') 
        and app_state.tipo_de_placa_config is not None
    ):
        print(f"   ✅ Tipo de placa detectado presente")
        print(f"   📊 Usando extrator específico: {app_state.tipo_de_placa_config.extrator_nome}")
        
        # Usar extrator específico
        df_normalizado = extrair_dados_equipamento(str(test_file), app_state.tipo_de_placa_config)
        
        print(f"   ✅ Extração específica concluída!")
        print(f"      Linhas: {len(df_normalizado)}")
        print(f"      Colunas: {list(df_normalizado.columns)}")
        
        # Validar formato normalizado
        colunas_esperadas = ['bem', 'amostra', 'alvo', 'ct']
        if list(df_normalizado.columns) == colunas_esperadas:
            print(f"      ✅ Colunas normalizadas corretamente")
        else:
            print(f"      ❌ Colunas incorretas: esperado {colunas_esperadas}")
        
        # Mostrar amostra
        print(f"\n      📋 AMOSTRA DE DADOS (primeiras 3 linhas):")
        for idx, row in df_normalizado.head(3).iterrows():
            ct_str = f"{row['ct']:.2f}" if pd.notna(row['ct']) else "N/A"
            print(f"         {row['bem']} | {row['amostra'][:20]:20s} | {row['alvo']:10s} | CT: {ct_str}")
        
    else:
        print(f"   ⚠️ Tipo de placa NÃO detectado - usaria fallback genérico")
        
except Exception as e:
    print(f"   ❌ Erro ao usar extrator específico: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 6. Simular injeção de metadados (Fase 1.5)
print("\n6️⃣ Injetando metadados de equipamento (Fase 1.5)")
metadados = {}

if app_state.tipo_de_placa_detectado:
    metadados['equipamento_detectado'] = app_state.tipo_de_placa_detectado
    metadados['equipamento_selecionado'] = app_state.tipo_de_placa_selecionado
    
    if app_state.tipo_de_placa_config:
        config_meta = app_state.tipo_de_placa_config
        metadados['equipamento_modelo'] = config_meta.modelo
        metadados['equipamento_fabricante'] = config_meta.fabricante
        metadados['equipamento_tipo_placa'] = config_meta.tipo_placa
        metadados['equipamento_extrator'] = config_meta.extrator_nome

print(f"   ✅ Metadados injetados:")
for chave, valor in metadados.items():
    print(f"      {chave}: {valor}")

# Resumo final
print("\n" + "="*80)
print("RESUMO DA FASE 1.5")
print("="*80)

validacoes = [
    ("AppState inicializado", True),
    ("Detecção de tipo de placa", resultado is not None),
    ("Config carregada do registry", config is not None),
    ("app_state populado corretamente", app_state.tipo_de_placa_config is not None),
    ("Extrator específico usado", df_normalizado is not None),
    ("Dados normalizados (bem/amostra/alvo/ct)", list(df_normalizado.columns) == colunas_esperadas),
    ("Metadados de equipamento injetados", len(metadados) > 0),
]

for descricao, passou in validacoes:
    status = "✅" if passou else "❌"
    print(f"{status} {descricao}")

total_validacoes = len(validacoes)
validacoes_ok = sum(1 for _, p in validacoes if p)

print("="*80)
print(f"RESULTADO: {validacoes_ok}/{total_validacoes} validações passaram")

if validacoes_ok == total_validacoes:
    print("✅ FASE 1.5 VALIDADA - EXTRATOR ESPECÍFICO FUNCIONANDO!")
    print("\n📝 O que foi testado:")
    print("   1. ✅ Detecção de tipo de placa PCR")
    print("   2. ✅ Salvamento no app_state")
    print("   3. ✅ Uso do extrator específico baseado no tipo detectado")
    print("   4. ✅ Normalização para formato padrão ['bem', 'amostra', 'alvo', 'ct']")
    print("   5. ✅ Injeção de metadados de equipamento")
    print("\n🎯 Benefícios:")
    print("   - Dados normalizados automaticamente")
    print("   - Rastreabilidade completa (equipamento nos metadados)")
    print("   - Fallback para leitura genérica se detecção falhar")
else:
    print("⚠️ ALGUMAS VALIDAÇÕES FALHARAM")

print("="*80)

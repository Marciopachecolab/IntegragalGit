"""
Script de teste para validar correção do bug de NaN após salvar mapa.

Este script simula o fluxo:
1. Carregar DataFrame com resultados
2. Criar PlateModel
3. Converter de volta para DataFrame via to_dataframe()
4. Verificar que resultados permanecem como texto (não NaN)

Executar: python tests/test_nan_bug.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from services.plate_viewer import PlateModel
from services.exam_registry import get_exam_cfg

def test_to_dataframe_preserva_resultados():
    """
    Teste: Verificar se to_dataframe() retorna resultados em formato completo
    """
    print("=" * 70)
    print("TESTE 1: to_dataframe() preserva resultados textuais")
    print("=" * 70)
    
    # Criar DataFrame de teste
    df_test = pd.DataFrame({
        'Poco': ['A01', 'A02', 'B01', 'B02'],
        'Amostra': ['S001', 'S002', 'S003', 'S004'],
        'Codigo': ['1001', '1002', '1003', '1004'],
        'Resultado_SC2': ['Detectado', 'Não Detectado', 'Inconclusivo', 'Detectado'],
        'CT_SC2': [25.5, None, 34.8, 28.2],
        'Resultado_HMPV': ['Não Detectado', 'Detectado', 'Não Detectado', 'Não Detectado'],
        'CT_HMPV': [None, 22.1, None, None],
        'Resultado_RSV': ['Não Detectado', 'Não Detectado', 'Detectado', 'Não Detectado'],
        'CT_RSV': [None, None, 30.5, None],
    })
    
    print(f"\n📊 DataFrame original:")
    print(df_test[['Poco', 'Resultado_SC2', 'Resultado_HMPV', 'Resultado_RSV']])
    
    # Criar PlateModel a partir do DataFrame
    print(f"\n🔄 Criando PlateModel...")
    plate_model = PlateModel.from_df(
        df_test,
        exame="VR1E2",
        group_size=1
    )
    
    # Converter de volta para DataFrame
    print(f"🔄 Convertendo PlateModel de volta para DataFrame...")
    df_resultado = plate_model.to_dataframe()
    
    print(f"\n📊 DataFrame retornado por to_dataframe():")
    print(df_resultado[['Poco', 'Resultado_SC2', 'Resultado_HMPV', 'Resultado_RSV']])
    
    # VALIDAÇÕES
    print(f"\n✅ VALIDAÇÕES:")
    
    # 1. Verificar tipos de dados
    print(f"\n1️⃣ Tipos de dados das colunas Resultado_*:")
    colunas_resultado = [c for c in df_resultado.columns if c.startswith('Resultado_')]
    for col in colunas_resultado:
        dtype = df_resultado[col].dtype
        print(f"   {col}: {dtype}")
        assert dtype == 'object', f"❌ ERRO: {col} deveria ser 'object', mas é '{dtype}'"
    print(f"   ✅ Todos os tipos corretos (object)")
    
    # 2. Verificar valores NaN
    print(f"\n2️⃣ Verificar ausência de NaN em resultados:")
    total_nan = 0
    for col in colunas_resultado:
        nan_count = df_resultado[col].isna().sum()
        total_nan += nan_count
        if nan_count > 0:
            print(f"   ❌ {col}: {nan_count} valores NaN detectados!")
        else:
            print(f"   ✅ {col}: 0 NaN")
    
    assert total_nan == 0, f"❌ ERRO: {total_nan} valores NaN encontrados!"
    print(f"   ✅ Nenhum NaN encontrado")
    
    # 3. Verificar formato dos resultados (texto completo, não abreviado)
    print(f"\n3️⃣ Verificar formato dos resultados:")
    valores_validos = ['Detectado', 'Não Detectado', 'Inconclusivo', 'Inválido', '']
    valores_invalidos = []
    
    for col in colunas_resultado:
        for val in df_resultado[col].unique():
            if pd.notna(val) and val not in valores_validos:
                valores_invalidos.append((col, val))
    
    if valores_invalidos:
        print(f"   ❌ Valores inválidos encontrados:")
        for col, val in valores_invalidos:
            print(f"      - {col}: '{val}'")
        raise AssertionError("Valores abreviados ('Det', 'ND', etc.) encontrados! Deveria retornar texto completo.")
    else:
        print(f"   ✅ Todos os resultados em formato completo")
    
    # 4. Comparar com original
    print(f"\n4️⃣ Comparar resultados com DataFrame original:")
    for idx, row in df_test.iterrows():
        poco = row['Poco']
        df_result_row = df_resultado[df_resultado['Poco'] == poco]
        
        if df_result_row.empty:
            print(f"   ❌ Poço {poco} não encontrado no resultado!")
            continue
        
        for col in colunas_resultado:
            original_val = row.get(col, '')
            result_val = df_result_row.iloc[0][col]
            
            # Normalizar valores vazios
            original_val = '' if pd.isna(original_val) else original_val
            result_val = '' if pd.isna(result_val) else result_val
            
            if original_val != result_val:
                print(f"   ⚠️  {poco} - {col}: '{original_val}' → '{result_val}'")
    
    print(f"   ✅ Comparação concluída")
    
    print(f"\n{'=' * 70}")
    print(f"✅ TESTE PASSOU! to_dataframe() retorna resultados corretos")
    print(f"{'=' * 70}")


def test_merge_preserva_resultados():
    """
    Teste: Simular merge como feito em _on_mapa_salvo()
    """
    print("\n" + "=" * 70)
    print("TESTE 2: Merge preserva resultados (sem criar _BACKUP)")
    print("=" * 70)
    
    # DataFrame "original" (antes de abrir mapa)
    df_analise = pd.DataFrame({
        'Poco': ['A01', 'A02', 'B01'],
        'Selecionado': [True, False, True],
        'Amostra': ['S001', 'S002', 'S003'],
        'Resultado_SC2': ['Detectado', 'Não Detectado', 'Detectado'],
        'CT_SC2': [25.5, None, 28.2],
    })
    
    # DataFrame "atualizado" (vindo do PlateModel após editar mapa)
    df_updated = pd.DataFrame({
        'Poco': ['A01', 'A02', 'B01'],
        'Amostra': ['S001', 'S002', 'S003'],
        'Resultado_SC2': ['Detectado', 'Não Detectado', 'Inconclusivo'],  # B01 mudou
        'CT_SC2': [25.5, None, 35.0],  # CT de B01 mudou
    })
    
    print(f"\n📊 DataFrame ANTES (df_analise):")
    print(df_analise)
    
    print(f"\n📊 DataFrame UPDATED (do PlateModel):")
    print(df_updated)
    
    # Simular merge como em _on_mapa_salvo()
    chave_merge = 'Poco'
    df_selecoes = df_analise[[chave_merge, 'Selecionado']].copy()
    df_resultado = df_updated.merge(df_selecoes, on=chave_merge, how='left')
    
    print(f"\n📊 DataFrame RESULTADO (após merge):")
    print(df_resultado)
    
    # VALIDAÇÕES
    print(f"\n✅ VALIDAÇÕES:")
    
    # 1. Número de colunas
    print(f"\n1️⃣ Verificar número de colunas:")
    print(f"   Antes: {len(df_analise.columns)} colunas")
    print(f"   Updated: {len(df_updated.columns)} colunas")
    print(f"   Resultado: {len(df_resultado.columns)} colunas")
    
    # Não deve criar colunas _BACKUP
    colunas_backup = [c for c in df_resultado.columns if '_BACKUP' in c]
    if colunas_backup:
        print(f"   ❌ ERRO: Colunas _BACKUP criadas: {colunas_backup}")
        raise AssertionError("Merge criou colunas duplicadas com _BACKUP!")
    else:
        print(f"   ✅ Nenhuma coluna _BACKUP criada")
    
    # Deve ter exatamente as colunas esperadas
    colunas_esperadas = set(df_updated.columns) | {'Selecionado'}
    colunas_resultantes = set(df_resultado.columns)
    
    if colunas_resultantes != colunas_esperadas:
        print(f"   ❌ Colunas inesperadas:")
        print(f"      Esperadas: {sorted(colunas_esperadas)}")
        print(f"      Obtidas: {sorted(colunas_resultantes)}")
        raise AssertionError("Colunas do merge não correspondem ao esperado!")
    else:
        print(f"   ✅ Colunas corretas: {sorted(colunas_resultantes)}")
    
    # 2. Verificar NaN
    print(f"\n2️⃣ Verificar NaN:")
    nan_count = df_resultado['Resultado_SC2'].isna().sum()
    print(f"   NaN em Resultado_SC2: {nan_count}")
    assert nan_count == 0, "❌ ERRO: NaN encontrados após merge!"
    print(f"   ✅ Nenhum NaN")
    
    # 3. Verificar Selecionado preservado
    print(f"\n3️⃣ Verificar coluna Selecionado preservada:")
    assert list(df_resultado['Selecionado']) == list(df_analise['Selecionado']), \
        "❌ ERRO: Coluna Selecionado não foi preservada corretamente!"
    print(f"   ✅ Coluna Selecionado preservada: {list(df_resultado['Selecionado'])}")
    
    # 4. Verificar atualização de B01
    print(f"\n4️⃣ Verificar atualização de valores:")
    b01_resultado = df_resultado[df_resultado['Poco'] == 'B01'].iloc[0]['Resultado_SC2']
    assert b01_resultado == 'Inconclusivo', \
        f"❌ ERRO: B01 deveria ser 'Inconclusivo', mas é '{b01_resultado}'"
    print(f"   ✅ B01 atualizado corretamente: {b01_resultado}")
    
    print(f"\n{'=' * 70}")
    print(f"✅ TESTE PASSOU! Merge funciona corretamente")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    try:
        test_to_dataframe_preserva_resultados()
        test_merge_preserva_resultados()
        
        print("\n" + "🎉" * 35)
        print("✅ TODOS OS TESTES PASSARAM!")
        print("🎉" * 35)
        
    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

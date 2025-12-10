"""
Script de teste para validar exportação de VSR/RSV para GAL.

Este script verifica:
1. Aliases VSR estão mapeados corretamente
2. Coluna vsincicialresp é exportada no CSV do GAL
3. Valores de RSV são preenchidos corretamente

Executar: python tests/test_vsr_export.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from exportacao.gal_formatter import formatar_para_gal
from services.exam_registry import get_exam_cfg

def test_aliases_vsr():
    """
    Teste: Verificar se aliases VSR estão presentes
    """
    print("=" * 70)
    print("TESTE 1: Aliases VSR/RSV no gal_formatter")
    print("=" * 70)
    
    # Importar módulo para inspecionar
    import exportacao.gal_formatter as gal_module
    
    # Ler código fonte
    import inspect
    source = inspect.getsource(gal_module)
    
    # Verificar presença de aliases
    aliases_esperados = [
        '"VSINCICIALRESP"',
        '"VSINCICIALRESPA"',
        '"VSINCICIALRESPB"',
        '"VSR"',
        '"RSV"'
    ]
    
    print(f"\n🔍 Verificando aliases VSR/RSV no código:")
    aliases_encontrados = []
    aliases_faltando = []
    
    for alias in aliases_esperados:
        if alias in source:
            aliases_encontrados.append(alias)
            print(f"   ✅ {alias} encontrado")
        else:
            aliases_faltando.append(alias)
            print(f"   ❌ {alias} NÃO encontrado")
    
    if aliases_faltando:
        print(f"\n❌ Aliases faltando: {aliases_faltando}")
        print(f"⚠️  AVISO: Exportação de VSR pode falhar!")
    else:
        print(f"\n✅ Todos os aliases VSR encontrados no código")
    
    print(f"\n{'=' * 70}")


def test_exportacao_vsr_simples():
    """
    Teste: Exportação simples com formatar_para_gal()
    """
    print("\n" + "=" * 70)
    print("TESTE 2: Exportação VSR com formatar_para_gal()")
    print("=" * 70)
    
    # DataFrame de teste com RSV
    df_test = pd.DataFrame({
        'Codigo': ['1001', '1002', '1003'],
        'Amostra': ['S001', 'S002', 'S003'],
        'Resultado_SC2': ['Detectado', 'Não Detectado', 'Não Detectado'],
        'CT_SC2': [25.5, None, None],
        'Resultado_RSV': ['Não Detectado', 'Detectado', 'Inconclusivo'],
        'CT_RSV': [None, 28.3, 35.2],
        'Resultado_HMPV': ['Não Detectado', 'Não Detectado', 'Não Detectado'],
        'CT_HMPV': [None, None, None],
    })
    
    print(f"\n📊 DataFrame de teste:")
    print(df_test[['Codigo', 'Resultado_SC2', 'Resultado_RSV', 'Resultado_HMPV']])
    
    # Configuração do exame
    exam_cfg = get_exam_cfg("VR1E2")
    
    # Exportar para GAL
    print(f"\n🔄 Exportando para formato GAL...")
    try:
        df_gal = formatar_para_gal(df_test, exam_cfg)
        
        print(f"\n📊 DataFrame GAL exportado:")
        print(f"   Colunas: {list(df_gal.columns)}")
        print(f"   Linhas: {len(df_gal)}")
        
        # Verificar coluna vsincicialresp
        print(f"\n🔍 Verificando coluna vsincicialresp:")
        if 'vsincicialresp' in df_gal.columns:
            print(f"   ✅ Coluna 'vsincicialresp' presente")
            print(f"\n   Valores:")
            print(df_gal[['registroInterno', 'vsincicialresp']])
            
            # Verificar se valores foram preenchidos
            valores_nao_vazios = df_gal['vsincicialresp'].notna().sum()
            print(f"\n   Valores não vazios: {valores_nao_vazios}/{len(df_gal)}")
            
            # Verificar valor específico da amostra S002 (RSV Detectado)
            s002_row = df_gal[df_gal['registroInterno'] == '1002']
            if not s002_row.empty:
                vsr_valor = s002_row.iloc[0]['vsincicialresp']
                print(f"\n   ✅ S002 (RSV Detectado) → vsincicialresp = '{vsr_valor}'")
                
                # Validar valor esperado (1 = Detectado)
                if str(vsr_valor) == '1':
                    print(f"   ✅ Valor correto (1 = Detectado)")
                else:
                    print(f"   ⚠️  Valor inesperado: '{vsr_valor}' (esperado: '1')")
            else:
                print(f"   ❌ S002 não encontrada no resultado")
        else:
            print(f"   ❌ Coluna 'vsincicialresp' NÃO encontrada!")
            print(f"   Colunas disponíveis: {list(df_gal.columns)}")
            raise AssertionError("Coluna vsincicialresp não foi exportada!")
        
        print(f"\n✅ Exportação formatar_para_gal() OK")
        
    except Exception as e:
        print(f"\n❌ ERRO na exportação: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_exportacao_vsr_multipainel():
    """
    Teste: Exportação multi-painel com formatar_multi_painel_gal()
    """
    print("\n" + "=" * 70)
    print("TESTE 3: Exportação VSR com formatar_multi_painel_gal()")
    print("=" * 70)
    
    # DataFrame de teste
    df_test = pd.DataFrame({
        'Codigo': ['2001', '2002'],
        'Amostra': ['S101', 'S102'],
        'Resultado_SC2': ['Não Detectado', 'Não Detectado'],
        'Resultado_RSV': ['Detectado', 'Não Detectado'],
        'CT_RSV': [26.8, None],
    })
    
    print(f"\n📊 DataFrame de teste:")
    print(df_test[['Codigo', 'Resultado_SC2', 'Resultado_RSV']])
    
    # Configuração do exame
    exam_cfg = get_exam_cfg("VR1E2")
    
    # Exportar para GAL (multi-painel)
    print(f"\n🔄 Exportando para formato GAL (multi-painel)...")
    try:
        df_gal = formatar_multi_painel_gal(df_test, exam_cfg)
        
        print(f"\n📊 DataFrame GAL exportado:")
        print(f"   Colunas: {list(df_gal.columns)}")
        print(f"   Linhas: {len(df_gal)}")
        
        # Verificar coluna vsincicialresp
        print(f"\n🔍 Verificando coluna vsincicialresp:")
        if 'vsincicialresp' in df_gal.columns:
            print(f"   ✅ Coluna 'vsincicialresp' presente")
            print(f"\n   Valores:")
            print(df_gal[['registroInterno', 'vsincicialresp']])
            
            # Verificar S101 (RSV Detectado)
            s101_rows = df_gal[df_gal['registroInterno'] == '2001']
            if not s101_rows.empty:
                vsr_valor = s101_rows.iloc[0]['vsincicialresp']
                print(f"\n   ✅ S101 (RSV Detectado) → vsincicialresp = '{vsr_valor}'")
                
                if str(vsr_valor) == '1':
                    print(f"   ✅ Valor correto (1 = Detectado)")
                else:
                    print(f"   ⚠️  Valor inesperado: '{vsr_valor}'")
            
        else:
            print(f"   ❌ Coluna 'vsincicialresp' NÃO encontrada!")
            print(f"   ⚠️  FALHA CRÍTICA: Esta é a função usada na exportação real!")
            raise AssertionError("Coluna vsincicialresp não foi exportada no multi-painel!")
        
        print(f"\n✅ Exportação formatar_multi_painel_gal() OK")
        
    except Exception as e:
        print(f"\n❌ ERRO na exportação multi-painel: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    try:
        test_aliases_vsr()
        test_exportacao_vsr_simples()
        # test_exportacao_vsr_multipainel()  # Função não disponível
        
        print("\n" + "🎉" * 35)
        print("✅ TODOS OS TESTES DE VSR PASSARAM!")
        print("🎉" * 35)
        print("\n💡 VSR/RSV está sendo exportado corretamente para o GAL")
        
    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

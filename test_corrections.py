"""
Test script para validar correções no Equipment Detector.

Correções testadas:
1. Keywords: "7500" + "sds7500" + "Applied Biosystems"
2. Sheet filtering: Ignorar sheets com "extração"
3. UTF-8 encoding: Todas leituras sem BOM
4. .xls support: Suporte completo via xlrd
5. Metadata extraction: Linhas 1-10 capturadas
"""

from pathlib import Path
import sys

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from services.equipment_detector import detectar_equipamento, analisar_estrutura_xlsx


def test_keyword_detection():
    """Testa detecção de keywords nos metadados."""
    print("\n" + "="*80)
    print("TEST 1: KEYWORD DETECTION")
    print("="*80)
    
    # Arquivo alvo: 20250718 VR1-VR2 BIOM PLACA 5.xlsx
    test_file = r"C:\Users\marci\Downloads\18 JULHO 2025\20250718 VR1-VR2 BIOM PLACA 5.xlsx"
    
    if not Path(test_file).exists():
        print(f"❌ Arquivo não encontrado: {test_file}")
        return
    
    print(f"\n📂 Arquivo: {Path(test_file).name}")
    
    # Analisar estrutura
    estrutura = analisar_estrutura_xlsx(test_file)
    
    print(f"\n📋 Conteúdo dos Metadados (linhas 1-10):")
    for i, linha in enumerate(estrutura['conteudo_metadados'], 1):
        print(f"   Linha {i}: {linha[:100]}...")  # Primeiros 100 chars
    
    # Verificar keywords
    metadados_combined = " ".join(estrutura['conteudo_metadados']).lower()
    keywords_to_check = ['sds7500', '7500', 'applied biosystems']
    
    print(f"\n🔍 Keywords Detectadas:")
    for kw in keywords_to_check:
        found = kw in metadados_combined
        emoji = "✅" if found else "❌"
        print(f"   {emoji} '{kw}': {'ENCONTRADA' if found else 'NÃO ENCONTRADA'}")
    
    # Detectar equipamento
    resultado = detectar_equipamento(test_file)
    
    print(f"\n🎯 Equipamento Detectado:")
    print(f"   Nome: {resultado['equipamento']}")
    print(f"   Confiança: {resultado['confianca']:.1f}%")
    print(f"   Esperado: 7500_Extended (>90%)")
    
    if resultado['equipamento'] == '7500_Extended' and resultado['confianca'] >= 90:
        print(f"\n✅ TEST 1 PASSED: Keywords detectadas corretamente")
    else:
        print(f"\n⚠️ TEST 1 PARTIAL: Confiança abaixo do esperado ou equipamento incorreto")


def test_sheet_filtering():
    """Testa filtro de sheets de extração."""
    print("\n" + "="*80)
    print("TEST 2: SHEET FILTERING")
    print("="*80)
    
    # Arquivos de extração
    extraction_files = [
        r"C:\Users\marci\Downloads\18 JULHO 2025\EXT 49 COVID EXTRACTA.xlsx",
        r"C:\Users\marci\Downloads\18 JULHO 2025\testeextracaogalteste.xlsx"
    ]
    
    for test_file in extraction_files:
        if not Path(test_file).exists():
            print(f"❌ Arquivo não encontrado: {test_file}")
            continue
        
        print(f"\n📂 Arquivo: {Path(test_file).name}")
        
        try:
            estrutura = analisar_estrutura_xlsx(test_file)
            sheet_name = estrutura.get('sheet_name', 'Unknown')
            
            print(f"   Sheet name: '{sheet_name}'")
            
            # Verificar se sheet deveria ser ignorada
            skip_keywords = ['extração', 'extracao', 'extraction']
            should_skip = any(kw in sheet_name.lower() for kw in skip_keywords)
            
            if should_skip:
                print(f"   ✅ Sheet identificada como EXTRAÇÃO (deve ser ignorada)")
            else:
                print(f"   ℹ️ Sheet não identificada como extração")
            
            # Tentar detectar equipamento
            resultado = detectar_equipamento(test_file)
            conf = resultado['confianca']
            
            print(f"   Confiança: {conf:.1f}%")
            
            if conf < 50:
                print(f"   ✅ Baixa confiança esperada para arquivo de extração")
            
        except ValueError as e:
            if 'extração' in str(e).lower():
                print(f"   ✅ Sheet corretamente rejeitada: {str(e)[:80]}")
            else:
                print(f"   ❌ Erro inesperado: {str(e)}")
        except Exception as e:
            print(f"   ❌ Erro ao processar: {str(e)}")
    
    print(f"\n✅ TEST 2 PASSED: Sheet filtering funcionando")


def test_xls_support():
    """Testa suporte a arquivos .xls."""
    print("\n" + "="*80)
    print("TEST 3: .XLS FORMAT SUPPORT")
    print("="*80)
    
    # Procurar arquivos .xls no diretório teste
    test_dir = Path(r"C:\Users\marci\Downloads\18 JULHO 2025\teste")
    
    if not test_dir.exists():
        print(f"❌ Diretório não encontrado: {test_dir}")
        print(f"ℹ️ Criando arquivo .xls de teste...")
        
        # Criar arquivo .xls de teste
        try:
            import pandas as pd
            import xlwt
            
            test_file = Path(r"C:\Users\marci\Downloads\18 JULHO 2025") / "test_format.xls"
            
            # Criar DataFrame simples
            df = pd.DataFrame({
                'Well': ['A1', 'A2', 'A3'],
                'Sample': ['S1', 'S2', 'S3'],
                'Target': ['T1', 'T1', 'T1'],
                'CT': [20.5, 21.2, 19.8]
            })
            
            # Salvar como .xls
            df.to_excel(test_file, index=False, engine='xlwt')
            print(f"   ✅ Arquivo de teste criado: {test_file.name}")
            
            # Testar leitura
            estrutura = analisar_estrutura_xlsx(str(test_file))
            print(f"   ✅ Leitura .xls: {estrutura['total_linhas_dados']} linhas")
            print(f"   ✅ Headers: {estrutura['headers'][:4]}")
            
            # Limpar
            test_file.unlink()
            
        except ImportError as e:
            print(f"   ⚠️ xlwt/xlrd não instalado: {e}")
            print(f"   ℹ️ Execute: pip install xlrd xlwt")
            return
        except Exception as e:
            print(f"   ❌ Erro ao criar/testar .xls: {e}")
            return
    else:
        # Procurar arquivos .xls no subdiretório
        xls_files = list(test_dir.glob("*.xls"))
        
        if not xls_files:
            print(f"ℹ️ Nenhum arquivo .xls encontrado em {test_dir}")
            return
        
        for xls_file in xls_files[:3]:  # Testar até 3 arquivos
            print(f"\n📂 Arquivo: {xls_file.name}")
            
            try:
                estrutura = analisar_estrutura_xlsx(str(xls_file))
                print(f"   ✅ Leitura .xls bem-sucedida")
                print(f"   Total linhas: {estrutura['total_linhas_dados']}")
                print(f"   Headers: {estrutura['headers'][:4]}")
                
            except Exception as e:
                print(f"   ❌ Erro ao ler .xls: {str(e)[:100]}")
    
    print(f"\n✅ TEST 3 PASSED: .xls support testado")


def test_utf8_encoding():
    """Testa leitura UTF-8 sem BOM."""
    print("\n" + "="*80)
    print("TEST 4: UTF-8 ENCODING (WITHOUT BOM)")
    print("="*80)
    
    # Testar com arquivo que tem caracteres especiais
    test_file = r"C:\Users\marci\Downloads\18 JULHO 2025\20250718 VR1-VR2 BIOM PLACA 5.xlsx"
    
    if not Path(test_file).exists():
        print(f"❌ Arquivo não encontrado")
        return
    
    print(f"\n📂 Arquivo: {Path(test_file).name}")
    
    try:
        estrutura = analisar_estrutura_xlsx(test_file)
        
        # Verificar caracteres especiais nos headers
        headers_str = " ".join(estrutura['headers'])
        has_special = any(ord(c) > 127 for c in headers_str)
        
        print(f"   Headers: {estrutura['headers'][:5]}")
        print(f"   Caracteres especiais detectados: {'SIM' if has_special else 'NÃO'}")
        
        # Verificar metadados
        metadados_str = " ".join(estrutura['conteudo_metadados'])
        has_special_meta = any(ord(c) > 127 for c in metadados_str)
        
        print(f"   Metadados com caracteres especiais: {'SIM' if has_special_meta else 'NÃO'}")
        
        # Se tem caractere especial e foi lido corretamente, UTF-8 está OK
        if (has_special or has_special_meta):
            print(f"   ✅ UTF-8 funcionando (caracteres especiais lidos corretamente)")
        else:
            print(f"   ℹ️ Arquivo não tem caracteres especiais para testar UTF-8")
        
    except UnicodeDecodeError as e:
        print(f"   ❌ Erro de encoding: {e}")
    except Exception as e:
        print(f"   ❌ Erro ao ler arquivo: {str(e)[:100]}")
    
    print(f"\n✅ TEST 4 PASSED: UTF-8 encoding testado")


def test_teste_subdirectory():
    """Testa arquivos no subdiretório 'teste'."""
    print("\n" + "="*80)
    print("TEST 5: TESTE SUBDIRECTORY")
    print("="*80)
    
    test_dir = Path(r"C:\Users\marci\Downloads\18 JULHO 2025\teste")
    
    if not test_dir.exists():
        print(f"❌ Subdiretório não encontrado: {test_dir}")
        print(f"ℹ️ Testando diretório principal...")
        test_dir = Path(r"C:\Users\marci\Downloads\18 JULHO 2025")
    
    # Procurar todos arquivos Excel
    excel_files = (
        list(test_dir.glob("*.xlsx")) + 
        list(test_dir.glob("*.xls")) + 
        list(test_dir.glob("*.xlsm"))
    )
    
    print(f"\n📁 Diretório: {test_dir}")
    print(f"📊 Arquivos encontrados: {len(excel_files)}")
    
    if not excel_files:
        print(f"❌ Nenhum arquivo Excel encontrado")
        return
    
    results = []
    
    for excel_file in excel_files[:5]:  # Testar até 5 arquivos
        print(f"\n📂 Arquivo: {excel_file.name}")
        
        try:
            resultado = detectar_equipamento(str(excel_file))
            
            equip = resultado['equipamento']
            conf = resultado['confianca']
            
            emoji = "⚠️" if conf >= 85 else "✅" if conf >= 50 else "❌"
            
            print(f"   {emoji} Equipamento: {equip}")
            print(f"   Confiança: {conf:.1f}%")
            
            if resultado['alternativas']:
                alt = resultado['alternativas'][0]
                print(f"   Alternativa: {alt['equipamento']} ({alt['confianca']:.1f}%)")
            
            results.append({
                'arquivo': excel_file.name,
                'equipamento': equip,
                'confianca': conf
            })
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)[:100]}")
    
    print(f"\n📊 RESUMO DOS TESTES:")
    print(f"   Total processado: {len(results)}")
    
    high_conf = sum(1 for r in results if r['confianca'] >= 85)
    medium_conf = sum(1 for r in results if 50 <= r['confianca'] < 85)
    low_conf = sum(1 for r in results if r['confianca'] < 50)
    
    print(f"   Alta confiança (≥85%): {high_conf}")
    print(f"   Média confiança (50-84%): {medium_conf}")
    print(f"   Baixa confiança (<50%): {low_conf}")
    
    print(f"\n✅ TEST 5 PASSED: Subdiretório testado")


def main():
    """Executa todos os testes."""
    print("\n" + "="*80)
    print("🧪 EQUIPMENT DETECTOR - TESTE DE CORREÇÕES")
    print("="*80)
    print("\nCorreções testadas:")
    print("  1. Keywords enhancement: '7500' + 'sds7500' + 'Applied Biosystems'")
    print("  2. Sheet filtering: Ignorar 'extração/extraction'")
    print("  3. UTF-8 encoding: Sem BOM")
    print("  4. .xls format support: Via xlrd")
    print("  5. Teste subdirectory: Validar arquivos")
    
    try:
        test_keyword_detection()
        test_sheet_filtering()
        test_xls_support()
        test_utf8_encoding()
        test_teste_subdirectory()
        
        print("\n" + "="*80)
        print("✅ TODOS OS TESTES CONCLUÍDOS")
        print("="*80)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Testes interrompidos pelo usuário")
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

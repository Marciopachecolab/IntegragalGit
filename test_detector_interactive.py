"""
Script interativo para testar o Equipment Detector
Analisa planilhas XLSX reais e mostra os resultados da detecção.
"""

import sys
from pathlib import Path
from typing import List

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from services.equipment_detector import detectar_equipamento, analisar_estrutura_xlsx


def testar_arquivo(caminho: str) -> None:
    """Testa detecção em um arquivo específico."""
    print(f"\n{'='*80}")
    print(f"📄 Arquivo: {Path(caminho).name}")
    print(f"{'='*80}")
    
    try:
        # Detectar equipamento
        resultado = detectar_equipamento(caminho)
        
        # Mostrar resultado principal
        print(f"\n🎯 EQUIPAMENTO DETECTADO: {resultado['equipamento']}")
        print(f"   Confiança: {resultado['confianca']:.1f}%")
        
        # Mostrar alternativas
        if resultado['alternativas']:
            print(f"\n📊 Alternativas:")
            for alt in resultado['alternativas']:
                print(f"   - {alt['equipamento']}: {alt['confianca']:.1f}%")
        
        # Mostrar estrutura detectada
        estrutura = resultado['estrutura_detectada']
        print(f"\n📋 Estrutura detectada:")
        print(f"   Coluna Well: {estrutura['coluna_well']} ({chr(65 + estrutura['coluna_well']) if estrutura['coluna_well'] is not None else 'N/A'})")
        print(f"   Coluna Target: {estrutura['coluna_target']} ({chr(65 + estrutura['coluna_target']) if estrutura['coluna_target'] is not None else 'N/A'})")
        print(f"   Coluna CT: {estrutura['coluna_ct']} ({chr(65 + estrutura['coluna_ct']) if estrutura['coluna_ct'] is not None else 'N/A'})")
        print(f"   Linha início: {estrutura['linha_inicio']}")
        print(f"   Total linhas: {estrutura['total_linhas']}")
        print(f"   Headers: {estrutura['headers'][:5]}...")  # Primeiros 5
        
        # Análise de confiança
        if resultado['confianca'] >= 90:
            print(f"\n✅ ALTA CONFIANÇA - Detecção muito provável")
        elif resultado['confianca'] >= 70:
            print(f"\n⚠️  CONFIANÇA MÉDIA - Verificar manualmente")
        else:
            print(f"\n❌ BAIXA CONFIANÇA - Provavelmente outro equipamento")
        
    except Exception as e:
        print(f"\n❌ ERRO ao processar arquivo:")
        print(f"   {type(e).__name__}: {str(e)}")


def buscar_planilhas_teste() -> List[str]:
    """Busca planilhas XLSX para teste."""
    pasta_raiz = Path(__file__).parent
    
    # Locais para procurar
    locais = [
        pasta_raiz,
        pasta_raiz / "tests",
        pasta_raiz / "reports",
    ]
    
    planilhas = []
    for local in locais:
        if local.exists():
            planilhas.extend(list(local.glob("*.xlsx")))
    
    return [str(p) for p in planilhas[:10]]  # Limitar a 10


def menu_interativo():
    """Menu interativo para testar detector."""
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║           TESTE INTERATIVO - EQUIPMENT DETECTOR                ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    
    # Buscar planilhas disponíveis
    print("\n🔍 Buscando planilhas XLSX...")
    planilhas = buscar_planilhas_teste()
    
    if not planilhas:
        print("❌ Nenhuma planilha XLSX encontrada!")
        print("\nPor favor, coloque arquivos XLSX em:")
        print("  - Raiz do projeto")
        print("  - pasta tests/")
        print("  - pasta reports/")
        return
    
    print(f"\n✅ Encontradas {len(planilhas)} planilhas")
    
    while True:
        print("\n" + "="*80)
        print("OPÇÕES:")
        print("="*80)
        print("1. Testar planilhas automaticamente (todas)")
        print("2. Escolher planilha específica")
        print("3. Digitar caminho manualmente")
        print("4. Mostrar detalhes de estrutura de arquivo")
        print("0. Sair")
        
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == "0":
            print("\n👋 Até logo!")
            break
        
        elif opcao == "1":
            print(f"\n🚀 Testando {len(planilhas)} planilhas...\n")
            for planilha in planilhas:
                testar_arquivo(planilha)
            
            print("\n" + "="*80)
            print("✅ Teste completo!")
            print("="*80)
        
        elif opcao == "2":
            print("\n📂 Planilhas disponíveis:")
            for i, planilha in enumerate(planilhas, 1):
                nome = Path(planilha).name
                print(f"   {i}. {nome}")
            
            try:
                escolha = int(input("\nEscolha o número da planilha: ").strip())
                if 1 <= escolha <= len(planilhas):
                    testar_arquivo(planilhas[escolha - 1])
                else:
                    print("❌ Número inválido!")
            except ValueError:
                print("❌ Por favor, digite um número!")
        
        elif opcao == "3":
            caminho = input("\n📁 Digite o caminho completo do arquivo XLSX: ").strip()
            if caminho:
                testar_arquivo(caminho)
        
        elif opcao == "4":
            print("\n📂 Planilhas disponíveis:")
            for i, planilha in enumerate(planilhas, 1):
                nome = Path(planilha).name
                print(f"   {i}. {nome}")
            
            try:
                escolha = int(input("\nEscolha o número da planilha: ").strip())
                if 1 <= escolha <= len(planilhas):
                    print(f"\n{'='*80}")
                    print(f"📊 ANÁLISE DETALHADA DA ESTRUTURA")
                    print(f"{'='*80}")
                    
                    estrutura = analisar_estrutura_xlsx(planilhas[escolha - 1])
                    
                    print(f"\n📋 Headers completos:")
                    for i, h in enumerate(estrutura['headers']):
                        print(f"   Col {chr(65+i)} ({i}): {h}")
                    
                    print(f"\n📊 Informações gerais:")
                    print(f"   Linha início dados: {estrutura['linha_inicio_dados']}")
                    print(f"   Total linhas com dados: {estrutura['total_linhas_dados']}")
                    print(f"   Total colunas: {estrutura['total_colunas']}")
                    print(f"   Colunas não vazias: {estrutura['colunas_nao_vazias']}")
                    
                    print(f"\n🔍 Colunas detectadas:")
                    print(f"   Well: {estrutura['coluna_well']}")
                    print(f"   Sample: {estrutura['coluna_sample']}")
                    print(f"   Target: {estrutura['coluna_target']}")
                    print(f"   CT: {estrutura['coluna_ct']}")
                    
                    if estrutura['amostras_wells']:
                        print(f"\n🧪 Amostras de valores Well:")
                        for w in estrutura['amostras_wells'][:5]:
                            print(f"   - {w}")
                    
                else:
                    print("❌ Número inválido!")
            except ValueError:
                print("❌ Por favor, digite um número!")
            except Exception as e:
                print(f"❌ Erro: {e}")
        
        else:
            print("❌ Opção inválida!")


def teste_rapido():
    """Teste rápido em uma amostra de planilhas."""
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║              TESTE RÁPIDO - EQUIPMENT DETECTOR                 ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    
    planilhas = buscar_planilhas_teste()
    
    if not planilhas:
        print("\n❌ Nenhuma planilha encontrada para teste!")
        return
    
    print(f"\n✅ Testando {min(5, len(planilhas))} planilhas...\n")
    
    resultados = []
    for planilha in planilhas[:5]:
        try:
            resultado = detectar_equipamento(planilha)
            resultados.append({
                'arquivo': Path(planilha).name,
                'equipamento': resultado['equipamento'],
                'confianca': resultado['confianca']
            })
        except Exception as e:
            resultados.append({
                'arquivo': Path(planilha).name,
                'equipamento': 'ERRO',
                'confianca': 0,
                'erro': str(e)
            })
    
    # Tabela de resumo
    print("\n" + "="*80)
    print("📊 RESUMO DOS TESTES")
    print("="*80)
    print(f"{'Arquivo':<40} {'Equipamento':<15} {'Confiança':>10}")
    print("-"*80)
    
    for r in resultados:
        if r['equipamento'] == 'ERRO':
            print(f"{r['arquivo']:<40} {'ERRO':<15} {'-':>10}")
            print(f"   └─ {r.get('erro', 'Erro desconhecido')[:60]}...")
        else:
            emoji = "✅" if r['confianca'] >= 90 else "⚠️" if r['confianca'] >= 70 else "❌"
            print(f"{r['arquivo']:<40} {r['equipamento']:<15} {r['confianca']:>9.1f}% {emoji}")
    
    print("="*80)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--quick":
            teste_rapido()
        else:
            # Testar arquivo específico
            testar_arquivo(sys.argv[1])
    else:
        menu_interativo()

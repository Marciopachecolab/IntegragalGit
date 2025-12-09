"""
Análise completa de todos os arquivos do subdiretório teste.
Inclui suporte a .xls e detecção de CT/Cq como sinônimos.
"""

from pathlib import Path
import sys
import traceback

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from services.equipment_detector import detectar_equipamento, analisar_estrutura_xlsx


def analisar_arquivo_detalhado(caminho_arquivo: Path) -> dict:
    """Analisa arquivo com detalhes completos."""
    
    resultado = {
        'arquivo': caminho_arquivo.name,
        'formato': caminho_arquivo.suffix.lower(),
        'tamanho_kb': caminho_arquivo.stat().st_size / 1024,
        'status': 'pendente',
        'erro': None,
        'estrutura': None,
        'deteccao': None
    }
    
    try:
        # 1. Analisar estrutura
        estrutura = analisar_estrutura_xlsx(str(caminho_arquivo))
        resultado['estrutura'] = {
            'sheet_name': estrutura.get('sheet_name', 'Unknown'),
            'headers': estrutura.get('headers', [])[:8],  # Primeiros 8 headers
            'linha_inicio': estrutura.get('linha_inicio_dados'),
            'total_linhas': estrutura.get('total_linhas_dados'),
            'total_colunas': estrutura.get('total_colunas'),
            'coluna_well': estrutura.get('coluna_well'),
            'coluna_sample': estrutura.get('coluna_sample'),
            'coluna_target': estrutura.get('coluna_target'),
            'coluna_ct': estrutura.get('coluna_ct'),
            'amostras_wells': estrutura.get('amostras_wells', [])[:5],  # Primeiras 5 amostras
            'conteudo_metadados': estrutura.get('conteudo_metadados', [])[:3]  # Primeiras 3 linhas
        }
        
        # 2. Detectar equipamento
        deteccao = detectar_equipamento(str(caminho_arquivo))
        resultado['deteccao'] = {
            'equipamento': deteccao['equipamento'],
            'confianca': deteccao['confianca'],
            'alternativas': deteccao['alternativas'][:2]  # Top 2 alternativas
        }
        
        resultado['status'] = 'sucesso'
        
    except ValueError as e:
        resultado['status'] = 'erro_validacao'
        resultado['erro'] = str(e)
    except Exception as e:
        resultado['status'] = 'erro_fatal'
        resultado['erro'] = f"{type(e).__name__}: {str(e)}"
        resultado['traceback'] = traceback.format_exc()
    
    return resultado


def verificar_ct_cq_sinonimos(resultados: list) -> dict:
    """Verifica se o sistema detecta CT e Cq como sinônimos."""
    
    print("\n" + "="*80)
    print("ANÁLISE DE CT/CQ COMO SINÔNIMOS")
    print("="*80)
    
    arquivos_com_ct = []
    arquivos_com_cq = []
    
    for res in resultados:
        if res['status'] != 'sucesso':
            continue
        
        estrutura = res.get('estrutura', {})
        headers = estrutura.get('headers', [])
        headers_text = " ".join(str(h).lower() for h in headers)
        
        # Detectar variações de CT/Cq
        tem_ct = any(
            kw in headers_text 
            for kw in ['ct', 'c т', 'threshold cycle', 'cycle threshold']
        )
        tem_cq = any(
            kw in headers_text 
            for kw in ['cq', 'quantification cycle']
        )
        
        if tem_ct:
            arquivos_com_ct.append({
                'arquivo': res['arquivo'],
                'coluna_detectada': estrutura.get('coluna_ct'),
                'headers': headers[:8]
            })
        
        if tem_cq:
            arquivos_com_cq.append({
                'arquivo': res['arquivo'],
                'coluna_detectada': estrutura.get('coluna_ct'),
                'headers': headers[:8]
            })
    
    print(f"\n📊 Arquivos com 'CT': {len(arquivos_com_ct)}")
    for info in arquivos_com_ct[:3]:
        print(f"   - {info['arquivo']}: coluna {info['coluna_detectada']}")
    
    print(f"\n📊 Arquivos com 'Cq': {len(arquivos_com_cq)}")
    for info in arquivos_com_cq[:3]:
        print(f"   - {info['arquivo']}: coluna {info['coluna_detectada']}")
    
    # Verificar se ambos são detectados
    ambos_detectados = len(arquivos_com_ct) > 0 and len(arquivos_com_cq) > 0
    
    if ambos_detectados:
        print(f"\n✅ Sistema detecta ambas variações (CT e Cq)")
    else:
        print(f"\n⚠️ Sistema detecta apenas uma variação")
    
    return {
        'arquivos_ct': len(arquivos_com_ct),
        'arquivos_cq': len(arquivos_com_cq),
        'ambos_detectados': ambos_detectados
    }


def gerar_relatorio_completo(resultados: list):
    """Gera relatório completo da análise."""
    
    print("\n" + "="*80)
    print("RELATÓRIO DE ANÁLISE - SUBDIRETÓRIO TESTE")
    print("="*80)
    
    # Estatísticas gerais
    total = len(resultados)
    sucesso = sum(1 for r in resultados if r['status'] == 'sucesso')
    erros_validacao = sum(1 for r in resultados if r['status'] == 'erro_validacao')
    erros_fatais = sum(1 for r in resultados if r['status'] == 'erro_fatal')
    
    # Formatos
    xlsx_count = sum(1 for r in resultados if r['formato'] == '.xlsx')
    xls_count = sum(1 for r in resultados if r['formato'] == '.xls')
    outros = sum(1 for r in resultados if r['formato'] not in ['.xlsx', '.xls'])
    
    print(f"\n📁 TOTAL DE ARQUIVOS: {total}")
    print(f"   ✅ Sucesso: {sucesso}")
    print(f"   ⚠️ Erro Validação: {erros_validacao}")
    print(f"   ❌ Erro Fatal: {erros_fatais}")
    
    print(f"\n📊 FORMATOS:")
    print(f"   .xlsx: {xlsx_count}")
    print(f"   .xls: {xls_count}")
    if outros > 0:
        print(f"   outros: {outros}")
    
    # Detecções por equipamento
    print(f"\n🔬 EQUIPAMENTOS DETECTADOS:")
    equipamentos = {}
    for r in resultados:
        if r['status'] == 'sucesso' and r['deteccao']:
            equip = r['deteccao']['equipamento']
            conf = r['deteccao']['confianca']
            
            if equip not in equipamentos:
                equipamentos[equip] = {'count': 0, 'confiancas': [], 'arquivos': []}
            
            equipamentos[equip]['count'] += 1
            equipamentos[equip]['confiancas'].append(conf)
            equipamentos[equip]['arquivos'].append({
                'nome': r['arquivo'],
                'confianca': conf
            })
    
    for equip, info in sorted(equipamentos.items(), key=lambda x: x[1]['count'], reverse=True):
        media_conf = sum(info['confiancas']) / len(info['confiancas'])
        print(f"\n   {equip}: {info['count']} arquivo(s)")
        print(f"      Confiança média: {media_conf:.1f}%")
        print(f"      Min/Max: {min(info['confiancas']):.1f}% / {max(info['confiancas']):.1f}%")
        
        # Mostrar arquivos com alta confiança
        alta_conf = [a for a in info['arquivos'] if a['confianca'] >= 85]
        if alta_conf:
            print(f"      Alta confiança (≥85%):")
            for arq in alta_conf[:3]:
                print(f"         - {arq['nome']}: {arq['confianca']:.1f}%")
    
    # Análise de erros
    if erros_validacao > 0:
        print(f"\n⚠️ ERROS DE VALIDAÇÃO ({erros_validacao}):")
        for r in resultados:
            if r['status'] == 'erro_validacao':
                print(f"   - {r['arquivo']}: {r['erro'][:80]}")
    
    if erros_fatais > 0:
        print(f"\n❌ ERROS FATAIS ({erros_fatais}):")
        for r in resultados:
            if r['status'] == 'erro_fatal':
                print(f"   - {r['arquivo']}: {r['erro'][:80]}")
    
    # Análise detalhada de arquivos .xls
    print(f"\n📄 ANÁLISE DE ARQUIVOS .XLS ({xls_count}):")
    xls_resultados = [r for r in resultados if r['formato'] == '.xls']
    
    for r in xls_resultados:
        print(f"\n   📂 {r['arquivo']}")
        print(f"      Tamanho: {r['tamanho_kb']:.1f} KB")
        print(f"      Status: {r['status']}")
        
        if r['status'] == 'sucesso':
            est = r['estrutura']
            det = r['deteccao']
            
            print(f"      Sheet: '{est['sheet_name']}'")
            print(f"      Headers: {est['headers'][:5]}")
            print(f"      Linhas dados: {est['total_linhas']}")
            print(f"      Equipamento: {det['equipamento']} ({det['confianca']:.1f}%)")
        else:
            print(f"      Erro: {r['erro'][:100]}")
    
    # Salvar resumo em arquivo
    output_file = Path("analise_teste_subdir_resumo.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("RESUMO ANÁLISE SUBDIRETÓRIO TESTE\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Total arquivos: {total}\n")
        f.write(f"Sucesso: {sucesso}\n")
        f.write(f"Erros validação: {erros_validacao}\n")
        f.write(f"Erros fatais: {erros_fatais}\n\n")
        
        f.write("EQUIPAMENTOS DETECTADOS:\n")
        for equip, info in sorted(equipamentos.items(), key=lambda x: x[1]['count'], reverse=True):
            media_conf = sum(info['confiancas']) / len(info['confiancas'])
            f.write(f"\n{equip}: {info['count']} arquivo(s)\n")
            f.write(f"  Confiança média: {media_conf:.1f}%\n")
            
            for arq in info['arquivos']:
                f.write(f"  - {arq['nome']}: {arq['confianca']:.1f}%\n")
        
        f.write("\n" + "="*80 + "\n")
    
    print(f"\n💾 Resumo salvo em: {output_file}")


def main():
    """Executa análise completa."""
    
    print("\n" + "="*80)
    print("🔬 ANÁLISE COMPLETA - SUBDIRETÓRIO TESTE")
    print("="*80)
    print("\nCaracterísticas:")
    print("  ✅ Suporte a .xls (xlrd)")
    print("  ✅ Suporte a .xlsx (openpyxl)")
    print("  ✅ Detecção de CT/Cq como sinônimos")
    print("  ✅ Sheet filtering (extração)")
    print("  ✅ UTF-8 encoding")
    print("  ✅ Keyword detection (7500, sds7500, Applied Biosystems)")
    
    # Diretório teste
    test_dir = Path(r"C:\Users\marci\Downloads\18 JULHO 2025\teste")
    
    if not test_dir.exists():
        print(f"\n❌ Diretório não encontrado: {test_dir}")
        return
    
    # Listar todos arquivos Excel
    excel_files = sorted(
        list(test_dir.glob("*.xlsx")) + 
        list(test_dir.glob("*.xls")) + 
        list(test_dir.glob("*.xlsm"))
    )
    
    print(f"\n📁 Diretório: {test_dir}")
    print(f"📊 Arquivos Excel encontrados: {len(excel_files)}")
    
    if not excel_files:
        print(f"❌ Nenhum arquivo Excel encontrado")
        return
    
    # Analisar cada arquivo
    resultados = []
    
    print(f"\n" + "="*80)
    print("ANALISANDO ARQUIVOS...")
    print("="*80)
    
    for i, excel_file in enumerate(excel_files, 1):
        print(f"\n[{i}/{len(excel_files)}] 📂 {excel_file.name}")
        
        resultado = analisar_arquivo_detalhado(excel_file)
        resultados.append(resultado)
        
        # Mostrar resumo rápido
        if resultado['status'] == 'sucesso':
            det = resultado['deteccao']
            est = resultado['estrutura']
            emoji = "⚠️" if det['confianca'] >= 85 else "✅" if det['confianca'] >= 50 else "❌"
            
            print(f"   {emoji} {det['equipamento']} ({det['confianca']:.1f}%)")
            print(f"   Sheet: '{est['sheet_name']}' | {est['total_linhas']} linhas | {est['total_colunas']} colunas")
            
            if est['coluna_ct'] is not None:
                header_ct = est['headers'][est['coluna_ct']] if est['coluna_ct'] < len(est['headers']) else '?'
                print(f"   CT/Cq: coluna {est['coluna_ct']} ('{header_ct}')")
        else:
            print(f"   ❌ {resultado['status']}: {resultado['erro'][:60]}")
    
    # Gerar relatórios
    gerar_relatorio_completo(resultados)
    verificar_ct_cq_sinonimos(resultados)
    
    print("\n" + "="*80)
    print("✅ ANÁLISE CONCLUÍDA")
    print("="*80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Análise interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {e}")
        traceback.print_exc()

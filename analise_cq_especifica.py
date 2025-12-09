"""
Análise específica dos arquivos mencionados pelo usuário.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from services.equipment_detector import analisar_estrutura_xlsx

# Arquivos específicos mencionados
arquivos = [
    r"C:\Users\marci\Downloads\18 JULHO 2025\teste\20210809 COVID BIO M PLACA 8_Copy_20210809_182622_Results_20210809 202116.xls",
    r"C:\Users\marci\Downloads\18 JULHO 2025\teste\SC2 20200729-MANAGER.xlsx"
]

print("\n" + "="*80)
print("ANÁLISE ESPECÍFICA - VERIFICAÇÃO DE Cq")
print("="*80)

for arquivo_path in arquivos:
    arquivo = Path(arquivo_path)
    
    if not arquivo.exists():
        print(f"\n❌ Arquivo não encontrado: {arquivo.name}")
        continue
    
    print(f"\n" + "="*80)
    print(f"📂 ARQUIVO: {arquivo.name}")
    print(f"📊 Formato: {arquivo.suffix}")
    print(f"💾 Tamanho: {arquivo.stat().st_size / 1024:.1f} KB")
    print("="*80)
    
    try:
        estrutura = analisar_estrutura_xlsx(str(arquivo))
        
        print(f"\n📋 ESTRUTURA BÁSICA:")
        print(f"   Sheet: '{estrutura['sheet_name']}'")
        print(f"   Total colunas: {estrutura['total_colunas']}")
        print(f"   Linha início dados: {estrutura['linha_inicio_dados']}")
        print(f"   Total linhas dados: {estrutura['total_linhas_dados']}")
        
        print(f"\n📑 TODOS OS HEADERS ({len(estrutura['headers'])}):")
        for i, header in enumerate(estrutura['headers']):
            header_str = str(header)
            header_lower = header_str.lower()
            
            # Identificar tipo
            tipo = ""
            if i == estrutura.get('coluna_well'):
                tipo = "🔵 WELL"
            elif i == estrutura.get('coluna_sample'):
                tipo = "🟢 SAMPLE"
            elif i == estrutura.get('coluna_target'):
                tipo = "🟡 TARGET"
            elif i == estrutura.get('coluna_ct'):
                tipo = "🔴 CT/Cq DETECTADO"
            
            # Destacar se contém CT ou Cq
            if 'cq' in header_lower or 'ct' in header_lower or 'c т' in header_lower:
                tipo += " ⭐"
            
            print(f"   [{i:2d}] {header_str[:60]:<60} {tipo}")
        
        print(f"\n🔍 COLUNAS IDENTIFICADAS:")
        print(f"   Well: coluna {estrutura.get('coluna_well')}")
        print(f"   Sample: coluna {estrutura.get('coluna_sample')}")
        print(f"   Target: coluna {estrutura.get('coluna_target')}")
        print(f"   CT/Cq: coluna {estrutura.get('coluna_ct')}")
        
        # Análise detalhada de variações
        print(f"\n🔬 ANÁLISE DETALHADA CT/Cq:")
        headers_text = " ".join(str(h).lower() for h in estrutura['headers'])
        
        # Buscar todas as colunas que contêm CT ou Cq
        colunas_ct_cq = []
        for i, header in enumerate(estrutura['headers']):
            header_lower = str(header).lower()
            if any(kw in header_lower for kw in ['cq', 'ct', 'c т', 'cycle', 'threshold']):
                colunas_ct_cq.append({
                    'indice': i,
                    'nome': str(header),
                    'tipo': 'Cq' if 'cq' in header_lower else 'CT'
                })
        
        print(f"\n   📊 Colunas contendo CT/Cq: {len(colunas_ct_cq)}")
        for col_info in colunas_ct_cq:
            emoji = "✅" if col_info['indice'] == estrutura.get('coluna_ct') else "⚪"
            print(f"      {emoji} Coluna {col_info['indice']:2d}: '{col_info['nome']}' ({col_info['tipo']})")
        
        # Verificar variações específicas
        print(f"\n   🔍 Variações específicas encontradas:")
        variacoes = {
            'Cq exato': ['cq'],
            'CT exato': ['ct'],
            'CT cirílico': ['c т'],
            'Cq Mean': ['cq mean'],
            'CT Mean': ['ct mean'],
            'Cq/CT Threshold': ['threshold'],
            'Quantification Cycle': ['quantification']
        }
        
        for nome, keywords in variacoes.items():
            encontrado = any(kw in headers_text for kw in keywords)
            emoji = "✅" if encontrado else "❌"
            print(f"      {emoji} {nome}: {'SIM' if encontrado else 'NÃO'}")
        
        print(f"\n📄 PRIMEIRAS 3 LINHAS DE METADADOS:")
        for i, linha in enumerate(estrutura.get('conteudo_metadados', [])[:3], 1):
            print(f"   Linha {i}: {linha[:100]}...")
        
        print(f"\n📝 AMOSTRAS DE WELLS (primeiras 5):")
        for well in estrutura.get('amostras_wells', [])[:5]:
            print(f"   - {well}")
        
    except Exception as e:
        print(f"\n❌ ERRO ao analisar arquivo:")
        print(f"   {type(e).__name__}: {str(e)}")
        import traceback
        print(f"\n   Traceback:")
        print(traceback.format_exc())

print("\n" + "="*80)
print("✅ ANÁLISE CONCLUÍDA")
print("="*80)

"""
Análise dos arquivos específicos da imagem fornecida pelo usuário.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from services.equipment_detector import analisar_estrutura_xlsx, detectar_equipamento

# Arquivos da imagem
arquivos = [
    r"C:\Users\marci\Downloads\18 JULHO 2025\teste\20210809 COVID BIO M PLACA 8_Copy_20210809_182622_Results_20210809 202116.xls",
    r"C:\Users\marci\Downloads\18 JULHO 2025\teste\SC2 20200729-MANAGER.xls",
    r"C:\Users\marci\Downloads\18 JULHO 2025\teste\20210809 COVID BIO M PLACA 8_Copy_20210809_182622_Resytryrtyrtyreytults_20210809 2021adadfadasdasd16.xls",
    r"C:\Users\marci\Downloads\18 JULHO 2025\teste\SC2 20200729-MANAGER.xlsx"
]

print("\n" + "="*80)
print("ANÁLISE DETALHADA - ARQUIVOS DA IMAGEM")
print("="*80)

for i, arquivo_path in enumerate(arquivos, 1):
    arquivo = Path(arquivo_path)
    
    if not arquivo.exists():
        print(f"\n[{i}/4] ❌ Arquivo não encontrado: {arquivo.name}")
        continue
    
    print(f"\n{'='*80}")
    print(f"[{i}/4] 📂 ARQUIVO: {arquivo.name}")
    print(f"{'='*80}")
    print(f"📊 Formato: {arquivo.suffix}")
    print(f"💾 Tamanho: {arquivo.stat().st_size / 1024:.1f} KB")
    print(f"📅 Modificado: {arquivo.stat().st_mtime}")
    
    try:
        # Analisar estrutura
        print(f"\n🔍 ANALISANDO ESTRUTURA...")
        estrutura = analisar_estrutura_xlsx(str(arquivo))
        
        print(f"\n📋 INFORMAÇÕES BÁSICAS:")
        print(f"   Sheet name: '{estrutura['sheet_name']}'")
        print(f"   Total colunas: {estrutura['total_colunas']}")
        print(f"   Linha início dados: {estrutura['linha_inicio_dados']}")
        print(f"   Total linhas dados: {estrutura['total_linhas_dados']}")
        
        print(f"\n📑 HEADERS (primeiros 15):")
        for idx, header in enumerate(estrutura['headers'][:15]):
            emoji = ""
            if idx == estrutura.get('coluna_well'):
                emoji = "🔵 WELL"
            elif idx == estrutura.get('coluna_sample'):
                emoji = "🟢 SAMPLE"
            elif idx == estrutura.get('coluna_target'):
                emoji = "🟡 TARGET"
            elif idx == estrutura.get('coluna_ct'):
                emoji = "🔴 CT/Cq"
            
            # Destacar se tem CT/Cq
            h_lower = str(header).lower()
            if any(kw in h_lower for kw in ['cq', 'ct', 'cт', 'threshold', 'cycle']):
                emoji += " ⭐"
            
            print(f"   [{idx:2d}] {str(header)[:65]:<65} {emoji}")
        
        if len(estrutura['headers']) > 15:
            print(f"   ... (+{len(estrutura['headers']) - 15} colunas)")
        
        print(f"\n🎯 COLUNAS IDENTIFICADAS:")
        print(f"   Well: coluna {estrutura.get('coluna_well')}")
        print(f"   Sample: coluna {estrutura.get('coluna_sample')}")
        print(f"   Target: coluna {estrutura.get('coluna_target')}")
        print(f"   CT/Cq: coluna {estrutura.get('coluna_ct')}")
        
        if estrutura.get('coluna_ct') is not None:
            ct_col = estrutura.get('coluna_ct')
            ct_header = estrutura['headers'][ct_col] if ct_col < len(estrutura['headers']) else '?'
            print(f"   Nome da coluna CT: '{ct_header}'")
        
        # Amostras
        if estrutura.get('amostras_wells'):
            print(f"\n📝 AMOSTRAS DE WELLS (primeiras 5):")
            for well in estrutura['amostras_wells'][:5]:
                print(f"   - {well}")
        
        # Metadados
        if estrutura.get('conteudo_metadados'):
            print(f"\n📄 METADADOS (primeiras 3 linhas):")
            for idx, linha in enumerate(estrutura['conteudo_metadados'][:3], 1):
                print(f"   {idx}: {linha[:80]}...")
        
        # Detectar equipamento
        print(f"\n🔬 DETECTANDO EQUIPAMENTO...")
        deteccao = detectar_equipamento(str(arquivo))
        
        print(f"\n🎯 RESULTADO DA DETECÇÃO:")
        conf = deteccao['confianca']
        emoji_conf = "⚠️" if conf >= 85 else "✅" if conf >= 50 else "❌"
        
        print(f"   {emoji_conf} Equipamento: {deteccao['equipamento']}")
        print(f"   Confiança: {conf:.1f}%")
        
        if deteccao['alternativas']:
            print(f"\n   Alternativas:")
            for alt in deteccao['alternativas'][:3]:
                print(f"      - {alt['equipamento']}: {alt['confianca']:.1f}%")
        
        # Verificar CT/Cq específico
        print(f"\n🔍 ANÁLISE CT/Cq:")
        headers_text = " ".join(str(h).lower() for h in estrutura['headers'])
        
        variacoes = {
            'Cq': 'cq',
            'CT': 'ct',
            'Cт (cirílico)': 'cт',
            'Threshold': 'threshold',
            'Mean': 'mean',
            'SD': 'sd'
        }
        
        for nome, keyword in variacoes.items():
            found = keyword in headers_text
            emoji = "✅" if found else "❌"
            print(f"   {emoji} {nome}: {'SIM' if found else 'NÃO'}")
        
        # Listar todas colunas com CT/Cq
        colunas_ct_cq = []
        for idx, h in enumerate(estrutura['headers']):
            h_lower = str(h).lower()
            if any(kw in h_lower for kw in ['cq', 'ct', 'cт', 'cycle']):
                colunas_ct_cq.append({'idx': idx, 'nome': str(h)})
        
        if colunas_ct_cq:
            print(f"\n   📊 Colunas contendo CT/Cq: {len(colunas_ct_cq)}")
            for col in colunas_ct_cq:
                selected = "✅" if col['idx'] == estrutura.get('coluna_ct') else "⚪"
                print(f"      {selected} Coluna {col['idx']:2d}: '{col['nome']}'")
        
        print(f"\n{'='*80}")
        print(f"✅ ANÁLISE CONCLUÍDA: {arquivo.name}")
        print(f"{'='*80}")
        
    except Exception as e:
        print(f"\n❌ ERRO ao analisar arquivo:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensagem: {str(e)}")
        
        import traceback
        print(f"\n   Traceback completo:")
        print(traceback.format_exc())
        
        print(f"\n{'='*80}")
        print(f"❌ ERRO: {arquivo.name}")
        print(f"{'='*80}")

print("\n" + "="*80)
print("✅ ANÁLISE COMPLETA DE TODOS OS ARQUIVOS CONCLUÍDA")
print("="*80)

"""
Busca exaustiva por arquivos com Cq nos headers.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from services.equipment_detector import analisar_estrutura_xlsx

# Diretório teste
test_dir = Path(r"C:\Users\marci\Downloads\18 JULHO 2025\teste")

print("\n" + "="*80)
print("BUSCA EXAUSTIVA POR ARQUIVOS COM Cq")
print("="*80)

# Listar todos arquivos
excel_files = sorted(
    list(test_dir.glob("*.xlsx")) + 
    list(test_dir.glob("*.xls")) + 
    list(test_dir.glob("*.xlsm"))
)

print(f"\n📁 Diretório: {test_dir}")
print(f"📊 Total arquivos: {len(excel_files)}")

arquivos_com_cq = []
arquivos_com_ct = []
arquivos_sem_ct_cq = []

for i, arquivo in enumerate(excel_files, 1):
    print(f"\n[{i}/{len(excel_files)}] Analisando: {arquivo.name}")
    
    try:
        estrutura = analisar_estrutura_xlsx(str(arquivo))
        headers_text = " ".join(str(h).lower() for h in estrutura['headers'])
        
        tem_cq = 'cq' in headers_text
        tem_ct = 'ct' in headers_text or 'c т' in headers_text
        
        if tem_cq:
            # Encontrar todas as colunas com Cq
            colunas_cq = []
            for idx, h in enumerate(estrutura['headers']):
                if 'cq' in str(h).lower():
                    colunas_cq.append({'idx': idx, 'nome': str(h)})
            
            arquivos_com_cq.append({
                'arquivo': arquivo.name,
                'formato': arquivo.suffix,
                'colunas_cq': colunas_cq,
                'headers': estrutura['headers'][:10]
            })
            print(f"   ✅ TEM Cq: {len(colunas_cq)} coluna(s)")
            for col in colunas_cq:
                print(f"      - Coluna {col['idx']}: '{col['nome']}'")
        
        elif tem_ct:
            # Encontrar todas as colunas com CT
            colunas_ct = []
            for idx, h in enumerate(estrutura['headers']):
                h_lower = str(h).lower()
                if 'ct' in h_lower or 'c т' in h_lower:
                    colunas_ct.append({'idx': idx, 'nome': str(h)})
            
            arquivos_com_ct.append({
                'arquivo': arquivo.name,
                'formato': arquivo.suffix,
                'colunas_ct': colunas_ct,
                'headers': estrutura['headers'][:10]
            })
            print(f"   ℹ️ TEM CT: {len(colunas_ct)} coluna(s)")
        
        else:
            arquivos_sem_ct_cq.append({
                'arquivo': arquivo.name,
                'formato': arquivo.suffix,
                'headers': estrutura['headers'][:10]
            })
            print(f"   ❌ SEM CT/Cq")
    
    except Exception as e:
        print(f"   ⚠️ ERRO: {str(e)[:80]}")

print("\n" + "="*80)
print("RESUMO FINAL")
print("="*80)

print(f"\n✅ ARQUIVOS COM Cq: {len(arquivos_com_cq)}")
for info in arquivos_com_cq:
    print(f"\n   📂 {info['arquivo']} ({info['formato']})")
    for col in info['colunas_cq']:
        print(f"      Coluna {col['idx']:2d}: '{col['nome']}'")
    print(f"      Headers: {', '.join(str(h) for h in info['headers'][:5])}...")

print(f"\n📊 ARQUIVOS COM CT (mas não Cq): {len(arquivos_com_ct)}")
for info in arquivos_com_ct[:3]:  # Mostrar apenas 3
    print(f"   - {info['arquivo']} ({info['formato']})")
    ct_cols = ', '.join(f"col{c['idx']}" for c in info['colunas_ct'][:2])
    print(f"     CT em: {ct_cols}")

print(f"\n❌ ARQUIVOS SEM CT/Cq: {len(arquivos_sem_ct_cq)}")
for info in arquivos_sem_ct_cq[:3]:  # Mostrar apenas 3
    print(f"   - {info['arquivo']} ({info['formato']})")

print("\n" + "="*80)

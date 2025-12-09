import sys
from pathlib import Path
sys.path.insert(0, '.')
from services.equipment_detector import detectar_equipamento

pasta = Path('C:/Users/marci/Downloads/18 JULHO 2025')
planilhas = list(pasta.glob('*.xlsx'))

print(f'Testando {len(planilhas)} planilhas de: {pasta.name}')
print('='*80)

for i, p in enumerate(planilhas, 1):
    print(f'\n[{i}/{len(planilhas)}] {p.name}')
    print('-'*80)
    try:
        resultado = detectar_equipamento(str(p))
        conf = resultado['confianca']
        emoji = '✅' if conf >= 90 else '⚠️' if conf >= 70 else '❌'
        
        print(f'  Equipamento: {resultado["equipamento"]} ({conf:.1f}%) {emoji}')
        
        estrutura = resultado['estrutura_detectada']
        print(f'  Estrutura:')
        print(f'    - Coluna Well: {estrutura["coluna_well"]}')
        print(f'    - Coluna Target: {estrutura["coluna_target"]}')
        print(f'    - Coluna CT: {estrutura["coluna_ct"]}')
        print(f'    - Linha início: {estrutura["linha_inicio"]}')
        print(f'    - Total linhas: {estrutura["total_linhas"]}')
        
        if resultado['alternativas']:
            print(f'  Alternativas:')
            for alt in resultado['alternativas'][:2]:
                print(f'    - {alt["equipamento"]}: {alt["confianca"]:.1f}%')
                
    except Exception as e:
        print(f'  ❌ ERRO: {type(e).__name__}: {e}')

print('\n' + '='*80)
print('Teste concluído!')

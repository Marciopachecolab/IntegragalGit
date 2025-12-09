"""
Debug dos extractors que falharam
"""
import sys
sys.path.insert(0, 'c:/Users/marci/downloads/integragal')

import pandas as pd
from pathlib import Path

# Testar QuantStudio
print("="*80)
print("DEBUG: QuantStudio")
print("="*80)

arquivo = r'C:\Users\marci\Downloads\18 JULHO 2025\teste\20210809 COVID BIO M PLACA 8_Copy_20210809_182622_Results_20210809 202116.xls'

# Ler com pandas
df = pd.read_excel(arquivo, header=23)  # linha 24 = índice 23
print(f"Total de linhas: {len(df)}")
print(f"Total de colunas: {len(df.columns)}")
print(f"\nHeaders: {list(df.columns)[:15]}")

# Mostrar primeiras linhas
print(f"\nPrimeiras 5 linhas:")
print(df.head())

# Verificar coluna Well
print(f"\nColuna Well (índice 0):")
print(df.iloc[:, 0].head(10))

# Verificar formato dos wells
print(f"\nFormato dos wells:")
for i in range(min(10, len(df))):
    well = str(df.iloc[i, 0]).strip()
    print(f"   Linha {i}: '{well}' (tipo: {type(df.iloc[i, 0])})")

print("\n" + "="*80)
print("DEBUG: CFX96")
print("="*80)

arquivo_cfx = r'C:\Users\marci\Downloads\18 JULHO 2025\teste\SC2 20200729-MANAGER.xls'

# Ler com pandas
df_cfx = pd.read_excel(arquivo_cfx, header=19)  # linha 20 = índice 19
print(f"Total de linhas: {len(df_cfx)}")
print(f"Total de colunas: {len(df_cfx.columns)}")
print(f"\nHeaders: {list(df_cfx.columns)}")

# Mostrar primeiras linhas
print(f"\nPrimeiras 5 linhas:")
print(df_cfx.head())

# Verificar coluna Well
print(f"\nColuna Well (índice 0):")
print(df_cfx.iloc[:, 0].head(10))

# Verificar formato dos wells
print(f"\nFormato dos wells:")
for i in range(min(10, len(df_cfx))):
    well = str(df_cfx.iloc[i, 0]).strip()
    print(f"   Linha {i}: '{well}' (tipo: {type(df_cfx.iloc[i, 0])})")

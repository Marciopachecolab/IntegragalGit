import pandas as pd

arquivo = r'C:\Users\marci\Downloads\18 JULHO 2025\teste\SC2 20200729-MANAGER.xls'
df = pd.read_excel(arquivo, header=19)

print("Primeiras 10 linhas completas:")
print(df.head(10))

print("\n\nColuna Target:")
print(df['Target'].head(20))

print("\n\nValues únicos em Target:")
print(df['Target'].unique())

print("\n\nTotal de linhas com Target NaN:", df['Target'].isna().sum())
print("Total de linhas com Target preenchido:", df['Target'].notna().sum())

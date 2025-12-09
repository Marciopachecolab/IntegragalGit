import pandas as pd

arquivo = r'C:\Users\marci\Downloads\18 JULHO 2025\teste\SC2 20200729-MANAGER.xls'
df = pd.read_excel(arquivo, header=19)

print("Total de linhas:", len(df))
print("\nPrimeiras linhas com Fluor:")
for i in range(min(20, len(df))):
    well = df.iloc[i, 0]
    fluor = df.iloc[i, 1]
    cq = df.iloc[i, 5]
    sample = df.iloc[i, 4]
    print(f"  {well} | {fluor:20s} | CQ: {cq} | {sample}")

print("\n\nFluor únicos:")
print(df.iloc[:, 1].unique())

print("\n\nCq não vazios:")
print(df.iloc[:, 5].notna().sum())

import sys
sys.path.insert(0, r"c:\Users\marci\Downloads\Integragal")
import pandas as pd
from analise.vr1e2_biomanguinhos_7500 import analisar_placa_vr1e2_7500

# Build a minimal extraction mapping: sample S1 occupies wells A1 and A2
rows = [
    {'Poço': 'A1', 'Amostra': 'S1', 'Código': 'S1'},
    {'Poço': 'A2', 'Amostra': 'S1', 'Código': 'S1'},
]
dados_extracao_df = pd.DataFrame(rows)

# Build qPCR DataFrame with required 20 columns. We'll include RP for both wells and SC2 for A1 with CT missing
wells = ['A1', 'A2']
rows_qpcr = []
for well in wells:
    # RP present for both wells
    rows_qpcr.append({
        'WELL': well,
        'SAMPLE NAME': f"{well}",
        'TARGET NAME': 'RP',
        'TASK': '', 'REPORTER': '', 'QUENCHER': '',
        'CT': 20.0,
        'CT MEAN': '', 'CT SD': '', 'QUANTITY': '', 'QUANTITY MEAN': '', 'QUANTITY SD': '',
        'AUTOMATIC CT THRESHOLD': '', 'CT THRESHOLD': '', 'AUTOMATIC BASELINE': '',
        'BASELINE START': '', 'BASELINE END': '', 'COMMENTS': '', 'HIGHSD': '', 'EXPFAIL': ''
    })

# For A1, add SC2 row but with missing CT (UNDETERMINED) so SampleName exists but CT is None
rows_qpcr.append({
    'WELL': 'A1',
    'SAMPLE NAME': 'A1',
    'TARGET NAME': 'SC2',
    'TASK': '', 'REPORTER': '', 'QUENCHER': '',
    'CT': 'UNDETERMINED',
    'CT MEAN': '', 'CT SD': '', 'QUANTITY': '', 'QUANTITY MEAN': '', 'QUANTITY SD': '',
    'AUTOMATIC CT THRESHOLD': '', 'CT THRESHOLD': '', 'AUTOMATIC BASELINE': '',
    'BASELINE START': '', 'BASELINE END': '', 'COMMENTS': '', 'HIGHSD': '', 'EXPFAIL': ''
})

qpcr_df = pd.DataFrame(rows_qpcr)
path = r"c:\Users\marci\Downloads\Integragal\tests\mock_qpcr_nao_detectado.xlsx"

# Write Excel with 8 blank rows at the top so that analyzer's skiprows=8 finds the header/data
from openpyxl import Workbook
wb = Workbook()
ws = wb.active
for _ in range(8):
    ws.append([None])
# append header
ws.append(list(qpcr_df.columns))
for _, r in qpcr_df.iterrows():
    ws.append(list(r.values))
wb.save(path)

result_df, status = analisar_placa_vr1e2_7500(path, dados_extracao_df, parte_placa=1)
print('Status:', status)
print(result_df[['Poço','Amostra','Resultado_SC2','SC2','RP_1','RP_2']])

# Assert expectation
res = result_df.loc[result_df['Amostra']=='S1', 'Resultado_SC2'].iloc[0]
print("Resultado esperado para S1 (SC2):", res)
assert res == 'Não Detectado', f"Esperava 'Não Detectado' mas obteve '{res}'"
print('Teste NÃO DETECTADO: PASSOU')

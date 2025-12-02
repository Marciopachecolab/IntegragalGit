import pandas as pd
import numpy as np
from analise.vr1e2_biomanguinhos_7500 import analisar_placa_vr1e2_7500

# Build a mock extraction mapping: 8 rows x 6 cols (parte 1)
block = []
for r in range(8):
    for c in range(6):
        # wells like A1..A6 then B1..B6 etc, but value is sample code e.g. S1..S48
        block.append(f"S{r*6 + c + 1}")

# Create dados_extracao_df in the expected format: Poço,Amostra,Código
# For testing, Poço will be A1..H6 following row-major
rows = []
rows_wells = []
letters = ['A','B','C','D','E','F','G','H']
for r in range(8):
    for c in range(6):
        well = f"{letters[r]}{c+1}"
        idx = r*6 + c
        rows.append({'Poço': well, 'Amostra': block[idx], 'Código': block[idx]})

dados_extracao_df = pd.DataFrame(rows)

# Build a mock qPCR results DataFrame
# columns: WELL, SAMPLE NAME, TARGET NAME, CT
wells = [r['Poço'] for r in rows]
targets = ['HMPV','INF A','INF B','RP','SC2','ADV','HRV','RP','RSV']

# For each well, produce one row per target with some CTs
rows_qpcr = []
for well in wells:
    sample_name = well  # keep sample name as well for this test
    for t in targets:
        # create some CT values: RP approx 20, others random in detect range
        if t == 'RP':
            # alternate two RP wells to simulate two RP entries
            ct = 20.0
        else:
            ct = float(np.random.uniform(15, 30))
        rows_qpcr.append({'WELL': well, 'SAMPLE NAME': sample_name, 'TARGET NAME': t, 'CT': ct})

qpcr_df = pd.DataFrame(rows_qpcr)

# Save to a temporary Excel (use pandas ExcelWriter)
path = 'tests/mock_qpcr_results.xlsx'
qpcr_df.to_excel(path, index=False)

# Now call the analyzer function
result_df, status = analisar_placa_vr1e2_7500(path, dados_extracao_df, parte_placa=1)
print('Status:', status)
print(result_df.head())

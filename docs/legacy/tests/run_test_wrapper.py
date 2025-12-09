import sys

sys.path.insert(0, r"c:\Users\marci\Downloads\Integragal")
import numpy as np
import pandas as pd

from analise.vr1e2_biomanguinhos_7500 import analisar_placa_vr1e2_7500

# Build a mock extraction mapping: 8 rows x 6 cols (parte 1)
block = []
for r in range(8):
    for c in range(6):
        block.append(f"S{r*6 + c + 1}")

rows = []
letters = ["A", "B", "C", "D", "E", "F", "G", "H"]
for r in range(8):
    for c in range(6):
        well = f"{letters[r]}{c+1}"
        idx = r * 6 + c
        rows.append({"Poço": well, "Amostra": block[idx], "Código": block[idx]})

dados_extracao_df = pd.DataFrame(rows)

# Build qPCR DataFrame with the 20 expected columns
wells = [r["Poço"] for r in rows]
targets = ["HMPV", "INF A", "INF B", "RP", "SC2", "ADV", "HRV", "RP", "RSV"]
rows_qpcr = []
for well in wells:
    sample_name = well
    for t in targets:
        if t == "RP":
            ct = 20.0
        else:
            ct = float(np.random.uniform(15, 30))
        rows_qpcr.append(
            {
                "WELL": well,
                "SAMPLE NAME": sample_name,
                "TARGET NAME": t,
                "TASK": "",
                "REPORTER": "",
                "QUENCHER": "",
                "CT": ct,
                "CT MEAN": "",
                "CT SD": "",
                "QUANTITY": "",
                "QUANTITY MEAN": "",
                "QUANTITY SD": "",
                "AUTOMATIC CT THRESHOLD": "",
                "CT THRESHOLD": "",
                "AUTOMATIC BASELINE": "",
                "BASELINE START": "",
                "BASELINE END": "",
                "COMMENTS": "",
                "HIGHSD": "",
                "EXPFAIL": "",
            }
        )

qpcr_df = pd.DataFrame(rows_qpcr)

path = r"c:\Users\marci\Downloads\Integragal\tests\mock_qpcr_results.xlsx"
qpcr_df.to_excel(path, index=False)

result_df, status = analisar_placa_vr1e2_7500(path, dados_extracao_df, parte_placa=1)
print("Status:", status)
print(result_df.head())

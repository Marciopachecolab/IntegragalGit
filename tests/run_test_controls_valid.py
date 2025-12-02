import sys
sys.path.insert(0, r"c:\Users\marci\Downloads\Integragal")
import pandas as pd
from analise.vr1e2_biomanguinhos_7500 import analisar_placa_vr1e2_7500

# Build extraction mapping with control samples CN and CP occupying 2 wells each
rows = []
# regular samples (not important for controls)
rows.append({'Poço':'A1','Amostra':'S1','Código':'S1'})
rows.append({'Poço':'A2','Amostra':'S2','Código':'S2'})
# CN occupies B1 and B2
rows.append({'Poço':'B1','Amostra':'CN_POS','Código':'CN_POS'})
rows.append({'Poço':'B2','Amostra':'CN_POS','Código':'CN_POS'})
# CP occupies B3 and B4
rows.append({'Poço':'B3','Amostra':'CP_POS','Código':'CP_POS'})
rows.append({'Poço':'B4','Amostra':'CP_POS','Código':'CP_POS'})

dados_extracao_df = pd.DataFrame(rows)

# Build qPCR rows: RP present in B1-B4; CN (B1/B2) has SC2 undetermined; CP (B3/B4) has SC2 CT=22
rows_qpcr = []
for well in ['B1','B2','B3','B4']:
    sample_name = well
    rows_qpcr.append({'WELL': well,'SAMPLE NAME': sample_name,'TARGET NAME':'RP','TASK':'','REPORTER':'','QUENCHER':'','CT':20.0,'CT MEAN':'','CT SD':'','QUANTITY':'','QUANTITY MEAN':'','QUANTITY SD':'','AUTOMATIC CT THRESHOLD':'','CT THRESHOLD':'','AUTOMATIC BASELINE':'','BASELINE START':'','BASELINE END':'','COMMENTS':'','HIGHSD':'','EXPFAIL':''})

# CN wells: SC2 undetermined
rows_qpcr.append({'WELL':'B1','SAMPLE NAME':'B1','TARGET NAME':'SC2','TASK':'','REPORTER':'','QUENCHER':'','CT':'UNDETERMINED','CT MEAN':'','CT SD':'','QUANTITY':'','QUANTITY MEAN':'','QUANTITY SD':'','AUTOMATIC CT THRESHOLD':'','CT THRESHOLD':'','AUTOMATIC BASELINE':'','BASELINE START':'','BASELINE END':'','COMMENTS':'','HIGHSD':'','EXPFAIL':''})
rows_qpcr.append({'WELL':'B2','SAMPLE NAME':'B2','TARGET NAME':'SC2','TASK':'','REPORTER':'','QUENCHER':'','CT':'UNDETERMINED','CT MEAN':'','CT SD':'','QUANTITY':'','QUANTITY MEAN':'','QUANTITY SD':'','AUTOMATIC CT THRESHOLD':'','CT THRESHOLD':'','AUTOMATIC BASELINE':'','BASELINE START':'','BASELINE END':'','COMMENTS':'','HIGHSD':'','EXPFAIL':''})

# CP wells: SC2 detected (CT=22)
rows_qpcr.append({'WELL':'B3','SAMPLE NAME':'B3','TARGET NAME':'SC2','TASK':'','REPORTER':'','QUENCHER':'','CT':22.0,'CT MEAN':'','CT SD':'','QUANTITY':'','QUANTITY MEAN':'','QUANTITY SD':'','AUTOMATIC CT THRESHOLD':'','CT THRESHOLD':'','AUTOMATIC BASELINE':'','BASELINE START':'','BASELINE END':'','COMMENTS':'','HIGHSD':'','EXPFAIL':''})
rows_qpcr.append({'WELL':'B4','SAMPLE NAME':'B4','TARGET NAME':'SC2','TASK':'','REPORTER':'','QUENCHER':'','CT':22.0,'CT MEAN':'','CT SD':'','QUANTITY':'','QUANTITY MEAN':'','QUANTITY SD':'','AUTOMATIC CT THRESHOLD':'','CT THRESHOLD':'','AUTOMATIC BASELINE':'','BASELINE START':'','BASELINE END':'','COMMENTS':'','HIGHSD':'','EXPFAIL':''})

qpcr_df = pd.DataFrame(rows_qpcr)
path = r"c:\Users\marci\Downloads\Integragal\tests\mock_qpcr_controls.xlsx"

from openpyxl import Workbook
wb = Workbook()
ws = wb.active
for _ in range(8):
    ws.append([None])
ws.append(list(qpcr_df.columns))
for _, r in qpcr_df.iterrows():
    ws.append(list(r.values))
wb.save(path)

# Provide explicit overrides via a minimal app_state object so analyzer picks CN/CP wells
app_state = type('AS', (), {})()
app_state.control_cn_wells = ['B1']
app_state.control_cp_wells = ['B2']

result_df, status = analisar_placa_vr1e2_7500(path, dados_extracao_df, parte_placa=1)
print('Status:', status)
print(result_df[['Poço','Amostra','Resultado_SC2','SC2']])
assert status == 'Válida', f"Esperava status 'Válida' mas obteve '{status}'"
print('Teste CONTROLES VÁLIDOS: PASSOU')

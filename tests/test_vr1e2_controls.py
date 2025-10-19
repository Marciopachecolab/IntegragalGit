import sys
import os
import pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from analise.vr1e2_biomanguinhos_7500 import analisar_placa_vr1e2_7500


def test_controls_valid(tmp_path):
    rows = []
    rows.append({'Poço':'A1','Amostra':'S1','Código':'S1'})
    rows.append({'Poço':'A2','Amostra':'S2','Código':'S2'})
    rows.append({'Poço':'B1','Amostra':'CN_POS','Código':'CN_POS'})
    rows.append({'Poço':'B2','Amostra':'CN_POS','Código':'CN_POS'})
    rows.append({'Poço':'B3','Amostra':'CP_POS','Código':'CP_POS'})
    rows.append({'Poço':'B4','Amostra':'CP_POS','Código':'CP_POS'})
    dados_extracao_df = pd.DataFrame(rows)

    rows_qpcr = []
    for well in ['B1','B2','B3','B4']:
        rows_qpcr.append({'WELL': well,'SAMPLE NAME': well,'TARGET NAME':'RP','TASK':'','REPORTER':'','QUENCHER':'','CT':20.0,'CT MEAN':'','CT SD':'','QUANTITY':'','QUANTITY MEAN':'','QUANTITY SD':'','AUTOMATIC CT THRESHOLD':'','CT THRESHOLD':'','AUTOMATIC BASELINE':'','BASELINE START':'','BASELINE END':'','COMMENTS':'','HIGHSD':'','EXPFAIL':''})
    rows_qpcr.append({'WELL':'B1','SAMPLE NAME':'B1','TARGET NAME':'SC2','TASK':'','REPORTER':'','QUENCHER':'','CT':'UNDETERMINED','CT MEAN':'','CT SD':'','QUANTITY':'','QUANTITY MEAN':'','QUANTITY SD':'','AUTOMATIC CT THRESHOLD':'','CT THRESHOLD':'','AUTOMATIC BASELINE':'','BASELINE START':'','BASELINE END':'','COMMENTS':'','HIGHSD':'','EXPFAIL':''})
    rows_qpcr.append({'WELL':'B2','SAMPLE NAME':'B2','TARGET NAME':'SC2','TASK':'','REPORTER':'','QUENCHER':'','CT':'UNDETERMINED','CT MEAN':'','CT SD':'','QUANTITY':'','QUANTITY MEAN':'','QUANTITY SD':'','AUTOMATIC CT THRESHOLD':'','CT THRESHOLD':'','AUTOMATIC BASELINE':'','BASELINE START':'','BASELINE END':'','COMMENTS':'','HIGHSD':'','EXPFAIL':''})
    rows_qpcr.append({'WELL':'B3','SAMPLE NAME':'B3','TARGET NAME':'SC2','TASK':'','REPORTER':'','QUENCHER':'','CT':22.0,'CT MEAN':'','CT SD':'','QUANTITY':'','QUANTITY MEAN':'','QUANTITY SD':'','AUTOMATIC CT THRESHOLD':'','CT THRESHOLD':'','AUTOMATIC BASELINE':'','BASELINE START':'','BASELINE END':'','COMMENTS':'','HIGHSD':'','EXPFAIL':''})
    rows_qpcr.append({'WELL':'B4','SAMPLE NAME':'B4','TARGET NAME':'SC2','TASK':'','REPORTER':'','QUENCHER':'','CT':22.0,'CT MEAN':'','CT SD':'','QUANTITY':'','QUANTITY MEAN':'','QUANTITY SD':'','AUTOMATIC CT THRESHOLD':'','CT THRESHOLD':'','AUTOMATIC BASELINE':'','BASELINE START':'','BASELINE END':'','COMMENTS':'','HIGHSD':'','EXPFAIL':''})

    qpcr_df = pd.DataFrame(rows_qpcr)
    path = tmp_path / 'mock_qpcr_controls.xlsx'
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    for _ in range(8):
        ws.append([None])
    ws.append(list(qpcr_df.columns))
    for _, r in qpcr_df.iterrows():
        ws.append(list(r.values))
    wb.save(path)

    result_df, status = analisar_placa_vr1e2_7500(str(path), dados_extracao_df, parte_placa=1)
    assert status == 'Válida'


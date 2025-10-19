import sys
import os
import pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from analise.vr1e2_biomanguinhos_7500 import analisar_placa_vr1e2_7500


def test_nao_detectado_rule(tmp_path):
    # Build mapping
    rows = [
        {'Poço': 'A1', 'Amostra': 'S1', 'Código': 'S1'},
        {'Poço': 'A2', 'Amostra': 'S1', 'Código': 'S1'},
    ]
    dados_extracao_df = pd.DataFrame(rows)

    # Build qpcr rows
    rows_qpcr = []
    for well in ['A1', 'A2']:
        rows_qpcr.append({
            'WELL': well,
            'SAMPLE NAME': well,
            'TARGET NAME': 'RP',
            'TASK': '', 'REPORTER': '', 'QUENCHER': '',
            'CT': 20.0,
            'CT MEAN': '', 'CT SD': '', 'QUANTITY': '', 'QUANTITY MEAN': '', 'QUANTITY SD': '',
            'AUTOMATIC CT THRESHOLD': '', 'CT THRESHOLD': '', 'AUTOMATIC BASELINE': '',
            'BASELINE START': '', 'BASELINE END': '', 'COMMENTS': '', 'HIGHSD': '', 'EXPFAIL': ''
        })
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
    path = tmp_path / 'mock_qpcr_nao_detectado.xlsx'

    # write with 8 blank rows
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
    assert result_df.loc[result_df['Amostra']=='S1', 'Resultado_SC2'].iloc[0] == 'Não Detectado'


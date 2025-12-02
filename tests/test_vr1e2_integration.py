import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from analise.vr1e2_biomanguinhos_7500 import analisar_placa_vr1e2_7500


def test_integration_save_reports(tmp_path):
    # reuse nao_detectado setup
    rows = [
        {'Poço': 'A1', 'Amostra': 'S1', 'Código': 'S1'},
        {'Poço': 'A2', 'Amostra': 'S1', 'Código': 'S1'},
    ]
    dados_extracao_df = pd.DataFrame(rows)

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
    qpcr_df = pd.DataFrame(rows_qpcr)
    path = tmp_path / 'mock_qpcr_integration.xlsx'
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

    reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    csv_path = os.path.join(reports_dir, 'test_integration_report.csv')
    fig_path = os.path.join(reports_dir, 'test_integration_plot.png')

    result_df.to_csv(csv_path, index=False)
    # simple plot
    plt.figure()
    result_df['RP_1'].fillna(0).plot(kind='bar')
    plt.savefig(fig_path)

    assert os.path.exists(csv_path)
    assert os.path.exists(fig_path)


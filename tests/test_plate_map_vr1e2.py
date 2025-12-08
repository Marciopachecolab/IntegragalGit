import sys
import tempfile
from pathlib import Path

import pandas as pd
import pytest

# Garante que o pacote raiz esteja no sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from services import history_report
from services.exam_registry import get_exam_cfg
from services.plate_viewer import PlateModel


RAW_MAP = [
    ("A1", "422386149R", "422386149R"),
    ("B1", "422386266R", "422386266R"),
    ("C1", "422386156R", "422386156R"),
    ("D1", "422386625", "422386625"),
    ("E1", "422386851", "422386851"),
    ("F1", "422386866", "422386866"),
    ("G1", "422386883", "422386883"),
    ("H1", "422386268", "422386268"),
    ("A3", "422386273", "422386273"),
    ("B3", "422387254", "422387254"),
    ("C3", "422386806", "422386806"),
    ("D3", "422386980", "422386980"),
    ("E3", "422385450", "422385450"),
    ("F3", "422386322", "422386322"),
    ("G3", "422386324", "422386324"),
    ("H3", "422386282", "422386282"),
    ("A5", "422386293", "422386293"),
    ("B5", "422386816", "422386816"),
    ("C5", "422386798", "422386798"),
    ("D5", "422387130", "422387130"),
    ("E5", "422386593", "422386593"),
    ("F5", "422386852", "422386852"),
    ("G5", "422386928", "422386928"),
    ("H5", "422387004", "422387004"),
    ("A7", "422387159", "422387159"),
    ("B7", "422387129", "422387129"),
    ("C7", "422387065", "422387065"),
    ("D7", "422387062", "422387062"),
    ("E7", "422387059", "422387059"),
    ("F7", "422387047", "422387047"),
    ("G7", "422387071", "422387071"),
    ("H7", "422387075", "422387075"),
    ("A9", "422386742", "422386742"),
    ("B9", "422385147", "422385147"),
    ("G11", "CN", "CN"),
    ("H11", "CP", "CP"),
]


def build_df_final():
    rows = []
    for poco, amostra, codigo in RAW_MAP:
        rows.append(
            {
                "Poco": poco,
                "Amostra": amostra,
                "Codigo": codigo,
                "Resultado_SC2": "Não Detectado",
                "Resultado_HMPV": "Não Detectado",
                "Resultado_INFA": "Não Detectado",
                "Resultado_INFB": "Não Detectado",
                "Resultado_ADV": "Não Detectado",
                "Resultado_RSV": "Não Detectado",
                "Resultado_HRV": "Não Detectado",
                "RP_1 - CT": 22.5,
                "RP_2 - CT": 22.5,
            }
        )
    return pd.DataFrame(rows)


def test_plate_map_model_renders_all_wells():
    exam_name = "VR1e2 Biomanguinhos 7500"
    if get_exam_cfg(exam_name) is None:
        pytest.skip(f"Exame '{exam_name}' não está configurado no registry.")

    df_final = build_df_final()
    arquivo_corrida = r"C:\Users\marci\Downloads\18 JULHO 2025\20250718 VR1-VR2 BIOM PLACA 5.xlsx"

    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "historico_analises_test.csv"
        history_report.gerar_historico_csv(
            df_final=df_final,
            exame=exam_name,
            usuario="tester",
            lote="qqq",
            arquivo_corrida=arquivo_corrida,
            caminho_csv=str(csv_path),
        )

        model = PlateModel.from_historico_csv(str(csv_path))
        # Verifica que todos os poços do mapeamento estão no modelo
        expected_pocos = {p for p, _, _ in RAW_MAP}
        model_pocos = {wd.poco for wd in model.wells}
        assert expected_pocos.issubset(model_pocos)
        # Confere que CN/CP foram identificados
        assert "G11" in model_pocos
        assert "H11" in model_pocos

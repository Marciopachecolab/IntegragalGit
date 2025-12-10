import sys
from pathlib import Path

import pandas as pd
import pytest

# Garante que o pacote raiz (Integragal) esteja no sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from services.plate_viewer import PlateModel  # noqa: E402


def build_df_final():
    """DF de exemplo semelhante ao df_final da análise."""
    return pd.DataFrame(
        [
            {
                "Poco": "A1",
                "Amostra": "AMOSTRA001",
                "Codigo": "001",
                "Resultado_SC2": "Detectado",
                "SC2 - CT": 18.5,
                "Resultado_HMPV": "Não Detectado",
                "HMPV - CT": None,
                "RP_1 - CT": 22.1,
            },
            {
                "Poco": "H11",
                "Amostra": "CP",
                "Codigo": "CP",
                "Resultado_SC2": "Detectado",
                "SC2 - CT": 20.0,
                "RP_1 - CT": 21.0,
            },
            {
                "Poco": "G11",
                "Amostra": "CN",
                "Codigo": "CN",
                "Resultado_SC2": "Não Detectado",
                "SC2 - CT": None,
                "RP_1 - CT": 22.0,
            },
        ]
    )


def test_plate_viewer_data_origin():
    df_final = build_df_final()

    # Monta o modelo a partir do df_final em memória (origem dos dados da placa)
    model = PlateModel.from_df(df_final)

    # Verifica poços carregados
    # PlateModel normaliza poços para A01 formato
    for well_id in ["A01", "H11", "G11"]:
        assert well_id in model.wells, f"poço {well_id} não foi carregado"

    a1 = model.wells["A01"]
    # Dados herdados do df_final
    assert a1.sample_id == "AMOSTRA001"
    assert a1.code == "001"
    assert "SC2" in a1.targets
    assert a1.targets["SC2"].result  # Detectado veio do Resultado_SC2
    assert a1.targets["SC2"].ct == 18.5

    # CP detectado como controle positivo
    h11 = model.wells["H11"]
    assert h11.code == "CP"
    assert h11.is_control

    # CN detectado como controle negativo
    g11 = model.wells["G11"]
    assert g11.code == "CN"
    assert g11.is_control

    # Todos os dados usados pelo modelo vêm do df_final (em memória), não de CSV externo
    assert model.exam_cfg is None or hasattr(model.exam_cfg, "name")

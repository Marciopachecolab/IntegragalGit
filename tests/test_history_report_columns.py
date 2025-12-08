import tempfile
from types import SimpleNamespace

import pandas as pd

import services.history_report as hr


def test_gerar_historico_csv_adds_missing_columns_without_set_indexer(monkeypatch):
    # Stub do registry para evitar dependência externa
    fake_cfg = SimpleNamespace(
        alvos=["SC2"],
        rps=["RP1"],
        normalize_target=lambda self, x: x,
    )

    # monkeypatch get_exam_cfg para retornar o stub
    monkeypatch.setattr(hr, "get_exam_cfg", lambda nome: fake_cfg)

    df_final = pd.DataFrame(
        [
            {
                "Codigo": "123",
                "Amostra": "AM1",
                "Poco": "A1",
                "Status_Corrida": "OK",
                "Resultado_SC2": "Detectado",
                "SC2 - CT": 20.1,
                "RP1": 15.2,
            }
        ]
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = f"{tmpdir}/hist.csv"

        # Arquivo existente com colunas diferentes (para disparar alinhamento)
        pd.DataFrame([{"codigo": "old_only"}]).to_csv(csv_path, sep=";", index=False)

        # Não deve levantar ValueError e deve escrever colunas novas
        hr.gerar_historico_csv(
            df_final=df_final,
            exame="VR1e2 Biomanguinhos 7500",
            usuario="tester",
            lote="l1",
            arquivo_corrida="run.xlsx",
            caminho_csv=csv_path,
        )

        result = pd.read_csv(csv_path, sep=";")
        # Colunas essenciais esperadas
        expected_cols = {
            "id_registro",
            "exame",
            "status_gal",
            "SC2 - R",
            "SC2 - CT",
            "RP1 - CT",
        }
        assert expected_cols.issubset(set(result.columns))
        # Deve ter acrescentado uma linha (arquivo pré-existente tinha 1 linha)
        assert len(result) == 2

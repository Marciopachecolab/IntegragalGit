"""
Gera um relatório dos principais DataFrames disponíveis no projeto.
- Lê CSVs conhecidos (historico_analises.csv em reports/logs)
- Opcionalmente lê outros arquivos passados via linha de comando
- Usa utils.dataframe_reporter para salvar amostras e resumo

Uso:
    python df_report_full.py [opcionais: caminhos_para_csv_ou_xlsx...]

Saída:
    - Logs em logs/dataframe_reports/<sessao>_summary.txt
    - Amostras CSV para cada DF inspecionado
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable

import pandas as pd

from utils.dataframe_reporter import log_dataframe, generate_report


def _load_file(path: Path):
    if not path.exists():
        print(f"[DFDBG] Arquivo não encontrado: {path}")
        return None
    try:
        if path.suffix.lower() in {".csv", ".txt"}:
            # Tenta separador ; primeiro (padrão do histórico)
            try:
                df = pd.read_csv(path, sep=";", encoding="utf-8")
            except Exception:
                df = pd.read_csv(path, encoding="utf-8")
            return df
        if path.suffix.lower() in {".xlsx", ".xls"}:
            return pd.read_excel(path)
        # Fallback genérico
        return pd.read_csv(path, encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        print(f"[DFDBG] Falha ao ler {path}: {exc}")
        return None


def main(args: Iterable[str]) -> int:
    # Alvos padrão conhecidos
    default_paths = [
        Path("reports/historico_analises.csv"),
        Path("logs/historico_analises.csv"),
        Path("tmp_df_norm_excerpt.csv"),
    ]

    # Acrescenta caminhos passados na linha de comando
    user_paths = [Path(a) for a in args if a]
    paths = default_paths + user_paths

    for p in paths:
        df = _load_file(p)
        if df is None:
            continue
        log_dataframe(df, name=p.name, stage="report_full", metadata={"path": str(p)}, save_sample=True)

    summary = generate_report()
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

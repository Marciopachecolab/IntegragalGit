# extracao/mapeamento_placas.py
from typing import Dict, List

# --- Bloco de Configuração Inicial ---
# Garante que os módulos do projeto (como o logger) possam ser importados
from utils.logger import registrar_log

LINHAS = "ABCDEFGH"


def gerar_mapeamento_96() -> List[Dict]:
    """
    Gera o mapeamento para uma placa de 96 poços (1:1 extração para análise).
    """
    mapeamento = []
    try:
        for i in range(96):
            linha_extracao = LINHAS[i % 8]
            coluna_extracao = (i // 8) + 1

            poco = f"{linha_extracao}{coluna_extracao}"

            mapeamento.append(
                {"amostra": i + 1, "extracao": (poco,), "analise": (poco,)}
            )
        registrar_log(
            "Mapeamento Placas",
            "Mapeamento de 96 poços gerado com sucesso.",
            level="INFO",
        )
    except Exception as e:
        registrar_log(
            "Mapeamento Placas",
            f"Erro ao gerar mapeamento de 96 poços: {e}",
            level="ERROR",
        )
        raise
    return mapeamento


# --- CORREÇÃO: Lógica de 1 amostra para 2 poços de análise ---
def gerar_mapeamento_48(parte: int = 1) -> List[Dict]:
    if parte not in [1, 2]:
        raise ValueError("Parte da placa para 48 poços deve ser 1 ou 2.")

    mapeamento = []
    col_offset_extracao = 0 if parte == 1 else 6

    for i in range(48):
        linha_idx = i % 8
        bloco_coluna_extracao = i // 8

        linha = LINHAS[linha_idx]
        coluna_extracao_real = col_offset_extracao + bloco_coluna_extracao + 1

        amostra_idx_global = (coluna_extracao_real - 1) * 8 + linha_idx

        # Mapeia para um par de poços de análise adjacentes
        coluna_analise_1 = 2 * bloco_coluna_extracao + 1
        coluna_analise_2 = 2 * bloco_coluna_extracao + 2

        mapeamento.append(
            {
                "amostra": amostra_idx_global + 1,
                "extracao": (f"{linha}{coluna_extracao_real}",),
                "analise": (f"{linha}{coluna_analise_1}", f"{linha}{coluna_analise_2}"),
            }
        )
    registrar_log(
        "Mapeamento Placas",
        f"Mapeamento 1-para-2 de 48 poços (parte {parte}) gerado.",
        "INFO",
    )
    return mapeamento


def gerar_mapeamento_32(parte: int = 1) -> List[Dict]:
    """
    Gera o mapeamento para uma placa de 32 poços.
    """
    if parte not in [1, 2, 3]:
        registrar_log(
            "Mapeamento Placas",
            f"Valor inválido para 'parte' em mapeamento 32 poços: {parte}. Esperado 1, 2 ou 3.",
            level="ERROR",
        )
        raise ValueError("Parte da placa para 32 poços deve ser 1, 2 ou 3.")

    mapeamento = []
    try:
        col_offset_extracao = (parte - 1) * 4
        for i in range(32):
            linha_idx = i % 8
            bloco_coluna_extracao = i // 8

            linha = LINHAS[linha_idx]
            coluna_extracao = col_offset_extracao + bloco_coluna_extracao + 1

            amostra_idx_global = (coluna_extracao - 1) * 8 + linha_idx

            cols_analise = [
                f"{linha}{3 * bloco_coluna_extracao + j + 1}" for j in range(3)
            ]

            mapeamento.append(
                {
                    "amostra": amostra_idx_global + 1,
                    "extracao": (f"{linha}{coluna_extracao}",),
                    "analise": tuple(cols_analise),
                }
            )
        registrar_log(
            "Mapeamento Placas",
            f"Mapeamento de 32 poços (parte {parte}) gerado com sucesso.",
            level="INFO",
        )
    except Exception as e:
        registrar_log(
            "Mapeamento Placas",
            f"Erro ao gerar mapeamento de 32 poços (parte {parte}): {e}",
            level="ERROR",
        )
        raise
    return mapeamento


def gerar_mapeamento_24(parte: int = 1) -> List[Dict]:
    """
    Gera o mapeamento para uma placa de 24 poços.
    """
    if parte not in [1, 2, 3, 4]:
        registrar_log(
            "Mapeamento Placas",
            f"Valor inválido para 'parte' em mapeamento 24 poços: {parte}. Esperado 1, 2, 3 ou 4.",
            level="ERROR",
        )
        raise ValueError("Parte da placa para 24 poços deve ser 1, 2, 3 ou 4.")

    mapeamento = []
    try:
        col_offset_extracao = (parte - 1) * 3
        for i in range(24):
            linha_idx = i % 8
            bloco_coluna_extracao = i // 8

            linha = LINHAS[linha_idx]
            coluna_extracao = col_offset_extracao + bloco_coluna_extracao + 1

            amostra_idx_global = (coluna_extracao - 1) * 8 + linha_idx

            cols_analise = [
                f"{linha}{4 * bloco_coluna_extracao + j + 1}" for j in range(4)
            ]

            mapeamento.append(
                {
                    "amostra": amostra_idx_global + 1,
                    "extracao": (f"{linha}{coluna_extracao}",),
                    "analise": tuple(cols_analise),
                }
            )
        registrar_log(
            "Mapeamento Placas",
            f"Mapeamento de 24 poços (parte {parte}) gerado com sucesso.",
            level="INFO",
        )
    except Exception as e:
        registrar_log(
            "Mapeamento Placas",
            f"Erro ao gerar mapeamento de 24 poços (parte {parte}): {e}",
            level="ERROR",
        )
        raise
    return mapeamento

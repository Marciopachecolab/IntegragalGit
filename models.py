# models.py
from typing import Optional

import pandas as pd


class AppState:
    """
    Armazena e gere o estado partilhado da aplicação.
    Este modelo de dados é importado por qualquer módulo que precise
    de aceder ou modificar o estado da aplicação.
    """

    def __init__(self):
        self.usuario_logado: Optional[str] = None
        self.dados_extracao: Optional[pd.DataFrame] = None
        self.parte_placa: Optional[int] = None
        self.resultados_analise: Optional[pd.DataFrame] = None
        self.lote_kit: Optional[str] = None
        self.exame_selecionado: Optional[str] = None
        # Optional overrides for control wells (lists of well names)
        self.control_cn_wells: Optional[list[str]] = None
        self.control_cp_wells: Optional[list[str]] = None
        # Equipment/Plate type detection (Fase 1.4)
        self.tipo_de_placa_detectado: Optional[str] = None  # Nome detectado automaticamente
        self.tipo_de_placa_config: Optional[object] = None  # EquipmentConfig object
        self.tipo_de_placa_selecionado: Optional[str] = None  # Nome confirmado pelo usuário

    def reset_analise_state(self):
        """Reseta o estado relacionado a uma análise específica."""
        self.resultados_analise = None
        self.lote_kit = None
        self.exame_selecionado = None
        self.tipo_de_placa_detectado = None
        self.tipo_de_placa_config = None
        self.tipo_de_placa_selecionado = None

    def reset_extracao_state(self):
        """Reseta o estado da extração e da análise."""
        self.dados_extracao = None
        self.parte_placa = None
        self.reset_analise_state()
        self.control_cn_wells = None
        self.control_cp_wells = None

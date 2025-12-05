"""
Ajustes no AnalysisService para suportar o motor universal.
Este módulo define o serviço de análise de placas, centralizando:
- Carregamento de arquivos de resultados e extração
- Chamada do motor universal (services.universal_engine)
- Interação com o AppState
- Integração com cadastros (exames_config, regras, etc.)
"""

from __future__ import annotations

import datetime
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from models import AppState
from services.config_loader import carregar_configuracoes_exames
from services.universal_engine import UniversalEngine
from services.system_paths import BASE_DIR
from utils.io_utils import read_data_with_auto_detection
from utils.logger import registrar_log


# ---------------------------------------------------------------------------
# Dataclasses de apoio
# ---------------------------------------------------------------------------


@dataclass
class AnaliseResultado:
    """
    Representa o resultado de uma análise de placa/protocolo.

    A ideia é encapsular, em um só objeto, os principais artefatos produzidos
    pela análise, mantendo compatibilidade com o que a UI espera.
    """

    df_processado: pd.DataFrame
    resumo: Dict[str, Any]
    metadados: Dict[str, Any]
    caminho_entrada_resultados: Optional[Path] = None
    caminho_entrada_extracao: Optional[Path] = None


# ---------------------------------------------------------------------------
# Classe principal AnalysisService
# ---------------------------------------------------------------------------


class AnalysisService:
    """
    Serviço de alto nível responsável por orquestrar a análise de placas.

    Ele faz a ponte entre:
    - AppState (estado global da aplicação)
    - Configurações de exames (banco/exames_config.csv e outros)
    - Motor universal de análise (UniversalEngine)
    - Leitura dos arquivos de entrada (resultados e extração)
    """

    def __init__(self, app_state: AppState) -> None:
        self.app_state = app_state

        # Engine universal que centraliza a lógica de análise
        self.engine = UniversalEngine()

        # Cache de exames disponíveis (preenchido sob demanda)
        # O MenuHandler verifica se é None; se for, dispara o carregamento.
        self.exames_disponiveis: Optional[List[str]] = None

        # Último resultado de análise realizado
        self.ultimo_resultado: Optional[AnaliseResultado] = None

    # ------------------------------------------------------------------
    # API pública principal
    # ------------------------------------------------------------------

    def listar_exames_disponiveis(self) -> List[str]:
        """
        Retorna a lista de exames cadastrados no sistema (exames_config.csv).

        A lista é adquirida via 'carregar_configuracoes_exames' e contém os
        nomes de exames que podem ser selecionados na UI.
        """
        try:
            config_exames = carregar_configuracoes_exames()
            exames = sorted(config_exames.keys())
            registrar_log(
                "info",
                f"[AnalysisService] Exames disponíveis carregados: {', '.join(exames)}",
            )
            # Atualiza o cache interno
            self.exames_disponiveis = exames
            return exames
        except Exception as exc:  # noqa: BLE001
            registrar_log(
                "erro",
                f"[AnalysisService] Erro ao carregar exames disponíveis: {exc}",
            )
            # Em caso de falha, o chamador decide como tratar
            raise

    def analisar_corrida(
        self,
        exame: str,
        arquivo_resultados: Path,
        arquivo_extracao: Optional[Path] = None,
        lote: Optional[str] = None,
    ) -> AnaliseResultado:
        """
        Executa a análise completa de uma corrida para um determinado exame.

        Parâmetros
        ----------
        exame : str
            Nome do exame, conforme cadastro em exames_config.csv
        arquivo_resultados : Path
            Caminho para o arquivo de resultados do equipamento (CSV/XLSX/etc.)
        arquivo_extracao : Path, opcional
            Caminho para o arquivo de extração / mapeamento de amostras
        lote : str, opcional
            Identificação de lote, se fornecida pela UI
        """
        registrar_log(
            "info",
            f"[AnalysisService] Iniciando análise para exame='{exame}', "
            f"arquivo_resultados='{arquivo_resultados}', arquivo_extracao='{arquivo_extracao}', "
            f"lote='{lote}'",
        )

        # 1. Carregar dados brutos dos arquivos
        df_resultados = self._carregar_arquivo_resultados(arquivo_resultados)
        df_extracao = (
            self._carregar_arquivo_extracao(arquivo_extracao)
            if arquivo_extracao is not None
            else None
        )

        # 2. Chamar o motor universal
        resultado_engine = self.engine.processar_exame(
            exame=exame,
            df_resultados=df_resultados,
            df_extracao=df_extracao,
            lote=lote,
        )

        # 3. Montar objeto AnaliseResultado
        analise_resultado = AnaliseResultado(
            df_processado=resultado_engine.df_final,
            resumo=resultado_engine.resumo,
            metadados=resultado_engine.metadados,
            caminho_entrada_resultados=arquivo_resultados,
            caminho_entrada_extracao=arquivo_extracao,
        )

        # 4. Atualizar AppState com os dados resultantes
        self._atualizar_app_state_com_resultado(analise_resultado)

        # 5. Armazenar como último resultado
        self.ultimo_resultado = analise_resultado

        registrar_log(
            "info",
            "[AnalysisService] Análise concluída com sucesso. "
            f"Total de linhas no df_processado: {len(analise_resultado.df_processado)}",
        )

        return analise_resultado

    # ------------------------------------------------------------------
    # Funções auxiliares internas
    # ------------------------------------------------------------------

    def _carregar_arquivo_resultados(self, caminho: Path) -> pd.DataFrame:
        """
        Carrega o arquivo de resultados (saída do equipamento).

        Utiliza 'read_data_with_auto_detection', que já faz inferência de
        separadores, codificação e tipo de planilha.
        """
        registrar_log(
            "info",
            f"[AnalysisService] Carregando arquivo de resultados: '{caminho}'",
        )

        if not caminho.exists():
            msg = f"Arquivo de resultados não encontrado: {caminho}"
            registrar_log("erro", f"[AnalysisService] {msg}")
            raise FileNotFoundError(msg)

        df = read_data_with_auto_detection(caminho)
        registrar_log(
            "debug",
            f"[AnalysisService] Arquivo de resultados carregado com shape={df.shape}",
        )
        return df

    def _carregar_arquivo_extracao(self, caminho: Path) -> pd.DataFrame:
        """
        Carrega o arquivo de extração / mapeamento de amostras.

        Também usa 'read_data_with_auto_detection' para reduzir a
        sensibilidade a variações de formato.
        """
        registrar_log(
            "info",
            f"[AnalysisService] Carregando arquivo de extração/mapeamento: '{caminho}'",
        )

        if not caminho.exists():
            msg = f"Arquivo de extração/mapeamento não encontrado: {caminho}"
            registrar_log("erro", f"[AnalysisService] {msg}")
            raise FileNotFoundError(msg)

        df = read_data_with_auto_detection(caminho)
        registrar_log(
            "debug",
            f"[AnalysisService] Arquivo de extração/mapeamento carregado com shape={df.shape}",
        )
        return df

    def _atualizar_app_state_com_resultado(self, resultado: AnaliseResultado) -> None:
        """
        Atualiza o AppState com os artefatos produzidos pela análise.

        Isso permite que outras partes da UI (por exemplo, visualizadores de
        placa, relatórios, exportação GAL) acessem os dados de forma coerente.
        """
        try:
            # Guarda o DataFrame processado no estado da aplicação
            self.app_state.df_processado = resultado.df_processado

            # Resumo e metadados
            self.app_state.analise_resumo = resultado.resumo
            self.app_state.analise_metadados = resultado.metadados

            # Caminhos de origem
            self.app_state.caminho_arquivo_resultados = (
                str(resultado.caminho_entrada_resultados)
                if resultado.caminho_entrada_resultados is not None
                else None
            )
            self.app_state.caminho_arquivo_extracao = (
                str(resultado.caminho_entrada_extracao)
                if resultado.caminho_entrada_extracao is not None
                else None
            )

            # Marca data/hora da última análise
            self.app_state.data_hora_ultima_analise = datetime.datetime.now()

            registrar_log(
                "info",
                "[AnalysisService] AppState atualizado com resultado da análise.",
            )
        except Exception as exc:  # noqa: BLE001
            registrar_log(
                "erro",
                f"[AnalysisService] Erro ao atualizar AppState com resultado da análise: {exc}",
            )
            # Em caso de falha, não interrompemos necessariamente a execução,
            # mas a UI pode não refletir o último resultado corretamente.

    # ------------------------------------------------------------------
    # Utilitários adicionais (opcionais / de apoio)
    # ------------------------------------------------------------------

    def obter_ultimo_dataframe_processado(self) -> Optional[pd.DataFrame]:
        """
        Retorna o último DataFrame processado (se houver).
        """
        if self.ultimo_resultado is None:
            return None
        return self.ultimo_resultado.df_processado

    def obter_resumo_ultima_analise(self) -> Optional[Dict[str, Any]]:
        """
        Retorna o resumo da última análise (se houver).
        """
        if self.ultimo_resultado is None:
            return None
        return self.ultimo_resultado.resumo

    def obter_metadados_ultima_analise(self) -> Optional[Dict[str, Any]]:
        """
        Retorna os metadados da última análise (se houver).
        """
        if self.ultimo_resultado is None:
            return None
        return self.ultimo_resultado.metadados

    def resolver_caminho_relativo(self, relative_path: str) -> Optional[Path]:
        """
        Resolve um caminho relativo em relação ao BASE_DIR do sistema.

        Útil para componentes da UI que recebem apenas o nome de um arquivo
        e precisam localizar o caminho completo dentro da estrutura do
        Integragal.
        """
        try:
            base = Path(BASE_DIR)
            caminho = base / relative_path
        except Exception as exc:  # noqa: BLE001
            registrar_log(
                "erro",
                f"[AnalysisService] Erro ao resolver caminho relativo '{relative_path}': {exc}",
            )
            return None

        if not caminho.exists():
            registrar_log(
                "warning",
                f"[AnalysisService] Caminho relativo '{relative_path}' "
                f"resolvido para '{caminho}', mas o arquivo não existe.",
            )
            return None
        return caminho

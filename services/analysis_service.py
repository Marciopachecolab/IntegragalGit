# services/analysis_service.py
import os
import sys
import pandas as pd
from tkinter import messagebox
from typing import Tuple, Optional

# --- Bloco de Configuração Inicial ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# --- Importações de Módulos do Projeto ---
from models import AppState
from utils.import_utils import importar_funcao
from utils.logger import registrar_log

# Caminho para o ficheiro de configuração dos exames
CAMINHO_EXAMES = os.path.join(BASE_DIR, "banco", "exames_config.csv")

class AnalysisService:
    """
    Encapsula a lógica de negócio para orquestrar o processo de análise.
    """
    def __init__(self):
        """Inicializa o serviço, carregando a configuração dos exames disponíveis."""
        self.exames_disponiveis = self._carregar_config_exames()

    def _carregar_config_exames(self) -> Optional[pd.DataFrame]:
        """
        Carrega a configuração dos exames a partir do arquivo CSV.
        Retorna um DataFrame com as configurações ou None em caso de erro.
        """
        try:
            if not os.path.exists(CAMINHO_EXAMES):
                registrar_log("AnalysisService", f"Arquivo de configuração de exames não encontrado: {CAMINHO_EXAMES}", "ERROR")
                return None
            
            df_exames = pd.read_csv(CAMINHO_EXAMES)
            registrar_log("AnalysisService", "Configuração de exames carregada com sucesso.", "INFO")
            return df_exames
        except Exception as e:
            registrar_log("AnalysisService", f"Erro crítico ao carregar o arquivo de configuração de exames: {e}", "CRITICAL")
            return None

    def executar_analise(self, app_state: AppState, master_window, exame_selecionado: str, lote_kit: str) -> Tuple[Optional[pd.DataFrame], str, str]:
        """
        Orquestra a execução de uma análise.

        1. Encontra o módulo de análise correto com base na configuração.
        2. Importa dinamicamente a sua função de ponto de entrada.
        3. Executa a função, que irá gerir a sua própria UI e lógica.
        4. Retorna os resultados para o fluxo principal.
        """
        if self.exames_disponiveis is None:
            messagebox.showerror("Erro Crítico", "A configuração de exames não pôde ser carregada.", parent=master_window)
            return None, exame_selecionado, lote_kit

        # Validação: garantir mapeamento de extração com colunas essenciais
        try:
            df_map = app_state.dados_extracao
            if df_map is None or getattr(df_map, 'empty', True):
                messagebox.showerror("Erro de Fluxo", "Mapeamento de extração não carregado.", parent=master_window)
                return None, exame_selecionado, lote_kit
            import unicodedata as _ud
            def _norm(s: str) -> str:
                return _ud.normalize('NFKD', str(s)).encode('ASCII','ignore').decode('ASCII').strip().lower()
            cols = {_norm(c) for c in df_map.columns}
            if not ("amostra" in cols and ("poco" in cols or "well" in cols)):
                messagebox.showerror("Erro de Dados", "Colunas obrigatórias ausentes no mapeamento (Amostra e Poço).", parent=master_window)
                return None, exame_selecionado, lote_kit
        except Exception:
            pass

        try:
            info_exame = self.exames_disponiveis[self.exames_disponiveis['exame'] == exame_selecionado]
            if info_exame.empty:
                raise ValueError(f"Nenhuma configuração encontrada para o exame '{exame_selecionado}'")

            # Constrói o caminho para a função de ponto de entrada (ex: 'analise.vr1.iniciar_fluxo_analise')
            # Extrai o nome do módulo (ex: 'analise.vr1e2_biomanguinhos_7500') da string completa da função
            modulo_base = info_exame.iloc[0]['modulo_analise'].rsplit('.', 1)[0]
            funcao_ui_string = f"{modulo_base}.iniciar_fluxo_analise"
            
            registrar_log("AnalysisService", f"A importar função de UI: '{funcao_ui_string}'", "INFO")
            funcao_iniciar_fluxo = importar_funcao(funcao_ui_string)
            
            # Chama a função de UI do módulo específico, passando a janela principal, o estado e o lote
            raw_ret = funcao_iniciar_fluxo(master_window, app_state, lote_kit)

            # Normalizar o retorno: a função de UI pode devolver várias formas
            # Possíveis formatos observados:
            # - pd.DataFrame
            # - (pd.DataFrame, exame_ret, lote_ret)
            # - (pd.DataFrame, metadata)
            resultados_df = None
            exame_ret = exame_selecionado
            lote_ret = lote_kit

            if isinstance(raw_ret, (tuple, list)):
                # tentar desempacotar formas comuns
                if len(raw_ret) >= 1:
                    candidate = raw_ret[0]
                    if hasattr(candidate, 'empty') or isinstance(candidate, pd.DataFrame):
                        resultados_df = candidate
                if len(raw_ret) >= 2:
                    # segundo elemento pode ser exame_ret ou metadata
                    if isinstance(raw_ret[1], str):
                        exame_ret = raw_ret[1]
                if len(raw_ret) >= 3:
                    if isinstance(raw_ret[2], str):
                        lote_ret = raw_ret[2]
                # Se ainda não temos DataFrame, procurar o primeiro elemento que pareça um DataFrame
                if resultados_df is None:
                    for item in raw_ret:
                        if hasattr(item, 'empty') or isinstance(item, pd.DataFrame):
                            resultados_df = item
                            break
            else:
                # retorno direto: pode ser um DataFrame ou None
                if hasattr(raw_ret, 'empty') or isinstance(raw_ret, pd.DataFrame):
                    resultados_df = raw_ret

            return resultados_df, exame_ret, lote_ret

        except Exception as e:
            registrar_log("AnalysisService", f"Erro ao executar análise: {e}", "CRITICAL")
            messagebox.showerror("Erro de Análise", f"Não foi possível iniciar o processo de análise.\n\nDetalhes: {e}", parent=master_window)
            return None, exame_selecionado, lote_kit

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

from dataclasses import dataclass

from pathlib import Path

from typing import Any, Dict, List, Optional



import pandas as pd



from models import AppState

from services.config_loader import carregar_exames_metadata

from services.universal_engine import UniversalEngine

from services.system_paths import BASE_DIR

from services.equipment_detector import detectar_equipamento

from services.equipment_registry import EquipmentRegistry

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

        self.engine = UniversalEngine(self.app_state)



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

            config_exames = carregar_exames_metadata()

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

        # 1.1. Usar extrator específico se tipo de placa foi detectado (Fase 1.5)

        df_resultados = self._carregar_arquivo_resultados_com_extrator(arquivo_resultados)

        

        df_extracao = (

            self._carregar_arquivo_extracao(arquivo_extracao)

            if arquivo_extracao is not None

            else None

        )

        # Se houver gabarito/arquivo de extração, armazena-o no AppState para integração no motor universal

        if df_extracao is not None:

            self.app_state.df_gabarito_extracao = df_extracao



        # 2. Chamar o motor universal

        resultado_engine = self.engine.processar_exame(

            exame=exame,

            df_resultados=df_resultados,

            df_extracao=df_extracao,

            lote=lote,

        )



        # 3. Montar objeto AnaliseResultado com metadados de equipamento (Fase 1.5)

        metadados_completos = resultado_engine.metadados.copy()

        

        # Injetar informações de equipamento detectado nos metadados

        if self.app_state.tipo_de_placa_detectado:

            metadados_completos['equipamento_detectado'] = self.app_state.tipo_de_placa_detectado

            metadados_completos['equipamento_selecionado'] = self.app_state.tipo_de_placa_selecionado

            

            if self.app_state.tipo_de_placa_config:

                config = self.app_state.tipo_de_placa_config

                metadados_completos['equipamento_modelo'] = config.modelo

                metadados_completos['equipamento_fabricante'] = config.fabricante

                metadados_completos['equipamento_tipo_placa'] = config.tipo_placa

                metadados_completos['equipamento_extrator'] = config.extrator_nome

        

        analise_resultado = AnaliseResultado(

            df_processado=resultado_engine.df_final,

            resumo=resultado_engine.resumo,

            metadados=metadados_completos,

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





    def executar_analise(

        self,

        app_state: AppState,

        parent_window: Any,

        exame: str,

        lote: str,

    ) -> Any:

        """

        Método de compatibilidade utilizado pelo MenuHandler (UI).



        Mantém a assinatura antiga ``executar_analise(app_state, parent_window, exame, lote)``,

        redirecionando para o novo fluxo baseado em ``analisar_corrida`` e no motor

        universal.



        Fluxo resumido:

        1. Sincroniza o ``AppState`` recebido com o interno deste serviço.

        2. Garante que o gabarito de extração (mapa da placa) esteja acessível ao motor,

           reaproveitando ``app_state.dados_extracao`` quando disponível.

        3. Abre um diálogo para seleção do arquivo de resultados do equipamento.

        4. Chama ``analisar_corrida`` com o exame, o arquivo selecionado e o lote.

        5. Devolve o ``DataFrame`` processado, que é o que o ``MenuHandler`` espera.

        """

        # 1. Sincronizar AppState (compatibilidade com versões anteriores)

        if app_state is not None and app_state is not self.app_state:

            self.app_state = app_state

            try:

                # Mantém engine alinhado com o novo AppState

                self.engine.app_state = app_state

            except Exception:

                # Se por algum motivo a engine ainda não existir ou não tiver o atributo,

                # simplesmente ignoramos – ela será recriada se necessário.

                pass



        # 2. Garantir que o gabarito de extração esteja acessível ao motor universal

        #    Reutiliza o DataFrame carregado na etapa de mapeamento da placa.

        if getattr(self.app_state, "dados_extracao", None) is not None:

            try:

                self.app_state.df_gabarito_extracao = self.app_state.dados_extracao

            except Exception:

                # Falha ao atribuir não deve impedir a análise; o motor apenas

                # seguirá sem integração com o gabarito.

                pass



        from tkinter import filedialog



        # 3. Selecionar arquivo de resultados do equipamento

        caminho = filedialog.askopenfilename(

            parent=parent_window,

            title="Selecione o arquivo de resultados do equipamento",

            filetypes=[

                ("Arquivos de planilha", "*.csv;*.xlsx;*.xls"),

                ("Todos os arquivos", "*.*"),

            ],

        )

        if not caminho:

            # Mantemos a semântica de erro para que a UI possa notificar o usuário.

            raise RuntimeError("Seleção de arquivo de resultados cancelada pelo usuário.")



        arquivo_resultados = Path(caminho)



        # 3.1. Detectar tipo de placa PCR automaticamente

        # DESABILITADO: Todos os exames usam o mesmo equipamento (7500)

        # Para reabilitar, descomente o bloco abaixo

        tipo_placa_selecionado = None

        # tipo_placa_selecionado = self._detectar_e_confirmar_tipo_placa(

        #     arquivo_resultados=arquivo_resultados,

        #     parent_window=parent_window,

        # )



        if tipo_placa_selecionado:

            registrar_log(

                "info",

                f"[AnalysisService] Prosseguindo com tipo de placa: {tipo_placa_selecionado}",

            )

        else:

            registrar_log(

                "info",

                "[AnalysisService] Prosseguindo sem detecção de tipo de placa (fallback genérico)",

            )



        # 4. Delegar para o novo fluxo de análise

        analise = self.analisar_corrida(

            exame=exame,

            arquivo_resultados=arquivo_resultados,

            arquivo_extracao=None,

            lote=lote,

        )



        # 5. Retorna apenas o DataFrame processado, que é o que o MenuHandler utiliza

        return analise.df_processado

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

    

    def _carregar_arquivo_resultados_com_extrator(self, caminho: Path) -> pd.DataFrame:

        """

        Carrega arquivo de resultados usando extrator específico quando disponível (Fase 1.5).

        

        Se app_state.tipo_de_placa_config existir, usa o extrator específico do equipamento

        para normalizar dados para formato padrão ['bem', 'amostra', 'alvo', 'ct'].

        

        Caso contrário, faz fallback para leitura genérica com read_data_with_auto_detection.

        

        Args:

            caminho: Path para arquivo de resultados

            

        Returns:

            DataFrame normalizado (com extrator específico) ou DataFrame bruto (fallback)

        """

        registrar_log(

            "info",

            f"[AnalysisService] Carregando arquivo de resultados: '{caminho}'",

        )



        if not caminho.exists():

            msg = f"Arquivo de resultados não encontrado: {caminho}"

            registrar_log("erro", f"[AnalysisService] {msg}")

            raise FileNotFoundError(msg)

        

        # Fase 1.5: Verificar se há tipo de placa detectado

        if (

            hasattr(self.app_state, 'tipo_de_placa_config') 

            and self.app_state.tipo_de_placa_config is not None

        ):

            try:

                from services.equipment_extractors import extrair_dados_equipamento

                

                config = self.app_state.tipo_de_placa_config

                equipamento = self.app_state.tipo_de_placa_selecionado

                

                registrar_log(

                    "info",

                    f"[AnalysisService] Usando extrator específico para: {equipamento}",

                )

                

                # Usar extrator específico

                df_normalizado = extrair_dados_equipamento(str(caminho), config)

                

                registrar_log(

                    "info",

                    f"[AnalysisService] Extração específica concluída: {len(df_normalizado)} linhas, "

                    f"colunas={list(df_normalizado.columns)}",

                )

                

                return df_normalizado

                

            except Exception as exc:

                registrar_log(

                    "aviso",

                    f"[AnalysisService] Falha no extrator específico: {exc}. "

                    "Fazendo fallback para leitura genérica.",

                )

                # Continua para fallback

        

        # Fallback: leitura genérica

        registrar_log(

            "info",

            "[AnalysisService] Usando leitura genérica (sem extrator específico)",

        )

        

        df = read_data_with_auto_detection(caminho)

        

        registrar_log(

            "debug",

            f"[AnalysisService] Arquivo de resultados carregado com shape={df.shape}",

        )

        

        return df



    def _detectar_e_confirmar_tipo_placa(

        self,

        arquivo_resultados: Path,

        parent_window: Any,

    ) -> Optional[str]:

        """

        Detecta automaticamente o tipo de placa PCR e solicita confirmação do usuário.



        Fluxo:

        1. Chama detectar_equipamento() no arquivo

        2. Exibe dialog com detecção + alternativas

        3. Permite escolha manual se necessário

        4. Salva no app_state: tipo_de_placa_detectado, tipo_de_placa_config, tipo_de_placa_selecionado



        Returns:

            Nome do equipamento selecionado ou None se cancelado/falhou

        """

        try:

            registrar_log(

                "info",

                f"[AnalysisService] Detectando tipo de placa em: {arquivo_resultados.name}",

            )



            # 1. Executar detecção automática

            resultado_deteccao = detectar_equipamento(str(arquivo_resultados))



            if not resultado_deteccao or not resultado_deteccao.get('equipamento'):

                registrar_log(

                    "aviso",

                    "[AnalysisService] Detecção de tipo de placa falhou ou não encontrou match",

                )

                return None



            # 2. Carregar registry para obter lista de equipamentos disponíveis

            registry = EquipmentRegistry()

            registry.load()

            equipamentos_disponiveis = registry.listar_equipamentos()



            # 3. Exibir dialog de confirmação

            from ui.equipment_detection_dialog import EquipmentDetectionDialog



            dialog = EquipmentDetectionDialog(

                master=parent_window,

                deteccao_resultado=resultado_deteccao,

                equipamentos_disponiveis=equipamentos_disponiveis,

                arquivo_nome=arquivo_resultados.name,

            )



            equipamento_selecionado = dialog.get_selecao()



            if not equipamento_selecionado:

                registrar_log(

                    "info",

                    "[AnalysisService] Usuário cancelou seleção de tipo de placa",

                )

                return None



            # 4. Carregar configuração do equipamento selecionado

            equipment_config = registry.get(equipamento_selecionado)



            if not equipment_config:

                registrar_log(

                    "erro",

                    f"[AnalysisService] Configuração não encontrada para: {equipamento_selecionado}",

                )

                return None



            # 5. Salvar no app_state

            self.app_state.tipo_de_placa_detectado = resultado_deteccao.get('equipamento')

            self.app_state.tipo_de_placa_config = equipment_config

            self.app_state.tipo_de_placa_selecionado = equipamento_selecionado



            registrar_log(

                "info",

                f"[AnalysisService] Tipo de placa confirmado: {equipamento_selecionado} "

                f"(detectado: {resultado_deteccao.get('equipamento')}, "

                f"confiança: {resultado_deteccao.get('confianca', 0)*100:.1f}%)",

            )



            return equipamento_selecionado



        except Exception as exc:

            registrar_log(

                "erro",

                f"[AnalysisService] Erro na detecção de tipo de placa: {exc}",

            )

            # Não propaga erro - continua sem detecção

            return None



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

            # Nome base do arquivo de corrida (para hist?rico e mapa)
            if resultado.caminho_entrada_resultados is not None:
                try:
                    from pathlib import Path as _Path

                    self.app_state.caminho_arquivo_corrida = _Path(
                        resultado.caminho_entrada_resultados
                    ).name
                except Exception:
                    self.app_state.caminho_arquivo_corrida = str(
                        resultado.caminho_entrada_resultados
                    )
            else:
                self.app_state.caminho_arquivo_corrida = None

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


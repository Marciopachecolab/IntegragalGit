"""
Ajustes no AnalysisService para suportar o motor universal de análise.

Este trecho assume a existência de:

- models.AppState, com pelo menos:
    - exame_selecionado: str | None
    - gabarito_extracao_montado: bool
    - resultados_analise: qualquer estrutura para armazenar o DataFrame

- Um módulo services.universal_engine com:
    - classe AnaliseContexto
    - função executar_analise_universal(contexto)

Integração:
- O método `executar_analise` passa a decidir entre o fluxo legado e o fluxo
  via motor universal, com base na presença dos metadados.
"""

from tkinter import messagebox
from typing import Dict, Optional

from models import AppState
from services import config_loader, universal_engine


class AnalysisService:
    def __init__(self, app_state: AppState) -> None:
        self.app_state = app_state

    # ------------------------------------------------------------------
    # Método público principal
    # ------------------------------------------------------------------
    def executar_analise(self) -> None:
        """
        Entrada principal do módulo de análise (chamada a partir do menu).

        1. Verifica se há exame selecionado.
        2. Tenta carregar metadados do exame, equipamento, placa e regras.
        3. Se qualquer metadado essencial estiver ausente, utiliza o fluxo
           legado (scripts específicos).
        4. Caso contrário, executa o fluxo com o motor universal.
        """
        exame = getattr(self.app_state, "exame_selecionado", None)
        if not exame:
            messagebox.showerror("Erro", "Nenhum exame selecionado.")
            return

        # 1) Configuração do exame
        config_exame = config_loader.obter_config_exame(exame)
        if not config_exame:
            # Sem metadados: mantém fluxo atual baseado em modulo_analise
            self._executar_fluxo_legado(exame)
            return

        # 2) Configurações complementares
        tipo_placa = (config_exame.get("tipo_placa") or "").strip()
        equipamento = (config_exame.get("equipamento") or "").strip()

        config_placa = config_loader.obter_config_placa(tipo_placa)
        config_equip = config_loader.obter_config_equipamento(equipamento)
        config_regras = config_loader.obter_regras_analise(exame)

        # 3) Se faltar qualquer configuração essencial, mantém fluxo legado
        if not (config_placa and config_equip and config_regras):
            self._executar_fluxo_legado(exame)
            return

        # 4) Fluxo com motor universal
        self._executar_fluxo_motor_universal(
            exame=exame,
            config_exame=config_exame,
            config_placa=config_placa,
            config_equip=config_equip,
            config_regras=config_regras,
        )

    # ------------------------------------------------------------------
    # Fluxo legado (já existente no sistema)
    # ------------------------------------------------------------------
    def _executar_fluxo_legado(self, exame: str) -> None:
        """
        Mantém o comportamento atual: utiliza modulo_analise e scripts
        específicos para cada exame.

        IMPORTANTE:
        - A implementação concreta deste método deve reutilizar a lógica
          já existente no seu arquivo original de AnalysisService
          (importação dinâmica do módulo de análise, chamada de função etc.).
        """
        # >>> IMPLEMENTAR reaproveitando o código original do seu projeto <<<
        messagebox.showinfo(
            "Fluxo legado",
            "Metadados incompletos para o exame '{}'. Usando fluxo legado de análise.".format(
                exame
            ),
        )
        # Exemplo (comentado) de como seria:
        # modulo_analise = config_exame.get("modulo_analise")
        # func = importar_funcao(modulo_analise)
        # df_resultados, meta = func(self.app_state)
        # self.app_state.resultados_analise = df_resultados
        # abrir_janela_resultados(df_resultados, meta)

    # ------------------------------------------------------------------
    # Fluxo com motor universal de análise
    # ------------------------------------------------------------------
    def _executar_fluxo_motor_universal(
        self,
        exame: str,
        config_exame: Dict[str, str],
        config_placa: Dict[str, str],
        config_equip: Dict[str, str],
        config_regras: Dict[str, str],
    ) -> None:
        """
        Executa o fluxo de análise utilizando o motor universal
        parametrizado por metadados.

        Passos:
        1. Verifica se a etapa de extração foi realizada (gabarito montado).
        2. Solicita ao usuário o arquivo de corrida.
        3. Monta o contexto de análise.
        4. Chama o motor universal.
        5. Atualiza AppState e UI.
        """
        # 1) Verificação da etapa de extração
        gabarito_ok = bool(getattr(self.app_state, "gabarito_extracao_montado", False))
        if not gabarito_ok:
            messagebox.showerror(
                "Análise impossível",
                "Etapa de extração não realizada, análise impossível. Faça a etapa de extração.",
            )
            return

        # 2) Seleção do arquivo de corrida
        caminho_arquivo_corrida = self._selecionar_arquivo_corrida()
        if not caminho_arquivo_corrida:
            # Usuário cancelou a seleção
            return

        # 3) Monta contexto de análise para o motor universal
        contexto = universal_engine.AnaliseContexto(
            app_state=self.app_state,
            exame=exame,
            config_exame=config_exame,
            config_placa=config_placa,
            config_equip=config_equip,
            config_regras=config_regras,
            caminho_arquivo_corrida=caminho_arquivo_corrida,
        )

        # 4) Executa motor universal
        df_resultados, meta = universal_engine.executar_analise_universal(contexto)

        # 5) Atualiza AppState e UI
        setattr(self.app_state, "resultados_analise", df_resultados)

        # Aqui você pode reutilizar a janela de resultados que já existe
        # no projeto para exibir df_resultados e meta.
        # Exemplo (dependendo da sua implementação atual):
        # abrir_janela_resultados(df_resultados, meta)

    # ------------------------------------------------------------------
    # Utilitário de seleção de arquivo de corrida
    # ------------------------------------------------------------------
    def _selecionar_arquivo_corrida(self) -> Optional[str]:
        """
        Abre um diálogo padrão para o usuário selecionar o arquivo de
        resultados da corrida (exportado pelo equipamento).

        Retorna o caminho selecionado ou None se o usuário cancelar.
        """
        try:
            from tkinter import filedialog
        except ImportError:
            messagebox.showerror(
                "Erro", "Tkinter/filedialog não disponível neste ambiente."
            )
            return None

        caminho = filedialog.askopenfilename(
            title="Selecione o arquivo de resultados da corrida",
            filetypes=[
                ("Arquivos Excel", "*.xlsx;*.xls"),
                ("Arquivos CSV", "*.csv"),
                ("Todos os arquivos", "*.*"),
            ],
        )
        if not caminho:
            return None
        return caminho

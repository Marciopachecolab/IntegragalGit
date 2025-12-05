"""
Gerenciador de Menu para a aplicação IntegraGAL.
Responsável por criar e gerenciar os botões do menu principal.
"""

from tkinter import messagebox, simpledialog
from typing import Optional, Tuple

import customtkinter as ctk

from exportacao.envio_gal import abrir_janela_envio_gal
from extracao.busca_extracao import carregar_dados_extracao
from services.analysis_service import AnalysisService
from utils.gui_utils import CTkSelectionDialog
from utils.logger import registrar_log


class MenuHandler:
    """Gerenciador de menu da aplicação"""

    def __init__(self, main_window):
        """
        Inicializa o gerenciador de menu

        Args:
            main_window: Instância da janela principal (App)
        """
        self.main_window = main_window
        self.analysis_service = AnalysisService()
        self._criar_botoes_menu()

    def _criar_botoes_menu(self):
        """Cria todos os botões do menu principal"""
        main_frame = self.main_window.main_frame
        frame_botoes = ctk.CTkFrame(main_frame)
        frame_botoes.pack(expand=True)

        # Lista de botões do menu
        botoes = [
            ("1. Mapeamento da Placa", self.abrir_busca_extracao),
            ("2. Realizar Análise", self.realizar_analise),
            ("3. Visualizar e Salvar Resultados", self.mostrar_resultados_analise),
            ("4. Enviar para o GAL", self.enviar_para_gal),
            ("🔧 Administração", self.abrir_administracao),  # NOVO
            ("👥 Gerenciar Usuários", self.gerenciar_usuarios),  # NOVO
            ("➕ Incluir Novo Exame", self.incluir_novo_exame),  # NOVO
            ("📊 Relatórios", self.gerar_relatorios),  # NOVO
        ]

        for texto, comando in botoes:
            ctk.CTkButton(
                frame_botoes, text=texto, command=comando, width=350, height=45
            ).pack(pady=12, padx=20)

    def abrir_busca_extracao(self):
        """Executa o mapeamento da placa/carregamento de dados"""
        self.main_window.update_status("A carregar extração...")
        self.main_window.app_state.reset_extracao_state()
        resultado = carregar_dados_extracao(self.main_window)
        if resultado:
            (
                self.main_window.app_state.dados_extracao,
                self.main_window.app_state.parte_placa,
            ) = resultado
            messagebox.showinfo(
                "Sucesso", "Extração carregada com sucesso!", parent=self.main_window
            )
            self.main_window.update_status(
                f"{len(self.main_window.app_state.dados_extracao)} amostras carregadas."
            )
        else:
            self.main_window.update_status("Carregamento de extração cancelado.")


    def _obter_detalhes_analise_via_dialogo(
        self,
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Exibe dialog para seleção de exame e lote.

        Returns
        -------
        Tuple[Optional[str], Optional[str]]
            (exame_selecionado, lote_kit) ou (None, None) se o usuário cancelar
            alguma etapa.
        """
        # Tenta obter a lista de exames disponíveis a partir do serviço.
        # Primeiro usa, se existir, o atributo de cache; se não existir ou estiver vazio,
        # chama o método público de listagem.
        try:
            exames_disponiveis = getattr(self.analysis_service, "exames_disponiveis", None)

            if (not exames_disponiveis) and hasattr(self.analysis_service, "listar_exames_disponiveis"):
                exames_disponiveis = self.analysis_service.listar_exames_disponiveis()

            # Normaliza para uma lista de strings, independentemente de como veio.
            if exames_disponiveis is None:
                lista_exames: list[str] = []
            else:
                try:
                    import pandas as _pd  # import local para evitar dependência no topo

                    # Caso seja DataFrame com coluna "exame"
                    if isinstance(exames_disponiveis, _pd.DataFrame) and "exame" in exames_disponiveis.columns:
                        lista_exames = exames_disponiveis["exame"].astype(str).tolist()
                    # Caso seja um dicionário com chave "exame"
                    elif isinstance(exames_disponiveis, dict) and "exame" in exames_disponiveis:
                        lista_exames = [str(x) for x in exames_disponiveis["exame"]]
                    else:
                        # Assume que é um iterável de strings (ou convertível para string)
                        lista_exames = [str(x) for x in exames_disponiveis]
                except Exception:
                    # Fallback extremamente defensivo
                    try:
                        lista_exames = [str(x) for x in exames_disponiveis]
                    except Exception:
                        lista_exames = []
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror(
                "Erro de Configuração",
                f"Falha ao carregar lista de exames disponíveis: {exc}",
                parent=self.main_window,
            )
            return None, None

        if not lista_exames:
            messagebox.showwarning(
                "Aviso",
                "Não há exames configurados para análise.",
                parent=self.main_window,
            )
            return None, None

        dialog = CTkSelectionDialog(
            self.main_window,
            title="Seleção de Exame",
            text="Selecione o exame para análise:",
            values=lista_exames,
        )
        exame_selecionado = dialog.get_selection()
        if not exame_selecionado:
            registrar_log("Análise", "Seleção de exame cancelada.", "INFO")
            return None, None

        lote_kit = simpledialog.askstring(
            "Lote do Kit",
            "Digite o lote do kit utilizado:",
            parent=self.main_window,
        )
        if not lote_kit:
            registrar_log("Análise", "Digitação do lote do kit cancelada.", "INFO")
            return None, None

        return exame_selecionado, lote_kit

    def _executar_servico_analise(self, exame: str, lote: str):
        """
        Executa o serviço de análise em background

        Args:
            exame: Nome do exame a ser executado
            lote: Lote do kit utilizado
        """
        try:
            ret = self.analysis_service.executar_analise(
                self.main_window.app_state, self.main_window, exame, lote
            )
            resultados_df = None

            # Extrair DataFrame de resultados do retorno
            if isinstance(ret, (tuple, list)):
                if len(ret) >= 1 and hasattr(ret[0], "empty"):
                    resultados_df = ret[0]
                else:
                    for item in ret:
                        if hasattr(item, "empty"):
                            resultados_df = item
                            break
            else:
                resultados_df = ret

            if (
                resultados_df is not None
                and hasattr(resultados_df, "empty")
                and not resultados_df.empty
            ):
                self.main_window.app_state.resultados_analise = resultados_df

                # Salvar resultado em arquivo
                try:
                    import os
                    from datetime import datetime, timezone

                    base_dir = os.path.dirname(
                        os.path.dirname(os.path.abspath(__file__))
                    )
                    reports_dir = os.path.join(base_dir, "reports")
                    os.makedirs(reports_dir, exist_ok=True)

                    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                    gal_path = os.path.join(reports_dir, f"gal_{ts}_exame.csv")

                    # Formatar dados para GAL
                    from main import _formatar_para_gal

                    df_gal = _formatar_para_gal(resultados_df)
                    df_gal.to_csv(gal_path, index=False)

                    gal_last = os.path.join(reports_dir, "gal_last_exame.csv")
                    df_gal.to_csv(gal_last, index=False)

                    # Notificar salvamento
                    from main import _notificar_gal_saved

                    _notificar_gal_saved(gal_last, parent=self.main_window)

                except Exception as e:
                    registrar_log("Export GAL", f"Falha ao gerar CSV GAL: {e}", "ERROR")

                self.mostrar_resultados_analise()
            else:
                messagebox.showwarning(
                    "Aviso", "Nenhum resultado a exibir.", parent=self.main_window
                )

        except Exception as e:
            registrar_log(
                "UI Main", f"Erro ao executar serviço de análise: {e}", "CRITICAL"
            )
            messagebox.showerror(
                "Erro", f"Falha ao executar a análise: {e}", parent=self.main_window
            )

    def realizar_analise(self):
        """Executa análise dos dados carregados"""
        if self.main_window.app_state.dados_extracao is None:
            messagebox.showerror(
                "Erro de Fluxo",
                "Execute o 'Mapeamento da Placa' primeiro.",
                parent=self.main_window,
            )
            return

        exame, lote = self._obter_detalhes_analise_via_dialogo()
        if not exame or not lote:
            return

        self.main_window.update_status(f"A executar análise para '{exame}'...")
        self.main_window.after(100, self._executar_servico_analise, exame, lote)

    def mostrar_resultados_analise(self):
        """Exibe os resultados da análise em tabela"""
        try:
            df = self.main_window.app_state.resultados_analise
            if df is None or df.empty:
                messagebox.showwarning(
                    "Aviso", "Sem resultados para exibir.", parent=self.main_window
                )
                return

            agravos = ["SC2", "HMPV", "INF A", "INF B", "ADV", "RSV", "HRV"]
            status_corrida = "N/A"
            num_placa = "N/A"
            from datetime import datetime

            data_placa_formatada = datetime.now().strftime("%d/%m/%Y")

            from utils.gui_utils import TabelaComSelecaoSimulada

            TabelaComSelecaoSimulada(
                self.main_window,
                df,
                status_corrida,
                num_placa,
                data_placa_formatada,
                agravos,
                usuario_logado=getattr(
                    self.main_window.app_state, "usuario_logado", "Desconhecido"
                ),
            )

        except Exception as e:
            registrar_log("UI Main", f"Erro ao exibir resultados: {e}", "ERROR")
            messagebox.showerror(
                "Erro", f"Falha ao exibir resultados: {e}", parent=self.main_window
            )

    def enviar_para_gal(self):
        """Abre o módulo de envio para o GAL"""
        self.main_window.update_status("Abrindo módulo de envio para o GAL...")
        try:
            abrir_janela_envio_gal(
                self.main_window, self.main_window.app_state.usuario_logado
            )
        except Exception as e:
            self.main_window.update_status("Erro ao abrir o módulo de envio.")
            registrar_log(
                "UI Main", f"Falha ao abrir a janela de envio ao GAL: {e}", "CRITICAL"
            )
            messagebox.showerror(
                "Erro Crítico",
                f"Não foi possível iniciar o módulo de envio ao GAL.\n\nDetalhes: {e}",
                parent=self.main_window,
            )

    def abrir_administracao(self):
        """Abre o painel administrativo"""
        from ui.admin_panel import AdminPanel

        AdminPanel(self.main_window, self.main_window.app_state.usuario_logado)

    def gerenciar_usuarios(self):
        """Abre o painel de gerenciamento de usuários"""
        from ui.user_management import UserManagementPanel

        UserManagementPanel(self.main_window, self.main_window.app_state.usuario_logado)

    def incluir_novo_exame(self):
        """Abre o módulo de Cadastros Diversos (exames, equipamentos, placas e regras)."""
        # Import local para evitar problemas de import circular.
        from ui.cadastros_diversos import CadastrosDiversosWindow

        CadastrosDiversosWindow(self.main_window)

    def gerar_relatorios(self):
        """Gera relatórios do sistema"""
        messagebox.showinfo(
            "Info", "Módulo de relatórios em desenvolvimento.", parent=self.main_window
        )

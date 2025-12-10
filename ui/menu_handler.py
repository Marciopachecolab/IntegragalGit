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
            main_window: InstÉ¬¢ncia da janela principal (App)
        """
        self.main_window = main_window
        # AnalysisService agora requer o AppState para operar corretamente.
        # Passamos o estado atual da aplicação (main_window.app_state).
        self.analysis_service = AnalysisService(self.main_window.app_state)
        
        # Controle de instâncias únicas de janelas
        self._resultado_window = None
        self._gal_window = None
        
        # Flags para prevenir race condition
        self._criando_janela_resultado = False
        self._criando_janela_gal = False
        
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
            ("5. Administração", self.abrir_administracao),
            ("6. Gerenciar Usuários", self.gerenciar_usuarios),
            ("7. Incluir Novo Exame", self.incluir_novo_exame),
            ("8. Relatórios", self.gerar_relatorios),
            ("9. 📊 Dashboards", self.abrir_dashboard),  # NOVO
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
        
        # Processar eventos pendentes após fechar janela modal
        self.main_window.update_idletasks()
        
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
                
                # Armazenar configuração do exame para uso posterior no GAL export
                exam_cfg = getattr(self.main_window.app_state, "exam_cfg", None)
                if exam_cfg:
                    self.main_window.app_state.exam_cfg_for_gal = exam_cfg
                
                # CSV GAL será gerado APÓS o histórico, na janela de confirmação
                registrar_log(
                    "Análise Completa",
                    "Análise concluída. CSV GAL será gerado após salvamento do histórico.",
                    "INFO",
                )

                # Só abrir janela se não houver uma já aberta OU em criação
                if self._criando_janela_resultado:
                    # Janela já está sendo criada, ignorar
                    registrar_log("UI Main", "Janela de resultados já está sendo criada, aguardando...", "INFO")
                    return
                
                if self._resultado_window and self._resultado_window.winfo_exists():
                    # Recarregar dados na janela existente
                    try:
                        self._resultado_window.recarregar_dados(resultados_df)
                        self._resultado_window.focus()
                        self._resultado_window.lift()
                        messagebox.showinfo(
                            "Análise Concluída",
                            "Nova análise concluída. Os resultados foram atualizados na janela existente.",
                            parent=self.main_window
                        )
                    except Exception as e:
                        registrar_log("UI Main", f"Erro ao recarregar dados: {e}", "ERROR")
                        # Se falhar ao recarregar, fechar janela antiga e abrir nova
                        try:
                            self._resultado_window.destroy()
                        except Exception:
                            pass
                        self._resultado_window = None
                        self.mostrar_resultados_analise()
                else:
                    # Criar nova janela
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

        # Escolher EXAME (não equipamento, pois todos usam 7500)
        exame_escolhido = self._escolher_exame()
        if not exame_escolhido:
            return  # Usuário cancelou
        
        # Obter lote
        lote = simpledialog.askstring(
            "Número do Lote/Kit",
            "Informe o número do lote/kit:",
            parent=self.main_window,
        )
        
        if not lote:
            return

        self.main_window.update_status(f"A executar análise para '{exame_escolhido}'...")
        self.main_window.after(100, self._executar_servico_analise, exame_escolhido, lote)

    def mostrar_resultados_analise(self):
        """Exibe os resultados da análise em tabela"""
        # Verificar se já está criando janela (proteção contra race condition)
        if self._criando_janela_resultado:
            registrar_log("UI Main", "Janela de resultados já está sendo criada, ignorando chamada duplicada.", "INFO")
            return
        
        # Verificar se janela de resultados já existe
        if self._resultado_window and self._resultado_window.winfo_exists():
            self._resultado_window.focus()
            self._resultado_window.lift()
            return
        
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

        # NOVO: Usar janela única com abas (elimina problemas de CTkToplevel aninhados)
        from ui.janela_analise_completa import JanelaAnaliseCompleta

        # Setar flag ANTES de criar janela (proteção contra race condition)
        self._criando_janela_resultado = True
        
        try:
            self._resultado_window = JanelaAnaliseCompleta(
                self.main_window,
                df,
                status_corrida,
                num_placa,
                data_placa_formatada,
                agravos,
                usuario_logado=getattr(
                    self.main_window.app_state, "usuario_logado", "Desconhecido"
                ),
                exame=getattr(self.main_window.app_state, "exame_selecionado", ""),
                lote=getattr(self.main_window.app_state, "lote", ""),
                arquivo_corrida=getattr(self.main_window.app_state, "caminho_arquivo_corrida", ""),
                bloco_tamanho=getattr(self.main_window.app_state, "bloco_tamanho", 2),
            )
        except Exception as e:
            registrar_log("UI Main", f"Erro ao exibir resultados: {e}", "ERROR")
            messagebox.showerror(
                "Erro", f"Falha ao exibir resultados: {e}", parent=self.main_window
            )
        finally:
            # Limpar flag após janela ser criada (sucesso ou falha)
            self._criando_janela_resultado = False

    def enviar_para_gal(self):
        """Abre o módulo de envio para o GAL"""
        # Verificar se já está criando janela (proteção contra race condition)
        if self._criando_janela_gal:
            registrar_log("UI Main", "Janela GAL já está sendo criada, ignorando chamada duplicada.", "INFO")
            return
        
        # Verificar se janela GAL já existe
        if self._gal_window and self._gal_window.winfo_exists():
            self._gal_window.focus()
            self._gal_window.lift()
            return
        
        self.main_window.update_status("Abrindo módulo de envio para o GAL...")
        
        # Setar flag ANTES de criar janela
        self._criando_janela_gal = True
        
        try:
            self._gal_window = abrir_janela_envio_gal(
                self.main_window, self.main_window.app_state.usuario_logado, 
                app_state=self.main_window.app_state
            )
        except Exception as e:
            # Garantir que flag seja limpa em caso de erro
            self.main_window.update_status("Erro ao abrir o módulo de envio.")
            registrar_log(
                "UI Main", f"Falha ao abrir a janela de envio ao GAL: {e}", "CRITICAL"
            )
            messagebox.showerror(
                "Erro Crítico",
                f"Não foi possível iniciar o módulo de envio ao GAL.\n\nDetalhes: {e}",
                parent=self.main_window,
            )
        finally:
            # Limpar flag após janela ser criada (sucesso ou falha)
            self._criando_janela_gal = False

    def abrir_administracao(self):
        """Abre o painel administrativo"""
        from ui.admin_panel import AdminPanel

        AdminPanel(self.main_window, self.main_window.app_state.usuario_logado)

    def gerenciar_usuarios(self):
        """Abre o painel de gerenciamento de usuários"""
        from ui.user_management import UserManagementPanel

        UserManagementPanel(self.main_window, self.main_window.app_state.usuario_logado)

    def incluir_novo_exame(self):
        """Abre o módulo de inclusão de novo exame"""
        from inclusao_testes.adicionar_teste import AdicionarTesteApp

        AdicionarTesteApp(self.main_window)

    def gerar_relatorios(self):
        """Abre o módulo de relatórios do sistema"""
        try:
            from relatorios.gerar_relatorios import abrir_menu_relatorios

            abrir_menu_relatorios(self.main_window)
        except Exception as e:
            registrar_log("Relatórios", f"Erro ao abrir módulo de relatórios: {e}", "ERROR")
            messagebox.showerror(
                "Erro",
                f"Falha ao abrir o módulo de relatórios:\n{e}",
                parent=self.main_window,
            )
    
    def abrir_dashboard(self):
        """Abre o Dashboard de Análises"""
        try:
            from interface.dashboard import Dashboard
            
            registrar_log("UI Main", "Abrindo Dashboard...", "INFO")
            
            # Abrir dashboard em janela separada
            dashboard = Dashboard()
            dashboard.mainloop()
            
        except Exception as e:
            registrar_log("UI Main", f"Erro ao abrir Dashboard: {e}", "ERROR")
            messagebox.showerror(
                "Erro",
                f"Falha ao abrir Dashboard:\n{str(e)}",
                parent=self.main_window
            )
    
    def _detectar_e_confirmar_equipamento(self) -> Optional[str]:
        """
        Detecta equipamento automaticamente e pede confirmação do usuário.
        
        NOTA: Atualmente usando seleção manual (OPÇÃO B).
        Para ativar detecção automática (OPÇÃO A), descomente o bloco abaixo
        e certifique-se de que app_state.arquivo_xlsx_path está sendo salvo
        durante o mapeamento da placa.
        
        Returns:
            Nome do equipamento escolhido ou None se cancelado
        """
        # ========================================================================
        # OPÇÃO B (ATIVA): Sempre usa seleção manual
        # ========================================================================
        return self._escolher_equipamento_manual()
        
        # ========================================================================
        # OPÇÃO A (DESATIVADA): Detecção automática por arquivo XLSX
        # ========================================================================
        # PARA ATIVAR OPÇÃO A:
        # 1. Comente a linha "return self._escolher_equipamento_manual()" acima
        # 2. Descomente o bloco abaixo
        # 3. Modifique busca_extracao.py para salvar o caminho do arquivo XLSX:
        #    - Adicionar self.arquivo_xlsx_path no BuscaExtracaoApp
        #    - Salvar path quando arquivo é carregado
        #    - Retornar tupla (df, parte, path) em carregar_dados_extracao()
        # 4. Modifique menu_handler.py abrir_busca_extracao() para capturar:
        #    - app_state.arquivo_xlsx_path = resultado[2]
        # ========================================================================
        
        # # Obter arquivo XLSX da extração
        # arquivo_xlsx = getattr(self.main_window.app_state, 'arquivo_xlsx_path', None)
        # 
        # # Verificação: se não tiver o caminho do arquivo, usar seleção manual
        # if not arquivo_xlsx or not os.path.exists(arquivo_xlsx):
        #     messagebox.showwarning(
        #         "Detecção Automática",
        #         "Arquivo XLSX não encontrado. Por favor, selecione o equipamento manualmente.",
        #         parent=self.main_window
        #     )
        #     return self._escolher_equipamento_manual()
        # 
        # try:
        #     # Detectar equipamento
        #     from services.equipment_detector import EquipmentDetector
        #     from services.equipment_registry import EquipmentRegistry
        #     from ui.equipment_confirmation_dialog import EquipmentConfirmationDialog
        #     
        #     self.main_window.update_status("Detectando equipamento...")
        #     
        #     detector = EquipmentDetector()
        #     resultado = detector.detectar_equipamento(arquivo_xlsx)
        #     
        #     # Carregar lista de equipamentos disponíveis
        #     registry = EquipmentRegistry()
        #     registry.load()
        #     equipamentos_disponiveis = [config.nome for config in registry.listar_todos()]
        #     
        #     # Abrir dialog de confirmação
        #     dialog = EquipmentConfirmationDialog(
        #         self.main_window,
        #         resultado,
        #         equipamentos_disponiveis
        #     )
        #     
        #     escolha = dialog.obter_escolha()
        #     
        #     if escolha:
        #         self.main_window.update_status(f"Equipamento selecionado: {escolha}")
        #         registrar_log("UI Main", f"Equipamento confirmado: {escolha}", "INFO")
        #     
        #     return escolha
        #     
        # except Exception as e:
        #     registrar_log("UI Main", f"Erro na detecção de equipamento: {e}", "ERROR")
        #     messagebox.showerror(
        #         "Erro na Detecção",
        #         f"Falha ao detectar equipamento:\n{str(e)}\n\nPor favor, selecione manualmente.",
        #         parent=self.main_window
        #     )
        #     return self._escolher_equipamento_manual()
    
    def _escolher_exame(self) -> Optional[str]:
        """
        Permite ao usuário escolher o exame para análise.
        
        Returns:
            Nome do exame ou None se cancelado
        """
        try:
            import pandas as pd
            import os
            
            # Carregar lista de exames do CSV
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            csv_path = os.path.join(base_dir, "banco", "exames_config.csv")
            
            if not os.path.exists(csv_path):
                messagebox.showerror(
                    "Erro",
                    "Arquivo de configuração de exames não encontrado.",
                    parent=self.main_window
                )
                return None
            
            df_exames = pd.read_csv(csv_path)
            lista_exames = df_exames["exame"].tolist()
            
            if not lista_exames:
                messagebox.showerror(
                    "Erro",
                    "Nenhum exame cadastrado no sistema.",
                    parent=self.main_window
                )
                return None
            
            # Usar CTkSelectionDialog para escolha
            escolha = CTkSelectionDialog(
                self.main_window,
                title="Seleção de Exame",
                text="Selecione o exame para análise:",
                values=lista_exames
            ).get_selection()
            
            return escolha
            
        except Exception as e:
            registrar_log("UI Main", f"Erro ao escolher exame: {e}", "ERROR")
            messagebox.showerror(
                "Erro",
                f"Falha ao carregar lista de exames:\n{str(e)}",
                parent=self.main_window
            )
            return None
    
    def _escolher_equipamento_manual(self) -> Optional[str]:
        """
        [OBSOLETO - Mantido para compatibilidade com código comentado]
        Permite ao usuário escolher equipamento manualmente via dialog.
        
        Returns:
            Nome do equipamento ou None se cancelado
        """
        try:
            from services.equipment_registry import EquipmentRegistry
            
            registry = EquipmentRegistry()
            registry.load()
            equipamentos = [config.nome for config in registry.listar_todos()]
            
            if not equipamentos:
                messagebox.showerror(
                    "Erro",
                    "Nenhum equipamento cadastrado no sistema.",
                    parent=self.main_window
                )
                return None
            
            # Usar CTkSelectionDialog para escolha
            escolha = CTkSelectionDialog(
                self.main_window,
                title="Seleção Manual",
                text="Selecione o equipamento:",
                values=equipamentos
            ).get_selection()
            
            return escolha
            
        except Exception as e:
            registrar_log("UI Main", f"Erro ao escolher equipamento manual: {e}", "ERROR")
            messagebox.showerror(
                "Erro",
                f"Falha ao carregar lista de equipamentos:\n{str(e)}",
                parent=self.main_window
            )
            return None

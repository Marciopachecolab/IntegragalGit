import os
import sys
import csv
from datetime import datetime
import pandas as pd
import tkinter as tk
from tkinter import messagebox, simpledialog
import customtkinter as ctk
from typing import Optional

# Define BASE_DIR e garante que ele esteja no sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# ImportaÃ§Ãµes absolutas (sempre preferÃ­vel para evitar problemas)
from utils.after_mixin import AfterManagerMixin
from utils.logger import registrar_log
from utils.gui_utils import TabelaComSelecaoSimulada
from autenticacao.login import autenticar_usuario
from extracao.busca_extracao import carregar_dados_extracao, carregar_json_temp
from utils.import_utils import importar_funcao

# Caminhos
CAMINHO_EXAMES = os.path.join(BASE_DIR, "banco", "exames_config.csv")


class App(AfterManagerMixin, ctk.CTk):
    """
    Classe principal da aplicaÃ§Ã£o que gerencia a interface grÃ¡fica e o fluxo de trabalho.
    """
    def __init__(self):
        super().__init__()
        self.title("Sistema de LaboratÃ³rio - Menu Principal")
        
        # --- MELHORIA: LÃ³gica de Estado Global ---
        # VariÃ¡veis de estado da aplicaÃ§Ã£o agora sÃ£o atributos da classe
        self.dados_extracao = None
        self.parte_placa = None
        self.resultados_analise = None
        self.lote_kit = None

        # Atributos para armazenar os dados de configuraÃ§Ã£o de exames
        self.exames_disponiveis = []
        self.modulos_analise = []

        self._carregar_configuracao_exames()
        self._configurar_interface()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        registrar_log("Sistema", "AplicaÃ§Ã£o principal inicializada.", level='INFO')

    def _carregar_configuracao_exames(self):
        """
        OtimizaÃ§Ã£o: Carrega a configuraÃ§Ã£o dos exames uma Ãºnica vez na inicializaÃ§Ã£o.
        Isso evita a leitura repetida do arquivo CSV.
        """
        registrar_log("ConfiguraÃ§Ã£o", "Carregando exames disponÃ­veis...", level='INFO')
        self.exames_disponiveis = []
        self.modulos_analise = []
        try:
            if os.path.exists(CAMINHO_EXAMES):
                with open(CAMINHO_EXAMES, newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        self.exames_disponiveis.append(row['exame'])
                        self.modulos_analise.append(row['modulo_analise'])
                registrar_log("ConfiguraÃ§Ã£o", "ConfiguraÃ§Ã£o de exames carregada com sucesso.", level='INFO')
            else:
                registrar_log("ConfiguraÃ§Ã£o", f"Arquivo de configuraÃ§Ã£o de exames nÃ£o encontrado: {CAMINHO_EXAMES}", level='ERROR')
                messagebox.showerror("Erro", f"Arquivo de configuraÃ§Ã£o de exames nÃ£o encontrado: {CAMINHO_EXAMES}")
        except Exception as e:
            registrar_log("ConfiguraÃ§Ã£o", f"Falha ao ler exames_config.csv: {e}", level='ERROR')
            messagebox.showerror("Erro", f"Falha ao ler exames_config.csv: {e}")

    def _configurar_interface(self):
        """Configura a interface principal do sistema."""
        largura_tela = self.winfo_screenwidth()
        altura_tela = self.winfo_screenheight()
        largura_janela = int(largura_tela * 0.6)
        altura_janela = int(altura_tela * 0.6)
        x_pos = int((largura_tela - largura_janela) / 2)
        y_pos = int((altura_tela - altura_janela) / 2)
        self.geometry(f"{largura_janela}x{altura_janela}+{x_pos}+{y_pos}")

        # Configurar tema
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        titulo = ctk.CTkLabel(
            self,
            text="MENU PRINCIPAL - INTEGRAÃ‡ÃƒO GAL",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        titulo.pack(pady=20)

        frame_botoes = ctk.CTkFrame(self)
        frame_botoes.pack(expand=True, padx=20, pady=20)

        botoes = [
            ("Busca de ExtraÃ§Ã£o", self.buscar_extracao),
            ("AnÃ¡lise", self.realizar_analise),
            ("Exportar Resultados CSV", self.exportar_resultados),
            ("Incluir Novo Exame", self.incluir_novo_exame),
            ("Enviar para o GAL", self.sair),  # Mantido conforme solicitado
            ("Salvar Resultados", self.salvar_resultados),
            ("SAIR", self.sair),
        ]

        for texto, comando in botoes:
            btn = ctk.CTkButton(
                frame_botoes,
                text=texto,
                width=300,
                height=40,
                command=comando,
                font=ctk.CTkFont(size=14),
                corner_radius=8
            )
            btn.pack(pady=10, padx=20)

    def buscar_extracao(self):
        """
        Inicia o processo de busca e carregamento de dados de extraÃ§Ã£o.
        Atualiza os atributos de estado da classe com os dados encontrados.
        """
        registrar_log("Menu", "Iniciando busca de extraÃ§Ã£o", level='INFO')
        
        try:
            resultado = carregar_dados_extracao(self)
            
            if resultado:
                if "dados_extracao" in resultado and "parte_placa" in resultado:
                    self.dados_extracao = resultado["dados_extracao"]
                    self.parte_placa = resultado["parte_placa"]
                    
                    registrar_log("BuscaExtraÃ§Ã£o", 
                                 f"Dados carregados: {len(self.dados_extracao)} amostras, parte {self.parte_placa}",
                                 level='INFO')
                    messagebox.showinfo("Sucesso", "Dados de extraÃ§Ã£o carregados com sucesso!")
                else:
                    registrar_log("BuscaExtraÃ§Ã£o", "Formato de dados invÃ¡lido", level='ERROR')
                    messagebox.showerror("Erro", "Formato de dados de extraÃ§Ã£o invÃ¡lido!")
            else:
                registrar_log("BuscaExtraÃ§Ã£o", "Processo cancelado ou sem dados", level='WARNING')
                messagebox.showwarning("Aviso", "Nenhum dado de extraÃ§Ã£o carregado ou processo cancelado")
                
        except Exception as e:
            registrar_log("ErroBusca", f"Falha na extraÃ§Ã£o: {str(e)}", level='ERROR')
            messagebox.showerror("Erro", f"Falha no processo de extraÃ§Ã£o:\n{str(e)}")
            
        self.focus_set()

    def realizar_analise(self):
        """
        Executa a anÃ¡lise dos dados extraÃ­dos.
        """
        registrar_log("Menu Principal", "BotÃ£o 'AnÃ¡lise' clicado.", level='INFO')

        if not self.dados_extracao or not self.parte_placa:
            json_carregado = carregar_json_temp()
            if json_carregado:
                self.dados_extracao = json_carregado.get("dados_extracao", {})
                self.parte_placa = json_carregado.get("parte_placa", 1)
            else:
                registrar_log("AnÃ¡lise", "Nenhum dado de extraÃ§Ã£o disponÃ­vel para anÃ¡lise.", level='WARNING')
                messagebox.showwarning("Aviso", "Nenhum dado de extraÃ§Ã£o carregado! Por favor, execute a 'Busca de ExtraÃ§Ã£o' primeiro.")
                return

        if not self.exames_disponiveis:
            registrar_log("AnÃ¡lise", "Nenhum exame configurado para anÃ¡lise.", level='WARNING')
            messagebox.showwarning("Aviso", "Nenhum exame foi configurado. Por favor, inclua um novo exame.")
            return

        escolha_usuario = self._exibir_dialogo_exames(self.exames_disponiveis)
        if escolha_usuario is None:
            registrar_log("AnÃ¡lise", "SeleÃ§Ã£o de exame cancelada pelo usuÃ¡rio.", level='INFO')
            return

        try:
            index_escolhido = int(escolha_usuario) - 1
            modulo_funcao_para_chamar = self.modulos_analise[index_escolhido]

            registrar_log("AnÃ¡lise", f"Iniciando anÃ¡lise para o exame: {self.exames_disponiveis[index_escolhido]} usando mÃ³dulo: {modulo_funcao_para_chamar}", level='INFO')

            funcao_analise = importar_funcao(modulo_funcao_para_chamar)
            self.resultados_analise = funcao_analise(self, self.dados_extracao, self.parte_placa)

            if self.resultados_analise is None or self.resultados_analise.empty:
                registrar_log("ExecuÃ§Ã£o AnÃ¡lise", "AnÃ¡lise retornou resultados vazios.", level='WARNING')
                messagebox.showwarning("Aviso", "A anÃ¡lise nÃ£o retornou resultados vÃ¡lidos.")
                return

            if 'Selecionado' not in self.resultados_analise.columns:
                self.resultados_analise['Selecionado'] = False
            else:
                self.resultados_analise['Selecionado'] = self.resultados_analise['Selecionado'].astype(bool)

            if 'PoÃ§os' in self.resultados_analise.columns:
                self.resultados_analise = self._ordenar_por_posicao(self.resultados_analise)
            else:
                registrar_log("AnÃ¡lise", "Coluna 'PoÃ§os' nÃ£o encontrada para ordenaÃ§Ã£o. Pulando ordenaÃ§Ã£o por posiÃ§Ã£o.", level='WARNING')

            self.abrir_analise_simulada(self.resultados_analise)
            registrar_log("ExecuÃ§Ã£o AnÃ¡lise", "AnÃ¡lise concluÃ­da e resultados exibidos na tabela de seleÃ§Ã£o.", level='INFO')

        except (IndexError, ValueError) as e:
            registrar_log("Erro AnÃ¡lise", f"Escolha de exame invÃ¡lida: {e}", level='ERROR')
            messagebox.showerror("Erro", "Escolha de exame invÃ¡lida. Por favor, selecione um nÃºmero da lista.")
        except ImportError as e:
            registrar_log("Erro AnÃ¡lise", f"Erro de importaÃ§Ã£o do mÃ³dulo de anÃ¡lise: {e}", level='ERROR')
            messagebox.showerror("Erro de ImportaÃ§Ã£o", f"NÃ£o foi possÃ­vel carregar o mÃ³dulo de anÃ¡lise: {e}\nVerifique o caminho no 'exames_config.csv'.")
        except Exception as e:
            registrar_log("Erro AnÃ¡lise", f"Ocorreu um erro inesperado durante a anÃ¡lise: {e}", level='ERROR')
            messagebox.showerror("Erro", f"Ocorreu um erro ao executar a anÃ¡lise: {e}")

    def _ordenar_por_posicao(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ordena o DataFrame pela posiÃ§Ã£o dos poÃ§os na ordem: A1+A2, A3+A4, ... H11+H12.
        Esta funÃ§Ã£o Ã© auxiliar e permanece aqui.
        """
        ordem_pocos = []
        for linha in "ABCDEFGH":
            for coluna in range(1, 13, 2):
                par = f"{linha}{coluna}+{linha}{coluna+1}"
                ordem_pocos.append(par)

        df['__ordem__'] = df['PoÃ§os'].apply(lambda x: ordem_pocos.index(x) if x in ordem_pocos else len(ordem_pocos))
        df_sorted = df.sort_values('__ordem__').drop(columns=['__ordem__']).reset_index(drop=True)
        registrar_log("AnÃ¡lise", "Resultados ordenados por posiÃ§Ã£o dos poÃ§os.", level='DEBUG')
        return df_sorted

    def abrir_analise_simulada(self, df_resultados: pd.DataFrame):
        """
        Abre a interface de anÃ¡lise com seleÃ§Ã£o simulada.
        """
        registrar_log("Menu Principal", "Abrindo janela de anÃ¡lise simulada.", level='INFO')
        if df_resultados is None or df_resultados.empty:
            messagebox.showwarning("Aviso", "Nenhum resultado vÃ¡lido encontrado para exibir na tabela.")
            return

        status_corrida = "Corrida VÃ¡lida (Simulada)"
        num_placa = "Placa de AnÃ¡lise"
        data_placa_formatada = datetime.now().strftime("%d/%m/%Y")
        agravos_para_tabela = ["SC2", "HMPV", "INF A", "INF B", "ADV", "RSV", "HRV"] # Exemplo para VR1e2

        janela_tabela = TabelaComSelecaoSimulada(
            root=self,
            dataframe=df_resultados,
            status_corrida=status_corrida,
            num_placa=num_placa,
            data_placa_formatada=data_placa_formatada,
            agravos=agravos_para_tabela,
        )
        janela_tabela.grab_set()
        self.wait_window(janela_tabela)

        registrar_log("Menu Principal", "Janela de anÃ¡lise simulada fechada.", level='INFO')
        # Atualiza a variÃ¡vel de estado apÃ³s a janela de seleÃ§Ã£o
        self.resultados_analise = janela_tabela.df_atualizado

    def _exibir_dialogo_exames(self, exames: list) -> Optional[str]:
        """
        Exibe um diÃ¡logo para seleÃ§Ã£o do exame a ser executado pelo usuÃ¡rio.
        Retorna a escolha do usuÃ¡rio ou None se o diÃ¡logo for cancelado/fechado.
        """
        registrar_log("Menu Principal", "Exibindo diÃ¡logo de seleÃ§Ã£o de exames.", level='INFO')
        dialog = ctk.CTkToplevel(master=self)
        dialog.title("Selecionar Exame")
        dialog.geometry("400x400")
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="Selecione o exame a ser executado:",
            font=ctk.CTkFont(size=12)
        ).pack(pady=15)

        frame_lista = ctk.CTkFrame(dialog)
        frame_lista.pack(fill="both", expand=True, padx=20, pady=10)

        scrollbar = ctk.CTkScrollbar(frame_lista)
        scrollbar.pack(side="right", fill="y")

        lista = tk.Listbox(
            frame_lista,
            yscrollcommand=scrollbar.set,
            font=("Arial", 11),
            selectmode="single",
            bg="#f0f0f0",
            relief="flat",
            highlightthickness=0,
        )
        lista.pack(fill="both", expand=True, padx=5, pady=5)

        for i, exame in enumerate(exames, 1):
            lista.insert("end", f"{i}. {exame}")

        scrollbar.configure(command=lista.yview)

        escolha = [None]

        def confirmar():
            selecao = lista.curselection()
            if selecao:
                escolha[0] = str(selecao[0] + 1)
            dialog.destroy()
        
        def cancelar():
            escolha[0] = None
            dialog.destroy()

        botoes_frame = ctk.CTkFrame(dialog)
        botoes_frame.pack(pady=10)

        ctk.CTkButton(
            botoes_frame,
            text="Confirmar",
            command=confirmar,
            width=100
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            botoes_frame,
            text="Cancelar",
            command=cancelar,
            width=100,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        ).pack(side="right", padx=10)
        
        dialog.protocol("WM_DELETE_WINDOW", cancelar)

        self.wait_window(dialog)
        registrar_log("Menu Principal", f"DiÃ¡logo de seleÃ§Ã£o de exames fechado. Escolha: {escolha[0]}", level='INFO')
        return escolha[0]

    def exportar_resultados(self):
        """
        Exporta os resultados de anÃ¡lise para um arquivo CSV.
        """
        registrar_log("Menu Principal", "BotÃ£o 'Exportar Resultados CSV' clicado.", level='INFO')

        if self.resultados_analise is None:
            messagebox.showwarning("ExportaÃ§Ã£o", "Nenhum resultado de anÃ¡lise disponÃ­vel para exportar. Realize uma anÃ¡lise primeiro.")
            registrar_log("ExportaÃ§Ã£o", "Tentativa de exportar sem resultados de anÃ¡lise.", level='WARNING')
            return
        
        if self.lote_kit is None:
            lote_input = simpledialog.askstring(
                "Lote do Kit",
                "Por favor, insira o nÃºmero do lote do kit para a exportaÃ§Ã£o:",
                parent=self
            )
            if not lote_input:
                messagebox.showwarning("ExportaÃ§Ã£o", "Lote do kit Ã© obrigatÃ³rio para exportar. OperaÃ§Ã£o cancelada.")
                registrar_log("ExportaÃ§Ã£o", "Lote do kit nÃ£o fornecido para exportaÃ§Ã£o.", level='WARNING')
                return
            self.lote_kit = lote_input

        try:
            export_function_path = "analise.vr1e2_biomanguinhos_7500.export_analysis_to_csv"
            export_analysis_to_csv = importar_funcao(export_function_path)
            
            export_analysis_to_csv(self.resultados_analise, self.lote_kit)
            registrar_log("ExportaÃ§Ã£o", "Resultados exportados com sucesso via funÃ§Ã£o de anÃ¡lise.", level='INFO')
        except ImportError as e:
            registrar_log("Erro ExportaÃ§Ã£o", f"FunÃ§Ã£o de exportaÃ§Ã£o nÃ£o encontrada: {e}", level='ERROR')
            messagebox.showerror(
                "Erro",
                f"Falha ao localizar a funÃ§Ã£o de exportaÃ§Ã£o:\n{e}\n"
            )
        except Exception as e:
            registrar_log("Erro ExportaÃ§Ã£o", f"Falha inesperada na exportaÃ§Ã£o dos resultados: {e}", level='ERROR')
            messagebox.showerror("Erro", f"Falha na exportaÃ§Ã£o dos resultados: {e}")

    def incluir_novo_exame(self):
        """
        Abre a interface para incluir um novo exame no sistema.
        """
        registrar_log("Menu Principal", "BotÃ£o 'Incluir Novo Exame' clicado.", level='INFO')
        try:
            adicionar_teste_path = "inclusao_testes.adicionar_teste.adicionar_novo_teste"
            adicionar_novo_teste = importar_funcao(adicionar_teste_path)
            adicionar_novo_teste()
            # ApÃ³s incluir o exame, recarrega a lista para atualizar o menu
            self._carregar_configuracao_exames()
            registrar_log("InclusÃ£o Exame", "Processo de inclusÃ£o de novo exame concluÃ­do. Lista de exames recarregada.", level='INFO')
        except ImportError as e:
            registrar_log("Erro InclusÃ£o Exame", f"MÃ³dulo de inclusÃ£o de teste nÃ£o encontrado: {e}", level='ERROR')
            messagebox.showerror("Erro", f"NÃ£o foi possÃ­vel carregar a funcionalidade de inclusÃ£o de exame: {e}")
        except Exception as e:
            registrar_log("Erro InclusÃ£o Exame", f"Erro ao iniciar inclusÃ£o de novo exame: {e}", level='ERROR')
            messagebox.showerror("Erro", f"Ocorreu um erro ao iniciar a inclusÃ£o de novo exame: {e}")

    def salvar_resultados(self):
        """
        Abre diÃ¡logo para preencher dados necessÃ¡rios para salvar resultados.
        """
        registrar_log("Menu Principal", "BotÃ£o 'Salvar Resultados' clicado.", level='INFO')

        if self.resultados_analise is None:
            messagebox.showwarning("Salvar Resultados", "Nenhum resultado disponÃ­vel para salvar.")
            registrar_log("Salvar Resultados", "Tentativa de salvar sem resultados de anÃ¡lise.", level='WARNING')
            return

        df_selecionados = self.resultados_analise[self.resultados_analise["Selecionado"]]

        if df_selecionados.empty:
            messagebox.showwarning("Salvar Resultados", "Nenhuma amostra foi marcada como 'Selecionado' para salvar.")
            registrar_log("Salvar Resultados", "Nenhuma amostra selecionada para salvar.", level='WARNING')
            return

        dialog = ctk.CTkToplevel(master=self)
        dialog.title("Salvar Resultados")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()

        campos = {
            "Lote": ctk.CTkEntry(dialog),
            "Data de LiberaÃ§Ã£o (dd/mm/aaaa)": ctk.CTkEntry(dialog),
            "Nome do Analista": ctk.CTkEntry(dialog),
        }

        for i, (label, entry) in enumerate(campos.items()):
            ctk.CTkLabel(dialog, text=label).pack(pady=(10 if i == 0 else 5))
            entry.pack(pady=5, padx=20, fill="x")

        def confirmar():
            valores = {k: v.get() for k, v in campos.items()}
            if not all(valores.values()):
                messagebox.showwarning("Campos ObrigatÃ³rios", "Todos os campos sÃ£o obrigatÃ³rios!")
                return

            try:
                datetime.strptime(valores["Data de LiberaÃ§Ã£o (dd/mm/aaaa)"], "%d/%m/%Y")
            except ValueError:
                messagebox.showerror("Erro", "Formato de data invÃ¡lido! Use dd/mm/aaaa.")
                return

            dialog.destroy()
            self._executar_salvamento(df_selecionados, valores)

        btn_frame = ctk.CTkFrame(dialog)
        btn_frame.pack(pady=15)

        ctk.CTkButton(btn_frame, text="Confirmar", command=confirmar).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancelar", command=dialog.destroy).pack(side="right", padx=10)

        self.wait_window(dialog)

    def _executar_salvamento(self, df_selecionados: pd.DataFrame, dados_adicionais: dict):
        """
        ImplementaÃ§Ã£o placeholder para salvar resultados.
        """
        registrar_log("Salvar Resultados", "Executando salvamento de resultados (placeholder).", level='INFO')
        try:
            df_copy = df_selecionados.copy()
            df_copy["Lote_Kit_Final"] = dados_adicionais["Lote"]
            df_copy["Data_Liberacao_Final"] = dados_adicionais["Data de LiberaÃ§Ã£o (dd/mm/aaaa)"]
            df_copy["Analista_Responsavel"] = dados_adicionais["Nome do Analista"]

            registrar_log("Salvar Resultados", "Resultados salvos com sucesso (placeholder).", level='INFO')
            messagebox.showinfo("Sucesso", "Resultados salvos com sucesso!")
        except Exception as e:
            registrar_log("Erro Salvar Resultados", f"Falha ao salvar resultados: {e}", level='ERROR')
            messagebox.showerror("Erro", f"Falha ao salvar resultados:\n{e}")

    def sair(self):
        """Finaliza o sistema, registra log e fecha a janela principal."""
        registrar_log("Sistema", "Sistema encerrado pelo usuÃ¡rio via Menu Principal.", level='INFO')
        self._on_close()

# ...

    def _on_close(self):
        """Callback para fechamento seguro da janela principal."""
        registrar_log("Sistema", "Janela principal fechada pelo usuÃ¡rio.", level='INFO')
        try:
            # Chama o dispose() do mixin para cancelar todos os after() agendados.
            self.dispose()
            # Verifica se a janela ainda existe antes de tentar destruÃ­-la.
            if self.winfo_exists():
                self.destroy()
        except Exception as e:
            registrar_log("Sistema", f"Erro ao fechar a janela principal: {e}", level='ERROR')
# ...

if __name__ == "__main__":
    os.chdir(BASE_DIR)
    if autenticar_usuario():
        registrar_log("Sistema", "Sistema iniciado com sucesso apÃ³s autenticaÃ§Ã£o.", level='INFO')
        root = App()
        root.mainloop()
    else:
        print("Login falhou. Programa encerrado.")
        registrar_log("Sistema", "Falha na autenticaÃ§Ã£o. Programa encerrado.", level='CRITICAL')
        sys.exit(0)

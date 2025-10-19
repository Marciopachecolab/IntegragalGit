# main_refatorado.py
import os
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog
import customtkinter as ctk
from typing import Optional
import pandas as pd

# --- Bloco de Configuração Inicial ---
# Define o diretório base e o adiciona ao path para garantir que os imports funcionem
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# --- Importações de Módulos da Aplicação ---
from utils.after_mixin import AfterManagerMixin
from utils.logger import registrar_log
from autenticacao.login import autenticar_usuario
from extracao.busca_extracao import carregar_dados_extracao
from utils.import_utils import importar_funcao
from utils.gui_utils import TabelaComSelecaoSimulada
# (Outras importações como 'adicionar_novo_teste' e 'envio_gal' iriam aqui)

# Caminho para o arquivo de configuração dos exames
CAMINHO_EXAMES = os.path.join(BASE_DIR, "banco", "exames_config.csv")

# ==============================================================================
# MELHORIA 1: Classe de Estado da Aplicação (AppState)
# Esta classe substitui as variáveis globais. Ela armazena todos os dados
# que precisam ser compartilhados entre as diferentes partes da aplicação.
# Uma instância desta classe será criada na App principal e passada para
# as janelas e funções que precisarem acessar ou modificar o estado.
# ==============================================================================
class AppState:
    """
    Armazena e gerencia o estado compartilhado da aplicação,
    eliminando a necessidade de variáveis globais.
    """
    def __init__(self):
        self.usuario_logado: Optional[str] = None
        self.dados_extracao: Optional[pd.DataFrame] = None
        self.parte_placa: Optional[int] = None
        self.resultados_analise: Optional[pd.DataFrame] = None
        self.lote_kit: Optional[str] = None

    def reset_analise_state(self):
        """Reseta o estado relacionado a uma análise específica."""
        self.resultados_analise = None
        self.lote_kit = None
        registrar_log("Estado", "Estado da análise foi resetado.", "DEBUG")

    def reset_extracao_state(self):
        """Reseta o estado da extração e da análise."""
        self.dados_extracao = None
        self.parte_placa = None
        self.reset_analise_state()
        registrar_log("Estado", "Estado da extração foi resetado.", "DEBUG")


class App(AfterManagerMixin, ctk.CTk):
    """
    Classe principal da aplicação que gerencia a interface gráfica e o fluxo de trabalho.
    """
    def __init__(self, app_state: AppState):
        super().__init__()
        
        # Armazena a instância do estado da aplicação
        self.app_state = app_state
        
        self.title("IntegraGAL - Menu Principal")
        self._configurar_janela()
        self._criar_widgets()
        
        # Callback para fechamento seguro da janela
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        registrar_log("Sistema", "Aplicação principal inicializada.", "INFO")

    def _configurar_janela(self):
        """Centraliza a configuração de geometria e aparência da janela."""
        largura_tela = self.winfo_screenwidth()
        altura_tela = self.winfo_screenheight()
        largura_janela = int(largura_tela * 0.5)
        altura_janela = int(altura_tela * 0.5)
        x_pos = int((largura_tela - largura_janela) / 2)
        y_pos = int((altura_tela - altura_janela) / 2)
        self.geometry(f"{largura_janela}x{altura_janela}+{x_pos}+{y_pos}")
        self.minsize(600, 400)
        
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

    def _criar_widgets(self):
        """Cria e posiciona os widgets da janela principal."""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        titulo = ctk.CTkLabel(main_frame, text="MENU PRINCIPAL - INTEGRAÇÃO GAL", font=ctk.CTkFont(size=24, weight="bold"))
        titulo.pack(pady=(10, 30))

        # --- Frame para os botões ---
        frame_botoes = ctk.CTkFrame(main_frame)
        frame_botoes.pack(expand=True)

        botoes = [
            ("1. Mapeamento da Placa", self.abrir_busca_extracao),
            ("2. Realizar Análise", self.realizar_analise),
            ("3. Exportar Resultados CSV", self.exportar_resultados),
            ("4. Enviar para o GAL", self.enviar_para_gal),
            ("Incluir Novo Exame", self.incluir_novo_exame),
            ("Sair", self.sair)
        ]

        for texto, comando in botoes:
            btn = ctk.CTkButton(frame_botoes, text=texto, command=comando, width=250, height=40)
            btn.pack(pady=10, padx=20)

    def abrir_busca_extracao(self):
        """Abre a janela de busca e mapeamento de extração."""
        registrar_log("Menu Principal", "Botão 'Mapeamento da Placa' clicado.", "INFO")
        
        # Reseta o estado anterior antes de carregar um novo
        self.app_state.reset_extracao_state()
        
        # A função agora recebe o estado para poder modificá-lo
        resultado = carregar_dados_extracao(self)
        
        if resultado:
            self.app_state.dados_extracao, self.app_state.parte_placa = resultado
            messagebox.showinfo(
                "Sucesso",
                f"Extração carregada com sucesso!\n- Amostras: {len(self.app_state.dados_extracao)}\n- Parte da Placa: {self.app_state.parte_placa}",
                parent=self
            )
            registrar_log("BuscaExtração", f"Dados carregados: {len(self.app_state.dados_extracao)} amostras, parte {self.app_state.parte_placa}", "INFO")
        else:
            registrar_log("BuscaExtração", "Processo de extração cancelado ou falhou.", "INFO")
            messagebox.showwarning("Aviso", "Nenhum dado de extração foi carregado.", parent=self)

    def realizar_analise(self):
        """Inicia o processo de análise dos dados de extração carregados."""
        registrar_log("Menu Principal", "Botão 'Análise' clicado.", "INFO")
        
        # --- Validação de Estado ---
        # Verifica se os dados necessários existem no AppState antes de prosseguir.
        if self.app_state.dados_extracao is None:
            messagebox.showerror("Erro", "Nenhum dado de extração carregado. Por favor, execute o 'Mapeamento da Placa' primeiro.", parent=self)
            return

        # (A lógica para selecionar o exame e chamar a função de análise viria aqui)
        # Exemplo:
        # self.app_state.resultados_analise, self.app_state.lote_kit = chamar_funcao_analise(self.app_state)
        
        messagebox.showinfo("Em desenvolvimento", "Funcionalidade de análise a ser integrada.", parent=self)

    def exportar_resultados(self):
        messagebox.showinfo("Em desenvolvimento", "Funcionalidade de exportação a ser integrada.", parent=self)
    
    def enviar_para_gal(self):
        messagebox.showinfo("Em desenvolvimento", "Funcionalidade de envio ao GAL a ser integrada.", parent=self)

    def incluir_novo_exame(self):
        messagebox.showinfo("Em desenvolvimento", "Funcionalidade de inclusão de exame a ser integrada.", parent=self)

    def sair(self):
        """Finaliza o sistema de forma segura."""
        if messagebox.askokcancel("Sair", "Tem a certeza que deseja fechar o sistema?", parent=self):
            registrar_log("Sistema", "Sistema encerrado pelo utilizador via Menu Principal.", "INFO")
            self._on_close()

    def _on_close(self):
        """Callback para fechamento seguro da janela principal."""
        registrar_log("Sistema", "Janela principal fechada pelo utilizador.", "INFO")
        try:
            # Cancela todos os timers agendados para evitar erros
            self.dispose()
            if self.winfo_exists():
                self.destroy()
        except Exception as e:
            registrar_log("Sistema", f"Erro ao fechar a janela principal: {e}", "ERROR")

# ==============================================================================
# Ponto de Entrada da Aplicação
# ==============================================================================
if __name__ == "__main__":
    # Garante que o diretório de trabalho é o do script
    os.chdir(BASE_DIR)
    
    # Inicia o processo de autenticação
    usuario_autenticado = autenticar_usuario()
    
    if usuario_autenticado:
        registrar_log("Sistema", "Sistema iniciado com sucesso após autenticação.", "INFO")
        
        # 1. Cria a instância do estado da aplicação
        estado_da_app = AppState()
        estado_da_app.usuario_logado = usuario_autenticado
        
        # 2. Injeta o estado na janela principal
        root = App(app_state=estado_da_app)
        root.mainloop()
    else:
        registrar_log("Sistema", "Login falhou ou foi cancelado. Programa encerrado.", "INFO")
        print("Login falhou. Programa encerrado.")
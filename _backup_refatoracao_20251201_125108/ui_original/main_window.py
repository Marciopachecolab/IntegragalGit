"""
Janela Principal Refatorada da aplicação IntegraGAL.
Versão modularizada para melhor manutenibilidade e escalabilidade.
"""

import os
import sys
from datetime import datetime
from typing import Optional

import customtkinter as ctk
import matplotlib
import matplotlib.pyplot as plt
from tkinter import messagebox

# Configurar matplotlib para modo não-interativo
_PLOT_OK = True
try:
    matplotlib.use('TkAgg')
except Exception:
    _PLOT_OK = False

# Garantir BASE_DIR no sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Importações locais
from autenticacao.login import autenticar_usuario
from models import AppState
from utils.after_mixin import AfterManagerMixin
from utils.logger import registrar_log

# Importações dos novos módulos
from ui.menu_handler import MenuHandler
from ui.status_manager import StatusManager
from ui.navigation import NavigationManager


class MainWindow(AfterManagerMixin, ctk.CTk):
    """Janela principal refatorada da aplicação IntegraGAL"""
    
    def __init__(self, app_state: AppState):
        """
        Inicializa a janela principal
        
        Args:
            app_state: Estado da aplicação
        """
        super().__init__()
        
        # Estado da aplicação
        self.app_state = app_state
        
        # Configuração da janela
        self.title("IntegraGAL - Menu Principal")
        self._configurar_janela()
        
        # Widgets principais
        self.main_frame: Optional[ctk.CTkFrame] = None
        
        # Gerenciadores de módulos
        self.menu_handler: Optional[MenuHandler] = None
        self.status_manager: Optional[StatusManager] = None
        self.navigation_manager: Optional[NavigationManager] = None
        
        # Criar interface
        self._criar_widgets()
        
        # Configurar eventos
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Log de inicialização
        registrar_log("Sistema", "Aplicação principal inicializada (versão refatorada).", "INFO")
    
    def _configurar_janela(self):
        """Configura as propriedades da janela principal"""
        # Obter dimensões da tela
        largura_tela = self.winfo_screenwidth()
        altura_tela = self.winfo_screenheight()
        
        # Definir dimensões da janela
        largura_janela, altura_janela = 800, 600
        x_pos = (largura_tela - largura_janela) // 2
        y_pos = (altura_tela - altura_janela) // 2
        
        # Configurar geometria
        self.geometry(f"{largura_janela}x{altura_janela}+{x_pos}+{y_pos}")
        self.minsize(700, 500)
        
        # Configurar appearance
        ctk.set_appearance_mode("System")
        
        # Configurar ícone se disponível
        try:
            # Adicionar ícone da aplicação se existir
            icon_path = os.path.join(BASE_DIR, 'assets', 'icon.ico')
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass  # Ignorar erros de ícone
    
    def _criar_widgets(self):
        """Cria todos os widgets da interface principal"""
        # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Título da aplicação
        self._criar_titulo()
        
        # Inicializar gerenciadores de módulos
        self._inicializar_gerenciadores()
    
    def _criar_titulo(self):
        """Cria o título da aplicação"""
        titulo = ctk.CTkLabel(
            self.main_frame, 
            text="MENU PRINCIPAL - INTEGRAÇÃO GAL", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        titulo.pack(pady=(10, 30))
    
    def _inicializar_gerenciadores(self):
        """Inicializa todos os gerenciadores de módulos"""
        try:
            # Gerenciador de status
            self.status_manager = StatusManager(self)
            
            # Gerenciador de navegação
            self.navigation_manager = NavigationManager(self)
            
            # Gerenciador de menu
            self.menu_handler = MenuHandler(self)
            
            registrar_log("Sistema", "Todos os gerenciadores de módulo inicializados com sucesso.", "INFO")
            
        except Exception as e:
            registrar_log("Sistema", f"Erro ao inicializar gerenciadores: {e}", "ERROR")
            # Fallback para caso de erro
            if hasattr(self, 'status_manager') and self.status_manager:
                self.status_manager.update_status("Erro na inicialização dos módulos")
    
    def update_status(self, message: str):
        """
        Atualiza a mensagem de status (método de compatibilidade)
        
        Args:
            message: Nova mensagem de status
        """
        if self.status_manager:
            self.status_manager.update_status(message)
    
    def get_main_frame(self):
        """
        Retorna o frame principal (método de compatibilidade)
        
        Returns:
            Frame principal da interface
        """
        return self.main_frame
    
    def get_app_state(self):
        """
        Retorna o estado da aplicação (método de compatibilidade)
        
        Returns:
            Estado atual da aplicação
        """
        return self.app_state
    
    def _on_close(self):
        """Handler para fechamento da aplicação"""
        if messagebox.askokcancel("Sair", "Tem a certeza que deseja fechar o sistema?", parent=self):
            registrar_log("Sistema", "Sistema encerrado pelo utilizador.", "INFO")
            
            try:
                # Finalizar a aplicação graciosamente
                self.dispose()
            except Exception:
                pass
                
            # Minimizar flash de erros de callbacks pendentes do Tk
            try:
                self.withdraw()
            except Exception:
                pass
                
            # Aguardar um pouco antes de destruir
            self.after(100, self.destroy)
    
    def show_info(self, title: str, message: str):
        """
        Exibe uma mensagem de informação (método de compatibilidade)
        
        Args:
            title: Título da janela
            message: Mensagem a ser exibida
        """
        messagebox.showinfo(title, message, parent=self)
    
    def show_warning(self, title: str, message: str):
        """
        Exibe uma mensagem de aviso (método de compatibilidade)
        
        Args:
            title: Título da janela
            message: Mensagem a ser exibida
        """
        messagebox.showwarning(title, message, parent=self)
    
    def show_error(self, title: str, message: str):
        """
        Exibe uma mensagem de erro (método de compatibilidade)
        
        Args:
            title: Título da janela
            message: Mensagem a ser exibida
        """
        messagebox.showerror(title, message, parent=self)
    
    def get_navigation_manager(self):
        """
        Retorna o gerenciador de navegação (método de acesso público)
        
        Returns:
            Instância do NavigationManager
        """
        return self.navigation_manager
    
    def get_menu_handler(self):
        """
        Retorna o gerenciador de menu (método de acesso público)
        
        Returns:
            Instância do MenuHandler
        """
        return self.menu_handler
    
    def get_status_manager(self):
        """
        Retorna o gerenciador de status (método de acesso público)
        
        Returns:
            Instância do StatusManager
        """
        return self.status_manager
    
    def refresh_interface(self):
        """Atualiza toda a interface (método para refresh manual)"""
        try:
            self._criar_widgets()
            registrar_log("Sistema", "Interface atualizada manualmente.", "INFO")
        except Exception as e:
            registrar_log("Sistema", f"Erro ao atualizar interface: {e}", "ERROR")


def criar_aplicacao_principal():
    """
    Função factory para criar a aplicação principal
    
    Returns:
        Instância da MainWindow ou None se falhar
    """
    try:
        # Autenticar usuário
        usuario_autenticado = autenticar_usuario()
        if usuario_autenticado:
            # Criar estado da aplicação
            estado = AppState()
            estado.usuario_logado = usuario_autenticado
            
            # Criar e retornar janela principal
            root = MainWindow(app_state=estado)
            return root
        else:
            registrar_log("Sistema", "Login falhou ou foi cancelado. Programa encerrado.", "INFO")
            return None
            
    except Exception as e:
        registrar_log("Sistema", f"Erro crítico ao criar aplicação principal: {e}", "CRITICAL")
        messagebox.showerror("Erro Crítico", f"Não foi possível inicializar a aplicação.\n\nDetalhes: {e}")
        return None


if __name__ == "__main__":
    """Ponto de entrada da aplicação (alternativo)"""
    import os
    os.chdir(BASE_DIR)
    
    app = criar_aplicacao_principal()
    if app:
        app.mainloop()
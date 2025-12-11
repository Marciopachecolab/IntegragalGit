# autenticacao/login.py
import sys
from tkinter import messagebox
from typing import Optional

import customtkinter as ctk

from utils.after_mixin import AfterManagerMixin
from utils.logger import registrar_log

from .auth_service import AuthService

MAX_TENTATIVAS = 3


class LoginDialog(AfterManagerMixin, ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.auth_service = AuthService()
        self.tentativas_restantes = MAX_TENTATIVAS
        self.usuario_autenticado: Optional[dict] = None  # Agora armazena dict com dados completos

        self.title("Autenticação - IntegraGAL")
        # --- CORREÇÃO: Aumenta a altura da janela ---
        self.geometry("350x350")
        self.transient(master)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._criar_widgets()
        self.grab_set()

    def _criar_widgets(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(main_frame, text="Utilizador:").pack(
            padx=10, pady=(0, 5), anchor="w"
        )
        self.user_entry = ctk.CTkEntry(main_frame)
        self.user_entry.pack(fill="x", padx=10)
        self.user_entry.focus()
        ctk.CTkLabel(main_frame, text="Senha:").pack(padx=10, pady=(10, 5), anchor="w")
        self.pass_entry = ctk.CTkEntry(main_frame, show="*")
        self.pass_entry.pack(fill="x", padx=10)
        self.pass_entry.bind("<Return>", self.verificar)
        self.login_button = ctk.CTkButton(
            main_frame, text="Login", command=self.verificar
        )
        self.login_button.pack(pady=20)

    def verificar(self, event=None):
        username = self.user_entry.get()
        password = self.pass_entry.get()
        if not username or not password:
            messagebox.showwarning(
                "Atenção", "Utilizador e senha devem ser preenchidos.", parent=self
            )
            return
        if self.auth_service.verificar_senha(username, password):
            # Obter dados completos do usuário
            dados_usuario = self.auth_service.obter_usuario(username)
            if dados_usuario:
                registrar_log(
                    "Login", f"Utilizador '{username}' autenticado com sucesso.", "INFO"
                )
                self.usuario_autenticado = dados_usuario
                self._on_close()
            else:
                registrar_log(
                    "Login", f"Erro ao obter dados do usuário '{username}'.", "ERROR"
                )
                messagebox.showerror(
                    "Erro", "Erro ao carregar dados do usuário.", parent=self
                )
        else:
            self.tentativas_restantes -= 1
            registrar_log(
                "Login",
                f"Tentativa de login falhada. Restam {self.tentativas_restantes} tentativas.",
                "WARNING",
            )
            if self.tentativas_restantes > 0:
                messagebox.showerror(
                    "Erro",
                    f"Credenciais inválidas. {self.tentativas_restantes} tentativa(s) restante(s).",
                    parent=self,
                )
            else:
                messagebox.showerror(
                    "Acesso Bloqueado",
                    "Número máximo de tentativas excedido!",
                    parent=self,
                )
                self.usuario_autenticado = None
                self._on_close(force_exit=True)

    def _on_close(self, force_exit=False):
        self.grab_release()
        self.dispose()
        self.destroy()
        if force_exit:
            sys.exit(1)


def autenticar_usuario() -> Optional[dict]:
    """
    Autentica o usuário através do diálogo de login.
    
    Returns:
        dict com dados do usuário (usuario, nivel_acesso, status) ou None se falhou/cancelou
    """
    temp_root = ctk.CTk()
    temp_root.withdraw()
    login_window = LoginDialog(master=temp_root)
    temp_root.wait_window(login_window)
    usuario_logado = login_window.usuario_autenticado
    temp_root.destroy()
    return usuario_logado

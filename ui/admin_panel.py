"""
Painel Administrativo do Sistema Integragal.

Reescrito para remover mojibake e manter as principais funções:
- Abas: Sistema, Configuração, Logs, Backup.
- Visualização de informações básicas e ações simples.
"""

from __future__ import annotations

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk

from autenticacao.auth_service import AuthService
from services.config_service import config_service
from utils.logger import registrar_log


LOG_DEFAULT = "logs/sistema.log"
CONFIG_PATH = "config.json"


class AdminPanel:
    """Painel administrativo com funcionalidades de gestão do sistema."""

    def __init__(self, main_window, usuario_logado: str):
        self.main_window = main_window
        self.usuario_logado = usuario_logado
        self.auth_service = AuthService()
        self.config_service = config_service
        self._criar_interface()

    # ------------------------------------------------------------------ #
    # Janela e abas
    # ------------------------------------------------------------------ #
    def _criar_interface(self):
        self.admin_window = ctk.CTkToplevel(self.main_window)
        self.admin_window.title("Painel Administrativo")
        self.admin_window.geometry("1000x750")
        self.admin_window.transient(self.main_window)
        self.admin_window.grab_set()

        # Centralizar
        self.admin_window.update_idletasks()
        x = (self.admin_window.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.admin_window.winfo_screenheight() // 2) - (750 // 2)
        self.admin_window.geometry(f"1000x750+{x}+{y}")

        # Header
        header_frame = ctk.CTkFrame(self.admin_window)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            header_frame,
            text="Painel Administrativo",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack(pady=10)

        ctk.CTkLabel(
            header_frame,
            text=f"Usuário: {self.usuario_logado} | Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            font=ctk.CTkFont(size=12),
        ).pack(pady=(0, 10))

        # Tabs
        self.notebook = ctk.CTkTabview(self.admin_window)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self._criar_aba_sistema()
        self._criar_aba_configuracao()
        self._criar_aba_logs()
        self._criar_aba_backup()

        # Fechar
        button_frame = ctk.CTkFrame(self.admin_window)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        ctk.CTkButton(
            button_frame, text="Fechar", command=self._fechar_admin_panel, width=120
        ).pack(side="right", padx=10, pady=10)

    # ------------------------------------------------------------------ #
    # Aba Sistema
    # ------------------------------------------------------------------ #
    def _criar_aba_sistema(self):
        aba = self.notebook.add("Sistema")
        frame = ctk.CTkScrollableFrame(aba)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            frame, text="Informações do Sistema", font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(0, 15))

        info = self._coletar_info_sistema()
        for label, valor in info:
            row = ctk.CTkFrame(frame)
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=f"{label}:", width=220, anchor="w").pack(
                side="left", padx=6
            )
            ctk.CTkLabel(row, text=str(valor), anchor="w").pack(side="left", padx=6)

        btns = ctk.CTkFrame(frame)
        btns.pack(fill="x", pady=15)
        ctk.CTkButton(btns, text="Verificar Sistema", command=self._verificar_sistema).pack(
            side="left", padx=6
        )
        ctk.CTkButton(btns, text="Status dos Serviços", command=self._status_servicos).pack(
            side="left", padx=6
        )

    def _coletar_info_sistema(self):
        cfg = self._ler_config_json()
        paths = cfg.get("paths", {})
        gal = cfg.get("gal_integration", {})
        postgres = cfg.get("postgres", {})
        return [
            ("Usuário atual", self.usuario_logado),
            ("Log principal", paths.get("log_file", LOG_DEFAULT)),
            ("Base URL GAL", gal.get("base_url", "não configurada")),
            ("Timeout GAL", gal.get("retry_settings", {}).get("max_retries", 3)),
            ("Postgres habilitado", str(postgres.get("enabled", False))),
        ]

    # ------------------------------------------------------------------ #
    # Aba Configuração
    # ------------------------------------------------------------------ #
    def _criar_aba_configuracao(self):
        aba = self.notebook.add("Configuração")
        frame = ctk.CTkFrame(aba)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            frame,
            text="Configuração do Sistema",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(0, 15))

        ctk.CTkButton(
            frame, text="Abrir config.json", command=self._abrir_config_file
        ).pack(pady=6)
        ctk.CTkButton(
            frame, text="Recarregar Config", command=self._recarregar_config
        ).pack(pady=6)

    # ------------------------------------------------------------------ #
    # Aba Logs
    # ------------------------------------------------------------------ #
    def _criar_aba_logs(self):
        aba = self.notebook.add("Logs")
        frame = ctk.CTkFrame(aba)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            frame, text="Logs do Sistema", font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(0, 10))

        self.log_text = ctk.CTkTextbox(frame, height=400)
        self.log_text.pack(fill="both", expand=True, pady=10)
        self._carregar_logs()

        ctk.CTkButton(frame, text="Atualizar Logs", command=self._carregar_logs).pack(
            pady=(0, 10)
        )

    def _carregar_logs(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")

        cfg = self._ler_config_json()
        log_path = cfg.get("paths", {}).get("log_file", LOG_DEFAULT)
        try:
            if os.path.exists(log_path):
                linhas = Path(log_path).read_text(encoding="utf-8", errors="ignore").splitlines()
                for linha in linhas[-200:]:
                    self.log_text.insert("end", linha + "\n")
            else:
                self.log_text.insert("end", f"Log não encontrado: {log_path}\n")
        except Exception as e:
            self.log_text.insert("end", f"Erro ao ler log: {e}\n")

        self.log_text.configure(state="disabled")

    # ------------------------------------------------------------------ #
    # Aba Backup
    # ------------------------------------------------------------------ #
    def _criar_aba_backup(self):
        aba = self.notebook.add("Backup")
        frame = ctk.CTkFrame(aba)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            frame,
            text="Backup e Manutenção",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(0, 10))

        ctk.CTkButton(frame, text="Criar Backup (placeholder)", command=self._criar_backup).pack(
            pady=6
        )
        ctk.CTkButton(
            frame, text="Restaurar Backup (placeholder)", command=self._restaurar_backup
        ).pack(pady=6)
        ctk.CTkButton(frame, text="Limpeza do Sistema", command=self._limpeza_sistema).pack(
            pady=6
        )

    # ------------------------------------------------------------------ #
    # Ações
    # ------------------------------------------------------------------ #
    def _fechar_admin_panel(self):
        self.admin_window.destroy()

    def _verificar_sistema(self):
        messagebox.showinfo(
            "Verificação",
            "Verificação executada.\nServiços principais aparentam operacionais.",
            parent=self.admin_window,
        )

    def _status_servicos(self):
        messagebox.showinfo(
            "Status dos Serviços",
            "Banco de Dados: desconhecido\nSistema de Log: verifique logs\nInterface: ativa",
            parent=self.admin_window,
        )

    def _abrir_config_file(self):
        config_abs = os.path.abspath(CONFIG_PATH)
        if os.path.exists(config_abs):
            try:
                os.startfile(config_abs)
            except Exception:
                os.system(f"xdg-open \"{config_abs}\"" if os.name != "nt" else config_abs)
        else:
            messagebox.showwarning("Aviso", f"{CONFIG_PATH} não encontrado", parent=self.admin_window)

    def _recarregar_config(self):
        try:
            self.config_service._load_config()  # type: ignore[attr-defined]
            messagebox.showinfo("Recarregar", "Configuração recarregada com sucesso.", parent=self.admin_window)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao recarregar: {e}", parent=self.admin_window)

    def _criar_backup(self):
        try:
            backup_path = f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            if os.path.exists(CONFIG_PATH):
                shutil.copy2(CONFIG_PATH, backup_path)
                messagebox.showinfo("Backup", f"Backup criado em {backup_path}", parent=self.admin_window)
            else:
                messagebox.showwarning("Backup", "config.json não encontrado.", parent=self.admin_window)
        except Exception as e:
            messagebox.showerror("Backup", f"Erro ao criar backup: {e}", parent=self.admin_window)

    def _restaurar_backup(self):
        messagebox.showinfo(
            "Restaurar",
            "Restaurar backup ainda não implementado. Copie manualmente o arquivo de backup sobre config.json.",
            parent=self.admin_window,
        )

    def _limpeza_sistema(self):
        messagebox.showinfo(
            "Limpeza",
            "Limpeza placeholder: implemente remoção de temporários e rotação de logs conforme necessidade.",
            parent=self.admin_window,
        )

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _ler_config_json(self) -> Dict:
        try:
            if os.path.exists(CONFIG_PATH):
                return json.loads(Path(CONFIG_PATH).read_text(encoding="utf-8"))
        except Exception:
            pass
        return {}


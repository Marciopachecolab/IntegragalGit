import os
import sys
import csv
from datetime import datetime
import pandas as pd
import tkinter as tk
from tkinter import messagebox, simpledialog
import customtkinter as ctk

# Import do mixin para gerenciamento de after() timers
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from utils.after_mixin import AfterManagerMixin
from typing import Optional

# Configurar caminhos e importaÃ§Ãµes locais
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# ImportaÃ§Ãµes de mÃ³dulos refatorados e utilitÃ¡rios
from autenticacao.login import autenticar_usuario
from extracao.busca_extracao import carregar_dados_extracao, carregar_json_temp
from utils.logger import registrar_log
from utils.import_utils import importar_funcao
from utils.gui_utils import TabelaComSelecaoSimulada

# Caminhos
CAMINHO_EXAMES = os.path.join(BASE_DIR, "banco", "exames_config.csv")

# VariÃ¡veis globais (mantidas conforme solicitado)
dados_extracao_global = None
parte_placa_global = None
resultados_analise_global = None
lote_kit_global = None


class App(AfterManagerMixin, ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de LaboratÃ³rio - Menu Principal")
        self._configurar_interface()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        registrar_log("Sistema", "AplicaÃ§Ã£o principal inicializada.", level='INFO')

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

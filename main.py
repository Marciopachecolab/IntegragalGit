"""
Ponto de entrada unificado da aplicação (sem dependência de main_refatorado).
Contém a classe App e utilitários necessários, usando AppState de models.
"""

import os
import sys
from datetime import datetime
from typing import Optional, Tuple

import customtkinter as ctk
import pandas as pd
from tkinter import messagebox, simpledialog, filedialog
import matplotlib
import matplotlib.pyplot as plt

from autenticacao.login import autenticar_usuario
from db.db_utils import salvar_historico_processamento
from extracao.busca_extracao import carregar_dados_extracao
from services.analysis_service import AnalysisService
from utils.after_mixin import AfterManagerMixin
from utils.gui_utils import TabelaComSelecaoSimulada, CTkSelectionDialog
from utils.logger import registrar_log
from exportacao.envio_gal import abrir_janela_envio_gal
from models import AppState

# Prefer TkAgg quando disponível
_PLOT_OK = True
try:
    matplotlib.use('TkAgg')
except Exception:
    _PLOT_OK = False

# Garante BASE_DIR no sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)


def _formatar_para_gal(df: 'pd.DataFrame') -> 'pd.DataFrame':
    df_out = df.copy()
    for c in ['Unnamed: 0', 'index']:
        if c in df_out.columns:
            df_out.drop(columns=[c], inplace=True)

    def _norm(col: str) -> str:
        import unicodedata
        col2 = str(col).strip()
        col2 = unicodedata.normalize('NFKD', col2).encode('ASCII', 'ignore').decode('ASCII')
        return col2.replace(' ', '_').lower()

    df_out.columns = [_norm(c) for c in df_out.columns]

    cols = list(df_out.columns)
    orden = []
    for c in ['poco','well','amostra','codigo']:
        if c in cols and c not in orden:
            orden.append(c)
    resultado_cols = [c for c in cols if c.startswith('resultado_')]
    orden.extend([c for c in resultado_cols if c not in orden])
    for t in ['sc2','hmpv','inf_a','inf_b','adv','rsv','hrv']:
        if t in cols and t not in orden:
            orden.append(t)
    for c in ['rp_1','rp_2','rp1','rp2']:
        if c in cols and c not in orden:
            orden.append(c)
    for c in cols:
        if c not in orden:
            orden.append(c)
    try:
        df_out = df_out[orden]
    except Exception:
        pass
    return df_out


def _notificar_gal_saved(path: str, parent=None, timeout: int = 5000):
    try:
        msg = f"GAL salvo: {os.path.basename(path)}\n{path}"
        if parent is None:
            registrar_log('Export GAL', msg, 'INFO')
            return
        notif = ctk.CTkToplevel(parent)
        notif.overrideredirect(True)
        notif.attributes('-topmost', True)
        lbl = ctk.CTkLabel(notif, text=msg, fg_color='#222', text_color='white', corner_radius=8)
        lbl.pack(padx=10, pady=(8, 6))
        btn_frame = ctk.CTkFrame(notif)
        btn_frame.pack(padx=8, pady=(0, 8))
        def _open_path(p):
            try:
                if os.name == 'nt':
                    os.startfile(p)
                else:
                    import subprocess
                    subprocess.Popen(['xdg-open' if os.name == 'posix' else 'open', p])
            except Exception:
                registrar_log('Export GAL', f'Falha ao abrir caminho {p}', 'WARNING')
        try:
            folder = os.path.dirname(path)
            ctk.CTkButton(btn_frame, text='Abrir pasta', width=120, command=lambda: _open_path(folder)).pack(side='left', padx=6)
            ctk.CTkButton(btn_frame, text='Abrir arquivo', width=120, command=lambda: _open_path(path)).pack(side='left', padx=6)
        except Exception:
            pass
        try:
            x = parent.winfo_rootx() + 50
            y = parent.winfo_rooty() + 50
            notif.geometry(f"+{x}+{y}")
        except Exception:
            pass
        notif.after(timeout, notif.destroy)
        registrar_log('Export GAL', f'Notificação exibida para arquivo GAL: {path}', 'INFO')
    except Exception:
        pass


class App(AfterManagerMixin, ctk.CTk):
    def __init__(self, app_state: AppState):
        super().__init__()
        self.app_state = app_state
        self.analysis_service = AnalysisService()
        self.title("IntegraGAL - Menu Principal")
        self._configurar_janela()
        self._criar_widgets()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        registrar_log("Sistema", "Aplicação principal inicializada.", "INFO")

    def _configurar_janela(self):
        largura_tela = self.winfo_screenwidth()
        altura_tela = self.winfo_screenheight()
        largura_janela, altura_janela = 800, 600
        x_pos = (largura_tela - largura_janela) // 2
        y_pos = (altura_tela - altura_janela) // 2
        self.geometry(f"{largura_janela}x{altura_janela}+{x_pos}+{y_pos}")
        self.minsize(700, 500)
        ctk.set_appearance_mode("System")

    def _criar_widgets(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(main_frame, text="MENU PRINCIPAL - INTEGRAÇÃO GAL", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(10, 30))
        frame_botoes = ctk.CTkFrame(main_frame)
        frame_botoes.pack(expand=True)
        botoes = [
            ("1. Mapeamento da Placa", self.abrir_busca_extracao),
            ("2. Realizar Análise", self.realizar_analise),
            ("3. Visualizar e Salvar Resultados", self.mostrar_resultados_analise),
            ("4. Enviar para o GAL", self.enviar_para_gal),
            ("Incluir Novo Exame", lambda: messagebox.showinfo("Info", "Funcionalidade em desenvolvimento.", parent=self)),
        ]
        for texto, comando in botoes:
            ctk.CTkButton(frame_botoes, text=texto, command=comando, width=350, height=45).pack(pady=12, padx=20)
        self.status_label = ctk.CTkLabel(main_frame, text="Status: Aguardando Ação", font=ctk.CTkFont(size=12))
        self.status_label.pack(side="bottom", pady=10)

    def update_status(self, message: str):
        self.status_label.configure(text=f"Status: {message}")
        self.update_idletasks()

    def abrir_busca_extracao(self):
        self.update_status("A carregar extração...")
        self.app_state.reset_extracao_state()
        resultado = carregar_dados_extracao(self)
        if resultado:
            self.app_state.dados_extracao, self.app_state.parte_placa = resultado
            messagebox.showinfo("Sucesso", "Extração carregada com sucesso!", parent=self)
            self.update_status(f"{len(self.app_state.dados_extracao)} amostras carregadas.")
        else:
            self.update_status("Carregamento de extração cancelado.")

    def _obter_detalhes_analise_via_dialogo(self) -> Tuple[Optional[str], Optional[str]]:
        if self.analysis_service.exames_disponiveis is None:
            messagebox.showerror("Erro de Configuração", "Lista de exames não carregada.", parent=self)
            return None, None
        lista_exames = self.analysis_service.exames_disponiveis['exame'].tolist()
        if not lista_exames:
            messagebox.showwarning("Aviso", "Não há exames configurados para análise.", parent=self)
            return None, None
        dialog = CTkSelectionDialog(self, title="Seleção de Exame", text="Selecione o exame para análise:", values=lista_exames)
        exame_selecionado = dialog.get_selection()
        if not exame_selecionado:
            registrar_log("Análise", "Seleção de exame cancelada.", "INFO")
            return None, None
        lote_kit = simpledialog.askstring("Lote do Kit", "Digite o lote do kit utilizado:", parent=self)
        if not lote_kit:
            registrar_log("Análise", "Digitação do lote do kit cancelada.", "INFO")
            return None, None
        return exame_selecionado, lote_kit

    def _executar_servico_analise(self, exame: str, lote: str):
        try:
            ret = self.analysis_service.executar_analise(self.app_state, self, exame, lote)
            resultados_df = None
            if isinstance(ret, (tuple, list)):
                if len(ret) >= 1 and hasattr(ret[0], 'empty'):
                    resultados_df = ret[0]
                else:
                    for item in ret:
                        if hasattr(item, 'empty'):
                            resultados_df = item
                            break
            else:
                resultados_df = ret
            if resultados_df is not None and hasattr(resultados_df, 'empty') and not resultados_df.empty:
                self.app_state.resultados_analise = resultados_df
                try:
                    reports_dir = os.path.join(BASE_DIR, 'reports')
                    os.makedirs(reports_dir, exist_ok=True)
                    from datetime import timezone
                    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
                    gal_path = os.path.join(reports_dir, f"gal_{ts}_exame.csv")
                    df_gal = _formatar_para_gal(resultados_df)
                    df_gal.to_csv(gal_path, index=False)
                    gal_last = os.path.join(reports_dir, 'gal_last_exame.csv')
                    df_gal.to_csv(gal_last, index=False)
                    _notificar_gal_saved(gal_last, parent=self)
                except Exception as e:
                    registrar_log('Export GAL', f'Falha ao gerar CSV GAL: {e}', 'ERROR')
                self.mostrar_resultados_analise()
            else:
                messagebox.showwarning("Aviso", "Nenhum resultado a exibir.", parent=self)
        except Exception as e:
            registrar_log("UI Main", f"Erro ao executar serviço de análise: {e}", "CRITICAL")
            messagebox.showerror("Erro", f"Falha ao executar a análise: {e}", parent=self)

    def realizar_analise(self):
        if self.app_state.dados_extracao is None:
            messagebox.showerror("Erro de Fluxo", "Execute o 'Mapeamento da Placa' primeiro.", parent=self)
            return
        exame, lote = self._obter_detalhes_analise_via_dialogo()
        if not exame or not lote:
            return
        self.update_status(f"A executar análise para '{exame}'...")
        self.after(100, self._executar_servico_analise, exame, lote)

    def mostrar_resultados_analise(self):
        try:
            df = self.app_state.resultados_analise
            if df is None or df.empty:
                messagebox.showwarning("Aviso", "Sem resultados para exibir.", parent=self)
                return
            agravos = ['SC2','HMPV','INF A','INF B','ADV','RSV','HRV']
            status_corrida = "N/A"; num_placa = "N/A"; data_placa_formatada = datetime.now().strftime('%d/%m/%Y')
            TabelaComSelecaoSimulada(self, df, status_corrida, num_placa, data_placa_formatada, agravos, usuario_logado=getattr(self.app_state,'usuario_logado','Desconhecido'))
        except Exception as e:
            registrar_log("UI Main", f"Erro ao exibir resultados: {e}", "ERROR")
            messagebox.showerror("Erro", f"Falha ao exibir resultados: {e}", parent=self)

    def enviar_para_gal(self):
        self.update_status("Abrindo módulo de envio para o GAL...")
        try:
            abrir_janela_envio_gal(self, self.app_state.usuario_logado)
        except Exception as e:
            self.update_status("Erro ao abrir o módulo de envio.")
            registrar_log("UI Main", f"Falha ao abrir a janela de envio ao GAL: {e}", "CRITICAL")
            messagebox.showerror("Erro Crítico", f"Não foi possível iniciar o módulo de envio ao GAL.\n\nDetalhes: {e}", parent=self)

    def _on_close(self):
        if messagebox.askokcancel("Sair", "Tem a certeza que deseja fechar o sistema?", parent=self):
            registrar_log("Sistema", "Sistema encerrado pelo utilizador.", "INFO")
            try:
                self.dispose()
            except Exception:
                pass
            # Minimiza pisca de erros de callbacks pendentes do Tk
            try:
                self.withdraw()
            except Exception:
                pass
            self.after(100, self.destroy)


if __name__ == "__main__":
    os.chdir(BASE_DIR)
    usuario_autenticado = autenticar_usuario()
    if usuario_autenticado:
        estado = AppState()
        estado.usuario_logado = usuario_autenticado
        root = App(app_state=estado)
        root.mainloop()
    else:
        registrar_log("Sistema", "Login falhou ou foi cancelado. Programa encerrado.", "INFO")

# main_refatorado.py
import os
import sys
from datetime import datetime
from typing import Optional, Tuple

import customtkinter as ctk
import pandas as pd
from tkinter import messagebox, simpledialog, filedialog
import matplotlib
import matplotlib.pyplot as plt

# If headless or matplotlib problems, use a fallback flag
_PLOT_OK = True
try:
    matplotlib.use('TkAgg')
except Exception:
    _PLOT_OK = False

# --- Bloco de Configuração Inicial ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# --- Importações de Módulos da Aplicação ---
from autenticacao.login import autenticar_usuario
from db.db_utils import salvar_historico_processamento
from extracao.busca_extracao import carregar_dados_extracao
from services.analysis_service import AnalysisService
from utils.after_mixin import AfterManagerMixin
from utils.gui_utils import TabelaComSelecaoSimulada, CTkSelectionDialog
from utils.logger import registrar_log
from exportacao.envio_gal import abrir_janela_envio_gal
from models import AppState


def _formatar_para_gal(df: 'pd.DataFrame') -> 'pd.DataFrame':
    """Aplica transformações necessárias ao DataFrame antes de exportar para o GAL.
    Atualmente faz:
    - remove colunas que não são necessárias (ex.: 'Código' se presente)
    - normaliza nomes de colunas para ASCII sem acentos e em minúsculas
    - ordena colunas em ordem previsível (poço, amostra, código, resultados..., rps...)
    Modifique conforme o layout exigido pelo GAL.
    """
    df_out = df.copy()
    # remove colunas temporárias ou internas que não são desejadas
    for c in ['Unnamed: 0', 'index']:
        if c in df_out.columns:
            df_out.drop(columns=[c], inplace=True)

    # basic normalization: strip and remove accents from column names
    def _norm(col: str) -> str:
        import unicodedata
        col2 = str(col).strip()
        col2 = unicodedata.normalize('NFKD', col2).encode('ASCII', 'ignore').decode('ASCII')
        return col2.replace(' ', '_').lower()

    df_out.columns = [_norm(c) for c in df_out.columns]

    # ensure typical ordering: poço, amostra, código, resultados (resultado_*), targets (SC2...), rp_1, rp_2
    cols = list(df_out.columns)
    orden = []
    for pref in ['poço','poco','poço','poco','poço'.lower(), 'poço'.upper(), 'poço']:
        pass
    # pick core columns if present
    for c in ['poço','poco','well','amostra','amostra','codigo','codigo']:
        if c in cols and c not in orden:
            orden.append(c)

    # add resultado_* cols first
    resultado_cols = [c for c in cols if c.startswith('resultado_')]
    orden.extend([c for c in resultado_cols if c not in orden])

    # then other target CT columns (SC2, HMPV etc.)
    for t in ['sc2','hmpv','inf_a','inf_b','adv','rsv','hrv']:
        if t in cols and t not in orden:
            orden.append(t)

    # rp columns
    for c in ['rp_1','rp_2','rp1','rp2']:
        if c in cols and c not in orden:
            orden.append(c)

    # finally add any remaining columns
    for c in cols:
        if c not in orden:
            orden.append(c)

    try:
        df_out = df_out[orden]
    except Exception:
        # if ordering fails, just return df with normalized columns
        pass

    return df_out


def _notificar_gal_saved(path: str, parent=None, timeout: int = 5000):
    """Mostra uma notificação transitória (não-modal) informando que o arquivo GAL foi gerado.

    parent: janela TK/CTk opcional; se não fornecida, essa rotina tentará ser silenciosa em headless mode.
    """
    try:
        # prefer customtkinter if available
        try:
            import customtkinter as ctk
            from tkinter import Toplevel
            use_ctk = True
        except Exception:
            use_ctk = False

        msg = f"GAL salvo: {os.path.basename(path)}\n{path}"
        if parent is None or not use_ctk:
            # fallback: just log
            try:
                registrar_log('Export GAL', msg, 'INFO')
            except Exception:
                pass
            return

        notif = ctk.CTkToplevel(parent)
        notif.overrideredirect(True)
        notif.attributes('-topmost', True)

        # message
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
                try:
                    registrar_log('Export GAL', f'Falha ao abrir caminho {p}', 'WARNING')
                except Exception:
                    pass

        # Open folder button
        try:
            folder = os.path.dirname(path)
            btn_open_folder = ctk.CTkButton(btn_frame, text='Abrir pasta', width=120, command=lambda: _open_path(folder))
            btn_open_folder.pack(side='left', padx=6)
        except Exception:
            pass

        # Open file button
        try:
            btn_open_file = ctk.CTkButton(btn_frame, text='Abrir arquivo', width=120, command=lambda: _open_path(path))
            btn_open_file.pack(side='left', padx=6)
        except Exception:
            pass

        try:
            x = parent.winfo_rootx() + 50
            y = parent.winfo_rooty() + 50
            notif.geometry(f"+{x}+{y}")
        except Exception:
            pass

        # auto-destroy after timeout
        notif.after(timeout, notif.destroy)
        try:
            registrar_log('Export GAL', f'Notificação exibida para arquivo GAL: {path}', 'INFO')
        except Exception:
            pass
    except Exception:
        # never raise from notification
        pass

# ==============================================================================
# CLASSE PRINCIPAL DA APLICAÇÃO (App)
# ==============================================================================
class App(AfterManagerMixin, ctk.CTk):
    """Classe principal da aplicação que gere a UI e o fluxo de trabalho."""
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
            ("Incluir Novo Exame", lambda: messagebox.showinfo("Info", "Funcionalidade em desenvolvimento.")),
        ]

        for texto, comando in botoes:
            btn = ctk.CTkButton(frame_botoes, text=texto, command=comando, width=350, height=45)
            btn.pack(pady=12, padx=20)
            
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

    def realizar_analise(self):
        if self.app_state.dados_extracao is None:
            messagebox.showerror("Erro de Fluxo", "Execute o 'Mapeamento da Placa' primeiro.", parent=self)
            return

        exame, lote = self._obter_detalhes_analise_via_dialogo()
        if not exame or not lote: return

        self.update_status(f"A executar análise para '{exame}'...")
        self.after(100, self._executar_servico_analise, exame, lote)

    def _obter_detalhes_analise_via_dialogo(self) -> Tuple[Optional[str], Optional[str]]:
        if self.analysis_service.exames_disponiveis is None:
            messagebox.showerror("Erro de Configuração", "Lista de exames não carregada.", parent=self)
            return None, None

        lista_exames = self.analysis_service.exames_disponiveis['exame'].tolist()
        if not lista_exames:
            messagebox.showwarning("Aviso", "Não há exames configurados para análise.", parent=self)
            return None, None
            
        dialog = CTkSelectionDialog(self,
                                    title="Seleção de Exame",
                                    text="Selecione o exame para análise:",
                                    values=lista_exames)
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

            # Normalize return into (resultados_df, exame_ret, lote_ret)
            resultados_df = None
            exame_ret = None
            lote_ret = None

            if isinstance(ret, (tuple, list)):
                if len(ret) == 3:
                    resultados_df, exame_ret, lote_ret = ret
                elif len(ret) == 2:
                    resultados_df, exame_ret = ret
                elif len(ret) == 1:
                    resultados_df = ret[0]
                else:
                    # Try to find the first DataFrame-like item
                    for item in ret:
                        if hasattr(item, 'empty') or isinstance(item, pd.DataFrame):
                            resultados_df = item
                            break
            else:
                resultados_df = ret

            # If resultados_df is still a tuple/list, pick the first DataFrame-like element
            if isinstance(resultados_df, (tuple, list)):
                for item in resultados_df:
                    if hasattr(item, 'empty') or isinstance(item, pd.DataFrame):
                        resultados_df = item
                        break

            # Final check: ensure resultados_df looks like a DataFrame
            if resultados_df is not None and hasattr(resultados_df, 'empty') and not resultados_df.empty:
                self.app_state.resultados_analise = resultados_df
                # --- gravação automática para GAL (arquivo previsível em reports/) ---
                try:
                    reports_dir = os.path.join(BASE_DIR, 'reports')
                    os.makedirs(reports_dir, exist_ok=True)
                    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
                    gal_name = f"gal_{ts}_exame.csv"
                    gal_path = os.path.join(reports_dir, gal_name)
                    # write CSV
                    try:
                        # format for GAL
                        try:
                            df_gal = _formatar_para_gal(resultados_df)
                        except Exception:
                            df_gal = resultados_df

                        df_gal.to_csv(gal_path, index=False)
                        # also write a fixed-name copy for GAL to read predictably
                        gal_last = os.path.join(reports_dir, 'gal_last_exame.csv')
                        try:
                            df_gal.to_csv(gal_last, index=False)
                        except Exception:
                            pass

                        # attempt to notify the UI (non-critical)
                        try:
                            _notificar_gal_saved(gal_last, parent=self)
                        except Exception:
                            pass

                        registrar_log('Export GAL', f'Arquivo GAL gravado automaticamente em {gal_path} e {gal_last}', 'INFO')
                        # try to register in history if available
                        try:
                            salvar_historico_processamento(gal_path, usuario=getattr(self.app_state, 'usuario_logado', 'unknown'))
                        except Exception:
                            pass
                    except Exception as e_csv:
                        registrar_log('Export GAL', f'Falha ao gravar CSV GAL: {e_csv}', 'ERROR')
                except Exception:
                    # não crítico se o diretório não puder ser criado
                    pass
                # Only set these if they were returned
                if exame_ret:
                    self.app_state.exame_selecionado = exame_ret
                if lote_ret:
                    self.app_state.lote_kit = lote_ret
                self.update_status(f"Análise de '{exame}' concluída.")
                messagebox.showinfo("Sucesso", "Análise concluída com sucesso! Pode agora visualizar os resultados.", parent=self)
            else:
                registrar_log("Análise", f"Retorno inesperado de executar_analise: type={type(ret)}, repr={repr(ret)[:500]}", "ERROR")
                self.update_status("Análise falhou ou foi cancelada.")
        except Exception as e:
            registrar_log("Análise", f"Erro ao executar análise: {e}", "ERROR")
            self.update_status("Análise interrompida por erro.")
            messagebox.showerror("Erro", f"Erro durante a execução da análise: {e}", parent=self)

    def mostrar_resultados_analise(self):
        if self.app_state.resultados_analise is None:
            messagebox.showerror("Erro de Fluxo", "Nenhum resultado de análise disponível. Execute a análise primeiro.", parent=self)
            return
            
        try:
            df_resultados = self.app_state.resultados_analise
            status_corrida = df_resultados['Status_Corrida'].iloc[0] if 'Status_Corrida' in df_resultados.columns else 'N/A'
            
            agravos = ['SC2', 'HMPV', 'INF A', 'INF B', 'ADV', 'RSV', 'HRV'] 

            tabela_window = TabelaComSelecaoSimulada(
                root=self,
                dataframe=df_resultados,
                status_corrida=status_corrida,
                num_placa=self.app_state.lote_kit or "N/A",
                data_placa_formatada=datetime.now().strftime("%d-%m-%Y"),
                agravos=agravos,
                usuario_logado=self.app_state.usuario_logado
            )
            tabela_window.grab_set()
            self.wait_window(tabela_window)
            self.update_status("Visualização e salvamento de resultados concluído.")
        except Exception as e:
            registrar_log("UI Main", f"Erro ao exibir tabela de resultados: {e}", "ERROR")
            # Fallback: show a simple summary window with stats and a small plot if matplotlib available
            try:
                df_resultados = self.app_state.resultados_analise
                win = ctk.CTkToplevel(self)
                win.title("Resumo de Resultados (fallback)")
                win.geometry("900x700")

                header = ctk.CTkLabel(win, text="Resumo Rápido de Resultados", font=ctk.CTkFont(size=16, weight='bold'))
                header.pack(padx=10, pady=(10, 5))

                frame_top = ctk.CTkFrame(win)
                frame_top.pack(fill='x', padx=10, pady=5)

                # prefer status from the dataframe if present
                try:
                    df_status = df_resultados['Status_Corrida'].iloc[0] if 'Status_Corrida' in df_resultados.columns else getattr(self.app_state, 'status_corrida', 'N/A')
                except Exception:
                    df_status = getattr(self.app_state, 'status_corrida', 'N/A')
                lbl_status = ctk.CTkLabel(frame_top, text=f"Status da corrida: {df_status}")
                lbl_status.grid(row=0, column=0, sticky='w', padx=6, pady=4)

                def _export_csv():
                    try:
                        # default reports directory
                        reports_dir = os.path.join(BASE_DIR, 'reports')
                        os.makedirs(reports_dir, exist_ok=True)
                        default_name = f"resultados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                        path = filedialog.asksaveasfilename(parent=win, initialdir=reports_dir, initialfile=default_name, defaultextension='.csv', filetypes=[('CSV files','*.csv')], title='Salvar CSV como')
                        if path:
                            df_resultados.to_csv(path, index=False)
                            registrar_log('Export', f'Resultados exportados para {path}', 'INFO')
                            # try to record in DB/historico if util available
                            try:
                                salvar_historico_processamento(path, usuario=getattr(self.app_state, 'usuario_logado', 'unknown'))
                            except Exception:
                                # not critical if this function isn't available/works
                                pass
                            messagebox.showinfo("Exportado", f"Arquivo salvo em: {path}", parent=win)
                            try:
                                # transient non-modal notification
                                def _show_notification(msg, timeout=3000):
                                    notif = ctk.CTkToplevel(self)
                                    notif.overrideredirect(True)
                                    notif.attributes('-topmost', True)
                                    lbl = ctk.CTkLabel(notif, text=msg, fg_color='#222', text_color='white', corner_radius=8)
                                    lbl.pack(padx=10, pady=6)
                                    # position near parent
                                    try:
                                        x = self.winfo_rootx() + 50
                                        y = self.winfo_rooty() + 50
                                        notif.geometry(f"+{x}+{y}")
                                    except Exception:
                                        pass
                                    notif.after(timeout, notif.destroy)
                                _show_notification(f"Arquivo salvo: {os.path.basename(path)}\n{path}")
                            except Exception:
                                pass
                    except Exception as ee:
                        registrar_log('Export', f'Falha ao exportar CSV: {ee}', 'ERROR')
                        messagebox.showerror("Erro", f"Falha ao salvar CSV: {ee}", parent=win)

                btn_export = ctk.CTkButton(frame_top, text="Exportar CSV", command=_export_csv)
                btn_export.grid(row=0, column=1, sticky='e', padx=6, pady=4)

                # Placeholder - will be enabled if a plot is rendered
                save_plot_btn = ctk.CTkButton(frame_top, text="Salvar Gráfico", state='disabled')
                save_plot_btn.grid(row=0, column=2, sticky='e', padx=6, pady=4)

                # Stats area
                stats_frame = ctk.CTkFrame(win)
                stats_frame.pack(fill='both', expand=False, padx=10, pady=6)

                stats_txt = ctk.CTkTextbox(stats_frame, wrap='none', height=220)
                stats_txt.pack(fill='both', expand=True, padx=6, pady=6)

                stats_lines = []
                for col in df_resultados.columns:
                    if str(col).startswith('Resultado_'):
                        vc = df_resultados[col].value_counts(dropna=True).to_dict()
                        stats_lines.append(f"{col}: {vc}")
                stats_txt.insert('0.0', "\n".join(stats_lines) if stats_lines else "Nenhuma coluna Resultado_* encontrada.")
                stats_txt.configure(state='disabled')

                # Optional plot area
                plot_frame = ctk.CTkFrame(win)
                plot_frame.pack(fill='both', expand=True, padx=10, pady=6)

                fig = None
                canvas = None
                if _PLOT_OK:
                    try:
                        fig, ax = plt.subplots(figsize=(6, 3))
                        if 'RP_1' in df_resultados.columns:
                            vals = pd.to_numeric(df_resultados['RP_1'], errors='coerce').dropna()
                            if not vals.empty:
                                ax.hist(vals, bins=10)
                                ax.set_title('Distribuição RP_1')
                            else:
                                ax.text(0.5, 0.5, 'Nenhum valor numérico em RP_1 para plotar', ha='center')
                        else:
                            ax.text(0.5, 0.5, 'Coluna RP_1 ausente', ha='center')

                        canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(fig, master=plot_frame)
                        canvas.draw()
                        canvas.get_tk_widget().pack(fill='both', expand=True)
                        # enable save button if we have a figure
                        def _save_plot():
                            try:
                                reports_dir = os.path.join(BASE_DIR, 'reports')
                                os.makedirs(reports_dir, exist_ok=True)
                                default_name = f"grafico_resultados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                                path = filedialog.asksaveasfilename(parent=win, initialdir=reports_dir, initialfile=default_name, defaultextension='.png', filetypes=[('PNG','*.png'),('PDF','*.pdf')], title='Salvar Gráfico como')
                                if path and fig is not None:
                                    fig.savefig(path)
                                    registrar_log('Export', f'Gráfico salvo em {path}', 'INFO')
                                    try:
                                        salvar_historico_processamento(path, usuario=getattr(self.app_state, 'usuario_logado', 'unknown'))
                                    except Exception:
                                        pass
                                    messagebox.showinfo('Salvo', f'Gráfico salvo em: {path}', parent=win)
                                    try:
                                        def _show_notification(msg, timeout=3000):
                                            notif = ctk.CTkToplevel(self)
                                            notif.overrideredirect(True)
                                            notif.attributes('-topmost', True)
                                            lbl = ctk.CTkLabel(notif, text=msg, fg_color='#222', text_color='white', corner_radius=8)
                                            lbl.pack(padx=10, pady=6)
                                            try:
                                                x = self.winfo_rootx() + 50
                                                y = self.winfo_rooty() + 50
                                                notif.geometry(f"+{x}+{y}")
                                            except Exception:
                                                pass
                                            notif.after(timeout, notif.destroy)
                                        _show_notification(f"Gráfico salvo: {os.path.basename(path)}\n{path}")
                                    except Exception:
                                        pass
                            except Exception as ee:
                                registrar_log('Export', f'Erro ao salvar gráfico: {ee}', 'ERROR')
                                messagebox.showerror('Erro', f'Não foi possível salvar o gráfico: {ee}', parent=win)

                        save_plot_btn.configure(state='normal', command=_save_plot)
                    except Exception:
                        lbl = ctk.CTkLabel(plot_frame, text='Plot indisponível no ambiente atual.')
                        lbl.pack(padx=10, pady=10)
                else:
                    lbl = ctk.CTkLabel(plot_frame, text='Matplotlib/TkAgg não disponível; sem plot.')
                    lbl.pack(padx=10, pady=10)

                messagebox.showinfo("Aviso", f"Interface principal falhou ao abrir (detalhes no log). Mostrando fallback.", parent=self)
            except Exception as e2:
                registrar_log("UI Main", f"Fallback também falhou: {e2}", "ERROR")
                messagebox.showerror("Erro de Visualização", f"Não foi possível exibir os resultados (fallback também falhou).\n\nDetalhes: {e2}", parent=self)

    def enviar_para_gal(self):
        self.update_status("A abrir o módulo de envio para o GAL...")
        try:
            abrir_janela_envio_gal(self, self.app_state.usuario_logado)
        except Exception as e:
            self.update_status("Erro ao abrir o módulo de envio.")
            registrar_log("UI Main", f"Falha ao abrir a janela de envio ao GAL: {e}", "CRITICAL")
            messagebox.showerror("Erro Crítico", f"Não foi possível iniciar o módulo de envio ao GAL.\n\nDetalhes: {e}", parent=self)

    def _on_close(self):
        if messagebox.askokcancel("Sair", "Tem a certeza que deseja fechar o sistema?", parent=self):
            registrar_log("Sistema", "Sistema encerrado pelo utilizador.", "INFO")
            self.dispose()
            self.destroy()

# ==============================================================================
# PONTO DE ENTRADA DA APLICAÇÃO
# ==============================================================================
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
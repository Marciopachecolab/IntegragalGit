# analise/vr1e2_biomanguinhos_7500.py
import os
import sys
from datetime import datetime
from typing import Optional, Tuple, Any
import unicodedata  # Importado para normalização de strings
import tkinter.simpledialog as simpledialog  # Para diálogos

import customtkinter as ctk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tkinter import filedialog, messagebox

# --- Bloco de Configuração Inicial ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from models import AppState
from utils.logger import registrar_log
from utils.after_mixin import AfterManagerMixin
from utils.gui_utils import TabelaComSelecaoSimulada

# ==============================================================================
# 1. CONSTANTES E FUNÇÕES DE LÓGICA PURA
# ==============================================================================
CT_RP_MIN = 10
CT_RP_MAX = 35
CT_DETECTAVEL_MIN = 10
CT_DETECTAVEL_MAX = 38
CT_INCONCLUSIVO_MIN = 38.01
CT_INCONCLUSIVO_MAX = 40
TARGET_LIST = ['SC2', 'HMPV', 'INF A', 'INF B', 'ADV', 'RSV', 'HRV']
ALL_TARGETS = [target.upper() for target in TARGET_LIST + ['RP']]  # Normalizado para maiúsculas

def _processar_ct(ct_value: Any) -> Optional[float]:
    if isinstance(ct_value, (int, float)) and pd.notna(ct_value): return float(ct_value)
    if isinstance(ct_value, str):
        ct_value = ct_value.strip().upper()  # Normaliza para maiúsculas
        if ct_value in ('UNDETERMINED', 'NA', '', 'N/D'): return None
        try: return float(ct_value.replace(',', '.'))
        except (ValueError, TypeError): return None
    return None

def _interpretar_resultado(ct_rp1: Optional[float], ct_rp2: Optional[float], ct_alvo: Optional[float]) -> str:
    """
    Interpreta resultado usando ambos os RPs. Ambos os RPs devem estar dentro do intervalo [CT_RP_MIN, CT_RP_MAX]
    para que um alvo possa ser considerado válido/detectado.
    """
    # Se alvo ausente -> por padrão considerar Inválido aqui.
    # A regra 'Não Detectado' é aplicada mais acima apenas quando o arquivo qPCR indica
    # que havia uma amostra (SampleName) para aquele well+target, mas o CT é ausente.
    if ct_alvo is None:
        return "Inválido"

    # Verifica RPs
    if ct_rp1 is None or ct_rp2 is None:
        return "Inválido"

    if not (CT_RP_MIN < ct_rp1 < CT_RP_MAX and CT_RP_MIN < ct_rp2 < CT_RP_MAX):
        return "Inválido"

    # Agora interpreta o alvo com base nos limites
    if ct_alvo <= CT_DETECTAVEL_MAX:
        return "Detectado"
    if CT_INCONCLUSIVO_MIN <= ct_alvo <= CT_INCONCLUSIVO_MAX:
        return "Inconclusivo"
    return "Inválido"

def preview_extracao_sheet(caminho_arquivo: str) -> None:
    """Exibe a pré-visualização da matriz no intervalo B10:M17 (8 linhas x 12 colunas)."""
    try:
        # Lê apenas o intervalo B10:M17: colunas B a M (índices 1 a 12)
        df_preview = pd.read_excel(caminho_arquivo, usecols="B:M", skiprows=9, nrows=8, header=None)
        
        preview_window = ctk.CTkToplevel()
        preview_window.title("Pré-Visualização da Matriz (B10:M17)")
        preview_window.geometry("600x400")
        
        label = ctk.CTkLabel(preview_window, text="Matriz da Planilha (B10:M17):", font=ctk.CTkFont(size=14, weight="bold"))
        label.pack(pady=10)
        
        table_frame = ctk.CTkFrame(preview_window)
        table_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        for i, row in df_preview.iterrows():
            for j, value in enumerate(row):
                cell_label = ctk.CTkLabel(table_frame, text=str(value), width=80, height=30, fg_color="transparent", corner_radius=5)
                cell_label.grid(row=i, column=j, padx=5, pady=5)
        
        registrar_log("Pré-Visualização", "Pré-visualização da matriz B10:M17 exibida com sucesso.", "INFO")
        preview_window.wait_window()
    except Exception as e:
        registrar_log("Pré-Visualização", f"Erro ao exibir pré-visualização: {e}", "ERROR")
        messagebox.showerror("Erro na Pré-Visualização", f"Não foi possível carregar a matriz. Erro: {e}")

def analisar_placa_vr1e2_7500(caminho_arquivo_resultados: str, dados_extracao_df: pd.DataFrame, parte_placa: int) -> Tuple[Optional[pd.DataFrame], str]:
    registrar_log("Análise VR1e2", f"Iniciando análise do arquivo: {os.path.basename(caminho_arquivo_resultados)}", "INFO")
    
    try:
        df_raw = pd.read_excel(caminho_arquivo_resultados, header=None, skiprows=8, engine='openpyxl')
        
        df_raw.columns = [
            unicodedata.normalize('NFKD', str(col))
            .encode('ASCII', 'ignore')
            .decode('ASCII')
            .upper()
            .strip() for col in df_raw.columns
        ]
        
        expected_columns = [
            'WELL', 'SAMPLE NAME', 'TARGET NAME', 'TASK', 'REPORTER', 'QUENCHER', 
            'CT', 'CT MEAN', 'CT SD', 'QUANTITY', 'QUANTITY MEAN', 'QUANTITY SD', 
            'AUTOMATIC CT THRESHOLD', 'CT THRESHOLD', 'AUTOMATIC BASELINE', 
            'BASELINE START', 'BASELINE END', 'COMMENTS', 'HIGHSD', 'EXPFAIL'
        ]
        
        if len(df_raw.columns) != len(expected_columns):
            raise ValueError(f"Número de colunas incorreto: esperado {len(expected_columns)}, encontrado {len(df_raw.columns)}.")
        
        df_raw.columns = expected_columns
        
        df_raw['TARGET NAME'] = df_raw['TARGET NAME'].apply(lambda x: str(x).upper().strip() if pd.notna(x) else x)
        
        required_cols = ['WELL', 'SAMPLE NAME', 'TARGET NAME', 'CT']
        missing_cols = [col for col in required_cols if col not in df_raw.columns]
        if missing_cols:
            raise KeyError(f"Colunas essenciais não encontradas: {missing_cols}.")
        
        registrar_log("Análise VR1e2", f"DataFrame após leitura: {df_raw.shape} linhas", "DEBUG")
        
    except Exception as e:
        registrar_log("Análise VR1e2", f"Erro ao ler o arquivo: {e}", "ERROR")
        raise ValueError(f"Erro na leitura: {e}")
    
    df_filtered = df_raw[required_cols].copy()
    df_filtered = df_filtered[df_filtered['TARGET NAME'].isin(ALL_TARGETS)]
    df_filtered.dropna(subset=['SAMPLE NAME'], inplace=True)

    registrar_log("Análise VR1e2", f"DataFrame filtrado: {df_filtered.shape} linhas", "DEBUG")

    # Normalize and process CT by WELL and TARGET
    df_proc = pd.DataFrame()
    df_proc['WELL'] = df_filtered['WELL'].astype(str).str.strip()
    df_proc['SampleName'] = df_filtered['SAMPLE NAME'].astype(str).str.replace('.0', '', regex=False).str.strip()
    df_proc['Target'] = df_filtered['TARGET NAME']
    df_proc['CT'] = df_filtered['CT'].apply(_processar_ct)

    if df_proc['CT'].isna().all():
        registrar_log("Análise VR1e2", "Aviso: Todos os valores de CT são NaN.", "WARNING")

    # Merge CT data (by WELL) with the extraction mapping (dados_extracao_df has 'Poço' column)
    if 'Poço' not in dados_extracao_df.columns:
        raise KeyError("dados_extracao_df deve conter a coluna 'Poço' com a designação dos poços (ex: A1).")

    # Ensure Poço values are strings and stripped
    dados_extracao_df = dados_extracao_df.copy()
    dados_extracao_df['Poço'] = dados_extracao_df['Poço'].astype(str).str.strip()

    merged = pd.merge(dados_extracao_df, df_proc, left_on='Poço', right_on='WELL', how='left')

    # Build per-sample results by using the two associated wells per Amostra.
    # Assumption: cada 'Amostra' no mapeamento aparece em dois poços (poço1, poço2).
    targets_poço1 = ['HMPV', 'INF A', 'INF B', 'SC2']
    targets_poço2 = ['ADV', 'HRV', 'RSV']

    samples = dados_extracao_df['Amostra'].astype(str).unique().tolist()
    rows = []
    import re
    def _parse_well(well: str):
        if not well or pd.isna(well):
            return None, None
        m = re.match(r"^([A-Za-z]+)(\d+)$", str(well).strip())
        if not m:
            return None, None
        row = m.group(1).upper()
        col = int(m.group(2))
        return row, col

    for samp in samples:
        # determine associated wells for this sample
        pocos = dados_extracao_df.loc[dados_extracao_df['Amostra'].astype(str) == str(samp), 'Poço'].astype(str).str.strip().tolist()
        well1 = None
        well2 = None
        if len(pocos) >= 2:
            well1 = pocos[0]
            well2 = pocos[1]
        elif len(pocos) == 1:
            r, c = _parse_well(pocos[0])
            if r is not None and c is not None:
                start = c if (c % 2 == 1) else (c - 1)
                well1 = f"{r}{start}"
                well2 = f"{r}{start + 1}"

        row = {'Sample': str(samp)}

        def _ct_for(target, well):
            if well is None:
                return None
            s = df_proc[(df_proc['WELL'] == str(well)) & (df_proc['Target'] == target.upper())]['CT']
            # olhar valores brutos para capturar Undetermined textual
            try:
                s_raw = df_filtered[(df_filtered['WELL'] == str(well)) & (df_filtered['TARGET NAME'] == target.upper())]['CT']
            except Exception:
                s_raw = []
            s_valid = [v for v in s.tolist() if v is not None and pd.notna(v)]
            if s_valid:
                return s_valid[0]
            # se n�o houver num�rico v�lido, mas houver 'Undetermined' textual, preserve
            try:
                for rv in (s_raw.tolist() if hasattr(s_raw, 'tolist') else list(s_raw)):
                    if isinstance(rv, str) and rv.strip().upper() == 'UNDETERMINED':
                        return 'Undetermined'
            except Exception:
                pass
            return None

        # initial RP reads
        rp1 = _ct_for('RP', well1)
        rp2 = _ct_for('RP', well2)

        def _count_present_targets(well, targets):
            if well is None:
                return 0
            cnt = 0
            for t in targets:
                v = _ct_for(t, well)
                if v is not None:
                    cnt += 1
            return cnt

        # swap heuristic
        swap = False
        if rp1 is None and rp2 is not None:
            swap = True
        else:
            cnt_w1 = _count_present_targets(well1, targets_poço1)
            cnt_w2 = _count_present_targets(well2, targets_poço1)
            if cnt_w2 > cnt_w1:
                swap = True

        if swap:
            # perform swap and record audit
            old_w1, old_w2 = well1, well2
            well1, well2 = well2, well1
            rp1, rp2 = rp2, rp1
            row['Swap_Reason'] = 'Heuristica:RP/target_count'
            row['Swap_Timestamp'] = datetime.utcnow().isoformat() + 'Z'
            try:
                registrar_log('Análise VR1e2', f"Swap automático aplicado para amostra {samp}: {old_w1}->{well1}, {old_w2}->{well2}", 'INFO')
            except Exception:
                pass

        # assign final values
        row['RP_1'] = rp1
        row['RP_2'] = rp2
        row['Valid'] = not (rp1 is None or rp2 is None)
        if 'Swap_Reason' not in row:
            row['Swap_Reason'] = None
            row['Swap_Timestamp'] = None
        row['Well1'] = well1
        row['Well2'] = well2

        # populate target CTs
        for t in TARGET_LIST:
            if t.upper() in [x.upper() for x in targets_poço1]:
                row[t.upper()] = _ct_for(t, well1)
            else:
                row[t.upper()] = _ct_for(t, well2)

        rows.append(row)

    # build pivot from rows
    df_pivot = pd.DataFrame(rows)

    status_corrida = "Válida"
    try:
        # 1) Prefer overrides from app_state if provided
        control_cn_wells = None
        control_cp_wells = None
        try:
            # app_state may or may not be available in this module; try to get overrides
            # (in UI flow, iniciar_fluxo_analise passes app_state via master_window.app_state)
            if hasattr(dados_extracao_df, '__dict__'):
                # nothing
                pass
        except Exception:
            pass

        # If the caller provided explicit overrides in the AppState, use them
        caller_app_state = None
        try:
            # try to find an AppState on the calling frame (best-effort)
            import inspect
            for fr in inspect.stack():
                locs = fr.frame.f_locals
                if 'app_state' in locs and hasattr(locs['app_state'], 'control_cn_wells'):
                    caller_app_state = locs['app_state']
                    break
        except Exception:
            caller_app_state = None

        if caller_app_state is not None and getattr(caller_app_state, 'control_cn_wells', None):
            control_cn_wells = [w.upper() for w in caller_app_state.control_cn_wells]
        if caller_app_state is not None and getattr(caller_app_state, 'control_cp_wells', None):
            control_cp_wells = [w.upper() for w in caller_app_state.control_cp_wells]

        # 2) If no overrides, attempt to auto-detect by scanning the extraction mapping for sample names containing 'CN'/'CP'
        amostras_cn = []
        amostras_cp = []
        if control_cn_wells:
            amostras_cn = dados_extracao_df[dados_extracao_df['Poço'].isin(control_cn_wells)]['Amostra'].tolist()
        else:
            # scan for sample names in mapping that contain 'CN'
            amostras_cn = dados_extracao_df[dados_extracao_df['Amostra'].astype(str).str.contains('CN', na=False, case=False)]['Amostra'].tolist()

        if control_cp_wells:
            amostras_cp = dados_extracao_df[dados_extracao_df['Poço'].isin(control_cp_wells)]['Amostra'].tolist()
        else:
            amostras_cp = dados_extracao_df[dados_extracao_df['Amostra'].astype(str).str.contains('CP', na=False, case=False)]['Amostra'].tolist()

        if not amostras_cn or not amostras_cp:
            raise IndexError("Controles ausentes na extração")

        # Find first non-NaN SC2 CT among the control sample codes
        ct_cn_sc2 = None
        for a in amostras_cn:
            tmp = df_pivot[df_pivot['Sample'] == str(a)]['SC2']
            if not tmp.empty:
                val = tmp.iloc[0]
                if isinstance(val, (int, float)) and pd.notna(val):
                    ct_cn_sc2 = float(val)
                    break

        ct_cp_sc2 = None
        for a in amostras_cp:
            tmp = df_pivot[df_pivot['Sample'] == str(a)]['SC2']
            if not tmp.empty:
                val = tmp.iloc[0]
                if isinstance(val, (int, float)) and pd.notna(val):
                    ct_cp_sc2 = float(val)
                    break

        if pd.notna(ct_cn_sc2):
            status_corrida = "Inválida (CN Detectado)"
            status_corrida = "Inválida (CP Fora do Intervalo)"
    except IndexError:
        status_corrida = "Inválida (Controles ausentes)"
    
    # helper to check if qPCR file had a SampleName recorded for a given well+target
    run_valid = not str(status_corrida).strip().upper().startswith('INV')
    def _qpc_sample_exists(well, target):
        if well is None: return False
        s = df_proc[(df_proc['WELL'] == str(well)) & (df_proc['Target'] == target.upper())]['SampleName']
        return not s.empty

    for target in TARGET_LIST:
        coluna_resultado = f"Resultado_{target.upper().replace(' ', '')}"
        def _compute_result(row, tgt=target):
            if not row.get('Valid', True) or not run_valid:
                return 'Inválido'
            ct_val = row.get(tgt.upper())
            if isinstance(ct_val, str) and ct_val.strip().upper() == 'UNDETERMINED':
                return 'Nao Detectado'
            # if ct missing but qPCR had a sample entry for that well+target -> 'Não Detectado'
            if ct_val is None:
                # decide which well to probe for this target
                if tgt.upper() in [x.upper() for x in targets_poço1]:
                    well = row.get('Well1')
                else:
                    well = row.get('Well2')
                if _qpc_sample_exists(well, tgt):
                    return 'Não Detectado'
                # otherwise, fall back to interpretar (will likely return 'Inválido')
                return _interpretar_resultado(row.get('RP_1'), row.get('RP_2'), ct_val)
            return _interpretar_resultado(row.get('RP_1'), row.get('RP_2'), ct_val)

        df_pivot[coluna_resultado] = df_pivot.apply(lambda r: _compute_result(r), axis=1)
    
    df_final = pd.merge(dados_extracao_df, df_pivot, left_on='Amostra', right_on='Sample', how='left')
    df_final['Status_Corrida'] = status_corrida
    if 'Poço' not in df_final.columns and 'Poco' in df_final.columns:
        df_final['Poço'] = df_final['Poco']
    if 'C�digo' not in df_final.columns and 'Codigo' in df_final.columns:
        df_final['C�digo'] = df_final['Codigo']
    
    colunas_resultado = [f"Resultado_{t.upper().replace(' ', '')}" for t in TARGET_LIST]
    colunas_ct = [t.upper() for t in TARGET_LIST] + ['RP_1', 'RP_2']
    colunas_finais = ['Poço', 'Amostra', 'Código'] + colunas_resultado + colunas_ct + ['Status_Corrida']
    
    for col in colunas_finais:
        if col not in df_final.columns: df_final[col] = None
    
    return df_final[colunas_finais], status_corrida

# ==============================================================================
# 2. CLASSE DE UI
# ==============================================================================
class AnalisarPlacaApp(AfterManagerMixin, ctk.CTkToplevel):
    def __init__(self, master, app_state: AppState):
        super().__init__(master)
        self.app_state = app_state
        self.title("Análise - VR1e2 Biomanguinhos 7500")
        self.geometry("500x300")
        self.df_results: Optional[pd.DataFrame] = None
        self._criar_widgets()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _criar_widgets(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(main_frame, text="Processo de Análise", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
        btn = ctk.CTkButton(main_frame, text="Iniciar Análise", command=self.iniciar_analise_teste)
        btn.pack(pady=10, fill="x")
        # Debug button to show current mapping without running full analysis
        dbg_btn = ctk.CTkButton(main_frame, text="Ver Mapeamento (debug)", command=self._debug_show_map)
        dbg_btn.pack(pady=10, fill="x")
        # Control overrides
        controls_frame = ctk.CTkFrame(main_frame)
        controls_frame.pack(fill="x", pady=(10,0))
        ctk.CTkLabel(controls_frame, text="Override Controles (CN, CP) - Poços (ex: G11,G12):", anchor="w").pack(anchor="w")
        self.cn_entry = ctk.CTkEntry(controls_frame, placeholder_text="CN wells (comma-separated)")
        self.cn_entry.pack(fill="x", pady=2)
        self.cp_entry = ctk.CTkEntry(controls_frame, placeholder_text="CP wells (comma-separated)")
        self.cp_entry.pack(fill="x", pady=2)

    def iniciar_analise_teste(self):
        caminho_arquivo = filedialog.askopenfilename(title="Selecione o arquivo", filetypes=[("Excel", "*.xlsx *.xls")], parent=self)
        if caminho_arquivo:
            preview_extracao_sheet(caminho_arquivo)  # Exibe a pré-visualização
            lote_kit = simpledialog.askstring("Input", "Digite o lote de kit:", parent=self)
            if lote_kit:
                # Save any control overrides back to app_state
                cn_text = (self.cn_entry.get() or "").strip()
                cp_text = (self.cp_entry.get() or "").strip()
                if cn_text:
                    self.app_state.control_cn_wells = [s.strip().upper() for s in cn_text.split(',') if s.strip()]
                if cp_text:
                    self.app_state.control_cp_wells = [s.strip().upper() for s in cp_text.split(',') if s.strip()]

                resultados = iniciar_fluxo_analise(self, self.app_state, lote_kit)
                if resultados is not None:
                    self.df_results = resultados
                    messagebox.showinfo("Sucesso", "Análise concluída.", parent=self)
                    self._on_close()
        else:
            messagebox.showwarning("Aviso", "Arquivo não selecionado.", parent=self)

    def _on_close(self):
        self.dispose()
        self.destroy()

    def _debug_show_map(self):
        """Mostrar o DataFrame de mapeamento armazenado em app_state (debug)."""
        try:
            df_map = self.app_state.dados_extracao
            if df_map is None or df_map.empty:
                messagebox.showinfo("Mapeamento", "Nenhum mapeamento carregado (execute Mapeamento da Placa primeiro).", parent=self)
                return

            # show in a simple top-level window
            win = ctk.CTkToplevel(self)
            win.title("Mapeamento - Debug")
            txt = ctk.CTkTextbox(win, wrap="none", width=800, height=400)
            txt.pack(expand=True, fill="both", padx=10, pady=10)
            txt.insert("0.0", df_map.to_string(index=False))
            txt.configure(state="disabled")
            win.grab_set()
        except Exception as e:
            registrar_log("Análise Debug", f"Erro ao mostrar mapeamento: {e}", "ERROR")
            messagebox.showerror("Erro", f"Erro ao exibir mapeamento: {e}", parent=self)

# ==============================================================================
# 3. E 4. Pontos de Entrada
# ==============================================================================
def iniciar_fluxo_analise(master_window, app_state: AppState, lote_kit: str) -> Optional[pd.DataFrame]:
    try:
        caminho_arquivo = filedialog.askopenfilename(title="Selecione o arquivo", filetypes=[("Dados", "*.csv *.xlsx *.xls")], parent=master_window)
        if not caminho_arquivo:
            return None
        # Log mapping for debug
        try:
            registrar_log("Análise VR1e2", f"Mapping (dados_extracao) preview:\n{str(app_state.dados_extracao.head(10))}", "DEBUG")
        except Exception:
            pass
        result_df, status = analisar_placa_vr1e2_7500(caminho_arquivo, app_state.dados_extracao, app_state.parte_placa)
        try:
            registrar_log("Análise VR1e2", f"Resultado final preview:\n{str(result_df.head(10))}", "DEBUG")
        except Exception:
            pass
        return result_df
    except Exception as e:
        registrar_log("Fluxo Análise", f"Erro: {e}", "CRITICAL")
        messagebox.showerror("Erro", str(e), parent=master_window)
        return None

if __name__ == "__main__":
    registrar_log("Execução", "Iniciando em modo de teste.", "INFO")
    class MockAppState:
        def __init__(self):
            self.dados_extracao = pd.DataFrame({'Poço': [], 'Amostra': [], 'Código': []})
            self.parte_placa = 1
    root = ctk.CTk()
    root.withdraw()
    app = AnalisarPlacaApp(root, MockAppState())
    root.wait_window(app)
    root.destroy()








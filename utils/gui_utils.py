from tkinter import messagebox, ttk

from typing import List, Optional



import customtkinter as ctk

import matplotlib.pyplot as plt



from db.db_utils import salvar_historico_processamento

from utils.after_mixin import AfterManagerMixin

from utils.logger import registrar_log


def safe_destroy_ctk_toplevel(window):
    """
    Destrói uma janela CTkToplevel de forma segura, evitando erros 'invalid command name'.
    
    CustomTkinter agenda callbacks internos (update, check_dpi_scaling, _click_animation)
    que podem executar após destroy(). Esta função:
    1. Oculta a janela imediatamente (withdraw)
    2. Aguarda 50ms para callbacks pendentes completarem
    3. Destrói a janela de forma segura
    
    Args:
        window: Janela CTkToplevel a ser destruída
    """
    try:
        # 1. Ocultar janela imediatamente
        window.withdraw()
        
        # 2. Agendar destruição após callbacks pendentes
        def _destroy_delayed():
            try:
                window.destroy()
            except Exception as e:
                registrar_log("SafeDestroy", f"Erro ao destruir janela: {e}", "WARNING")
        
        window.after(200, _destroy_delayed)
        
    except Exception as e:
        registrar_log("SafeDestroy", f"Erro em safe_destroy: {e}", "ERROR")
        # Fallback: tentar destruir diretamente
        try:
            window.destroy()
        except Exception:
            pass





def _norm_res_label(val: str) -> str:

    try:

        s = str(val).strip().lower()

    except Exception:

        return ""

    s = (

        s.replace("detectável", "detectavel")

        .replace("não", "nao")

        .replace("inválido", "invalido")

    )

    if s in {"detectavel", "detectado"}:

        return "detectavel"

    if s in {"nao detectavel", "nao detectado"}:

        return "nao_detectavel"

    if s in {"invalido"}:

        return "invalido"

    return s





class TabelaComSelecaoSimulada(AfterManagerMixin, ctk.CTkToplevel):

    """Interface para exibir resultados em tabela com seleção simulada."""



    def __init__(

        self,

        root,

        dataframe,

        status_corrida,

        num_placa,

        data_placa_formatada,

        agravos,

        usuario_logado: str = "Desconhecido",

        exame: str = "",

        lote: str = "",

        arquivo_corrida: str = "",

    ):
        super().__init__(master=root)
        self.title("RT-PCR - Análise com Seleção Simulada")
        
        # Armazenar referência ao parent para limpeza posterior
        self._parent = root
        
        # Rastrear callback de restaurar_grab para cancelar se necessário
        self._restore_grab_callback_id = None

        self.df = dataframe.copy()

        # Seleciona por padrão todas exceto inválidas

        if "Selecionado" not in self.df.columns:

            result_cols = [

                c for c in self.df.columns if str(c).startswith("Resultado_")

            ]

            selecoes = []

            for _, r in self.df.iterrows():

                inval = any(

                    _norm_res_label(r.get(c, "")) == "invalido" for c in result_cols

                )

                selecoes.append(False if inval else True)

            self.df.insert(0, "Selecionado", selecoes)



        self.status_corrida = status_corrida

        self.num_placa = num_placa

        self.data_placa_formatada = data_placa_formatada

        self.agravos = agravos

        self.usuario_logado = usuario_logado

        self.exame = exame

        self.lote = lote

        self.arquivo_corrida = arquivo_corrida

        # Criar interface primeiro
        self._criar_widgets()
        self._popular_tabela()
        
        # Configurar comportamento da janela DEPOIS de criar widgets
        self.transient(root)
        self.grab_set()
        
        # Maximizar por último para evitar problemas com transient/grab
        # Proteger contra "invalid command name" se janela for destruída antes do callback
        def maximizar_seguro():
            try:
                if self.winfo_exists():
                    self.state("zoomed")
            except Exception:
                pass
        
        self.after(100, maximizar_seguro)
        
        self.protocol("WM_DELETE_WINDOW", self._on_close)



    def _criar_widgets(self):

        main_frame = ctk.CTkFrame(self)

        main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        main_frame.grid_columnconfigure(0, weight=1)

        main_frame.grid_rowconfigure(1, weight=1)



        # Frame superior para informações e botões

        top_frame = ctk.CTkFrame(main_frame)

        top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        top_frame.grid_columnconfigure(3, weight=1)



        ctk.CTkLabel(

            top_frame, text=f"Placa: {self.num_placa}", font=("", 12, "bold")

        ).grid(row=0, column=0, padx=10)

        ctk.CTkLabel(

            top_frame, text=f"Data: {self.data_placa_formatada}", font=("", 12, "bold")

        ).grid(row=0, column=1, padx=10)

        ctk.CTkLabel(

            top_frame,

            text=f"Status da Corrida: {self.status_corrida}",

            font=("", 12, "bold"),

        ).grid(row=0, column=2, padx=10)



        # Botões de ação

        btn_relatorio = ctk.CTkButton(

            top_frame, text="Relatório Estatístico", command=self._mostrar_relatorio

        )

        btn_relatorio.grid(row=0, column=4, padx=5)



        btn_grafico = ctk.CTkButton(

            top_frame,

            text="Gráfico de Detecção",

            command=self._gerar_grafico_detectaveis,

        )

        btn_grafico.grid(row=0, column=5, padx=5)



        btn_mapa = ctk.CTkButton(

            top_frame,

            text="Mapa da Placa",

            command=self._gerar_mapa_placa,

        )

        btn_mapa.grid(row=0, column=6, padx=5)



        btn_salvar = ctk.CTkButton(

            top_frame,

            text="Salvar Selecionados no Histórico",

            command=self._salvar_selecionados,

        )

        btn_salvar.grid(row=0, column=7, padx=10)



        # Frame da Tabela

        table_frame = ctk.CTkFrame(main_frame)

        table_frame.grid(row=1, column=0, sticky="nsew")

        table_frame.grid_columnconfigure(0, weight=1)

        table_frame.grid_rowconfigure(0, weight=1)



        self.tree = ttk.Treeview(

            table_frame, columns=list(self.df.columns), show="headings"

        )



        # Scrollbars

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)

        vsb.grid(row=0, column=1, sticky="ns")

        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)

        hsb.grid(row=1, column=0, sticky="ew")

        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)



        self.tree.grid(row=0, column=0, sticky="nsew")

        self.tree.bind("<Double-1>", self._on_double_click)



    def _popular_tabela(self):
        for col in self.df.columns:
            self.tree.heading(
                col,
                text=col,
                command=lambda _col=col: self._ordenar_coluna(_col, False),
            )
            self.tree.column(col, width=100, anchor="center")

        for index, row in self.df.iterrows():
            row_values = list(row)
            if isinstance(row_values[0], bool):
                row_values[0] = "V" if row_values[0] else ""
            self.tree.insert("", "end", values=row_values, iid=str(index))
    
    def recarregar_dados(self, novo_df):
        """Recarrega a tabela com novos dados sem fechar a janela."""
        try:
            # Limpar tabela existente
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Atualizar DataFrame
            self.df = novo_df.copy()
            
            # Adicionar coluna de seleção se não existir
            if "Selecionado" not in self.df.columns:
                result_cols = [
                    c for c in self.df.columns if str(c).startswith("Resultado_")
                ]
                selecoes = []
                for _, r in self.df.iterrows():
                    inval = any(
                        _norm_res_label(r.get(c, "")) == "invalido" for c in result_cols
                    )
                    selecoes.append(False if inval else True)
                self.df.insert(0, "Selecionado", selecoes)
            
            # Repopular tabela
            self._popular_tabela()
            
            # Atualizar título com timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.title(f"RT-PCR - Análise com Seleção Simulada (Atualizado: {timestamp})")
            
        except Exception as e:
            registrar_log("TabelaComSelecaoSimulada", f"Erro ao recarregar dados: {e}", "ERROR")



    def _on_double_click(self, event):

        item_id = self.tree.identify_row(event.y)

        if not item_id:

            return



        index = int(item_id)

        # Bloqueia alteração de seleção em amostras de controlo

        amostra = self.df.loc[index, "Amostra"]

        if any(ctrl in str(amostra).upper() for ctrl in ["CN", "CP", "NEG", "POS"]):

            messagebox.showwarning(

                "Ação Bloqueada",

                "Não é permitido alterar a seleção de amostras de controlo.",

                parent=self,

            )

            return



        # Impede selecionar amostras Inválidas

        result_cols = [c for c in self.df.columns if str(c).startswith("Resultado_")]

        if any(

            _norm_res_label(self.df.loc[index, c]) == "invalido"

            for c in result_cols

            if c in self.df.columns

        ):

            messagebox.showwarning(

                "Ação Bloqueada",

                "Amostras inválidas não podem ser selecionadas.",

                parent=self,

            )

            return



        # Alterna o valor

        current_value = self.df.loc[index, "Selecionado"]

        self.df.loc[index, "Selecionado"] = not current_value



        new_symbol = "V" if not current_value else ""

        self.tree.item(item_id, values=[new_symbol] + list(self.df.iloc[index, 1:]))



    def _ordenar_coluna(self, col, reverse):

        # Implementação de ordenação opcional

        pass



    def _salvar_selecionados(self):
        """
        Salva TODAS as amostras no histórico (PostgreSQL) e pergunta se deseja
        enviar apenas as SELECIONADAS para o GAL.
        """
        # Reforça invariância: desmarca inválidas antes de salvar
        result_cols = [c for c in self.df.columns if str(c).startswith("Resultado_")]
        invalid_mask = self.df.apply(
            lambda r: any(
                _norm_res_label(r.get(c, "")) == "invalido" for c in result_cols
            ),
            axis=1,
        )
        if invalid_mask.any():
            self.df.loc[invalid_mask, "Selecionado"] = False

        # Contar selecionadas para envio ao GAL
        df_selecionados = self.df[self.df["Selecionado"]]
        total_selecionados = len(df_selecionados)
        
        # Detectar coluna de código (pode ser "Código" ou "Codigo")
        col_codigo = "Código" if "Código" in self.df.columns else ("Codigo" if "Codigo" in self.df.columns else None)
        if not col_codigo:
            messagebox.showerror("Erro", "Coluna de código não encontrada no DataFrame.", parent=self)
            return
        
        total_amostras = len(self.df[self.df[col_codigo].notna() & (self.df[col_codigo] != "")])

        try:
            from services.history_report import gerar_historico_csv

            # PASSO 1: Salvar TODAS as amostras no histórico (não apenas selecionadas)
            df_todas_amostras = self.df[self.df[col_codigo].notna() & (self.df[col_codigo] != "")]
            
            if len(df_todas_amostras) == 0:
                messagebox.showinfo(
                    "Informação", 
                    "Nenhuma amostra disponível para salvar.", 
                    parent=self
                )
                return
            
            # Prepara todas as amostras para o histórico
            df_para_historico = self._preparar_df_para_historico(df_todas_amostras)

            # Salvar no histórico (PostgreSQL/CSV)
            gerar_historico_csv(
                df_para_historico,
                exame=getattr(self, "exame", ""),
                usuario=self.usuario_logado or "Desconhecido",
                lote=getattr(self, "lote", ""),
                arquivo_corrida=getattr(self, "arquivo_corrida", ""),
                caminho_csv="logs/historico_analises.csv",
            )

            detalhes = f"Placa: {self.num_placa}; {total_amostras} amostras salvas no histórico."
            salvar_historico_processamento(
                self.usuario_logado, "Análise Completa", "Concluído", detalhes
            )

            registrar_log(
                "Salvar Histórico",
                f"{total_amostras} amostras salvas no histórico pelo usuário {self.usuario_logado}.",
                "INFO",
            )

            # PASSO 2: Confirmar sucesso e perguntar sobre envio ao GAL
            if total_selecionados == 0:
                messagebox.showinfo(
                    "Histórico Salvo",
                    f"✅ {total_amostras} amostras foram salvas no histórico.\n\n"
                    "⚠️ Nenhuma amostra foi selecionada para envio ao GAL.",
                    parent=self,
                )
                return

            # Perguntar se deseja enviar selecionadas ao GAL
            resposta = messagebox.askyesno(
                "Enviar para o GAL?",
                f"✅ {total_amostras} amostras salvas no histórico com sucesso!\n\n"
                f"📊 {total_selecionados} amostras estão selecionadas.\n\n"
                "Deseja enviar as amostras SELECIONADAS para o GAL?",
                parent=self,
            )

            if resposta:
                # PASSO 3: Enviar apenas selecionadas para o GAL
                self._enviar_selecionadas_gal(df_selecionados)
            else:
                messagebox.showinfo(
                    "Concluído",
                    "Amostras salvas no histórico. Envio ao GAL cancelado.",
                    parent=self,
                )

        except Exception as e:
            messagebox.showerror(
                "Erro ao Salvar",
                f"Não foi possível salvar o histórico.\n\nErro: {e}",
                parent=self,
            )
            registrar_log(
                "Salvar Histórico", f"Falha ao salvar histórico: {e}", "ERROR"
            )

    def _preparar_df_para_historico(self, df):
        """
        Garante colunas chave antes de salvar:
        - arquivo_corrida preenchido com nome do arquivo, se conhecido
        - Resultado_RP_1/Resultado_RP_2 se houver CT de RP
        """
        df_out = df.copy()

        arq = getattr(self, "arquivo_corrida", "") or ""
        if arq:
            try:
                from pathlib import Path as _Path
                arq_nome = _Path(arq).name
            except Exception:
                arq_nome = str(arq)
            df_out["arquivo_corrida"] = arq_nome
        elif "arquivo_corrida" not in df_out.columns:
            df_out["arquivo_corrida"] = ""

        for rp_col in ("RP_1", "RP_2", "RP1", "RP2"):
            ct_col = f"{rp_col} - CT"
            res_col = f"Resultado_{rp_col}"
            if ct_col in df_out.columns and res_col not in df_out.columns:
                df_out[res_col] = ""

        return df_out
    
    def _enviar_selecionadas_gal(self, df_selecionadas):
        """
        Gera CSV GAL e abre interface de envio para as amostras SELECIONADAS.
        Este método é chamado APÓS o salvamento do histórico.
        """
        try:
            import os
            from datetime import datetime, timezone
            from exportacao.gal_formatter import formatar_para_gal
            from exportacao.envio_gal import abrir_janela_envio_gal
            from utils.notifications import notificar_gal_saved
            
            total = len(df_selecionadas)
            
            # Preparar dados para GAL
            df_para_gal = self._preparar_df_para_historico(df_selecionadas)
            
            # Obter configuração do exame
            app_state = getattr(self.master, "app_state", None)
            exam_cfg = getattr(app_state, "exam_cfg_for_gal", None) if app_state else None
            exame = getattr(self, "exame", "")
            
            # GERAR CSV GAL (agora sim, após histórico salvo)
            df_gal = formatar_para_gal(df_para_gal, exam_cfg=exam_cfg, exame=exame)
            
            # Salvar arquivos CSV
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            reports_dir = os.path.join(base_dir, "reports")
            os.makedirs(reports_dir, exist_ok=True)
            
            ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            gal_path = os.path.join(reports_dir, f"gal_{ts}_exame.csv")
            df_gal.to_csv(gal_path, index=False)
            
            gal_last = os.path.join(reports_dir, "gal_last_exame.csv")
            df_gal.to_csv(gal_last, index=False)
            
            registrar_log(
                "GAL Export",
                f"CSV GAL gerado com {len(df_gal)} linhas em {gal_path}",
                "INFO",
            )
            
            # Salvar no app_state para módulo GAL
            if app_state:
                setattr(app_state, "resultados_gal", df_para_gal)
            
            # Notificar salvamento
            notificar_gal_saved(gal_last, parent=self.master)
            
            # Abrir interface de envio GAL
            abrir_janela_envio_gal(self.master)
            
        except Exception as e:
            messagebox.showerror(
                "Erro ao Gerar CSV GAL",
                f"Não foi possível gerar o CSV para o GAL.\n\nErro: {e}",
                parent=self,
            )
            registrar_log(
                "GAL Export", f"Falha ao gerar CSV GAL: {e}", "ERROR"
            )

    def _mostrar_relatorio(self):

        # Linha comentada devido a alerta do ruff (E712): comparação direta com True.

        # df_selecionados = self.df[self.df["Selecionado"] == True]

        df_selecionados = self.df[self.df["Selecionado"]]

        total_amostras = len(df_selecionados)

        if total_amostras == 0:

            messagebox.showinfo(

                "Relatório", "Nenhuma amostra selecionada.", parent=self

            )

            return



        report_text = f"Total de Amostras Selecionadas: {total_amostras}\n"

        report_text += "--------------------------------------\n"



        for agravo in self.agravos:

            col_resultado = f"Resultado_{agravo.replace(' ', '')}"

            if col_resultado in df_selecionados.columns:

                vals = (

                    df_selecionados[col_resultado].astype(str).str.strip().str.lower()

                )

                detectaveis = vals.isin(["detectável", "detectavel", "detectado"]).sum()

                nao_detectaveis = vals.isin(

                    ["não detectável", "nao detectavel", "nao detectado"]

                ).sum()

                invalidos = total_amostras - (detectaveis + nao_detectaveis)

                report_text += f"\nAgravo: {agravo}\n"

                report_text += f"  - Detectáveis: {detectaveis}\n"

                report_text += f"  - Não Detectáveis: {nao_detectaveis}\n"

                report_text += f"  - Inválidos/Outros: {invalidos}\n"



        messagebox.showinfo("Relatório Estatístico", report_text, parent=self)



    def _gerar_grafico_detectaveis(self):

        contagem = {}

        for agravo in self.agravos:

            col_resultado = "Resultado_" + agravo.replace(" ", "")

            if col_resultado in self.df.columns:

                vals = self.df[col_resultado].astype(str).str.strip().str.lower()

                contagem[agravo] = int(

                    vals.isin(["detectável", "detectavel", "detectado"]).sum()

                )

        plot_data = {k: v for k, v in contagem.items() if v > 0}

        if not plot_data:

            messagebox.showinfo(

                "Gráfico de Detecção",

                "Nenhum alvo detectável para gerar o gráfico.",

                parent=self,

            )

            return

        plt.figure(figsize=(10, 6))

        plt.bar(plot_data.keys(), plot_data.values(), color="skyblue")

        plt.title("Distribuição de Agravos Detectáveis")

        plt.xlabel("Agravos")

        plt.ylabel("Amostras Detectáveis")

        plt.xticks(rotation=45, ha="right")

        plt.tight_layout()

        plt.show()



    def _gerar_mapa_placa(self):

        try:

            from services.plate_viewer import abrir_placa_ctk



            app_state = getattr(self.master, "app_state", None)

            df_final = getattr(app_state, "resultados_analise", None)

            df_norm = getattr(app_state, "df_norm", None)

            # prioriza df_final consolidado; senão, df_norm

            df_to_use = df_final if df_final is not None and not df_final.empty else df_norm

            if df_to_use is None or df_to_use.empty:

                messagebox.showerror(

                    "Erro",

                    "Não foi possível gerar o mapa: resultados não disponíveis.",

                    parent=self,

                )

                return



            meta = {

                "data": getattr(app_state, "data_corrida", ""),

                "extracao": getattr(app_state, "arquivo_corrida", "") or getattr(app_state, "lote", ""),

                "exame": getattr(app_state, "exame_selecionado", ""),

                "usuario": getattr(app_state, "usuario_logado", ""),

                "teste": getattr(app_state, "exame_selecionado", ""),

            }

            bloco_tam = getattr(app_state, "bloco_tamanho", 2)

            
            # Callback para atualizar dados após salvamento no mapa da placa
            def on_plate_save(plate_model):
                """Atualiza app_state com dados do plate_model após edições"""
                try:
                    # Converter PlateModel de volta para DataFrame
                    df_updated = plate_model.to_dataframe()
                    
                    # Atualizar app_state com DataFrame modificado
                    setattr(app_state, "resultados_analise", df_updated)
                    
                    registrar_log("Mapa Placa", "Alterações salvas e sincronizadas com resultados", "INFO")
                except Exception as e:
                    registrar_log("Mapa Placa", f"Erro ao sincronizar alterações: {e}", "ERROR")
            
            # CRÍTICO: Liberar grab antes de abrir janela filha para evitar conflito modal
            # Solução baseada na análise de problemas comuns do Tkinter com grab_set
            try:
                self.grab_release()
            except Exception:
                pass
            
            # Função segura para restaurar grab sem causar "invalid command name"
            def restaurar_grab_seguro():
                try:
                    if self.winfo_exists():
                        self.grab_set()
                        self._restore_grab_callback_id = None  # Limpar ID após execução
                except Exception:
                    pass  # Janela foi destruída, ignorar silenciosamente
            
            try:
                abrir_placa_ctk(df_to_use, meta_extra=meta, group_size=bloco_tam, parent=self, on_save_callback=on_plate_save)
            finally:
                # Restaurar grab após PlateWindow ser criada
                # Usar after_idle ao invés de after(100) para reduzir janela de vulnerabilidade
                # Rastrear ID do callback para poder cancelar no _on_close se necessário
                try:
                    self._restore_grab_callback_id = self.after_idle(restaurar_grab_seguro)
                except Exception:
                    # Se after_idle falhar, restaurar imediatamente
                    restaurar_grab_seguro()

            registrar_log("Mapa Placa", "Mapa exibido na janela CTk", "INFO")

        except Exception as e:

            registrar_log("Mapa Placa", f"Erro ao gerar mapa: {e}", "ERROR")

            messagebox.showerror(

                "Erro", f"Falha ao gerar mapa da placa:\n{e}", parent=self

            )



    def _on_close(self):
        # Cancelar callbacks pendentes do AfterManagerMixin
        self.dispose()
        
        # CRÍTICO: Cancelar callback de restaurar_grab se ainda pendente
        # Isso previne "invalid command name" quando janela é fechada rapidamente
        if self._restore_grab_callback_id is not None:
            try:
                self.after_cancel(self._restore_grab_callback_id)
                self._restore_grab_callback_id = None
            except Exception:
                pass
        
        # Limpar referência e flag no MenuHandler se aplicável
        if hasattr(self._parent, 'menu_handler'):
            try:
                if hasattr(self._parent.menu_handler, '_resultado_window'):
                    if self._parent.menu_handler._resultado_window is self:
                        self._parent.menu_handler._resultado_window = None
                # Limpar flag de criação também
                if hasattr(self._parent.menu_handler, '_criando_janela_resultado'):
                    self._parent.menu_handler._criando_janela_resultado = False
            except Exception:
                pass
        
        # Liberar grab antes de ocultar
        try:
            self.grab_release()
        except Exception:
            pass
        
        # SOLUÇÃO: Ocultar janela imediatamente (usuário vê como "fechou")
        # Isso previne interação mas mantém widget Tcl vivo para callbacks terminarem
        try:
            self.withdraw()
        except Exception:
            pass
        
        # Destruir após delay para permitir callbacks internos do CustomTkinter terminarem
        # CustomTkinter agenda update() a cada 30ms e check_dpi_scaling() a cada 100ms
        # 300ms garante que callbacks pendentes terminem antes do destroy()
        def destruir_seguro():
            try:
                if self.winfo_exists():
                    self.destroy()
            except Exception:
                pass
        
        # Usar after() com delay explícito (after_idle não é suficiente)
        try:
            self.after(300, destruir_seguro)
        except Exception:
            # Se after() falhar, destruir imediatamente
            destruir_seguro()





class CTkSelectionDialog(ctk.CTkToplevel):

    def __init__(self, master, title: str, text: str, values: List[str]):

        super().__init__(master)

        self.title(title)

        self.geometry("400x180")



        self._values = values

        self._selection: Optional[str] = None



        self.transient(master)

        self.grab_set()

        self._create_widgets(text)



    def _create_widgets(self, text: str):

        main_frame = ctk.CTkFrame(self, fg_color="transparent")

        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(main_frame, text=text).pack(anchor="w")



        self.combobox = ctk.CTkComboBox(main_frame, values=self._values)

        self.combobox.pack(fill="x", pady=(5, 20))

        if self._values:

            self.combobox.set(self._values[0])



        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")

        button_frame.pack(fill="x")

        button_frame.grid_columnconfigure((0, 1), weight=1)



        ok_button = ctk.CTkButton(button_frame, text="OK", command=self._on_ok)

        ok_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        cancel_button = ctk.CTkButton(

            button_frame, text="Cancelar", command=self._on_cancel, fg_color="gray"

        )

        cancel_button.grid(row=0, column=1, padx=(5, 0), sticky="ew")



    def _on_ok(self):

        self._selection = self.combobox.get()

        self.destroy()



    def _on_cancel(self):

        self._selection = None

        self.destroy()



    def get_selection(self) -> Optional[str]:

        self.wait_window()

        return self._selection


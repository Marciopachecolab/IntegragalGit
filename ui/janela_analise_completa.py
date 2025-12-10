"""
Janela única com abas: Análise + Mapa da Placa
Solução para eliminar problemas com múltiplos CTkToplevel e travamentos.
Baseado na recomendação do especialista em Tkinter/CustomTkinter.
"""

from __future__ import annotations
import customtkinter as ctk
import pandas as pd
from tkinter import ttk, messagebox
from typing import Dict, List, Optional, Any
import math

from services.plate_viewer import PlateModel, PlateView
from utils.logger import registrar_log
from utils.after_mixin import AfterManagerMixin


def _norm_res_label(val: str) -> str:
    """Normaliza rótulos de resultado para comparação."""
    s = str(val).strip().upper()
    if "INVAL" in s or "INV" in s:
        return "invalido"
    if "DET" in s or "POS" in s:
        return "positivo"
    if "INC" in s:
        return "inconclusivo"
    if "ND" in s or "NEG" in s:
        return "negativo"
    return s.lower()


class JanelaAnaliseCompleta(AfterManagerMixin, ctk.CTkToplevel):
    """
    Janela única com abas: Análise + Mapa da Placa.
    Elimina necessidade de CTkToplevel aninhados e resolve travamentos.
    """

    def __init__(
        self,
        root,
        dataframe: pd.DataFrame,
        status_corrida: str,
        num_placa: str,
        data_placa_formatada: str,
        agravos: List[str],
        usuario_logado: str = "Desconhecido",
        exame: str = "",
        lote: str = "",
        arquivo_corrida: str = "",
        bloco_tamanho: int = 2,
    ):
        super().__init__(master=root)
        self.title("RT-PCR - Análise Completa")
        
        # Estado compartilhado entre abas
        self.df_analise = dataframe.copy()
        self.plate_model: Optional[PlateModel] = None
        
        # Metadados
        self.status_corrida = status_corrida
        self.num_placa = num_placa
        self.data_placa_formatada = data_placa_formatada
        self.agravos = agravos
        self.usuario_logado = usuario_logado
        self.exame = exame
        self.lote = lote
        self.arquivo_corrida = arquivo_corrida
        self.bloco_tamanho = bloco_tamanho
        
        # Adicionar coluna de seleção se não existir
        if "Selecionado" not in self.df_analise.columns:
            result_cols = [c for c in self.df_analise.columns if str(c).startswith("Resultado_")]
            selecoes = []
            for _, r in self.df_analise.iterrows():
                inval = any(_norm_res_label(r.get(c, "")) == "invalido" for c in result_cols)
                selecoes.append(False if inval else True)
            self.df_analise.insert(0, "Selecionado", selecoes)
        
        # Configurar janela
        self.transient(root)
        self.grab_set()
        
        # Definir tamanho (85% da tela)
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = int(screen_width * 0.85)
        window_height = int(screen_height * 0.85)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Criar interface
        self._criar_header()
        self._criar_tabview()
        
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _criar_header(self):
        """Cria header com informações da corrida."""
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(3, weight=1)
        
        ctk.CTkLabel(
            header_frame, 
            text=f"Placa: {self.num_placa}", 
            font=("Segoe UI", 12, "bold")
        ).grid(row=0, column=0, padx=10, sticky="w")
        
        ctk.CTkLabel(
            header_frame,
            text=f"Data: {self.data_placa_formatada}",
            font=("Segoe UI", 12, "bold")
        ).grid(row=0, column=1, padx=10, sticky="w")
        
        ctk.CTkLabel(
            header_frame,
            text=f"Status: {self.status_corrida}",
            font=("Segoe UI", 12, "bold")
        ).grid(row=0, column=2, padx=10, sticky="w")
        
        ctk.CTkLabel(
            header_frame,
            text=f"Exame: {self.exame}",
            font=("Segoe UI", 12, "bold")
        ).grid(row=0, column=3, padx=10, sticky="e")
    
    def _criar_tabview(self):
        """Cria TabView com abas de Análise e Mapa."""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        # Aba 1: Análise
        self.tab_analise = self.tabview.add("📊 Análise")
        self._construir_aba_analise()
        
        # Aba 2: Mapa da Placa
        self.tab_mapa = self.tabview.add("🧬 Mapa da Placa")
        self._mapa_frame: Optional[PlateView] = None
        self._mapa_placeholder = None
        
        # Callback ao trocar aba
        self.tabview.configure(command=self._on_tab_change)
        
        # NOVO: Carregar mapa automaticamente após pequeno delay
        # (permite janela renderizar completamente antes)
        self.after(100, self._carregar_mapa_inicial)
    
    def _construir_aba_analise(self):
        """Constrói conteúdo da aba de análise."""
        # Frame principal
        main_frame = ctk.CTkFrame(self.tab_analise)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Barra de botões
        btn_frame = ctk.CTkFrame(main_frame)
        btn_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        btn_frame.grid_columnconfigure(5, weight=1)
        
        ctk.CTkButton(
            btn_frame,
            text="Relatório Estatístico",
            command=self._mostrar_relatorio
        ).grid(row=0, column=0, padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Gráfico de Detecção",
            command=self._gerar_grafico
        ).grid(row=0, column=1, padx=5)
        
        # Botão 'Ir para Mapa' REMOVIDO - mapa já está na aba ao lado
        
        ctk.CTkButton(
            btn_frame,
            text="💾 Salvar Selecionados",
            command=self._salvar_selecionados,
            fg_color="#27AE60",
            hover_color="#229954"
        ).grid(row=0, column=2, padx=5)
        
        # Frame da tabela
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Treeview
        self.tree = ttk.Treeview(
            table_frame,
            columns=list(self.df_analise.columns),
            show="headings"
        )
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        hsb.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<Double-1>", self._on_double_click)
        
        # Popular tabela
        self._popular_tabela()
    
    def _popular_tabela(self):
        """Popula treeview com dados do DataFrame."""
        # Limpar existente
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # CRÍTICO: Reconfigurar colunas do TreeView para match com DataFrame atual
        colunas_atuais = list(self.df_analise.columns)
        self.tree.config(columns=colunas_atuais)
        self.tree["displaycolumns"] = colunas_atuais
        
        # Configurar cada coluna
        for col in colunas_atuais:
            self.tree.heading(
                col,
                text=col,
                command=lambda _col=col: self._ordenar_coluna(_col, False)
            )
            self.tree.column(col, width=100, anchor="center")
        
        # Inserir linhas
        for index, row in self.df_analise.iterrows():
            row_values = list(row)
            if isinstance(row_values[0], bool):
                row_values[0] = "✓" if row_values[0] else ""
            self.tree.insert("", "end", values=row_values, iid=str(index))
    
    def _ordenar_coluna(self, col: str, reverse: bool):
        """Ordena tabela por coluna."""
        try:
            self.df_analise = self.df_analise.sort_values(by=col, ascending=not reverse)
            self._popular_tabela()
            # Próximo clique inverte ordem
            self.tree.heading(
                col,
                command=lambda: self._ordenar_coluna(col, not reverse)
            )
        except Exception as e:
            registrar_log("Ordenação", f"Erro: {e}", "ERROR")
    
    def _on_double_click(self, event):
        """Toggle seleção ao dar duplo clique."""
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
        
        index = int(item_id)
        
        # Bloquear controles
        amostra = self.df_analise.loc[index, "Amostra"]
        if any(ctrl in str(amostra).upper() for ctrl in ["CN", "CP", "NEG", "POS"]):
            messagebox.showwarning(
                "Ação Bloqueada",
                "Não é permitido alterar seleção de controles.",
                parent=self
            )
            return
        
        # Bloquear inválidos
        result_cols = [c for c in self.df_analise.columns if str(c).startswith("Resultado_")]
        if any(_norm_res_label(self.df_analise.loc[index, c]) == "invalido" for c in result_cols):
            messagebox.showwarning(
                "Ação Bloqueada",
                "Amostras inválidas não podem ser selecionadas.",
                parent=self
            )
            return
        
        # Toggle seleção
        self.df_analise.loc[index, "Selecionado"] = not self.df_analise.loc[index, "Selecionado"]
        self._popular_tabela()
    
    def _carregar_mapa_inicial(self):
        """Carrega mapa automaticamente ao abrir janela (chamado via after)."""
        try:
            self._carregar_mapa()
            registrar_log("Mapa", "Mapa carregado automaticamente", "INFO")
            
            # Informar usuário sobre sincronização automática
            messagebox.showinfo(
                "Mapa Carregado",
                "✅ Mapa da placa carregado!\n\n"
                "💡 IMPORTANTE:\n"
                "• Ao clicar 'Aplicar' no mapa, as mudanças são\n"
                "  automaticamente recalculadas em toda a placa\n"
                "• Clique '💾 Salvar e Voltar' para sincronizar\n"
                "  com a aba de análise",
                parent=self
            )
            
        except Exception as e:
            registrar_log("Mapa", f"Erro ao carregar mapa inicial: {e}", "ERROR")
            # Mostrar placeholder de erro
            self._mapa_placeholder = ctk.CTkLabel(
                self.tab_mapa,
                text=f"Erro ao carregar mapa:\n{str(e)}",
                font=("Segoe UI", 12),
                text_color="#e74c3c"
            )
            self._mapa_placeholder.pack(expand=True)
    
    def _carregar_mapa(self):
        """Cria PlateView pela primeira vez."""
        # Remover placeholder
        if self._mapa_placeholder:
            self._mapa_placeholder.destroy()
            self._mapa_placeholder = None
        
        # CRÍTICO: Garantir que DataFrame tem coluna 'Poco' (sem acento)
        df_para_mapa = self.df_analise.copy()
        
        # Renomear 'Poço' para 'Poco' se necessário
        if 'Poço' in df_para_mapa.columns and 'Poco' not in df_para_mapa.columns:
            df_para_mapa.rename(columns={'Poço': 'Poco'}, inplace=True)
        if 'Código' in df_para_mapa.columns and 'Codigo' not in df_para_mapa.columns:
            df_para_mapa.rename(columns={'Código': 'Codigo'}, inplace=True)
        
        # Criar PlateModel
        self.plate_model = PlateModel.from_df(
            df_para_mapa,
            group_size=self.bloco_tamanho,
            exame=self.exame
        )
        
        # Criar PlateView como Frame DENTRO da aba
        meta = {
            "data": self.data_placa_formatada,
            "extracao": self.arquivo_corrida or self.lote,
            "exame": self.exame,
            "usuario": self.usuario_logado,
        }
        
        self._mapa_frame = PlateView(
            self.tab_mapa,
            self.plate_model,
            meta=meta,
            on_save_callback=self._on_mapa_salvo
        )
        self._mapa_frame.pack(fill="both", expand=True)
        
        registrar_log("Mapa", "PlateView criado com sucesso", "INFO")
    
    def _atualizar_mapa(self):
        """Atualiza mapa existente com dados mais recentes."""
        if self._mapa_frame and self.plate_model:
            # Recriar PlateModel com dados atualizados
            self.plate_model = PlateModel.from_df(
                self.df_analise,
                group_size=self.bloco_tamanho,
                exame=self.exame
            )
            
            # Atualizar PlateView
            self._mapa_frame.plate_model = self.plate_model
            self._mapa_frame.render_plate()
            
            registrar_log("Mapa", "PlateView atualizado", "INFO")
    
    def _on_mapa_salvo(self, plate_model: PlateModel):
        """
        Callback quando usuário salva no mapa.
        RECALCULA TODA A PLACA e sincroniza IMEDIATAMENTE com aba de análise.
        """
        try:
            # PASSO 1: Converter PlateModel de volta para DataFrame
            df_updated = plate_model.to_dataframe()
            
            if df_updated.empty:
                messagebox.showwarning("Aviso", "Mapa retornou dados vazios", parent=self)
                return
            
            # PASSO 2: Fazer merge inteligente preservando TODAS as colunas originais
            colunas_originais = list(self.df_analise.columns)
            
            # Identificar chave de merge (Poco ou Poço)
            chave_merge = None
            if "Poco" in df_updated.columns and "Poco" in self.df_analise.columns:
                chave_merge = "Poco"
            elif "Poço" in df_updated.columns and "Poço" in self.df_analise.columns:
                chave_merge = "Poço"
            
            if chave_merge:
                # MERGE INTELIGENTE: Atualizar apenas colunas que existem no updated
                # Preservar colunas que não existem no mapa
                selecoes_backup = self.df_analise[[chave_merge, "Selecionado"]].copy()
                
                # Manter colunas que NÃO vieram do mapa
                colunas_do_mapa = set(df_updated.columns)
                colunas_preservar = [c for c in colunas_originais if c not in colunas_do_mapa and c != "Selecionado"]
                
                if colunas_preservar:
                    df_preservado = self.df_analise[[chave_merge] + colunas_preservar].copy()
                    # Merge: atualizar do mapa + adicionar colunas preservadas
                    self.df_analise = df_updated.merge(df_preservado, on=chave_merge, how="left")
                else:
                    self.df_analise = df_updated.copy()
                
                # Restaurar seleções
                self.df_analise = self.df_analise.merge(selecoes_backup, on=chave_merge, how="left")
                self.df_analise["Selecionado"] = self.df_analise["Selecionado"].fillna(False)
                
            else:
                # FALLBACK: Substituição direta se não houver chave
                self.df_analise = df_updated.copy()
                if "Selecionado" not in self.df_analise.columns:
                    self.df_analise.insert(0, "Selecionado", False)
            
            # PASSO 3: Garantir ordem das colunas (Selecionado primeiro)
            if "Selecionado" in self.df_analise.columns:
                cols = ["Selecionado"] + [c for c in self.df_analise.columns if c != "Selecionado"]
                self.df_analise = self.df_analise[cols]
            
            # PASSO 4: Recarregar tabela IMEDIATAMENTE (TreeView será reconfigurado)
            self._popular_tabela()
            
            # PASSO 5: Voltar para aba de análise
            self.tabview.set("📊 Análise")
            
            # PASSO 6: Feedback visual
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.title(f"RT-PCR - Análise Completa (✅ Sincronizado: {timestamp})")
            
            registrar_log("Sincronização", "Dados do mapa sincronizados com sucesso", "INFO")
            
        except Exception as e:
            import traceback
            erro_completo = traceback.format_exc()
            registrar_log("Sincronização", f"Erro: {erro_completo}", "ERROR")
            messagebox.showerror("Erro de Sincronização", f"Falha ao sincronizar:\n{e}\n\nVeja logs para detalhes.", parent=self)
    
    def _on_tab_change(self):
        """Callback ao trocar de aba."""
        aba_atual = self.tabview.get()
        registrar_log("TabView", f"Aba alterada para: {aba_atual}", "DEBUG")
    
    def _mostrar_relatorio(self):
        """Exibe relatório estatístico."""
        try:
            import matplotlib.pyplot as plt
            
            # Preparar estatísticas
            result_cols = [c for c in self.df_analise.columns if str(c).startswith("Resultado_")]
            
            total = len(self.df_analise)
            stats_text = f"=== RELATÓRIO ESTATÍSTICO ===\n\n"
            stats_text += f"Exame: {self.exame}\n"
            stats_text += f"Data: {self.data_placa_formatada}\n"
            stats_text += f"Total de Amostras: {total}\n\n"
            
            # Contar resultados por alvo
            for col in result_cols:
                alvo = col.replace("Resultado_", "")
                valores = self.df_analise[col].astype(str).str.strip().str.upper()
                
                detectados = valores.str.contains("DET|POS", regex=True, na=False).sum()
                nao_detectados = valores.str.contains("ND|NEG", regex=True, na=False).sum()
                inconclusivos = valores.str.contains("INC", regex=True, na=False).sum()
                invalidos = valores.str.contains("INV", regex=True, na=False).sum()
                
                stats_text += f"{alvo}:\n"
                stats_text += f"  Detectados: {detectados}\n"
                stats_text += f"  Não Detectados: {nao_detectados}\n"
                stats_text += f"  Inconclusivos: {inconclusivos}\n"
                stats_text += f"  Inválidos: {invalidos}\n\n"
            
            messagebox.showinfo("Relatório Estatístico", stats_text, parent=self)
            registrar_log("Relatório", "Relatório exibido", "INFO")
            
        except Exception as e:
            registrar_log("Relatório", f"Erro: {e}", "ERROR")
            messagebox.showerror("Erro", f"Falha ao gerar relatório:\n{e}", parent=self)
    
    def _gerar_grafico(self):
        """Gera gráfico de detecção."""
        try:
            import matplotlib.pyplot as plt
            
            # Contar detectáveis por agravo
            result_cols = [c for c in self.df_analise.columns if str(c).startswith("Resultado_")]
            contagem = {}
            
            for col in result_cols:
                alvo = col.replace("Resultado_", "")
                valores = self.df_analise[col].astype(str).str.strip().str.upper()
                detectados = valores.str.contains("DET|POS", regex=True, na=False).sum()
                if detectados > 0:
                    contagem[alvo] = detectados
            
            if not contagem:
                messagebox.showinfo("Gráfico", "Nenhum alvo detectável para gráfico.", parent=self)
                return
            
            # Gerar gráfico
            plt.figure(figsize=(10, 6))
            plt.bar(contagem.keys(), contagem.values(), color="skyblue")
            plt.title("Distribuição de Amostras Detectáveis")
            plt.xlabel("Alvos")
            plt.ylabel("Quantidade Detectada")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            plt.show()
            
            registrar_log("Gráfico", "Gráfico gerado", "INFO")
            
        except Exception as e:
            registrar_log("Gráfico", f"Erro: {e}", "ERROR")
            messagebox.showerror("Erro", f"Falha ao gerar gráfico:\n{e}", parent=self)
    
    def _salvar_selecionados(self):
        """Salva TODAS as amostras no histórico e pergunta sobre envio ao GAL."""
        try:
            from services.history_report import gerar_historico_csv
            from db.db_utils import salvar_historico_processamento
            from exportacao.gal_formatter import formatar_para_gal
            from datetime import datetime, timezone
            
            # Detectar coluna de código
            col_codigo = "Codigo" if "Codigo" in self.df_analise.columns else "Código"
            
            # Preparar TODAS as amostras (não apenas selecionadas)
            df_todas = self.df_analise[self.df_analise[col_codigo].notna() & (self.df_analise[col_codigo] != "")]
            selecionados = self.df_analise[self.df_analise["Selecionado"] == True]
            
            if len(df_todas) == 0:
                messagebox.showinfo("Informação", "Nenhuma amostra para salvar.", parent=self)
                return
            
            # PASSO 1: Salvar TODAS no histórico CSV
            gerar_historico_csv(
                df_todas,
                exame=self.exame,
                usuario=self.usuario_logado,
                lote=self.lote,
                arquivo_corrida=self.arquivo_corrida,
                caminho_csv="logs/historico_analises.csv",
            )
            
            # Salvar também no PostgreSQL
            detalhes = f"Placa: {self.num_placa}; {len(df_todas)} amostras salvas."
            salvar_historico_processamento(
                self.usuario_logado, self.exame, "Concluído", detalhes
            )
            
            registrar_log("Histórico", f"{len(df_todas)} amostras salvas no histórico", "INFO")
            
            # PASSO 2: Verificar se há selecionadas para envio ao GAL
            if len(selecionados) == 0:
                messagebox.showinfo(
                    "Histórico Salvo",
                    f"✅ {len(df_todas)} amostras salvas no histórico.\n\n⚠️ Nenhuma selecionada para envio ao GAL.",
                    parent=self
                )
                return
            
            # PASSO 3: Perguntar sobre envio ao GAL
            resposta = messagebox.askyesno(
                "Enviar para GAL?",
                f"✅ {len(df_todas)} amostras salvas no histórico!\n\n📊 {len(selecionados)} amostras selecionadas.\n\nDeseja enviar as selecionadas para o GAL?",
                parent=self
            )
            
            if resposta:
                self._enviar_para_gal(selecionados)
            else:
                messagebox.showinfo("Concluído", "Histórico salvo. Envio ao GAL cancelado.", parent=self)
            
        except Exception as e:
            registrar_log("Salvar", f"Erro: {e}", "ERROR")
            messagebox.showerror("Erro", f"Falha ao salvar:\n{e}", parent=self)
    
    def _enviar_para_gal(self, df_selecionadas):
        """Processa envio das amostras selecionadas para o GAL."""
        try:
            from exportacao.gal_formatter import formatar_para_gal
            from exportacao.envio_gal import abrir_janela_envio_gal
            from utils.notifications import notificar_gal_saved
            from datetime import datetime, timezone
            import os
            
            # Formatar para GAL (sem depender de app_state)
            df_gal = formatar_para_gal(df_selecionadas, exam_cfg=None, exame=self.exame)
            
            # Salvar arquivos CSV
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            reports_dir = os.path.join(base_dir, "reports")
            os.makedirs(reports_dir, exist_ok=True)
            
            ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            gal_path = os.path.join(reports_dir, f"gal_{ts}_exame.csv")
            df_gal.to_csv(gal_path, index=False)
            
            gal_last = os.path.join(reports_dir, "gal_last_exame.csv")
            df_gal.to_csv(gal_last, index=False)
            
            registrar_log("GAL Export", f"CSV GAL gerado: {gal_path}", "INFO")
            
            # Notificar e abrir interface GAL
            notificar_gal_saved(gal_last, parent=self.master)
            abrir_janela_envio_gal(self.master, self.usuario_logado)
            
        except Exception as e:
            registrar_log("GAL", f"Erro ao enviar para GAL: {e}", "ERROR")
            messagebox.showerror("Erro GAL", f"Falha ao processar GAL:\n{e}", parent=self)
            messagebox.showerror("Erro", f"Falha ao enviar para GAL:\n{e}", parent=self)
    
    def _on_close(self):
        """Fecha janela com limpeza adequada."""
        try:
            # Limpar callbacks pendentes
            self.dispose()
            
            # Destruir janela
            self.destroy()
            
        except Exception as e:
            registrar_log("Fechar", f"Erro: {e}", "ERROR")

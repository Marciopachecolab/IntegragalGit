"""
Painel de Gerenciamento de Usu√°rios do Sistema IntegragalGit.
Fornece funcionalidades para gerenciar usu√°rios do sistema.
"""

import os
from datetime import datetime
from tkinter import messagebox, simpledialog
import tkinter as tk

import bcrypt
import customtkinter as ctk
import pandas as pd

from autenticacao.auth_service import AuthService
from utils.logger import registrar_log


class UserManagementPanel:
    """Painel de gerenciamento de usu√°rios"""

    def __init__(self, main_window, usuario_logado: str):
        """
        Inicializa o painel de gerenciamento de usu√°rios

        Args:
            main_window: Janela principal da aplica√ß√£o
            usuario_logado: Nome do usu√°rio logado
        """
        self.main_window = main_window
        self.usuario_logado = usuario_logado
        self.auth_service = AuthService()
        self.usuarios_path = "banco/usuarios.csv"
        self._criar_interface()

    def _criar_interface(self):
        """Cria a interface do painel de gerenciamento"""
        # Janela modal
        # Linha comentada devido a problemas recorrentes de fechamento com CTkToplevel em algumas vers√µes do customtkinter.
        # self.user_window = ctk.CTkToplevel(self.main_window)
        self.user_window = tk.Toplevel(self.main_window)
        self.user_window.title("üë• Gerenciamento de Usu√°rios")
        self.user_window.geometry("1100x800")
        self.user_window.transient(self.main_window)
        self.user_window.grab_set()

        # Protocolo de fechamento correto
        self.user_window.protocol("WM_DELETE_WINDOW", self._fechar_janela)

        # Centrar janela
        self.user_window.update_idletasks()
        x = (self.user_window.winfo_screenwidth() // 2) - (1100 // 2)
        y = (self.user_window.winfo_screenheight() // 2) - (800 // 2)
        self.user_window.geometry(f"1100x800+{x}+{y}")

        # Header
        header_frame = ctk.CTkFrame(self.user_window)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        title_label = ctk.CTkLabel(
            header_frame,
            text="üë• Gerenciamento de Usu√°rios",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title_label.pack(pady=15)

        info_label = ctk.CTkLabel(
            header_frame,
            text=f"Operador: {self.usuario_logado} | Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            font=ctk.CTkFont(size=12),
        )
        info_label.pack(pady=(0, 15))

        # Toolbar
        self._criar_toolbar()

        # √Årea principal com scroll
        main_scroll_frame = ctk.CTkScrollableFrame(self.user_window)
        main_scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Lista de usu√°rios
        self._carregar_usuarios(main_scroll_frame)

    def _criar_toolbar(self):
        """Cria barra de ferramentas"""
        toolbar_frame = ctk.CTkFrame(self.user_window)
        toolbar_frame.pack(fill="x", padx=20, pady=(0, 10))

        # Bot√µes de a√ß√£o
        ctk.CTkButton(
            toolbar_frame,
            text="‚ûï Adicionar Usu√°rio",
            command=self._adicionar_usuario,
            width=150,
        ).pack(side="left", padx=5, pady=10)

        ctk.CTkButton(
            toolbar_frame,
            text="√¢≈ì¬è√Ø¬∏¬è Editar Usu√°rio",
            command=self._editar_usuario,
            width=150,
        ).pack(side="left", padx=5, pady=10)

        ctk.CTkButton(
            toolbar_frame,
            text="üîÑ Alterar Senha",
            command=self._alterar_senha,
            width=150,
        ).pack(side="left", padx=5, pady=10)

        ctk.CTkButton(
            toolbar_frame,
            text="üóëÔ∏è¬è Remover Usu√°rio",
            command=self._remover_usuario,
            width=150,
        ).pack(side="left", padx=5, pady=10)

        # Bot√£o para voltar ao menu principal
        ctk.CTkButton(
            toolbar_frame,
            text="ÔøΩ≈°¬™ SAIR PARA O MENU INICIAL",
            command=self._sair_para_menu_principal,
            width=200,
            fg_color="#d32f2f",
            hover_color="#c62828",
        ).pack(side="left", padx=(20, 5), pady=10)

        ctk.CTkButton(
            toolbar_frame, text="ÔøΩ‚Äù¬ç Buscar", command=self._buscar_usuario, width=100
        ).pack(side="right", padx=5, pady=10)

        ctk.CTkButton(
            toolbar_frame, text="üîÑ Atualizar", command=self._atualizar_lista, width=100
        ).pack(side="right", padx=5, pady=10)

    def _carregar_usuarios(self, parent):
        """Carrega e exibe lista de usu√°rios"""
        try:
            if not os.path.exists(self.usuarios_path):
                self._mostrar_mensagem_erro(
                    parent, "Arquivo de credenciais n√£o encontrado"
                )
                return

            # Ler arquivo CSV com separador correto
            try:
                df = pd.read_csv(self.usuarios_path, sep=";", encoding="utf-8")
                print(f"‚úÖ CSV lido com separador ';' - {len(df)} usu√°rios carregados")
            except Exception:
                print(
                    "√¢≈°¬†√Ø¬∏¬è  Erro ao ler CSV com separador ';' - Tentando separador ','..."
                )
                try:
                    df = pd.read_csv(self.usuarios_path, sep=",", encoding="utf-8")
                    print(
                        f"‚úÖ CSV lido com separador ',' - {len(df)} usu√°rios carregados"
                    )
                except Exception as e2:
                    print(f"√¢¬ù≈í Erro ao ler arquivo de usu√°rios: {str(e2)}")
                    self._mostrar_mensagem_erro(
                        parent, f"Erro ao carregar usu√°rios: {str(e2)}"
                    )
                    return

            if df.empty:
                self._mostrar_mensagem_info(
                    parent, "Nenhum usu√°rio cadastrado no sistema"
                )
                return


            # Contador de usu√°rios
            total_usuarios = len(df)
            # Linha comentada devido a corre√ß√£o de compatibilidade: alguns arquivos CSV legados podem n√£o possuir a coluna 'senha_hash'.
            # usuarios_ativos = len(
            #     df[df["senha_hash"].notna() & (df["senha_hash"] != "")]
            # )
            if "senha_hash" in df.columns:
                usuarios_ativos = len(
                    df[df["senha_hash"].notna() & (df["senha_hash"] != "")]
                )
            else:
                # Caso de arquivo legado sem coluna de hash: considera-se 0 usu√°rios com senha configurada.
                usuarios_ativos = 0
            # Header com estat√≠sticas
            stats_frame = ctk.CTkFrame(parent)
            stats_frame.pack(fill="x", pady=(0, 20))

            ctk.CTkLabel(
                stats_frame,
                text=f"üìä Total de Usu√°rios: {total_usuarios} | ÔøΩ‚Äò¬§ Ativos: {usuarios_ativos}",
                font=ctk.CTkFont(size=14, weight="bold"),
            ).pack(pady=10)

            # Lista de usu√°rios
            for idx, usuario in df.iterrows():
                self._criar_card_usuario(parent, usuario)

        except Exception as e:
            self._mostrar_mensagem_erro(parent, f"Erro ao carregar usu√°rios: {str(e)}")

    def _criar_card_usuario(self, parent, usuario):
        """Cria card individual para cada usu√°rio"""
        card_frame = ctk.CTkFrame(parent)
        card_frame.pack(fill="x", pady=5)

        # Informa√ß√µes principais
        info_frame = ctk.CTkFrame(card_frame)
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Nome do usu√°rio
        nome_label = ctk.CTkLabel(
            info_frame,
            text=f"ÔøΩ‚Äò¬§ {usuario['usuario']}",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        nome_label.pack(anchor="w")

        # N√≠vel de acesso
        nivel_label = ctk.CTkLabel(
            info_frame,
            text=f"ÔøΩ‚Äù‚Äò N√≠vel: {usuario['nivel_acesso']}",
            font=ctk.CTkFont(size=12),
        )
        nivel_label.pack(anchor="w", pady=(2, 0))

        # Status
        senha_hash = usuario.get("senha_hash", "")
        if pd.notna(senha_hash) and senha_hash != "":
            status_text = "‚úÖ Ativo"
            status_color = "green"
        else:
            status_text = "√¢¬ù≈í Inativo"
            status_color = "red"

        status_label = ctk.CTkLabel(
            info_frame,
            text=status_text,
            text_color=status_color,
            font=ctk.CTkFont(size=12),
        )
        status_label.pack(anchor="w", pady=(2, 0))

        # Informa√ß√µes de hash (parcial)
        if pd.notna(senha_hash) and senha_hash != "":
            hash_preview = (
                senha_hash[:20] + "..." if len(senha_hash) > 20 else senha_hash
            )
            hash_label = ctk.CTkLabel(
                info_frame,
                text=f"ÔøΩ‚Äù‚Äô Hash: {hash_preview}",
                font=ctk.CTkFont(size=10),
                text_color="gray",
            )
            hash_label.pack(anchor="w", pady=(2, 0))

        # Bot√µes de a√ß√£o r√°pida
        acoes_frame = ctk.CTkFrame(card_frame)
        acoes_frame.pack(side="right", padx=10, pady=10)

        ctk.CTkButton(
            acoes_frame,
            text="√¢≈ì¬è√Ø¬∏¬è",
            width=30,
            command=lambda u=usuario: self._editar_usuario_rapido(u),
        ).pack(pady=2)

        ctk.CTkButton(
            acoes_frame,
            text="ÔøΩ‚Äù‚Äò",
            width=30,
            command=lambda u=usuario: self._alterar_senha_rapido(u),
        ).pack(pady=2)

        if usuario["usuario"] != self.usuario_logado:  # N√£o permitir remover a si mesmo
            ctk.CTkButton(
                acoes_frame,
                text="üóëÔ∏è¬è",
                width=30,
                command=lambda u=usuario: self._remover_usuario_rapido(u),
            ).pack(pady=2)

    def _adicionar_usuario(self):
        """Abre di√°logo para adicionar novo usu√°rio"""
        try:
            dialog = AdicionarUsuarioDialog(self.user_window)
            if dialog.result:
                username, password, nivel = dialog.result
                self._salvar_usuario(username, password, nivel)
                self._atualizar_lista()
        except Exception as e:
            messagebox.showerror(
                "Erro", f"Erro ao abrir di√°logo: {str(e)}", parent=self.user_window
            )
            # Fallback para m√©todo simples
            self._adicionar_usuario_simples()

    def _editar_usuario(self):
        """Abre di√°logo para editar usu√°rio existente"""
        usuario = self._selecionar_usuario()
        if usuario is not None:
            self._editar_usuario_completo(usuario)

    def _editar_usuario_rapido(self, usuario):
        """Edita usu√°rio rapidamente"""
        self._editar_usuario_completo(usuario)

    def _editar_usuario_completo(self, usuario):
        """Edita usu√°rio com di√°logo completo e melhor valida√ß√£o"""
        try:
            # Extrair informa√ß√µes do usu√°rio de forma segura
            if isinstance(usuario, dict):
                usuario_nome = usuario.get("usuario", "usu√°rio")
                usuario_nivel = usuario.get("nivel_acesso", "USER")
            else:
                usuario_nome = getattr(usuario, "usuario", "usu√°rio")
                usuario_nivel = getattr(usuario, "nivel_acesso", "USER")

            novo_nivel = simpledialog.askstring(
                "Editar Usu√°rio",
                f"Novo n√≠vel de acesso para {usuario_nome}:\n(ADMIN, MASTER, DIAGNOSTICO, USER)",
                initialvalue=usuario_nivel,
                parent=self.user_window,
            )

            if novo_nivel and novo_nivel.strip():
                novo_nivel = novo_nivel.upper().strip()
                niveis_validos = ["ADMIN", "MASTER", "DIAGNOSTICO", "USER"]

                if novo_nivel in niveis_validos:
                    # Carregar arquivo
                    df = pd.read_csv(self.usuarios_path, sep=";")

                    # Verificar se o usu√°rio existe
                    if usuario_nome in df["usuario"].values:
                        # Atualizar n√≠vel
                        df.loc[df["usuario"] == usuario_nome, "nivel_acesso"] = (
                            novo_nivel
                        )

                        # Salvar
                        df.to_csv(self.usuarios_path, sep=";", index=False)

                        messagebox.showinfo(
                            "Sucesso",
                            f"N√≠vel de {usuario_nome} alterado para {novo_nivel}",
                            parent=self.user_window,
                        )

                        if "registrar_log" in globals():
                            registrar_log(
                                "UserManagement",
                                f"Usu√°rio {usuario_nome} editado por {self.usuario_logado}",
                                "INFO",
                            )

                        self._atualizar_lista()
                    else:
                        messagebox.showerror(
                            "Erro",
                            f"Usu√°rio {usuario_nome} n√£o encontrado no arquivo!",
                            parent=self.user_window,
                        )
                else:
                    messagebox.showerror(
                        "Erro",
                        f"N√≠vel '{novo_nivel}' n√£o √© v√°lido!\nUse: {', '.join(niveis_validos)}",
                        parent=self.user_window,
                    )
        except Exception as e:
            messagebox.showerror(
                "Erro", f"Erro ao editar usu√°rio: {str(e)}", parent=self.user_window
            )

    def _alterar_senha(self):
        """Abre di√°logo para alterar senha"""
        usuario = self._selecionar_usuario()
        if usuario is not None:
            self._alterar_senha_usuario(usuario)

    def _alterar_senha_rapido(self, usuario):
        """Altera senha rapidamente"""
        self._alterar_senha_usuario(usuario)

    def _alterar_senha_usuario(self, usuario):
        """Altera senha de usu√°rio espec√≠fico com melhor tratamento de erros"""
        try:
            # Extrair nome do usu√°rio de forma segura
            if isinstance(usuario, dict):
                usuario_nome = usuario.get("usuario", "usu√°rio")
            else:
                usuario_nome = getattr(usuario, "usuario", "usu√°rio")

            nova_senha = simpledialog.askstring(
                "Alterar Senha",
                f"Nova senha para {usuario_nome}:",
                show="*",
                parent=self.user_window,
            )

            if nova_senha and nova_senha.strip():
                if len(nova_senha) < 6:
                    messagebox.showwarning(
                        "Aviso",
                        "A senha deve ter pelo menos 6 caracteres!",
                        parent=self.user_window,
                    )
                    return

                # Confirmar senha
                confirmar_senha = simpledialog.askstring(
                    "Confirmar Senha",
                    f"Confirme a senha para {usuario_nome}:",
                    show="*",
                    parent=self.user_window,
                )

                if nova_senha == confirmar_senha:
                    try:
                        # Gerar hash da nova senha
                        try:
                            import bcrypt

                            senha_bytes = nova_senha.encode("utf-8")
                            salt = bcrypt.gensalt()
                            hash_senha = bcrypt.hashpw(senha_bytes, salt).decode(
                                "utf-8"
                            )
                        except ImportError:
                            messagebox.showerror(
                                "Erro",
                                "Biblioteca bcrypt n√£o dispon√≠vel!",
                                parent=self.user_window,
                            )
                            return

                        # Carregar arquivo
                        df = pd.read_csv(self.usuarios_path, sep=";")

                        # Verificar se o usu√°rio existe
                        if usuario_nome in df["usuario"].values:
                            # Atualizar senha (campo correto √© senha_hash)
                            df.loc[df["usuario"] == usuario_nome, "senha_hash"] = (
                                hash_senha
                            )

                            # Salvar
                            df.to_csv(self.usuarios_path, sep=";", index=False)

                            messagebox.showinfo(
                                "Sucesso",
                                f"Senha do usu√°rio {usuario_nome} alterada com sucesso!",
                                parent=self.user_window,
                            )

                            if "registrar_log" in globals():
                                registrar_log(
                                    "UserManagement",
                                    f"Senha do usu√°rio {usuario_nome} alterada por {self.usuario_logado}",
                                    "INFO",
                                )

                            self._atualizar_lista()
                        else:
                            messagebox.showerror(
                                "Erro",
                                f"Usu√°rio {usuario_nome} n√£o encontrado!",
                                parent=self.user_window,
                            )

                    except Exception as e:
                        messagebox.showerror(
                            "Erro",
                            f"Erro ao alterar senha: {str(e)}",
                            parent=self.user_window,
                        )
                else:
                    messagebox.showwarning(
                        "Aviso", "As senhas n√£o coincidem!", parent=self.user_window
                    )
            else:
                messagebox.showwarning(
                    "Aviso", "Senha n√£o pode estar vazia!", parent=self.user_window
                )
        except Exception as e:
            messagebox.showerror(
                "Erro", f"Erro ao alterar senha: {str(e)}", parent=self.user_window
            )

    def _remover_usuario(self):
        """Remove usu√°rio do sistema"""
        usuario = self._selecionar_usuario()
        if usuario is not None:
            self._remover_usuario_confirmado(usuario)

    def _remover_usuario_rapido(self, usuario):
        """Remove usu√°rio rapidamente com confirma√ß√£o"""
        self._remover_usuario_confirmado(usuario)

    def _remover_usuario_confirmado(self, usuario):
        """Remove usu√°rio com confirma√ß√£o"""
        if usuario["usuario"] == self.usuario_logado:
            messagebox.showwarning(
                "Aviso", "Voc√™ n√£o pode remover a si mesmo!", parent=self.user_window
            )
            return

        if messagebox.askyesno(
            "Confirmar Remo√ß√£o",
            f"Tem certeza que deseja remover o usu√°rio '{usuario['usuario']}'?\n\nEsta a√ß√£o n√£o pode ser desfeita!",
            parent=self.user_window,
        ):
            try:
                # Carregar arquivo
                df = pd.read_csv(self.usuarios_path)

                # Remover usu√°rio
                df = df[df["usuario"] != usuario["usuario"]]

                # Salvar
                df.to_csv(self.usuarios_path, index=False)

                messagebox.showinfo(
                    "Sucesso",
                    f"Usu√°rio {usuario['usuario']} removido com sucesso!",
                    parent=self.user_window,
                )
                registrar_log(
                    "UserManagement",
                    f"Usu√°rio {usuario['usuario']} removido por {self.usuario_logado}",
                    "WARNING",
                )
                self._atualizar_lista()

            except Exception as e:
                messagebox.showerror(
                    "Erro",
                    f"Erro ao remover usu√°rio: {str(e)}",
                    parent=self.user_window,
                )

    def _buscar_usuario(self):
        """Busca usu√°rio por nome"""
        nome_busca = simpledialog.askstring(
            "Buscar Usu√°rio",
            "Digite o nome do usu√°rio para buscar:",
            parent=self.user_window,
        )

        if nome_busca and nome_busca.strip():
            try:
                if not os.path.exists(self.usuarios_path):
                    messagebox.showerror(
                        "Erro",
                        "Arquivo de credenciais n√£o encontrado!",
                        parent=self.user_window,
                    )
                    return

                # Ler arquivo com separador correto
                try:
                    df = pd.read_csv(self.usuarios_path, sep=";")
                except Exception:
                    df = pd.read_csv(self.usuarios_path, sep=",")

                # Normalizar nome para busca (case-insensitive)
                nome_busca = nome_busca.strip().lower()

                # Buscar usu√°rios que contenham o nome
                usuarios_encontrados = df[
                    df["usuario"].str.lower().str.contains(nome_busca, na=False)
                ]

                if not usuarios_encontrados.empty:
                    # Mostrar resultados da busca
                    resultado = f"ÔøΩ‚Äù¬ç Resultados da busca por '{nome_busca}':\n\n"

                    for _, usuario in usuarios_encontrados.iterrows():
                        nivel = usuario.get("nivel_acesso", "USER")
                        resultado += f"ÔøΩ‚Äò¬§ {usuario['usuario']} | ÔøΩ‚Äù‚Äò {nivel}\n"

                    # Criar janela de resultados
                    resultado_window = ctk.CTkToplevel(self.user_window)
                    resultado_window.title("Resultados da Busca")
                    resultado_window.geometry("400x300")
                    resultado_window.transient(self.user_window)
                    resultado_window.grab_set()

                    # Texto com resultados
                    texto_resultado = ctk.CTkTextbox(resultado_window, height=200)
                    texto_resultado.pack(fill="both", expand=True, padx=20, pady=20)
                    texto_resultado.insert("1.0", resultado)
                    texto_resultado.configure(state="disabled")

                    # Bot√£o fechar
                    ctk.CTkButton(
                        resultado_window,
                        text="Fechar",
                        command=resultado_window.destroy,
                    ).pack(pady=10)

                else:
                    messagebox.showinfo(
                        "Busca",
                        f"Nenhum usu√°rio encontrado com o nome '{nome_busca}'.",
                        parent=self.user_window,
                    )

            except Exception as e:
                messagebox.showerror(
                    "Erro", f"Erro durante a busca: {str(e)}", parent=self.user_window
                )

    def _sair_para_menu_principal(self):
        """Fecha a janela de gerenciamento de usu√°rios e volta ao menu principal"""
        self.user_window.destroy()
        self.main_window.deiconify()  # Volta a mostrar a janela principal

    def _atualizar_lista(self):
        """Atualiza lista de usu√°rios"""
        try:
            # Encontrar o scrollable frame principal e recarregar apenas ele
            for widget in self.user_window.winfo_children():
                if hasattr(widget, "winfo_name") and "scrollable_frame" in str(
                    widget.__class__
                ):
                    # Limpar apenas o conte√∫do do scrollable frame
                    for child in widget.winfo_children():
                        child.destroy()

                    # Recarregar usu√°rios
                    self._carregar_usuarios(widget)
                    break
            else:
                # Se n√£o encontrou scrollable frame, recriar interface completa
                self._criar_interface()

            messagebox.showinfo(
                "Atualizar", "Lista de usu√°rios atualizada!", parent=self.user_window
            )

        except Exception as e:
            messagebox.showerror(
                "Erro", f"Erro ao atualizar lista: {str(e)}", parent=self.user_window
            )

    def _selecionar_usuario(self, parent):
        """Permite selecionar um usu√°rio do arquivo de credenciais para edi√ß√£o/remo√ß√£o."""
        try:
            # Verifica se o arquivo existe
            if not os.path.exists(self.usuarios_path):
                messagebox.showerror(
                    "Erro",
                    f"Arquivo de credenciais n√£o encontrado em:\n{self.usuarios_path}",
                    parent=self.user_window,
                )
                return None

            # Tenta ler com separador ';' e, se falhar, com ','
            try:
                df = pd.read_csv(self.usuarios_path, sep=";")
            except Exception:
                try:
                    df = pd.read_csv(self.usuarios_path, sep=",")
                except Exception as read_error:
                    messagebox.showerror(
                        "Erro",
                        f"Erro ao ler arquivo de credenciais: {str(read_error)}",
                        parent=self.user_window,
                    )
                    return None

            if df.empty:
                messagebox.showwarning(
                    "Aviso",
                    "Nenhum usu√°rio cadastrado!",
                    parent=self.user_window,
                )
                return None

            # Normaliza nomes de colunas (remove BOM, espa√ßos e coloca em min√∫sculas)
            # original_columns = list(df.columns)
            # Comentado devido ao aviso F841 do Ruff (vari√°vel n√£o utilizada, mantido apenas para hist√≥rico).
            df.columns = [
                str(c).replace("\ufeff", "").strip().lower() for c in df.columns
            ]

            # Identifica a coluna que representa o "usu√°rio" (login)
            candidatos = ["usuario", "user", "login", "nome_usuario", "username", "nome"]
            col_usuario = None
            for nome in candidatos:
                if nome in df.columns:
                    col_usuario = nome
                    break

            if col_usuario is None:
                # Linha comentada devido √É¬† rigidez anterior que exigia exatamente 'usuario'.
                # messagebox.showerror(
                #     "Erro",
                #     "Coluna 'usuario' n√£o encontrada no arquivo de credenciais (mesmo ap√≥s normaliza√ß√£o de headers).",
                #     parent=self.user_window,
                # )
                # return None

                # Fallback: usa a primeira coluna como identificador para n√£o quebrar a interface.
                col_usuario = df.columns[0]

            # Monta lista de op√ß√µes de usu√°rio
            usuarios_opcoes = df[col_usuario].dropna().astype(str).tolist()
            if not usuarios_opcoes:
                messagebox.showwarning(
                    "Aviso",
                    "Nenhum usu√°rio encontrado na coluna de identifica√ß√£o.",
                    parent=self.user_window,
                )
                return None

            # Caixa de di√°logo simples para confirmar / digitar o usu√°rio
            usuario_selecionado = simpledialog.askstring(
                "Selecionar usu√°rio",
                "Digite ou confirme o usu√°rio a ser editado:",
                initialvalue=usuarios_opcoes[0],
                parent=self.user_window,
            )
            if not usuario_selecionado:
                return None

            # Filtro case-insensitive, ignorando espa√ßos
            filtro = (
                df[col_usuario]
                .astype(str)
                .str.strip()
                .str.lower()
                == str(usuario_selecionado).strip().lower()
            )
            df_filtrado = df[filtro]

            if df_filtrado.empty:
                messagebox.showerror(
                    "Erro",
                    f"Usu√°rio '{usuario_selecionado}' n√£o encontrado.",
                    parent=self.user_window,
                )
                return None

            # Retorna a linha como dict para uso nos outros m√©todos
            return df_filtrado.iloc[0].to_dict()

        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao selecionar usu√°rio: {str(e)}",
                parent=self.user_window,
            )
            return None

    def _adicionar_usuario_simples(self):
        """M√©todo simplificado para adicionar usu√°rio (fallback)"""
        try:
            username = simpledialog.askstring(
                "Adicionar Usu√°rio", "Nome do usu√°rio:", parent=self.user_window
            )
            if not username or not username.strip():
                return

            password = simpledialog.askstring(
                "Adicionar Usu√°rio", "Senha:", show="*", parent=self.user_window
            )
            if not password or len(password.strip()) < 6:
                messagebox.showwarning(
                    "Aviso",
                    "Senha deve ter pelo menos 6 caracteres!",
                    parent=self.user_window,
                )
                return

            nivel = simpledialog.askstring(
                "Adicionar Usu√°rio",
                "N√≠vel (USER/ADMIN/OPERATOR):",
                initialvalue="USER",
                parent=self.user_window,
            )
            if not nivel:
                nivel = "USER"

            self._salvar_usuario(username.strip(), password.strip(), nivel.strip())
            self._atualizar_lista()

        except Exception as e:
            messagebox.showerror(
                "Erro", f"Erro ao adicionar usu√°rio: {str(e)}", parent=self.user_window
            )

    def _salvar_usuario(self, username: str, password: str, nivel: str):
        """Salva novo usu√°rio no sistema"""
        try:
            # Valida√ß√µes
            if not username or not password or not nivel:
                messagebox.showerror(
                    "Erro", "Todos os campos s√£o obrigat√≥rios!", parent=self.user_window
                )
                return

            if len(password) < 6:
                messagebox.showerror(
                    "Erro",
                    "A senha deve ter pelo menos 6 caracteres!",
                    parent=self.user_window,
                )
                return

            # Gerar hash da senha
            try:
                senha_bytes = password.encode("utf-8")
                salt = bcrypt.gensalt()
                hash_senha = bcrypt.hashpw(senha_bytes, salt).decode("utf-8")
            except Exception as bcrypt_error:
                messagebox.showerror(
                    "Erro",
                    f"Erro ao criptografar senha: {str(bcrypt_error)}",
                    parent=self.user_window,
                )
                return

            # Criar diret√≥rio banco se n√£o existir
            banco_dir = os.path.dirname(self.usuarios_path)
            if banco_dir and not os.path.exists(banco_dir):
                os.makedirs(banco_dir, exist_ok=True)

            # Carregar arquivo existente ou criar novo
            try:
                if os.path.exists(self.usuarios_path):
                    # Tentar ler com separador correto
                    try:
                        df = pd.read_csv(self.usuarios_path, sep=";")
                    except Exception:
                        # Se falhar, tentar com v√≠rgula
                        try:
                            df = pd.read_csv(self.usuarios_path, sep=",")
                        except Exception:
                            # Se ainda falhar, criar novo dataframe
                            df = pd.DataFrame(
                                columns=["usuario", "senha_hash", "nivel_acesso"]
                            )

                    # Verificar e ajustar estrutura das colunas
                    colunas_esperadas = ["usuario", "senha_hash", "nivel_acesso"]
                    colunas_encontradas = df.columns.tolist()

                    # Mapear colunas existentes para o padr√£o esperado
                    if (
                        "senha_hash" in colunas_encontradas
                        and "senha" not in colunas_encontradas
                    ):
                        df = df.rename(columns={"senha_hash": "senha"})

                    # Adicionar coluna nivel_acesso se n√£o existir
                    if "nivel_acesso" not in colunas_encontradas:
                        df["nivel_acesso"] = "USER"  # Padr√£o

                    # Garantir que todas as colunas existem
                    for col in colunas_esperadas:
                        if col not in df.columns:
                            df[col] = ""

                    # Selecionar apenas as colunas esperadas
                    df = df[colunas_esperadas]

                else:
                    df = pd.DataFrame(columns=["usuario", "senha_hash", "nivel_acesso"])
                    # Criar arquivo vazio
                    os.makedirs(os.path.dirname(self.usuarios_path), exist_ok=True)
                    df.to_csv(self.usuarios_path, sep=";", index=False)

            except Exception as csv_error:
                messagebox.showerror(
                    "Erro",
                    f"Erro ao acessar arquivo de credenciais: {str(csv_error)}",
                    parent=self.user_window,
                )
                return

            # Verificar se usu√°rio j√° existe
            if username in df["usuario"].values:
                messagebox.showwarning(
                    "Aviso", f"Usu√°rio '{username}' j√° existe!", parent=self.user_window
                )
                return

            # Adicionar novo usu√°rio
            novo_usuario = {
                "usuario": username,
                "senha_hash": hash_senha,
                "nivel_acesso": nivel.upper(),  # Padronizar para mai√∫sculo
            }

            try:
                df = pd.concat([df, pd.DataFrame([novo_usuario])], ignore_index=True)
                # Salvar com separador ponto-e-v√≠rgula para compatibilidade
                df.to_csv(self.usuarios_path, sep=";", index=False)
            except Exception as save_error:
                messagebox.showerror(
                    "Erro",
                    f"Erro ao salvar arquivo: {str(save_error)}",
                    parent=self.user_window,
                )
                return

            messagebox.showinfo(
                "Sucesso",
                f"Usu√°rio '{username}' criado com sucesso!\n\nN√≠vel: {nivel.upper()}",
                parent=self.user_window,
            )
            registrar_log(
                "UserManagement",
                f"Usu√°rio {username} criado por {self.usuario_logado}",
                "INFO",
            )

        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro inesperado ao salvar usu√°rio: {str(e)}",
                parent=self.user_window,
            )

    def _mostrar_mensagem_erro(self, parent, mensagem: str):
        """Exibe mensagem de erro"""
        ctk.CTkLabel(
            parent, text=f"√¢¬ù≈í {mensagem}", text_color="red", font=ctk.CTkFont(size=14)
        ).pack(pady=20)

    def _mostrar_mensagem_info(self, parent, mensagem: str):
        """Exibe mensagem informativa"""
        ctk.CTkLabel(
            parent, text=f"√¢‚Äû¬π√Ø¬∏¬è {mensagem}", text_color="blue", font=ctk.CTkFont(size=14)
        ).pack(pady=20)

    def _fechar_janela(self):
        """Fecha a janela de gerenciamento corretamente"""
        try:
            # Liberar grab se estiver ativo
            if hasattr(self, "user_window") and self.user_window.winfo_exists():
                try:
                    self.user_window.grab_release()
                    # For√ßar o release de qualquer grab ativo
                    if (
                        hasattr(self.user_window, "tk")
                        and self.user_window.tk.call("grab", "status", self.user_window)
                        != "none"
                    ):
                        self.user_window.tk.call("grab", "release", self.user_window)
                except Exception as grab_error:
                    print(f"Erro no grab: {grab_error}")

                # Ocultar e destruir
                self.user_window.withdraw()
                self.user_window.destroy()

                # Garbage collection manual para garantir limpeza
                del self.user_window
        except Exception as e:
            print(f"Erro ao fechar janela: {e}")
            # Fallback - tentar ocultar mesmo em caso de erro
            try:
                if hasattr(self, "user_window"):
                    self.user_window.withdraw()
            except Exception as e:
                pass

    def _on_closing(self):
        """Handler para fechamento da janela"""
        self._fechar_janela()


class AdicionarUsuarioDialog:
    """Di√°logo para adicionar novo usu√°rio"""

    def __init__(self, parent):
        self.result = None

        # Janela de di√°logo
        # Linha comentada devido a problemas recorrentes de fechamento com CTkToplevel em algumas vers√µes do customtkinter.
        # self.dialog = ctk.CTkToplevel(parent)
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("‚ûï Adicionar Novo Usu√°rio")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Centrar janela
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (300 // 2)
        self.dialog.geometry(f"400x300+{x}+{y}")

        self._criar_interface()
        self.dialog.wait_window()

    def _criar_interface(self):
        """Cria interface do di√°logo"""
        # Frame principal
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # T√≠tulo
        title_label = ctk.CTkLabel(
            main_frame,
            text="‚ûï Adicionar Novo Usu√°rio",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        title_label.pack(pady=(20, 30))

        # Campo nome de usu√°rio
        username_frame = ctk.CTkFrame(main_frame)
        username_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(username_frame, text="Nome de Usu√°rio:").pack(
            anchor="w", padx=10, pady=(10, 5)
        )
        self.username_entry = ctk.CTkEntry(
            username_frame, placeholder_text="Digite o nome do usu√°rio"
        )
        self.username_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Campo senha
        password_frame = ctk.CTkFrame(main_frame)
        password_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(password_frame, text="Senha:").pack(
            anchor="w", padx=10, pady=(10, 5)
        )
        self.password_entry = ctk.CTkEntry(
            password_frame, placeholder_text="Digite a senha", show="*"
        )
        self.password_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Campo confirmar senha
        confirm_password_frame = ctk.CTkFrame(main_frame)
        confirm_password_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(confirm_password_frame, text="Confirmar Senha:").pack(
            anchor="w", padx=10, pady=(10, 5)
        )
        self.confirm_password_entry = ctk.CTkEntry(
            confirm_password_frame, placeholder_text="Confirme a senha", show="*"
        )
        self.confirm_password_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Campo n√≠vel de acesso
        level_frame = ctk.CTkFrame(main_frame)
        level_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(level_frame, text="N√≠vel de Acesso:").pack(
            anchor="w", padx=10, pady=(10, 5)
        )
        self.level_combo = ctk.CTkComboBox(
            level_frame, values=["USER", "ADMIN", "OPERATOR"], state="readonly"
        )
        self.level_combo.set("USER")
        self.level_combo.pack(fill="x", padx=10, pady=(0, 10))

        # Bot√µes
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(
            button_frame, text="Cancelar", command=self._cancelar, width=100
        ).pack(side="right", padx=(10, 0))

        ctk.CTkButton(
            button_frame, text="Criar Usu√°rio", command=self._criar_usuario, width=100
        ).pack(side="right")

    def _criar_usuario(self):
        """Valida e cria o usu√°rio"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        level = self.level_combo.get()

        # Valida√ß√µes
        if not username:
            messagebox.showwarning(
                "Aviso", "Nome de usu√°rio √© obrigat√≥rio!", parent=self.dialog
            )
            return

        if not password:
            messagebox.showwarning("Aviso", "Senha √© obrigat√≥ria!", parent=self.dialog)
            return

        if password != confirm_password:
            messagebox.showwarning(
                "Aviso", "As senhas n√£o coincidem!", parent=self.dialog
            )
            return

        if len(password) < 6:
            messagebox.showwarning(
                "Aviso", "A senha deve ter pelo menos 6 caracteres!", parent=self.dialog
            )
            return

        # Sucesso
        self.result = (username, password, level)
        self.dialog.destroy()

    def _cancelar(self):
        """Cancela a opera√ß√£o"""
        self.dialog.destroy()
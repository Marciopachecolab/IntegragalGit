"""
Painel de Gerenciamento de Usuários do Sistema IntegragalGit.
Fornece funcionalidades para gerenciar usuários do sistema.
"""

import os
from datetime import datetime
from tkinter import messagebox, simpledialog

import bcrypt
import customtkinter as ctk
import pandas as pd

from autenticacao.auth_service import AuthService
from utils.logger import registrar_log


class UserManagementPanel:
    """Painel de gerenciamento de usuários"""

    def __init__(self, main_window, usuario_logado: str):
        """
        Inicializa o painel de gerenciamento de usuários

        Args:
            main_window: Janela principal da aplicação
            usuario_logado: Nome do usuário logado
        """
        self.main_window = main_window
        self.usuario_logado = usuario_logado
        self.auth_service = AuthService()
        self.usuarios_path = "banco/usuarios.csv"
        self._criar_interface()

    def _criar_interface(self):
        """Cria a interface do painel de gerenciamento"""
        # Janela modal
        self.user_window = ctk.CTkToplevel(self.main_window)
        self.user_window.title("👥 Gerenciamento de Usuários")
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
            text="👥 Gerenciamento de Usuários",
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

        # Área principal com scroll
        main_scroll_frame = ctk.CTkScrollableFrame(self.user_window)
        main_scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Lista de usuários
        self._carregar_usuarios(main_scroll_frame)

    def _criar_toolbar(self):
        """Cria barra de ferramentas"""
        toolbar_frame = ctk.CTkFrame(self.user_window)
        toolbar_frame.pack(fill="x", padx=20, pady=(0, 10))

        # Botões de ação
        ctk.CTkButton(
            toolbar_frame,
            text="➕ Adicionar Usuário",
            command=self._adicionar_usuario,
            width=150,
        ).pack(side="left", padx=5, pady=10)

        ctk.CTkButton(
            toolbar_frame,
            text="✏️ Editar Usuário",
            command=self._editar_usuario,
            width=150,
        ).pack(side="left", padx=5, pady=10)

        ctk.CTkButton(
            toolbar_frame,
            text="🔄 Alterar Senha",
            command=self._alterar_senha,
            width=150,
        ).pack(side="left", padx=5, pady=10)

        ctk.CTkButton(
            toolbar_frame,
            text="🗑️ Remover Usuário",
            command=self._remover_usuario,
            width=150,
        ).pack(side="left", padx=5, pady=10)

        # Botão para voltar ao menu principal
        ctk.CTkButton(
            toolbar_frame,
            text="🚪 SAIR PARA O MENU INICIAL",
            command=self._sair_para_menu_principal,
            width=200,
            fg_color="#d32f2f",
            hover_color="#c62828",
        ).pack(side="left", padx=(20, 5), pady=10)

        ctk.CTkButton(
            toolbar_frame, text="🔍 Buscar", command=self._buscar_usuario, width=100
        ).pack(side="right", padx=5, pady=10)

        ctk.CTkButton(
            toolbar_frame, text="🔄 Atualizar", command=self._atualizar_lista, width=100
        ).pack(side="right", padx=5, pady=10)

    def _carregar_usuarios(self, parent):
        """Carrega e exibe lista de usuários"""
        try:
            if not os.path.exists(self.usuarios_path):
                self._mostrar_mensagem_erro(
                    parent, "Arquivo de credenciais não encontrado"
                )
                return

            # Ler arquivo CSV com separador correto
            try:
                df = pd.read_csv(self.usuarios_path, sep=";", encoding="utf-8")
                print(f"✅ CSV lido com separador ';' - {len(df)} usuários carregados")
            except Exception:
                print(
                    "⚠️  Erro ao ler CSV com separador ';' - Tentando separador ','..."
                )
                try:
                    df = pd.read_csv(self.usuarios_path, sep=",", encoding="utf-8")
                    print(
                        f"✅ CSV lido com separador ',' - {len(df)} usuários carregados"
                    )
                except Exception as e2:
                    print(f"❌ Erro ao ler arquivo de usuários: {str(e2)}")
                    self._mostrar_mensagem_erro(
                        parent, f"Erro ao carregar usuários: {str(e2)}"
                    )
                    return

            if df.empty:
                self._mostrar_mensagem_info(
                    parent, "Nenhum usuário cadastrado no sistema"
                )
                return

            # Contador de usuários
            total_usuarios = len(df)
            usuarios_ativos = len(
                df[df["senha_hash"].notna() & (df["senha_hash"] != "")]
            )

            # Header com estatísticas
            stats_frame = ctk.CTkFrame(parent)
            stats_frame.pack(fill="x", pady=(0, 20))

            ctk.CTkLabel(
                stats_frame,
                text=f"📊 Total de Usuários: {total_usuarios} | 👤 Ativos: {usuarios_ativos}",
                font=ctk.CTkFont(size=14, weight="bold"),
            ).pack(pady=10)

            # Lista de usuários
            for idx, usuario in df.iterrows():
                self._criar_card_usuario(parent, usuario)

        except Exception as e:
            self._mostrar_mensagem_erro(parent, f"Erro ao carregar usuários: {str(e)}")

    def _criar_card_usuario(self, parent, usuario):
        """Cria card individual para cada usuário"""
        card_frame = ctk.CTkFrame(parent)
        card_frame.pack(fill="x", pady=5)

        # Informações principais
        info_frame = ctk.CTkFrame(card_frame)
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Nome do usuário
        nome_label = ctk.CTkLabel(
            info_frame,
            text=f"👤 {usuario['usuario']}",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        nome_label.pack(anchor="w")

        # Nível de acesso
        nivel_label = ctk.CTkLabel(
            info_frame,
            text=f"🔑 Nível: {usuario['nivel_acesso']}",
            font=ctk.CTkFont(size=12),
        )
        nivel_label.pack(anchor="w", pady=(2, 0))

        # Status
        senha_hash = usuario.get("senha_hash", "")
        if pd.notna(senha_hash) and senha_hash != "":
            status_text = "✅ Ativo"
            status_color = "green"
        else:
            status_text = "❌ Inativo"
            status_color = "red"

        status_label = ctk.CTkLabel(
            info_frame,
            text=status_text,
            text_color=status_color,
            font=ctk.CTkFont(size=12),
        )
        status_label.pack(anchor="w", pady=(2, 0))

        # Informações de hash (parcial)
        if pd.notna(senha_hash) and senha_hash != "":
            hash_preview = (
                senha_hash[:20] + "..." if len(senha_hash) > 20 else senha_hash
            )
            hash_label = ctk.CTkLabel(
                info_frame,
                text=f"🔒 Hash: {hash_preview}",
                font=ctk.CTkFont(size=10),
                text_color="gray",
            )
            hash_label.pack(anchor="w", pady=(2, 0))

        # Botões de ação rápida
        acoes_frame = ctk.CTkFrame(card_frame)
        acoes_frame.pack(side="right", padx=10, pady=10)

        ctk.CTkButton(
            acoes_frame,
            text="✏️",
            width=30,
            command=lambda u=usuario: self._editar_usuario_rapido(u),
        ).pack(pady=2)

        ctk.CTkButton(
            acoes_frame,
            text="🔑",
            width=30,
            command=lambda u=usuario: self._alterar_senha_rapido(u),
        ).pack(pady=2)

        if usuario["usuario"] != self.usuario_logado:  # Não permitir remover a si mesmo
            ctk.CTkButton(
                acoes_frame,
                text="🗑️",
                width=30,
                command=lambda u=usuario: self._remover_usuario_rapido(u),
            ).pack(pady=2)

    def _adicionar_usuario(self):
        """Abre diálogo para adicionar novo usuário"""
        try:
            dialog = AdicionarUsuarioDialog(self.user_window)
            if dialog.result:
                username, password, nivel = dialog.result
                self._salvar_usuario(username, password, nivel)
                self._atualizar_lista()
        except Exception as e:
            messagebox.showerror(
                "Erro", f"Erro ao abrir diálogo: {str(e)}", parent=self.user_window
            )
            # Fallback para método simples
            self._adicionar_usuario_simples()

    def _editar_usuario(self):
        """Abre diálogo para editar usuário existente"""
        usuario = self._selecionar_usuario()
        if usuario is not None:
            self._editar_usuario_completo(usuario)

    def _editar_usuario_rapido(self, usuario):
        """Edita usuário rapidamente"""
        self._editar_usuario_completo(usuario)

    def _editar_usuario_completo(self, usuario):
        """Edita usuário com diálogo completo e melhor validação"""
        try:
            # Extrair informações do usuário de forma segura
            if isinstance(usuario, dict):
                usuario_nome = usuario.get("usuario", "usuário")
                usuario_nivel = usuario.get("nivel_acesso", "USER")
            else:
                usuario_nome = getattr(usuario, "usuario", "usuário")
                usuario_nivel = getattr(usuario, "nivel_acesso", "USER")

            novo_nivel = simpledialog.askstring(
                "Editar Usuário",
                f"Novo nível de acesso para {usuario_nome}:\n(ADMIN, MASTER, DIAGNOSTICO, USER)",
                initialvalue=usuario_nivel,
                parent=self.user_window,
            )

            if novo_nivel and novo_nivel.strip():
                novo_nivel = novo_nivel.upper().strip()
                niveis_validos = ["ADMIN", "MASTER", "DIAGNOSTICO", "USER"]

                if novo_nivel in niveis_validos:
                    # Carregar arquivo
                    df = pd.read_csv(self.usuarios_path, sep=";")

                    # Verificar se o usuário existe
                    if usuario_nome in df["usuario"].values:
                        # Atualizar nível
                        df.loc[df["usuario"] == usuario_nome, "nivel_acesso"] = (
                            novo_nivel
                        )

                        # Salvar
                        df.to_csv(self.usuarios_path, sep=";", index=False)

                        messagebox.showinfo(
                            "Sucesso",
                            f"Nível de {usuario_nome} alterado para {novo_nivel}",
                            parent=self.user_window,
                        )

                        if "registrar_log" in globals():
                            registrar_log(
                                "UserManagement",
                                f"Usuário {usuario_nome} editado por {self.usuario_logado}",
                                "INFO",
                            )

                        self._atualizar_lista()
                    else:
                        messagebox.showerror(
                            "Erro",
                            f"Usuário {usuario_nome} não encontrado no arquivo!",
                            parent=self.user_window,
                        )
                else:
                    messagebox.showerror(
                        "Erro",
                        f"Nível '{novo_nivel}' não é válido!\nUse: {', '.join(niveis_validos)}",
                        parent=self.user_window,
                    )
        except Exception as e:
            messagebox.showerror(
                "Erro", f"Erro ao editar usuário: {str(e)}", parent=self.user_window
            )

    def _alterar_senha(self):
        """Abre diálogo para alterar senha"""
        usuario = self._selecionar_usuario()
        if usuario is not None:
            self._alterar_senha_usuario(usuario)

    def _alterar_senha_rapido(self, usuario):
        """Altera senha rapidamente"""
        self._alterar_senha_usuario(usuario)

    def _alterar_senha_usuario(self, usuario):
        """Altera senha de usuário específico com melhor tratamento de erros"""
        try:
            # Extrair nome do usuário de forma segura
            if isinstance(usuario, dict):
                usuario_nome = usuario.get("usuario", "usuário")
            else:
                usuario_nome = getattr(usuario, "usuario", "usuário")

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
                                "Biblioteca bcrypt não disponível!",
                                parent=self.user_window,
                            )
                            return

                        # Carregar arquivo
                        df = pd.read_csv(self.usuarios_path, sep=";")

                        # Verificar se o usuário existe
                        if usuario_nome in df["usuario"].values:
                            # Atualizar senha (campo correto é senha_hash)
                            df.loc[df["usuario"] == usuario_nome, "senha_hash"] = (
                                hash_senha
                            )

                            # Salvar
                            df.to_csv(self.usuarios_path, sep=";", index=False)

                            messagebox.showinfo(
                                "Sucesso",
                                f"Senha do usuário {usuario_nome} alterada com sucesso!",
                                parent=self.user_window,
                            )

                            if "registrar_log" in globals():
                                registrar_log(
                                    "UserManagement",
                                    f"Senha do usuário {usuario_nome} alterada por {self.usuario_logado}",
                                    "INFO",
                                )

                            self._atualizar_lista()
                        else:
                            messagebox.showerror(
                                "Erro",
                                f"Usuário {usuario_nome} não encontrado!",
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
                        "Aviso", "As senhas não coincidem!", parent=self.user_window
                    )
            else:
                messagebox.showwarning(
                    "Aviso", "Senha não pode estar vazia!", parent=self.user_window
                )
        except Exception as e:
            messagebox.showerror(
                "Erro", f"Erro ao alterar senha: {str(e)}", parent=self.user_window
            )

    def _remover_usuario(self):
        """Remove usuário do sistema"""
        usuario = self._selecionar_usuario()
        if usuario is not None:
            self._remover_usuario_confirmado(usuario)

    def _remover_usuario_rapido(self, usuario):
        """Remove usuário rapidamente com confirmação"""
        self._remover_usuario_confirmado(usuario)

    def _remover_usuario_confirmado(self, usuario):
        """Remove usuário com confirmação"""
        if usuario["usuario"] == self.usuario_logado:
            messagebox.showwarning(
                "Aviso", "Você não pode remover a si mesmo!", parent=self.user_window
            )
            return

        if messagebox.askyesno(
            "Confirmar Remoção",
            f"Tem certeza que deseja remover o usuário '{usuario['usuario']}'?\n\nEsta ação não pode ser desfeita!",
            parent=self.user_window,
        ):
            try:
                # Carregar arquivo
                df = pd.read_csv(self.usuarios_path)

                # Remover usuário
                df = df[df["usuario"] != usuario["usuario"]]

                # Salvar
                df.to_csv(self.usuarios_path, index=False)

                messagebox.showinfo(
                    "Sucesso",
                    f"Usuário {usuario['usuario']} removido com sucesso!",
                    parent=self.user_window,
                )
                registrar_log(
                    "UserManagement",
                    f"Usuário {usuario['usuario']} removido por {self.usuario_logado}",
                    "WARNING",
                )
                self._atualizar_lista()

            except Exception as e:
                messagebox.showerror(
                    "Erro",
                    f"Erro ao remover usuário: {str(e)}",
                    parent=self.user_window,
                )

    def _buscar_usuario(self):
        """Busca usuário por nome"""
        nome_busca = simpledialog.askstring(
            "Buscar Usuário",
            "Digite o nome do usuário para buscar:",
            parent=self.user_window,
        )

        if nome_busca and nome_busca.strip():
            try:
                if not os.path.exists(self.usuarios_path):
                    messagebox.showerror(
                        "Erro",
                        "Arquivo de credenciais não encontrado!",
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

                # Buscar usuários que contenham o nome
                usuarios_encontrados = df[
                    df["usuario"].str.lower().str.contains(nome_busca, na=False)
                ]

                if not usuarios_encontrados.empty:
                    # Mostrar resultados da busca
                    resultado = f"🔍 Resultados da busca por '{nome_busca}':\n\n"

                    for _, usuario in usuarios_encontrados.iterrows():
                        nivel = usuario.get("nivel_acesso", "USER")
                        resultado += f"👤 {usuario['usuario']} | 🔑 {nivel}\n"

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

                    # Botão fechar
                    ctk.CTkButton(
                        resultado_window,
                        text="Fechar",
                        command=resultado_window.destroy,
                    ).pack(pady=10)

                else:
                    messagebox.showinfo(
                        "Busca",
                        f"Nenhum usuário encontrado com o nome '{nome_busca}'.",
                        parent=self.user_window,
                    )

            except Exception as e:
                messagebox.showerror(
                    "Erro", f"Erro durante a busca: {str(e)}", parent=self.user_window
                )

    def _sair_para_menu_principal(self):
        """Fecha a janela de gerenciamento de usuários e volta ao menu principal"""
        self.user_window.destroy()
        self.main_window.deiconify()  # Volta a mostrar a janela principal

    def _atualizar_lista(self):
        """Atualiza lista de usuários"""
        try:
            # Encontrar o scrollable frame principal e recarregar apenas ele
            for widget in self.user_window.winfo_children():
                if hasattr(widget, "winfo_name") and "scrollable_frame" in str(
                    widget.__class__
                ):
                    # Limpar apenas o conteúdo do scrollable frame
                    for child in widget.winfo_children():
                        child.destroy()

                    # Recarregar usuários
                    self._carregar_usuarios(widget)
                    break
            else:
                # Se não encontrou scrollable frame, recriar interface completa
                self._criar_interface()

            messagebox.showinfo(
                "Atualizar", "Lista de usuários atualizada!", parent=self.user_window
            )

        except Exception as e:
            messagebox.showerror(
                "Erro", f"Erro ao atualizar lista: {str(e)}", parent=self.user_window
            )

    def _selecionar_usuario(self):
        """Permite seleção de usuário da lista"""
        try:
            if not os.path.exists(self.usuarios_path):
                messagebox.showerror(
                    "Erro",
                    "Arquivo de credenciais não encontrado!",
                    parent=self.user_window,
                )
                return None

            # Tentar ler com separador correto
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
                    "Aviso", "Nenhum usuário cadastrado!", parent=self.user_window
                )
                return None

            # Verificar se a coluna usuario existe
            if "usuario" not in df.columns:
                messagebox.showerror(
                    "Erro",
                    "Coluna 'usuario' não encontrada no arquivo de credenciais!",
                    parent=self.user_window,
                )
                return None

            # Criar lista de opções mais limpa
            usuarios_opcoes = df["usuario"].dropna().tolist()
            if not usuarios_opcoes:
                messagebox.showwarning(
                    "Aviso",
                    "Nenhum usuário válido encontrado!",
                    parent=self.user_window,
                )
                return None

            lista_usuarios = "\n".join(
                [f"{i+1}. {u}" for i, u in enumerate(usuarios_opcoes)]
            )

            # Diálogo de seleção melhorado
            nome_usuario = simpledialog.askstring(
                "Selecionar Usuário",
                f"Usuários disponíveis:\n\n{lista_usuarios}\n\nDigite o nome exato do usuário:",
                parent=self.user_window,
            )

            if nome_usuario and nome_usuario.strip():
                nome_usuario = nome_usuario.strip()

                # Buscar usuário (case-insensitive)
                usuario_encontrado = None
                for idx, row in df.iterrows():
                    if str(row["usuario"]).strip().lower() == nome_usuario.lower():
                        usuario_encontrado = row
                        break

                if usuario_encontrado is not None:
                    return usuario_encontrado
                else:
                    messagebox.showwarning(
                        "Aviso",
                        f"Usuário '{nome_usuario}' não encontrado!\n\nVerifique a ortografia.",
                        parent=self.user_window,
                    )
                    return None
            return None

        except Exception as e:
            messagebox.showerror(
                "Erro", f"Erro ao selecionar usuário: {str(e)}", parent=self.user_window
            )
            return None

    def _adicionar_usuario_simples(self):
        """Método simplificado para adicionar usuário (fallback)"""
        try:
            username = simpledialog.askstring(
                "Adicionar Usuário", "Nome do usuário:", parent=self.user_window
            )
            if not username or not username.strip():
                return

            password = simpledialog.askstring(
                "Adicionar Usuário", "Senha:", show="*", parent=self.user_window
            )
            if not password or len(password.strip()) < 6:
                messagebox.showwarning(
                    "Aviso",
                    "Senha deve ter pelo menos 6 caracteres!",
                    parent=self.user_window,
                )
                return

            nivel = simpledialog.askstring(
                "Adicionar Usuário",
                "Nível (USER/ADMIN/OPERATOR):",
                initialvalue="USER",
                parent=self.user_window,
            )
            if not nivel:
                nivel = "USER"

            self._salvar_usuario(username.strip(), password.strip(), nivel.strip())
            self._atualizar_lista()

        except Exception as e:
            messagebox.showerror(
                "Erro", f"Erro ao adicionar usuário: {str(e)}", parent=self.user_window
            )

    def _salvar_usuario(self, username: str, password: str, nivel: str):
        """Salva novo usuário no sistema"""
        try:
            # Validações
            if not username or not password or not nivel:
                messagebox.showerror(
                    "Erro", "Todos os campos são obrigatórios!", parent=self.user_window
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

            # Criar diretório banco se não existir
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
                        # Se falhar, tentar com vírgula
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

                    # Mapear colunas existentes para o padrão esperado
                    if (
                        "senha_hash" in colunas_encontradas
                        and "senha" not in colunas_encontradas
                    ):
                        df = df.rename(columns={"senha_hash": "senha"})

                    # Adicionar coluna nivel_acesso se não existir
                    if "nivel_acesso" not in colunas_encontradas:
                        df["nivel_acesso"] = "USER"  # Padrão

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

            # Verificar se usuário já existe
            if username in df["usuario"].values:
                messagebox.showwarning(
                    "Aviso", f"Usuário '{username}' já existe!", parent=self.user_window
                )
                return

            # Adicionar novo usuário
            novo_usuario = {
                "usuario": username,
                "senha_hash": hash_senha,
                "nivel_acesso": nivel.upper(),  # Padronizar para maiúsculo
            }

            try:
                df = pd.concat([df, pd.DataFrame([novo_usuario])], ignore_index=True)
                # Salvar com separador ponto-e-vírgula para compatibilidade
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
                f"Usuário '{username}' criado com sucesso!\n\nNível: {nivel.upper()}",
                parent=self.user_window,
            )
            registrar_log(
                "UserManagement",
                f"Usuário {username} criado por {self.usuario_logado}",
                "INFO",
            )

        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro inesperado ao salvar usuário: {str(e)}",
                parent=self.user_window,
            )

    def _mostrar_mensagem_erro(self, parent, mensagem: str):
        """Exibe mensagem de erro"""
        ctk.CTkLabel(
            parent, text=f"❌ {mensagem}", text_color="red", font=ctk.CTkFont(size=14)
        ).pack(pady=20)

    def _mostrar_mensagem_info(self, parent, mensagem: str):
        """Exibe mensagem informativa"""
        ctk.CTkLabel(
            parent, text=f"ℹ️ {mensagem}", text_color="blue", font=ctk.CTkFont(size=14)
        ).pack(pady=20)

    def _fechar_janela(self):
        """Fecha a janela de gerenciamento corretamente"""
        try:
            # Liberar grab se estiver ativo
            if hasattr(self, "user_window") and self.user_window.winfo_exists():
                try:
                    self.user_window.grab_release()
                    # Forçar o release de qualquer grab ativo
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
    """Diálogo para adicionar novo usuário"""

    def __init__(self, parent):
        self.result = None

        # Janela de diálogo
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("➕ Adicionar Novo Usuário")
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
        """Cria interface do diálogo"""
        # Frame principal
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title_label = ctk.CTkLabel(
            main_frame,
            text="➕ Adicionar Novo Usuário",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        title_label.pack(pady=(20, 30))

        # Campo nome de usuário
        username_frame = ctk.CTkFrame(main_frame)
        username_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(username_frame, text="Nome de Usuário:").pack(
            anchor="w", padx=10, pady=(10, 5)
        )
        self.username_entry = ctk.CTkEntry(
            username_frame, placeholder_text="Digite o nome do usuário"
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

        # Campo nível de acesso
        level_frame = ctk.CTkFrame(main_frame)
        level_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(level_frame, text="Nível de Acesso:").pack(
            anchor="w", padx=10, pady=(10, 5)
        )
        self.level_combo = ctk.CTkComboBox(
            level_frame, values=["USER", "ADMIN", "OPERATOR"], state="readonly"
        )
        self.level_combo.set("USER")
        self.level_combo.pack(fill="x", padx=10, pady=(0, 10))

        # Botões
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(
            button_frame, text="Cancelar", command=self._cancelar, width=100
        ).pack(side="right", padx=(10, 0))

        ctk.CTkButton(
            button_frame, text="Criar Usuário", command=self._criar_usuario, width=100
        ).pack(side="right")

    def _criar_usuario(self):
        """Valida e cria o usuário"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        level = self.level_combo.get()

        # Validações
        if not username:
            messagebox.showwarning(
                "Aviso", "Nome de usuário é obrigatório!", parent=self.dialog
            )
            return

        if not password:
            messagebox.showwarning("Aviso", "Senha é obrigatória!", parent=self.dialog)
            return

        if password != confirm_password:
            messagebox.showwarning(
                "Aviso", "As senhas não coincidem!", parent=self.dialog
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
        """Cancela a operação"""
        self.dialog.destroy()

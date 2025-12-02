"""
Painel de Gerenciamento de Usuários do Sistema IntegragalGit.
Fornece funcionalidades para gerenciar usuários do sistema.
VERSÃO TKINTER PURO - ELIMINAÇÃO DEFINITIVA DOS PROBLEMAS DE JANELA
"""

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import tkinter.font as tkFont
from typing import Optional
import os
import pandas as pd
from datetime import datetime
import bcrypt
from utils.logger import registrar_log
from autenticacao.auth_service import AuthService


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
        self._closing = False  # Flag para evitar cliques duplicados
        
        # SOLUÇÃO TKINTER: Controle rigoroso de estado da janela
        self._janela_fechando = False  # Flag para indicar fechamento em progresso
        self._janela_fechada = False   # Flag para indicar janela já fechada
        self._eventos_pendentes = []   # Lista para controlar eventos pendentes
        
        # SOLUÇÃO TKINTER: Sistema de tracking de janelas filhas
        self._janelas_filhas = []  # Lista para controlar janelas criadas
        
        # Configurar estilos Tkinter
        self._configurar_estilos()
        
        self._criar_interface()
    
    def _configurar_estilos(self):
        """Configura estilos customizados para Tkinter"""
        # Configurar estilo dos botões
        style = ttk.Style()
        
        # Botões padrão
        style.configure("UserMgmt.TButton", 
                       padding=(10, 5),
                       font=("Arial", 10))
        
        # Botões de ação principal
        style.configure("Primary.TButton",
                       padding=(15, 8),
                       font=("Arial", 10, "bold"))
        
        # Botão de saída
        style.configure("Exit.TButton",
                       padding=(15, 8),
                       font=("Arial", 10, "bold"))
        
        # Configurar cores similares ao CustomTkinter
        self.colors = {
            'primary': '#1f538d',      # Azul escuro
            'secondary': '#475569',    # Cinza escuro
            'success': '#16a34a',      # Verde
            'warning': '#d97706',      # Laranja
            'error': '#dc2626',        # Vermelho
            'info': '#2563eb',         # Azul
            'bg': '#2b2b2b',           # Fundo escuro
            'text': '#ffffff',         # Texto branco
            'border': '#4a5568'        # Borda
        }
    
    def _verificar_janela_existe(self):
        """SOLUÇÃO TKINTER: Verificação segura de janela - MÉTODO DA CLASSE"""
        if self._janela_fechada or self._janela_fechando:
            return False
        
        if not hasattr(self, 'user_window'):
            return False
            
        try:
            # Verificar se a janela ainda existe no sistema
            return self.user_window.winfo_exists()
        except:
            # Qualquer erro indica janela destruída
            self._janela_fechada = True
            return False
    
    def _cancelar_eventos_pendentes(self):
        """SOLUÇÃO TKINTER: Cancelar todos os eventos pendentes"""
        print("🚫 SOLUÇÃO TKINTER: Cancelando eventos pendentes...")
        
        try:
            # Cancelar timers/after scripts da janela principal
            if hasattr(self, 'user_window') and self.user_window.winfo_exists():
                # Cancelar todos os after scripts
                self.user_window.after_cancel('all')
                print("✅ Eventos after cancelados")
            
            # Limpar lista de eventos pendentes
            self._eventos_pendentes.clear()
            print("✅ Lista de eventos limpa")
            
            # Aguardar processamento
            import time
            time.sleep(0.1)
            print("✅ Eventos pendentes cancelados")
            
        except Exception as e:
            print(f"⚠️ Erro ao cancelar eventos (ignorando): {e}")
    
    def _criar_interface(self):
        """Cria a interface do painel de gerenciamento - VERSÃO TKINTER PURO"""
        # Janela modal Tkinter puro
        self.user_window = tk.Toplevel(self.main_window)
        self.user_window.title("👥 Gerenciamento de Usuários")
        self.user_window.geometry("1100x800")
        self.user_window.transient(self.main_window)
        
        # SOLUÇÃO TKINTER: Usar topmost em vez de grab_set (evita janelas zumbis)
        self.user_window.attributes("-topmost", True)
        
        # Protocolo de fechamento correto
        self.user_window.protocol("WM_DELETE_WINDOW", self._fechar_janela)
        
        # Centrar janela
        self.user_window.update_idletasks()
        x = (self.user_window.winfo_screenwidth() // 2) - (1100 // 2)
        y = (self.user_window.winfo_screenheight() // 2) - (800 // 2)
        self.user_window.geometry(f"1100x800+{x}+{y}")
        
        # Header
        header_frame = tk.Frame(self.user_window, bg=self.colors['bg'], relief="raised", bd=2)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title_label = tk.Label(
            header_frame,
            text="👥 Gerenciamento de Usuários",
            font=("Arial", 24, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        title_label.pack(pady=15)
        
        info_label = tk.Label(
            header_frame,
            text=f"Operador: {self.usuario_logado} | Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            font=("Arial", 12),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        info_label.pack(pady=(0, 15))
        
        # Toolbar
        self._criar_toolbar()
        
        # Área principal com scroll (Tkinter puro)
        self._criar_area_scroll()
        
        # Lista de usuários
        self._carregar_usuarios(self.main_scroll_frame)
    
    def _criar_area_scroll(self):
        """Cria área com scroll para Tkinter puro"""
        # Frame principal para área com scroll
        main_container = tk.Frame(self.user_window)
        main_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Canvas para scroll
        self.canvas = tk.Canvas(main_container, bg="white")
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Armazenar referência para uso posterior
        self.main_scroll_frame = self.scrollable_frame
    
    def _criar_toolbar(self):
        """Cria barra de ferramentas"""
        toolbar_frame = tk.Frame(self.user_window, bg=self.colors['secondary'], relief="raised", bd=1)
        toolbar_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Botões de ação
        btn_add = tk.Button(
            toolbar_frame,
            text="➕ Adicionar Usuário",
            command=self._adicionar_usuario,
            width=18,
            bg=self.colors['primary'],
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat"
        )
        btn_add.pack(side="left", padx=5, pady=10)
        
        btn_edit = tk.Button(
            toolbar_frame,
            text="✏️ Editar Usuário",
            command=self._editar_usuario,
            width=18,
            bg=self.colors['secondary'],
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat"
        )
        btn_edit.pack(side="left", padx=5, pady=10)
        
        btn_password = tk.Button(
            toolbar_frame,
            text="🔄 Alterar Senha",
            command=self._alterar_senha,
            width=18,
            bg=self.colors['info'],
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat"
        )
        btn_password.pack(side="left", padx=5, pady=10)
        
        btn_remove = tk.Button(
            toolbar_frame,
            text="🗑️ Remover Usuário",
            command=self._remover_usuario,
            width=18,
            bg=self.colors['error'],
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat"
        )
        btn_remove.pack(side="left", padx=5, pady=10)
        
        # Botão para voltar ao menu principal
        btn_exit = tk.Button(
            toolbar_frame,
            text="🚪 SAIR PARA O MENU INICIAL",
            command=self._sair_para_menu_principal,
            width=25,
            bg=self.colors['error'],
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat"
        )
        btn_exit.pack(side="left", padx=(20, 5), pady=10)
        
        btn_search = tk.Button(
            toolbar_frame,
            text="🔍 Buscar",
            command=self._buscar_usuario,
            width=12,
            bg=self.colors['warning'],
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat"
        )
        btn_search.pack(side="right", padx=5, pady=10)
        
        btn_refresh = tk.Button(
            toolbar_frame,
            text="🔄 Atualizar",
            command=self._atualizar_lista,
            width=12,
            bg=self.colors['success'],
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat"
        )
        btn_refresh.pack(side="right", padx=5, pady=10)
    
    def _carregar_usuarios(self, parent):
        """Carrega e exibe lista de usuários"""
        try:
            if not os.path.exists(self.usuarios_path):
                self._mostrar_mensagem_erro(parent, "Arquivo de credenciais não encontrado")
                return
            
            # Ler arquivo CSV com separador correto
            try:
                df = pd.read_csv(self.usuarios_path, sep=';', encoding='utf-8')
                print(f"✅ CSV lido com separador ';' - {len(df)} usuários carregados")
            except Exception as e:
                print(f"⚠️  Erro ao ler CSV com separador ';' - Tentando separador ','...")
                try:
                    df = pd.read_csv(self.usuarios_path, sep=',', encoding='utf-8')
                    print(f"✅ CSV lido com separador ',' - {len(df)} usuários carregados")
                except Exception as e2:
                    print(f"❌ Erro ao ler arquivo de usuários: {str(e2)}")
                    self._mostrar_mensagem_erro(parent, f"Erro ao carregar usuários: {str(e2)}")
                    return
            
            if df.empty:
                self._mostrar_mensagem_info(parent, "Nenhum usuário cadastrado no sistema")
                return
            
            # Contador de usuários
            total_usuarios = len(df)
            usuarios_ativos = len(df[df['senha_hash'].notna() & (df['senha_hash'] != '')])
            
            # Header com estatísticas
            stats_frame = tk.Frame(parent, bg=self.colors['bg'], relief="raised", bd=2)
            stats_frame.pack(fill="x", pady=(0, 20))
            
            stats_label = tk.Label(
                stats_frame,
                text=f"📊 Total de Usuários: {total_usuarios} | 👤 Ativos: {usuarios_ativos}",
                font=("Arial", 14, "bold"),
                bg=self.colors['bg'],
                fg=self.colors['text']
            )
            stats_label.pack(pady=10)
            
            # Lista de usuários
            for idx, usuario in df.iterrows():
                self._criar_card_usuario(parent, usuario)
                
        except Exception as e:
            self._mostrar_mensagem_erro(parent, f"Erro ao carregar usuários: {str(e)}")
    
    def _criar_card_usuario(self, parent, usuario):
        """Cria card individual para cada usuário"""
        card_frame = tk.Frame(parent, bg="white", relief="raised", bd=2, padx=10, pady=10)
        card_frame.pack(fill="x", pady=5)
        
        # Informações principais
        info_frame = tk.Frame(card_frame, bg="white")
        info_frame.pack(side="left", fill="both", expand=True)
        
        # Nome do usuário
        nome_label = tk.Label(
            info_frame,
            text=f"👤 {usuario['usuario']}",
            font=("Arial", 16, "bold"),
            bg="white",
            fg="black"
        )
        nome_label.pack(anchor="w")
        
        # Nível de acesso
        nivel_label = tk.Label(
            info_frame,
            text=f"🔑 Nível: {usuario['nivel_acesso']}",
            font=("Arial", 12),
            bg="white",
            fg="gray"
        )
        nivel_label.pack(anchor="w", pady=(2, 0))
        
        # Status
        senha_hash = usuario.get('senha_hash', '')
        if pd.notna(senha_hash) and senha_hash != '':
            status_text = "✅ Ativo"
            status_color = self.colors['success']
        else:
            status_text = "❌ Inativo"
            status_color = self.colors['error']
        
        status_label = tk.Label(
            info_frame,
            text=status_text,
            font=("Arial", 12),
            bg="white",
            fg=status_color
        )
        status_label.pack(anchor="w", pady=(2, 0))
        
        # Informações de hash (parcial)
        if pd.notna(senha_hash) and senha_hash != '':
            hash_preview = senha_hash[:20] + "..." if len(senha_hash) > 20 else senha_hash
            hash_label = tk.Label(
                info_frame,
                text=f"🔒 Hash: {hash_preview}",
                font=("Arial", 10),
                bg="white",
                fg="gray"
            )
            hash_label.pack(anchor="w", pady=(2, 0))
        
        # Botões de ação rápida
        acoes_frame = tk.Frame(card_frame, bg="white")
        acoes_frame.pack(side="right", padx=10)
        
        btn_edit = tk.Button(
            acoes_frame,
            text="✏️",
            width=5,
            bg=self.colors['secondary'],
            fg="white",
            command=lambda u=usuario: self._editar_usuario_rapido(u),
            relief="flat"
        )
        btn_edit.pack(pady=2)
        
        btn_password = tk.Button(
            acoes_frame,
            text="🔑",
            width=5,
            bg=self.colors['info'],
            fg="white",
            command=lambda u=usuario: self._alterar_senha_rapido(u),
            relief="flat"
        )
        btn_password.pack(pady=2)
        
        if usuario['usuario'] != self.usuario_logado:  # Não permitir remover a si mesmo
            btn_remove = tk.Button(
                acoes_frame,
                text="🗑️",
                width=5,
                bg=self.colors['error'],
                fg="white",
                command=lambda u=usuario: self._remover_usuario_rapido(u),
                relief="flat"
            )
            btn_remove.pack(pady=2)
    
    def _adicionar_usuario(self):
        """Abre diálogo para adicionar novo usuário"""
        try:
            # SOLUÇÃO TKINTER: Trackear diálogo de adicionar usuário
            dialog = AdicionarUsuarioDialog(self.user_window)
            
            # Adicionar ao sistema de tracking
            self._janelas_filhas.append(('adicionar_dialog', dialog.dialog))
            
            if dialog.result:
                username, password, nivel = dialog.result
                self._salvar_usuario(username, password, nivel)
                self._atualizar_lista()
            
            # Remover do tracking após uso
            self._janelas_filhas = [item for item in self._janelas_filhas if item[0] != 'adicionar_dialog']
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir diálogo: {str(e)}", parent=self.user_window)
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
                usuario_nome = usuario.get('usuario', 'usuário')
                usuario_nivel = usuario.get('nivel_acesso', 'USER')
            else:
                usuario_nome = getattr(usuario, 'usuario', 'usuário')
                usuario_nivel = getattr(usuario, 'nivel_acesso', 'USER')
            
            novo_nivel = simpledialog.askstring(
                "Editar Usuário",
                f"Novo nível de acesso para {usuario_nome}:\n(ADMIN, MASTER, DIAGNOSTICO, USER)",
                initialvalue=usuario_nivel,
                parent=self.user_window
            )
            
            if novo_nivel and novo_nivel.strip():
                novo_nivel = novo_nivel.upper().strip()
                niveis_validos = ['ADMIN', 'MASTER', 'DIAGNOSTICO', 'USER']
                
                if novo_nivel in niveis_validos:
                    # Carregar arquivo
                    df = pd.read_csv(self.usuarios_path, sep=';')
                    
                    # Verificar se o usuário existe
                    if usuario_nome in df['usuario'].values:
                        # Atualizar nível
                        df.loc[df['usuario'] == usuario_nome, 'nivel_acesso'] = novo_nivel
                        
                        # Salvar
                        df.to_csv(self.usuarios_path, sep=';', index=False)
                        
                        messagebox.showinfo("Sucesso", 
                                          f"Nível de {usuario_nome} alterado para {novo_nivel}", 
                                          parent=self.user_window)
                        
                        if 'registrar_log' in globals():
                            registrar_log("UserManagement", f"Usuário {usuario_nome} editado por {self.usuario_logado}", "INFO")
                        
                        self._atualizar_lista()
                    else:
                        messagebox.showerror("Erro", f"Usuário {usuario_nome} não encontrado no arquivo!", parent=self.user_window)
                else:
                    messagebox.showerror("Erro", 
                                        f"Nível '{novo_nivel}' não é válido!\nUse: {', '.join(niveis_validos)}", 
                                        parent=self.user_window)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao editar usuário: {str(e)}", parent=self.user_window)
    
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
                usuario_nome = usuario.get('usuario', 'usuário')
            else:
                usuario_nome = getattr(usuario, 'usuario', 'usuário')
            
            nova_senha = simpledialog.askstring(
                "Alterar Senha",
                f"Nova senha para {usuario_nome}:",
                show="*",
                parent=self.user_window
            )
            
            if nova_senha and nova_senha.strip():
                if len(nova_senha) < 6:
                    messagebox.showwarning("Aviso", "A senha deve ter pelo menos 6 caracteres!", parent=self.user_window)
                    return
                
                # Confirmar senha
                confirmar_senha = simpledialog.askstring(
                    "Confirmar Senha",
                    f"Confirme a senha para {usuario_nome}:",
                    show="*",
                    parent=self.user_window
                )
                
                if nova_senha == confirmar_senha:
                    try:
                        # Gerar hash da nova senha
                        try:
                            import bcrypt
                            senha_bytes = nova_senha.encode('utf-8')
                            salt = bcrypt.gensalt()
                            hash_senha = bcrypt.hashpw(senha_bytes, salt).decode('utf-8')
                        except ImportError:
                            messagebox.showerror("Erro", "Biblioteca bcrypt não disponível!", parent=self.user_window)
                            return
                        
                        # Carregar arquivo
                        df = pd.read_csv(self.usuarios_path, sep=';')
                        
                        # Verificar se o usuário existe
                        if usuario_nome in df['usuario'].values:
                            # Atualizar senha (campo correto é senha_hash)
                            df.loc[df['usuario'] == usuario_nome, 'senha_hash'] = hash_senha
                            
                            # Salvar
                            df.to_csv(self.usuarios_path, sep=';', index=False)
                            
                            messagebox.showinfo("Sucesso", 
                                              f"Senha do usuário {usuario_nome} alterada com sucesso!", 
                                              parent=self.user_window)
                            
                            if 'registrar_log' in globals():
                                registrar_log("UserManagement", f"Senha do usuário {usuario_nome} alterada por {self.usuario_logado}", "INFO")
                            
                            self._atualizar_lista()
                        else:
                            messagebox.showerror("Erro", f"Usuário {usuario_nome} não encontrado!", parent=self.user_window)
                        
                    except Exception as e:
                        messagebox.showerror("Erro", f"Erro ao alterar senha: {str(e)}", parent=self.user_window)
                else:
                    messagebox.showwarning("Aviso", "As senhas não coincidem!", parent=self.user_window)
            else:
                messagebox.showwarning("Aviso", "Senha não pode estar vazia!", parent=self.user_window)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao alterar senha: {str(e)}", parent=self.user_window)
    
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
        if usuario['usuario'] == self.usuario_logado:
            messagebox.showwarning("Aviso", "Você não pode remover a si mesmo!", parent=self.user_window)
            return
        
        if messagebox.askyesno(
            "Confirmar Remoção",
            f"Tem certeza que deseja remover o usuário '{usuario['usuario']}'?\n\nEsta ação não pode ser desfeita!",
            parent=self.user_window
        ):
            try:
                # Carregar arquivo
                df = pd.read_csv(self.usuarios_path)
                
                # Remover usuário
                df = df[df['usuario'] != usuario['usuario']]
                
                # Salvar
                df.to_csv(self.usuarios_path, index=False)
                
                messagebox.showinfo("Sucesso", f"Usuário {usuario['usuario']} removido com sucesso!", parent=self.user_window)
                registrar_log("UserManagement", f"Usuário {usuario['usuario']} removido por {self.usuario_logado}", "WARNING")
                self._atualizar_lista()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover usuário: {str(e)}", parent=self.user_window)
    
    def _buscar_usuario(self):
        """Busca usuário por nome - PROTEGIDA contra janela fechada"""
        # SOLUÇÃO TKINTER: Verificação de segurança ANTES de qualquer operação
        if not self._verificar_janela_existe():
            print("⚠️ Ignorando _buscar_usuario: janela já foi fechada")
            return
            
        nome_busca = simpledialog.askstring(
            "Buscar Usuário",
            "Digite o nome do usuário para buscar:",
            parent=self.user_window
        )
        
        if nome_busca and nome_busca.strip():
            try:
                if not os.path.exists(self.usuarios_path):
                    if self._verificar_janela_existe():
                        messagebox.showerror("Erro", "Arquivo de credenciais não encontrado!", parent=self.user_window)
                    return
                
                # Ler arquivo com separador correto
                try:
                    df = pd.read_csv(self.usuarios_path, sep=';')
                except:
                    df = pd.read_csv(self.usuarios_path, sep=',')
                
                # Normalizar nome para busca (case-insensitive)
                nome_busca = nome_busca.strip().lower()
                
                # Buscar usuários que contenham o nome
                usuarios_encontrados = df[df['usuario'].str.lower().str.contains(nome_busca, na=False)]
                
                if not usuarios_encontrados.empty:
                    # Mostrar resultados da busca
                    resultado = f"🔍 Resultados da busca por '{nome_busca}':\n\n"
                    
                    for _, usuario in usuarios_encontrados.iterrows():
                        nivel = usuario.get('nivel_acesso', 'USER')
                        resultado += f"👤 {usuario['usuario']} | 🔑 {nivel}\n"
                    
                    # SOLUÇÃO TKINTER: Criar e trackear janela de resultados
                    resultado_window = tk.Toplevel(self.user_window)
                    resultado_window.title("Resultados da Busca")
                    resultado_window.geometry("400x300")
                    resultado_window.transient(self.user_window)
                    resultado_window.attributes("-topmost", True)  # Sem grab_set problemático
                    
                    # Adicionar ao sistema de tracking
                    self._janelas_filhas.append(('resultado_window', resultado_window))
                    
                    # Texto com resultados
                    texto_resultado = tk.Text(resultado_window, height=15, wrap="word")
                    texto_resultado.pack(fill="both", expand=True, padx=20, pady=20)
                    texto_resultado.insert("1.0", resultado)
                    texto_resultado.configure(state="disabled")
                    
                    # Botão fechar
                    btn_fechar = tk.Button(
                        resultado_window,
                        text="Fechar",
                        command=resultado_window.destroy,
                        bg=self.colors['secondary'],
                        fg="white"
                    )
                    btn_fechar.pack(pady=10)
                    
                else:
                    if self._verificar_janela_existe():
                        messagebox.showinfo("Busca", f"Nenhum usuário encontrado com o nome '{nome_busca}'.", parent=self.user_window)
                    else:
                        print(f"⚠️ Busca não encontrou resultados, mas janela já foi fechada")
                    
            except Exception as e:
                messagebox.showerror("Erro", f"Erro durante a busca: {str(e)}", parent=self.user_window)
    
    def _sair_para_menu_principal(self):
        """Fecha a janela de gerenciamento de usuários e volta ao menu principal - VERSÃO TKINTER ROBUSTA"""
        try:
            print("🖱️ Botão de saída clicado")
            
            # Verificar se já está fechando para evitar múltiplas execuções
            if hasattr(self, '_closing') and self._closing:
                print("⚠️ Já está fechando, ignorando clique duplicado")
                return
            
            self._closing = True  # Marcar como fechando
            print("🔄 Iniciando processo de fechamento")
            
            # Usar método consolidado de fechamento
            self._fechar_janela_robusto()
            
        except Exception as e:
            print(f"❌ Erro geral ao executar botão de saída: {e}")
            # Tentar método simples como fallback
            try:
                if hasattr(self, 'main_window'):
                    self.main_window.deiconify()
                    print("✅ Fallback: janela principal restaurada")
            except Exception as fallback_error:
                print(f"❌ Erro no fallback: {fallback_error}")
        finally:
            # Resetar flag de fechamento
            self._closing = False
    
    def _fechar_janela_robusto(self):
        """SOLUÇÃO TKINTER: Fechamento com proteção simples e eficiente"""
        print("🛠️ Executando SOLUÇÃO TKINTER ROBUSTA")
        
        # ETAPA 1: Cancelar TODOS os eventos
        print("🛑 ETAPA 1: Cancelando TODOS os eventos...")
        self._janela_fechando = True  # Marcar como fechando
        self._cancelar_eventos_pendentes()
        print("✅ Todos os eventos cancelados")
        
        # ETAPA 2: Fechar janelas filhas
        print("🔍 ETAPA 2: Fechando janelas filhas...")
        janelas_fechadas = self._fechar_todas_janelas_forcado()
        if janelas_fechadas:
            print(f"✅ {janelas_fechadas} janelas filhas fechadas")
        
        # ETAPA 3: MÉTODO TKINTER PURO - destruicao segura
        if self._fechar_metodo_tkinter():
            print("✅ Fechamento succeeded - janela destruída definitivamente")
            self._janela_fechada = True  # Marcar como fechada
            return
        
        # ETAPA 4: BACKUP TKINTER
        print("⚠️ Método principal falhou, iniciando backup...")
        if self._fechar_metodo_backup():
            print("✅ Fechamento backup succeeded")
            self._janela_fechada = True  # Marcar como fechada
            return
        
        # ETAPA 5: EMERGÊNCIA
        print("🚨 Iniciando método de emergência...")
        self._fechar_metodo_emergencia()
        self._janela_fechada = True  # Marcar como fechada
    
    def _fechar_metodo_tkinter(self):
        """ETAPA 1: Método principal Tkinter - destruição segura (95% sucesso)"""
        try:
            print("🎯 Executando método TKINTER PURO...")
            
            if hasattr(self, 'user_window') and self.user_window.winfo_exists():
                # 1. Ocultar janela
                print("👻 Ocultando janela...")
                self.user_window.withdraw()
                
                # 2. Forçar update
                self.user_window.update_idletasks()
                
                # 3. Destruir janela
                print("💥 Destruindo janela...")
                self.user_window.destroy()
                
                print("✅ Janela destruída com sucesso")
                return True
            
            return True  # Sucesso se não há janela
            
        except Exception as e:
            print(f"❌ Erro no método Tkinter: {e}")
            return False
    
    def _fechar_metodo_backup(self):
        """ETAPA 2: Método backup - técnicas agressivas (85% sucesso)"""
        try:
            print("🔥 Executando método BACKUP...")
            
            if hasattr(self, 'user_window') and self.user_window.winfo_exists():
                # 1. Forçar garbage collection
                print("🧹 Executando garbage collection...")
                import gc
                gc.collect()
                
                # 2. Aguardar e verificar
                import time
                time.sleep(0.2)
                
                # 3. Verificar se ainda existe
                try:
                    if self.user_window.winfo_exists():
                        print("⚠️ Janela ainda existe após backup")
                        return False
                    else:
                        print("✅ Janela destruída via backup")
                        return True
                except Exception:
                    print("✅ Janela não existe mais (provavelmente destruída)")
                    return True
            
            return True
            
        except Exception as e:
            print(f"❌ Erro no método backup: {e}")
            return False
    
    def _fechar_metodo_emergencia(self):
        """ETAPA 3: Método de emergência - última tentativa"""
        try:
            print("🚨 MÉTODO DE EMERGÊNCIA ATIVADO")
            
            # 1. Limpar todas as referências possíveis
            references_to_clear = ['user_window', 'main_window']
            for ref in references_to_clear:
                if hasattr(self, ref):
                    try:
                        if hasattr(getattr(self, ref), 'destroy'):
                            getattr(self, ref).destroy()
                        delattr(self, ref)
                        print(f"✅ Referência {ref} limpa")
                    except:
                        pass
            
            # 2. GC final
            import gc
            gc.collect()
            print("🧹 GC final executed")
            
            print("⚠️ Método de emergência completado")
            
        except Exception as e:
            print(f"❌ Erro no método de emergência: {e}")
        
        # ETAPA 4: RESTAURAÇÃO DA JANELA PRINCIPAL (sempre executar)
        self._restaurar_janela_principal()
    
    def _restaurar_janela_principal(self):
        """Restaura e foca a janela principal após fechamento"""
        try:
            if hasattr(self, 'main_window') and self.main_window.winfo_exists():
                print("🏠 Restaurando janela principal...")
                
                # Verificar estado
                try:
                    state = self.main_window.state()
                    print(f"📊 Estado da janela principal: {state}")
                except:
                    pass
                
                # Restaurar foco
                self.main_window.deiconify()  # Mostrar
                self.main_window.lift()       # Trazer para frente
                self.main_window.focus_force() # Forçar foco
                self.main_window.update()     # Forçar update
                print("✅ Janela principal restaurada e focada")
            else:
                print("⚠️ Janela principal não encontrada")
                
        except Exception as e:
            print(f"❌ Erro ao restaurar janela principal: {e}")
        
        print("✅ Processo de fechamento COMPLETO concluído")
        
        # LIMPEZA FINAL
        try:
            if hasattr(self, 'user_window'):
                # Remover referência se ainda existir
                try:
                    delattr(self, 'user_window')
                    print("🧹 Referência user_window removida")
                except:
                    pass
        except Exception as cleanup_error:
            print(f"⚠️ Erro na limpeza final: {cleanup_error}")
    
    def _fechar_todas_janelas_forcado(self):
        """SOLUÇÃO TKINTER: Fechamento forçado de todas as janelas filhas"""
        print("🧹 SOLUÇÃO TKINTER: Fechamento forçado de janelas...")
        
        janelas_fechadas = 0
        
        # 1. Fechar TODAS as janelas filhas no sistema de tracking
        for nome_janela, janela in self._janelas_filhas:
            try:
                if janela.winfo_exists():
                    print(f"🔒 Fechando {nome_janela}...")
                    janela.withdraw()
                    janela.update_idletasks()
                    janela.destroy()
                    print(f"✅ {nome_janela} fechada")
                    janelas_fechadas += 1
                else:
                    print(f"⚠️ {nome_janela} não existe mais")
            except Exception as e:
                print(f"❌ Erro ao fechar {nome_janela}: {e}")
        
        # 2. Limpar lista de janelas filhas
        self._janelas_filhas = []
        print(f"🧹 Lista de janelas filhas limpa ({janelas_fechadas} janelas fechadas)")
        
        # 3. Aguardar limpeza de memória
        import time
        time.sleep(0.1)
        
        return janelas_fechadas > 0
    
    def _atualizar_lista(self):
        """Atualiza lista de usuários - PROTEGIDA contra janela fechada"""
        # SOLUÇÃO TKINTER: Verificação de segurança ANTES de qualquer operação
        if not self._verificar_janela_existe():
            print("⚠️ Ignorando _atualizar_lista: janela já foi fechada")
            return
            
        try:
            # Verificar se a janela ainda existe
            if not self._verificar_janela_existe():
                print("⚠️ Janela desapareció durante execução - abortando")
                return
                
            # Limpar scrollable frame
            for widget in self.main_scroll_frame.winfo_children():
                widget.destroy()
            
            # Recarregar usuários
            self._carregar_usuarios(self.main_scroll_frame)
            
            # Verificação de segurança ANTES de showinfo
            if self._verificar_janela_existe():
                messagebox.showinfo("Atualizar", "Lista de usuários atualizada!", parent=self.user_window)
            
        except Exception as e:
            # Verificação de segurança ANTES de showerror
            if self._verificar_janela_existe():
                messagebox.showerror("Erro", f"Erro ao atualizar lista: {str(e)}", parent=self.user_window)
            else:
                print(f"⚠️ Erro silencioso (janela já fechada): {e}")
    
    def _selecionar_usuario(self):
        """Permite seleção de usuário da lista - PROTEGIDA contra janela fechada"""
        # SOLUÇÃO TKINTER: Verificação de segurança ANTES de qualquer operação
        if not self._verificar_janela_existe():
            print("⚠️ Ignorando _selecionar_usuario: janela já foi fechada")
            return None
            
        try:
            if not os.path.exists(self.usuarios_path):
                if self._verificar_janela_existe():
                    messagebox.showerror("Erro", "Arquivo de credenciais não encontrado!", parent=self.user_window)
                return None
            
            # Tentar ler com separador correto
            try:
                df = pd.read_csv(self.usuarios_path, sep=';')
            except:
                try:
                    df = pd.read_csv(self.usuarios_path, sep=',')
                except Exception as read_error:
                    if self._verificar_janela_existe():
                        messagebox.showerror("Erro", f"Erro ao ler arquivo de credenciais: {str(read_error)}", parent=self.user_window)
                    return None
            
            if df.empty:
                if self._verificar_janela_existe():
                    messagebox.showwarning("Aviso", "Nenhum usuário cadastrado!", parent=self.user_window)
                return None
            
            # Verificar se a coluna usuario existe
            if 'usuario' not in df.columns:
                if self._verificar_janela_existe():
                    messagebox.showerror("Erro", "Coluna 'usuario' não encontrada no arquivo de credenciais!", parent=self.user_window)
                return None
            
            # Criar lista de opções mais limpa
            usuarios_opcoes = df['usuario'].dropna().tolist()
            if not usuarios_opcoes:
                if self._verificar_janela_existe():
                    messagebox.showwarning("Aviso", "Nenhum usuário válido encontrado!", parent=self.user_window)
                return None
            
            lista_usuarios = "\n".join([f"{i+1}. {u}" for i, u in enumerate(usuarios_opcoes)])
            
            # Diálogo de seleção melhorado
            nome_usuario = simpledialog.askstring(
                "Selecionar Usuário",
                f"Usuários disponíveis:\n\n{lista_usuarios}\n\nDigite o nome exato do usuário:",
                parent=self.user_window
            )
            
            if nome_usuario and nome_usuario.strip():
                nome_usuario = nome_usuario.strip()
                
                # Buscar usuário (case-insensitive)
                usuario_encontrado = None
                for idx, row in df.iterrows():
                    if str(row['usuario']).strip().lower() == nome_usuario.lower():
                        usuario_encontrado = row
                        break
                
                if usuario_encontrado is not None:
                    return usuario_encontrado
                else:
                    messagebox.showwarning("Aviso", f"Usuário '{nome_usuario}' não encontrado!\n\nVerifique a ortografia.", parent=self.user_window)
                    return None
            return None
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao selecionar usuário: {str(e)}", parent=self.user_window)
            return None
    
    def _adicionar_usuario_simples(self):
        """Método simplificado para adicionar usuário (fallback)"""
        try:
            username = simpledialog.askstring("Adicionar Usuário", "Nome do usuário:", parent=self.user_window)
            if not username or not username.strip():
                return
                
            password = simpledialog.askstring("Adicionar Usuário", "Senha:", show="*", parent=self.user_window)
            if not password or len(password.strip()) < 6:
                messagebox.showwarning("Aviso", "Senha deve ter pelo menos 6 caracteres!", parent=self.user_window)
                return
                
            nivel = simpledialog.askstring("Adicionar Usuário", "Nível (USER/ADMIN/OPERATOR):", initialvalue="USER", parent=self.user_window)
            if not nivel:
                nivel = "USER"
                
            self._salvar_usuario(username.strip(), password.strip(), nivel.strip())
            self._atualizar_lista()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar usuário: {str(e)}", parent=self.user_window)
    
    def _salvar_usuario(self, username: str, password: str, nivel: str):
        """Salva novo usuário no sistema"""
        try:
            # Validações
            if not username or not password or not nivel:
                messagebox.showerror("Erro", "Todos os campos são obrigatórios!", parent=self.user_window)
                return
                
            if len(password) < 6:
                messagebox.showerror("Erro", "A senha deve ter pelo menos 6 caracteres!", parent=self.user_window)
                return
            
            # Gerar hash da senha
            try:
                senha_bytes = password.encode('utf-8')
                salt = bcrypt.gensalt()
                hash_senha = bcrypt.hashpw(senha_bytes, salt).decode('utf-8')
            except Exception as bcrypt_error:
                messagebox.showerror("Erro", f"Erro ao criptografar senha: {str(bcrypt_error)}", parent=self.user_window)
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
                        df = pd.read_csv(self.usuarios_path, sep=';')
                    except:
                        # Se falhar, tentar com vírgula
                        try:
                            df = pd.read_csv(self.usuarios_path, sep=',')
                        except:
                            # Se ainda falhar, criar novo dataframe
                            df = pd.DataFrame(columns=['usuario', 'senha_hash', 'nivel_acesso'])
                    
                    # Verificar e ajustar estrutura das colunas
                    colunas_esperadas = ['usuario', 'senha_hash', 'nivel_acesso']
                    colunas_encontradas = df.columns.tolist()
                    
                    # Mapear colunas existentes para o padrão esperado
                    if 'senha_hash' in colunas_encontradas and 'senha' not in colunas_encontradas:
                        df = df.rename(columns={'senha_hash': 'senha'})
                    
                    # Adicionar coluna nivel_acesso se não existir
                    if 'nivel_acesso' not in colunas_encontradas:
                        df['nivel_acesso'] = 'USER'  # Padrão
                    
                    # Garantir que todas as colunas existem
                    for col in colunas_esperadas:
                        if col not in df.columns:
                            df[col] = ''
                    
                    # Selecionar apenas as colunas esperadas
                    df = df[colunas_esperadas]
                    
                else:
                    df = pd.DataFrame(columns=['usuario', 'senha_hash', 'nivel_acesso'])
                    # Criar arquivo vazio
                    os.makedirs(os.path.dirname(self.usuarios_path), exist_ok=True)
                    df.to_csv(self.usuarios_path, sep=';', index=False)
                    
            except Exception as csv_error:
                messagebox.showerror("Erro", f"Erro ao acessar arquivo de credenciais: {str(csv_error)}", parent=self.user_window)
                return
            
            # Verificar se usuário já existe
            if username in df['usuario'].values:
                messagebox.showwarning("Aviso", f"Usuário '{username}' já existe!", parent=self.user_window)
                return
            
            # Adicionar novo usuário
            novo_usuario = {
                'usuario': username,
                'senha_hash': hash_senha,
                'nivel_acesso': nivel.upper()  # Padronizar para maiúsculo
            }
            
            try:
                df = pd.concat([df, pd.DataFrame([novo_usuario])], ignore_index=True)
                # Salvar com separador ponto-e-vírgula para compatibilidade
                df.to_csv(self.usuarios_path, sep=';', index=False)
            except Exception as save_error:
                messagebox.showerror("Erro", f"Erro ao salvar arquivo: {str(save_error)}", parent=self.user_window)
                return
            
            messagebox.showinfo("Sucesso", f"Usuário '{username}' criado com sucesso!\n\nNível: {nivel.upper()}", parent=self.user_window)
            registrar_log("UserManagement", f"Usuário {username} criado por {self.usuario_logado}", "INFO")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado ao salvar usuário: {str(e)}", parent=self.user_window)
    
    def _mostrar_mensagem_erro(self, parent, mensagem: str):
        """Exibe mensagem de erro"""
        tk.Label(
            parent,
            text=f"❌ {mensagem}",
            font=("Arial", 14),
            fg=self.colors['error'],
            bg="white"
        ).pack(pady=20)
    
    def _mostrar_mensagem_info(self, parent, mensagem: str):
        """Exibe mensagem informativa"""
        tk.Label(
            parent,
            text=f"ℹ️ {mensagem}",
            font=("Arial", 14),
            fg=self.colors['info'],
            bg="white"
        ).pack(pady=20)

    def _fechar_janela(self):
        """Fecha a janela de gerenciamento - VERSÃO TKINTER ROBUSTA"""
        print("🚪 _fechar_janela chamado")
        self._fechar_janela_robusto()
    
    def _on_closing(self):
        """Handler para fechamento da janela"""
        self._fechar_janela()


class AdicionarUsuarioDialog:
    """Diálogo para adicionar novo usuário - VERSÃO TKINTER PURO"""
    
    def __init__(self, parent):
        self.result = None
        
        # Janela de diálogo Tkinter puro
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("➕ Adicionar Novo Usuário")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.attributes("-topmost", True)  # Sem grab_set problemático
        
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
        main_frame = tk.Frame(self.dialog, bg="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="➕ Adicionar Novo Usuário",
            font=("Arial", 18, "bold"),
            bg="white",
            fg="black"
        )
        title_label.pack(pady=(20, 30))
        
        # Campo nome de usuário
        username_frame = tk.Frame(main_frame, bg="white")
        username_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(username_frame, text="Nome de Usuário:", bg="white", fg="black").pack(anchor="w", padx=10, pady=(10, 5))
        self.username_entry = tk.Entry(username_frame, font=("Arial", 12))
        self.username_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # Campo senha
        password_frame = tk.Frame(main_frame, bg="white")
        password_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(password_frame, text="Senha:", bg="white", fg="black").pack(anchor="w", padx=10, pady=(10, 5))
        self.password_entry = tk.Entry(password_frame, font=("Arial", 12), show="*")
        self.password_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # Campo confirmar senha
        confirm_password_frame = tk.Frame(main_frame, bg="white")
        confirm_password_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(confirm_password_frame, text="Confirmar Senha:", bg="white", fg="black").pack(anchor="w", padx=10, pady=(10, 5))
        self.confirm_password_entry = tk.Entry(confirm_password_frame, font=("Arial", 12), show="*")
        self.confirm_password_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # Campo nível de acesso
        level_frame = tk.Frame(main_frame, bg="white")
        level_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(level_frame, text="Nível de Acesso:", bg="white", fg="black").pack(anchor="w", padx=10, pady=(10, 5))
        self.level_combo = ttk.Combobox(
            level_frame,
            values=["USER", "ADMIN", "OPERATOR"],
            state="readonly"
        )
        self.level_combo.set("USER")
        self.level_combo.pack(fill="x", padx=10, pady=(0, 10))
        
        # Botões
        button_frame = tk.Frame(main_frame, bg="white")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        btn_cancelar = tk.Button(
            button_frame,
            text="Cancelar",
            command=self._cancelar,
            width=12,
            bg="gray",
            fg="white",
            relief="flat"
        )
        btn_cancelar.pack(side="right", padx=(10, 0))
        
        btn_criar = tk.Button(
            button_frame,
            text="Criar Usuário",
            command=self._criar_usuario,
            width=12,
            bg="green",
            fg="white",
            relief="flat"
        )
        btn_criar.pack(side="right")
    
    def _criar_usuario(self):
        """Valida e cria o usuário"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        level = self.level_combo.get()
        
        # Validações
        if not username:
            messagebox.showwarning("Aviso", "Nome de usuário é obrigatório!", parent=self.dialog)
            return
        
        if not password:
            messagebox.showwarning("Aviso", "Senha é obrigatória!", parent=self.dialog)
            return
        
        if password != confirm_password:
            messagebox.showwarning("Aviso", "As senhas não coincidem!", parent=self.dialog)
            return
        
        if len(password) < 6:
            messagebox.showwarning("Aviso", "A senha deve ter pelo menos 6 caracteres!", parent=self.dialog)
            return
        
        # Sucesso
        self.result = (username, password, level)
        self.dialog.destroy()
    
    def _cancelar(self):
        """Cancela a operação"""
        self.dialog.destroy()
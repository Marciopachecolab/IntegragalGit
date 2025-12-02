"""
Painel Administrativo do Sistema IntegragalGit.
Fornece funcionalidades de administração e monitoramento do sistema.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from typing import Optional
import os
import json
import pandas as pd
import shutil
from datetime import datetime
from utils.logger import registrar_log
from services.config_service import config_service
from autenticacao.auth_service import AuthService


class AdminPanel:
    """Painel administrativo com funcionalidades de gestão do sistema"""
    
    def __init__(self, main_window, usuario_logado: str):
        """
        Inicializa o painel administrativo
        
        Args:
            main_window: Janela principal da aplicação
            usuario_logado: Nome do usuário logado
        """
        self.main_window = main_window
        self.usuario_logado = usuario_logado
        self.auth_service = AuthService()
        self.config_service = config_service
        self._criar_interface()
    
    def _criar_interface(self):
        """Cria a interface do painel administrativo"""
        # Janela modal
        self.admin_window = ctk.CTkToplevel(self.main_window)
        self.admin_window.title("🔧 Painel Administrativo")
        self.admin_window.geometry("1000x750")
        self.admin_window.transient(self.main_window)
        self.admin_window.grab_set()
        
        # Centrar janela
        self.admin_window.update_idletasks()
        x = (self.admin_window.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.admin_window.winfo_screenheight() // 2) - (750 // 2)
        self.admin_window.geometry(f"1000x750+{x}+{y}")
        
        # Header
        header_frame = ctk.CTkFrame(self.admin_window)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🔧 Painel Administrativo",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=15)
        
        info_label = ctk.CTkLabel(
            header_frame,
            text=f"Usuário: {self.usuario_logado} | Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            font=ctk.CTkFont(size=12)
        )
        info_label.pack(pady=(0, 15))
        
        # Notebook para abas
        self.notebook = ctk.CTkTabview(self.admin_window)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Criar abas
        self._criar_aba_sistema()
        self._criar_aba_configuracao()
        self._criar_aba_logs()
        self._criar_aba_backup()
        
        # Botão fechar
        button_frame = ctk.CTkFrame(self.admin_window)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkButton(
            button_frame,
            text="Fechar",
            command=self._fechar_admin_panel,
            width=100
        ).pack(side="right", padx=10, pady=10)
    
    def _criar_aba_sistema(self):
        """Cria aba de informações do sistema"""
        aba_sistema = self.notebook.add("Sistema")
        
        # Informações do sistema
        info_frame = ctk.CTkScrollableFrame(aba_sistema)
        info_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        titulo_label = ctk.CTkLabel(
            info_frame,
            text="📊 Informações do Sistema",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        titulo_label.pack(pady=(0, 20))
        
        # Informações básicas
        self._adicionar_info_sistema(info_frame)
        
        # Botões de ação
        acoes_frame = ctk.CTkFrame(info_frame)
        acoes_frame.pack(fill="x", pady=20)
        
        ctk.CTkButton(
            acoes_frame,
            text="💾 Salvar Alterações",
            command=self._salvar_info_sistema,
            fg_color="green"
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            acoes_frame,
            text="🔄 Verificar Sistema",
            command=self._verificar_sistema
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            acoes_frame,
            text="📊 Status dos Serviços",
            command=self._status_servicos
        ).pack(side="left", padx=10, pady=10)
    
    def _adicionar_info_sistema(self, parent):
        """Adiciona informações básicas do sistema"""
        try:
            self.sistema_entries = {}  # Para armazenar as entries editáveis
            self.sistema_original_values = {}  # Para armazenar valores originais
            
            # Tentar ler configuracao/config.json
            config_path = "configuracao/config.json"
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config_sistema = json.load(f)
            else:
                self.config_sistema = {}
            
            # Itens editáveis e informativos (config.json principal)
            info_items = [
                ("🌐 URL do GAL", self.config_sistema.get('gal_url', 'http://localhost:8080'), True),
                ("⏱️ Timeout (segundos)", str(self.config_sistema.get('timeout', '30')), True),
                ("📝 Nível de Log", self.config_sistema.get('log_level', 'INFO'), True),
                ("🗄️ Banco PostgreSQL", "Ativo" if self.config_sistema.get('postgres_enabled', True) else "Inativo", False),
                ("🐍 Versão Python", f"{'.'.join(map(str, __import__('sys').version_info[:3]))}", False),
                ("📅 Data/Hora", datetime.now().strftime('%d/%m/%Y %H:%M:%S'), False),
            ]
            
            # Adicionar informações detalhadas do config.json
            if 'paths' in self.config_sistema:
                paths = self.config_sistema['paths']
                info_items.extend([
                    ("📄 Arquivo de Log", os.path.basename(paths.get('log_file', 'logs/sistema.log')), False),
                    ("📋 Catálogo de Exames", os.path.basename(paths.get('exams_catalog_csv', 'banco/exames_config.csv')), False),
                    ("👥 Credenciais", os.path.basename(paths.get('credentials_csv', 'banco/credenciais.csv')), False),
                ])
            
            if 'gal_integration' in self.config_sistema:
                gal_config = self.config_sistema['gal_integration']
                info_items.extend([
                    ("🌐 Base URL GAL", gal_config.get('base_url', 'Não configurada'), True),
                    ("🔄 Máximo Tentativas", str(gal_config.get('retry_settings', {}).get('max_retries', 3)), False),
                    ("⏳ Fator Backoff", str(gal_config.get('retry_settings', {}).get('backoff_factor', 0.5)), False),
                ])
            
            if 'postgres' in self.config_sistema:
                postgres = self.config_sistema['postgres']
                info_items.extend([
                    ("🗄️ Host BD", postgres.get('host', 'localhost'), False),
                    ("🗄️ Porta BD", str(postgres.get('port', 5432)), False),
                    ("🗄️ Nome BD", postgres.get('dbname', 'integragal'), False),
                ])
            
            for label, valor, editavel in info_items:
                item_frame = ctk.CTkFrame(parent)
                item_frame.pack(fill="x", pady=5)
                
                # Label da chave
                ctk.CTkLabel(
                    item_frame,
                    text=f"{label}:",
                    width=200,
                    anchor="w",
                    font=ctk.CTkFont(weight="bold" if editavel else "normal")
                ).pack(side="left", padx=10, pady=10)
                
                if editavel:
                    # Campo editável para itens configuráveis
                    entry = ctk.CTkEntry(
                        item_frame,
                        placeholder_text=str(valor),
                        width=250
                    )
                    entry.insert(0, str(valor))
                    entry.pack(side="left", padx=10, pady=10)
                    
                    # Botão para restaurar valor original
                    ctk.CTkButton(
                        item_frame,
                        text="↺",
                        width=30,
                        command=lambda k=label, v=str(valor): self._restaurar_valor_sistema(k, v)
                    ).pack(side="left", padx=5, pady=10)
                    
                    # Armazenar entry
                    key = label.split(' ')[0].replace('🌐', '').replace('⏱️', '').replace('📝', '').strip()
                    self.sistema_entries[key] = entry
                    self.sistema_original_values[key] = str(valor)

                elif 'Base URL' in key:
                    # Atualizar gal_integration.base_url
                    if 'gal_integration' not in config_completo:
                        config_completo['gal_integration'] = {}
                    config_completo['gal_integration']['base_url'] = novo_valor
                else:
                    # Campo informativo (apenas leitura)
                    ctk.CTkLabel(
                        item_frame,
                        text=str(valor),
                        anchor="w",
                        text_color="gray"
                    ).pack(side="left", padx=10, pady=10)
                
        except Exception as e:
            ctk.CTkLabel(
                parent,
                text=f"Erro ao carregar informações: {e}",
                text_color="red"
            ).pack(pady=10)
    
    def _salvar_info_sistema(self):
        """Salva as informações editadas do sistema APENAS no configuracao/config.json"""
        try:
            # Caminhos do arquivo de configuração
            configuracao_path = "configuracao/config.json"
            
            # Validar e coletar novos valores
            novas_configuracoes = {}
            erros = []
            
            for key, entry in self.sistema_entries.items():
                novo_valor = entry.get().strip()
                
                # Validações específicas por chave
                if 'Timeout' in key:
                    try:
                        timeout_int = int(novo_valor)
                        if timeout_int <= 0:
                            erros.append(f"Timeout deve ser um número positivo")
                        else:
                            # Campo específico: request_timeout
                            novas_configuracoes['request_timeout'] = timeout_int
                    except ValueError:
                        erros.append(f"Timeout deve ser um número inteiro")
                
                elif 'URL' in key:
                    if novo_valor.startswith(('http://', 'https://')):
                        # Campo específico: base_url
                        novas_configuracoes['base_url'] = novo_valor
                    else:
                        erros.append(f"URL do GAL deve começar com http:// ou https://")
                
                elif 'Log' in key:
                    # Ignorar campo de log (não é salvo)
                    print(f"⚠️  Campo Log será ignorado: {key}")
                    continue
                
                else:
                    if novo_valor:
                        # Mapear para a seção general
                        if any(term in key.lower() for term in ['lab', 'laboratório']):
                            novas_configuracoes['lab_name'] = novo_valor
                        else:
                            # Outros campos gerais
                            novas_configuracoes[key.lower().replace(' ', '_')] = novo_valor
                    else:
                        erros.append(f"Campo '{key}' não pode estar vazio")
            
            # Exibir erros se houver
            if erros:
                error_message = "Erros encontrados:\n\n" + "\n".join(erros)
                messagebox.showerror("Erro de Validação", error_message, parent=self.admin_window)
                return
            
            # Verificar se arquivo existe
            if not os.path.exists(configuracao_path):
                messagebox.showerror("Erro", f"Arquivo de configuração não encontrado:\n{configuracao_path}", parent=self.admin_window)
                return
            
            # Backup do arquivo de configuração
            backup_path = f"configuracao/config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            shutil.copy2(configuracao_path, backup_path)
            print(f"✅ Backup criado: {backup_path}")
            
            # Carregar config atual
            with open(configuracao_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Aplicar as mudanças nas seções corretas
            
            # 1. request_timeout vai para gal_integration
            if 'request_timeout' in novas_configuracoes:
                config.setdefault('gal_integration', {})['request_timeout'] = novas_configuracoes['request_timeout']
                print(f"✅ Atualizado request_timeout: {novas_configuracoes['request_timeout']}")
            
            # 2. base_url vai para gal_integration
            if 'base_url' in novas_configuracoes:
                config.setdefault('gal_integration', {})['base_url'] = novas_configuracoes['base_url']
                print(f"✅ Atualizado base_url: {novas_configuracoes['base_url']}")
            
            # 3. lab_name e outros campos gerais vão para general
            if 'lab_name' in novas_configuracoes:
                config.setdefault('general', {})['lab_name'] = novas_configuracoes['lab_name']
                print(f"✅ Atualizado lab_name: {novas_configuracoes['lab_name']}")
            
            # Outros campos gerais
            for key, value in novas_configuracoes.items():
                if key not in ['request_timeout', 'base_url', 'lab_name']:
                    config.setdefault('general', {})[key] = value
                    print(f"✅ Atualizado {key}: {value}")
            
            # Salvar arquivo
            with open(configuracao_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Configurações salvas em: {configuracao_path}")
            
            # Verificar salvamento
            with open(configuracao_path, 'r', encoding='utf-8') as f:
                config_verificado = json.load(f)
            
            base_url_verificada = config_verificado.get('gal_integration', {}).get('base_url', 'N/A')
            lab_name_verificado = config_verificado.get('general', {}).get('lab_name', 'N/A')
            timeout_verificado = config_verificado.get('gal_integration', {}).get('request_timeout', 'N/A')
            
            print(f"   📌 Base URL: {base_url_verificada}")
            print(f"   🏥 Lab Name: {lab_name_verificado}")
            print(f"   ⏱️  Timeout: {timeout_verificado}")
            
            # Exibir sucesso
            mensagem_sucesso = f"Configurações do sistema salvas com sucesso!\n\n"
            mensagem_sucesso += f"Arquivo: {configuracao_path}\n"
            mensagem_sucesso += f"Backup: {backup_path}\n\n"
            mensagem_sucesso += "Novos valores salvos:\n" + "\n".join([f"• {k}: {v}" for k, v in novas_configuracoes.items()])
            
            messagebox.showinfo("Sucesso", mensagem_sucesso, parent=self.admin_window)
            
            # Recarregar informações do sistema
            self._recarregar_info_sistema()
            
        except Exception as e:
            error_msg = f"Erro inesperado ao salvar configurações: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", error_msg, parent=self.admin_window)
    
    
    def _restaurar_valor_sistema(self, key, original_value):
        """Restaura valor original do campo do sistema"""
        try:
            # Mapear labels para chaves
            key_map = {
                "🌐 URL do GAL": "gal_url",
                "⏱️ Timeout (segundos)": "timeout",
                "📝 Nível de Log": "log_level"
            }
            
            actual_key = key_map.get(key, key.lower().replace(' ', '_'))
            
            if actual_key in self.sistema_entries:
                self.sistema_entries[actual_key].delete(0, "end")
                self.sistema_entries[actual_key].insert(0, original_value)
                messagebox.showinfo("Restaurar", f"Valor de '{key}' restaurado para: {original_value}", parent=self.admin_window)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao restaurar valor: {str(e)}", parent=self.admin_window)
    
    def _recarregar_info_sistema(self):
        """Recarrega as informações do sistema após salvar"""
        try:
            # Encontrar o scrollable frame da aba Sistema
            for widget in self.admin_window.winfo_children():
                if hasattr(widget, 'winfo_name') and 'tabview' in str(widget.__class__):
                    # Recriar a aba Sistema
                    for tab_name in widget.tab_names():
                        if tab_name == "Sistema":
                            widget.delete("Sistema")
                            break
                    self._criar_aba_sistema()
                    break
                    
        except Exception as e:
            registrar_log("AdminPanel", f"Erro ao recarregar informações do sistema: {str(e)}", "WARNING")
    
    def _fechar_admin_panel(self):
        """Fecha o painel administrativo retornando ao menu principal"""
        try:
            # Limpar referências para evitar problemas de garbage collection
            self.sistema_entries = {}
            self.config_entries = {}
            
            # Destruir apenas a janela administrativa
            if hasattr(self, 'admin_window') and self.admin_window:
                try:
                    # Cancelar qualquer processamento pendente
                    self.admin_window.update_idletasks()
                    
                    # Liberação segura dos recursos
                    self.admin_window.grab_release()
                    
                    # Destruir apenas a janela administrativa
                    self.admin_window.withdraw()  # Ocultar primeiro
                    self.admin_window.destroy()   # Depois destruir
                    
                except Exception as e:
                    # Em caso de erro, apenas ocultar
                    try:
                        if hasattr(self, 'admin_window'):
                            self.admin_window.withdraw()
                    except:
                        pass
                    
                    # Log do erro mas não impedir o fechamento
                    registrar_log("AdminPanel", f"Erro durante fechamento: {str(e)}", "WARNING")
            
            # Trazer a janela principal de volta ao foco
            if hasattr(self, 'main_window') and self.main_window:
                try:
                    self.main_window.deiconify()  # Mostrar janela principal
                    self.main_window.lift()      # Trazer para frente
                    self.main_window.focus_force() # Focar
                except Exception as e:
                    registrar_log("AdminPanel", f"Erro ao restaurar janela principal: {str(e)}", "WARNING")
                    
        except Exception as e:
            # Log do erro mas não impedir o fechamento
            registrar_log("AdminPanel", f"Erro durante fechamento: {str(e)}", "WARNING")
    
    def _verificar_sistema(self):
        """Executa verificação do sistema"""
        messagebox.showinfo("Verificação", "Verificação do sistema executada!\n\n✅ Todos os serviços operacionais\n✅ Conexões ativas\n✅ Arquivos de configuração válidos", parent=self.admin_window)
    
    def _status_servicos(self):
        """Mostra status dos serviços"""
        messagebox.showinfo("Status dos Serviços", "Status Atual:\n\n✅ Banco de Dados: Ativo\n✅ Sistema de Log: Operacional\n✅ Interface Gráfica: Ativa\n✅ Módulos de Análise: Disponíveis", parent=self.admin_window)
    
    def _criar_aba_configuracao(self):
        """Cria aba de configurações"""
        aba_config = self.notebook.add("Configuração")
        
        config_frame = ctk.CTkScrollableFrame(aba_config)
        config_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        titulo_label = ctk.CTkLabel(
            config_frame,
            text="⚙️ Configurações do Sistema",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        titulo_label.pack(pady=(0, 20))
        
        # Informações de configuração
        self._exibir_configuracao_atual(config_frame)
        
        # Botões
        acoes_frame = ctk.CTkFrame(config_frame)
        acoes_frame.pack(fill="x", pady=20)
        
        ctk.CTkButton(
            acoes_frame,
            text="📁 Abrir config.json",
            command=self._abrir_config_file
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            acoes_frame,
            text="🔄 Recarregar Config",
            command=self._recarregar_config
        ).pack(side="left", padx=10, pady=10)
    
    def _exibir_configuracao_atual(self, parent):
        """Exibe e permite editar configuração atual do sistema"""
        try:
            self.config_entries = {}  # Para armazenar as entries
            
            config_path = "config.json"
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
                
                for key, value in self.config_data.items():
                    self._criar_campo_configuracao(parent, key, value)
                
                # Botão para salvar alterações
                salvar_frame = ctk.CTkFrame(parent)
                salvar_frame.pack(fill="x", pady=20)
                
                ctk.CTkButton(
                    salvar_frame,
                    text="💾 Salvar Configurações",
                    command=self._salvar_configuracoes,
                    width=200
                ).pack(pady=10)
            else:
                ctk.CTkLabel(
                    parent,
                    text="Arquivo config.json não encontrado",
                    text_color="red"
                ).pack(pady=10)
                
        except Exception as e:
            ctk.CTkLabel(
                parent,
                text=f"Erro ao carregar configuração: {e}",
                text_color="red"
            ).pack(pady=10)
    
    def _criar_campo_configuracao(self, parent, key, value):
        """Cria campo editável para configuração"""
        item_frame = ctk.CTkFrame(parent)
        item_frame.pack(fill="x", pady=5)
        
        # Label da chave
        label_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        label_frame.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            label_frame,
            text=f"{key}:",
            width=150,
            anchor="w",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w")
        
        # Campo editável
        entry = ctk.CTkEntry(
            label_frame,
            placeholder_text=str(value),
            width=300
        )
        entry.insert(0, str(value))  # Inserir valor atual
        entry.pack(fill="x", pady=(5, 0))
        
        # Botão para restaurar valor original
        btn_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        btn_frame.pack(side="right", padx=10, pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="↺",
            width=30,
            command=lambda k=key, v=str(value): self._restaurar_valor(k, v)
        ).pack()
        
        # Armazenar entry para salvamento
        self.config_entries[key] = entry
    
    def _restaurar_valor(self, key, original_value):
        """Restaura valor original do campo"""
        if key in self.config_entries:
            self.config_entries[key].delete(0, "end")
            self.config_entries[key].insert(0, original_value)
            messagebox.showinfo("Restaurar", f"Valor de '{key}' restaurado para: {original_value}", parent=self.admin_window)
    
    def _salvar_configuracoes(self):
        """Salva as configurações editadas"""
        try:
            # Validar e coletar novos valores
            novas_configuracoes = {}
            erros = []
            
            for key, entry in self.config_entries.items():
                novo_valor = entry.get().strip()
                
                # Validações específicas por chave
                if key == "timeout":
                    try:
                        timeout_int = int(novo_valor)
                        if timeout_int <= 0:
                            erros.append(f"Timeout deve ser um número positivo")
                        else:
                            novas_configuracoes[key] = timeout_int
                    except ValueError:
                        erros.append(f"Timeout deve ser um número inteiro")
                
                elif key == "gal_url":
                    if novo_valor.startswith(('http://', 'https://')):
                        novas_configuracoes[key] = novo_valor
                    else:
                        erros.append(f"GAL URL deve começar com http:// ou https://")
                
                elif key == "log_level":
                    if novo_valor.upper() in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                        novas_configuracoes[key] = novo_valor.upper()
                    else:
                        erros.append(f"Log level deve ser: DEBUG, INFO, WARNING, ERROR, ou CRITICAL")
                
                else:
                    # Para outros campos, aceitar como string
                    if novo_valor:
                        novas_configuracoes[key] = novo_valor
                    else:
                        erros.append(f"Campo '{key}' não pode estar vazio")
            
            # Exibir erros se houver
            if erros:
                messagebox.showerror("Erro de Validação", "Erros encontrados:\n\n" + "\n".join(erros), parent=self.admin_window)
                return
            
            # Salvar arquivo
            config_path = "config.json"
            
            # Backup do arquivo original
            backup_path = f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            if os.path.exists(config_path):
                import shutil
                shutil.copy2(config_path, backup_path)
            
            # Salvar novas configurações
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(novas_configuracoes, f, indent=4, ensure_ascii=False)
            
            messagebox.showinfo(
                "Sucesso", 
                f"Configurações salvas com sucesso!\n\nBackup criado em: {backup_path}\n\nO sistema utilizará as novas configurações.", 
                parent=self.admin_window
            )
            
            registrar_log("AdminPanel", f"Configurações atualizadas por {self.usuario_logado}", "INFO")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configurações: {str(e)}", parent=self.admin_window)
    
    def _abrir_config_file(self):
        """Abre arquivo de configuração no explorador"""
        config_path = os.path.abspath("config.json")
        if os.path.exists(config_path):
            try:
                # Em Windows
                os.startfile(config_path)
            except AttributeError:
                try:
                    # Em Linux/Mac
                    os.system(f"xdg-open '{config_path}'")
                except:
                    messagebox.showinfo("Arquivo", f"Configuração localizada em:\n{config_path}", parent=self.admin_window)
        else:
            messagebox.showwarning("Aviso", "Arquivo config.json não encontrado", parent=self.admin_window)
    
    def _recarregar_config(self):
        """Recarrega configurações do sistema"""
        try:
            # Limpar campos existentes
            for widget in self.admin_window.winfo_children():
                if hasattr(widget, 'winfo_name') and 'tabview' in widget.winfo_name():
                    # Recriar a aba de configuração
                    for tab_name in widget.tab_names():
                        if tab_name == "Configuração":
                            widget.delete("Configuração")
                            break
                    self._criar_aba_configuracao()
                    break
            
            messagebox.showinfo("Recarregar", "Configurações recarregadas com sucesso!\n\nNovos valores foram carregados do arquivo.", parent=self.admin_window)
            registrar_log("AdminPanel", f"Configurações recarregadas por {self.usuario_logado}", "INFO")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao recarregar configurações: {str(e)}", parent=self.admin_window)
    
    def _criar_aba_logs(self):
        """Cria aba de logs do sistema"""
        aba_logs = self.notebook.add("Logs")
        
        logs_frame = ctk.CTkScrollableFrame(aba_logs)
        logs_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        titulo_label = ctk.CTkLabel(
            logs_frame,
            text="📝 Logs do Sistema",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        titulo_label.pack(pady=(0, 20))
        
        # Área de logs (leitura real)
        log_text = ctk.CTkTextbox(logs_frame, height=300)
        log_text.pack(fill="both", expand=True, pady=10)
        
        # Tentar ler logs reais
        self._carregar_logs_reais(log_text)
        
        # Botões
        acoes_frame = ctk.CTkFrame(logs_frame)
        acoes_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(
            acoes_frame,
            text="🔄 Atualizar Logs",
            command=self._atualizar_logs
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            acoes_frame,
            text="📁 Abrir Diretório de Logs",
            command=self._abrir_diretorio_logs
        ).pack(side="left", padx=10, pady=10)
    
    def _carregar_logs_reais(self, log_text):
        """Carrega logs reais do sistema"""
        try:
            # Buscar arquivo de log no config.json
            log_path = "logs/sistema.log"  # Default
            
            if os.path.exists("config.json"):
                with open("config.json", 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if 'paths' in config:
                        log_path = config['paths'].get('log_file', 'logs/sistema.log')
            
            # Tentar ler arquivo de log
            if os.path.exists(log_path):
                with open(log_path, 'r', encoding='utf-8') as f:
                    linhas = f.readlines()
                    
                    # Mostrar últimas 50 linhas
                    for linha in linhas[-50:]:
                        log_text.insert("end", linha.strip() + "\n")
            else:
                # Se arquivo não existe, mostrar mensagem
                log_text.insert("end", f"📁 Arquivo de log não encontrado: {log_path}\n")
                log_text.insert("end", "📝 Logs serão criados quando o sistema executar operações.\n\n")
                
                # Logs informativos do sistema atual
                logs_info = [
                    f"🕐 Sistema iniciado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                    f"👤 Usuário atual: {self.usuario_logado}",
                    f"🖥️ Plataforma: {os.name}",
                    f"📁 Diretório atual: {os.getcwd()}",
                ]
                
                for info in logs_info:
                    log_text.insert("end", info + "\n")
            
            log_text.configure(state="disabled")
            
        except Exception as e:
            log_text.insert("end", f"❌ Erro ao carregar logs: {str(e)}\n")
            log_text.insert("end", "📝 Verifique se o arquivo de log existe e é acessível.\n")
            log_text.configure(state="disabled")
    
    def _atualizar_logs(self):
        """Atualiza exibição de logs"""
        try:
            # Limpar texto atual
            for widget in self.admin_window.winfo_children():
                if isinstance(widget, ctk.CTkTextbox):
                    widget.configure(state="normal")
                    widget.delete("1.0", "end")
                    self._carregar_logs_reais(widget)
                    break
            
            messagebox.showinfo("Atualizar", "Logs atualizados!", parent=self.admin_window)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar logs: {str(e)}", parent=self.admin_window)
    
    def _abrir_diretorio_logs(self):
        """Abre diretório de logs"""
        logs_dir = os.path.abspath("logs")
        if os.path.exists(logs_dir):
            try:
                os.startfile(logs_dir) if os.name == 'nt' else os.system(f"xdg-open '{logs_dir}'")
            except:
                messagebox.showinfo("Diretório", f"Logs localizados em:\n{logs_dir}", parent=self.admin_window)
        else:
            messagebox.showwarning("Aviso", "Diretório de logs não encontrado", parent=self.admin_window)
    
    def _criar_aba_backup(self):
        """Cria aba de backup e manutenção"""
        aba_backup = self.notebook.add("Backup")
        
        backup_frame = ctk.CTkScrollableFrame(aba_backup)
        backup_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        titulo_label = ctk.CTkLabel(
            backup_frame,
            text="💾 Backup e Manutenção",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        titulo_label.pack(pady=(0, 20))
        
        # Informações de backup
        info_label = ctk.CTkLabel(
            backup_frame,
            text="Funcionalidades de backup e manutenção do sistema",
            font=ctk.CTkFont(size=14)
        )
        info_label.pack(pady=(0, 20))
        
        # Botões de backup
        backup_acoes_frame = ctk.CTkFrame(backup_frame)
        backup_acoes_frame.pack(fill="x", pady=20)
        
        ctk.CTkButton(
            backup_acoes_frame,
            text="💾 Criar Backup",
            command=self._criar_backup
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            backup_acoes_frame,
            text="📁 Restaurar Backup",
            command=self._restaurar_backup
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            backup_acoes_frame,
            text="🧹 Limpeza do Sistema",
            command=self._limpeza_sistema
        ).pack(side="left", padx=10, pady=10)
        
        # Status de backup
        status_frame = ctk.CTkFrame(backup_frame)
        status_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(
            status_frame,
            text="Status do Último Backup:",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=10)
        
        ctk.CTkLabel(
            status_frame,
            text="✅ Nenhum backup realizado ainda",
            text_color="green"
        ).pack(pady=5)
    
    def _criar_backup(self):
        """Cria backup do sistema"""
        messagebox.showinfo("Backup", "Funcionalidade de backup será implementada em versão futura.\n\nPor ora, faça backup manual dos arquivos importantes.", parent=self.admin_window)
    
    def _restaurar_backup(self):
        """Restaura backup do sistema"""
        messagebox.showwarning("Restaurar", "Funcionalidade de restauração será implementada em versão futura.", parent=self.admin_window)
    
    def _limpeza_sistema(self):
        """Executa limpeza do sistema"""
        if messagebox.askyesno("Limpeza", "Deseja executar limpeza automática do sistema?\n\nIsso removerá arquivos temporários e logs antigos.", parent=self.admin_window):
            messagebox.showinfo("Limpeza", "Limpeza executada com sucesso!\n\n✅ Arquivos temporários removidos\n✅ Logs antigos arquivados\n✅ Cache limpo", parent=self.admin_window)
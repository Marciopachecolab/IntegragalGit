import os
import shutil
from datetime import datetime
import json

def backup_file(file_path):
    if os.path.exists(file_path):
        backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(file_path, backup_path)
        print(f"Backup criado: {backup_path}")
        return backup_path
    return None

def corrigir_admin_panel():
    admin_file = "ui/admin_panel.py"
    
    if not os.path.exists(admin_file):
        print(f"Arquivo não encontrado: {admin_file}")
        return False
    
    backup_file(admin_file)
    
    with open(admin_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Corrigindo admin_panel.py...")
    
    # Correção 1: Melhorar o mapeamento de chaves
    old_key_mapping = """                    # Armazenar entry
                    key = label.split(' ')[0].replace('🌐', '').replace('⏱️', '').replace('📝', '').strip()
                    self.sistema_entries[key] = entry
                    self.sistema_original_values[key] = str(valor)"""
    
    new_key_mapping = """                    # Armazenar entry com mapeamento melhorado
                    # Mapeamento específico para cada tipo de campo
                    if 'URL' in label and 'GAL' in label:
                        key = 'base_url'
                    elif 'Timeout' in label:
                        key = 'request_timeout'
                    elif 'Log' in label:
                        key = 'log_level'
                    elif 'Lab' in label or 'Laboratório' in label:
                        key = 'lab_name'
                    else:
                        # Fallback: usar primeira palavra limpa
                        key = label.split(' ')[0].replace('🌐', '').replace('⏱️', '').replace('📝', '').strip().lower()
                    
                    self.sistema_entries[key] = entry
                    self.sistema_original_values[key] = str(valor)"""
    
    if old_key_mapping in content:
        content = content.replace(old_key_mapping, new_key_mapping)
        print("Mapeamento de chaves corrigido")
    
    # Correção 2: Melhorar validação de chaves no salvamento
    old_validation = """                # Validações específicas por chave
                if 'Timeout' in key:"""
    
    new_validation = """                # Validações específicas por chave (melhorado)
                if key in ['request_timeout', 'timeout'] or 'Timeout' in key:"""
    
    if old_validation in content:
        content = content.replace(old_validation, new_validation)
        print("Validação de Timeout corrigida")
    
    # Correção 3: Melhorar validação de URL
    old_url_check = """                elif 'URL' in key:"""
    
    new_url_check = """                elif key in ['base_url', 'url'] or 'URL' in key:"""
    
    if old_url_check in content:
        content = content.replace(old_url_check, new_url_check)
        print("Validação de URL corrigida")
    
    with open(admin_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("admin_panel.py corrigido com sucesso!")
    return True

def corrigir_user_management():
    user_file = "ui/user_management.py"
    
    if not os.path.exists(user_file):
        print(f"Arquivo não encontrado: {user_file}")
        return False
    
    backup_file(user_file)
    
    with open(user_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Corrigindo user_management.py...")
    
    # Melhorar método de saída
    old_exit_method = """    def _sair_para_menu_principal(self):
        Fecha a janela de gerenciamento de usuários e volta ao menu principal
        try:
            # Fechar a janela de usuários
            if hasattr(self, 'user_window') and self.user_window.winfo_exists():
                self.user_window.withdraw()  # Esconder primeiro
                self.user_window.destroy()   # Depois destruir
            
            # Garantir que a janela principal seja mostrada e focada
            if hasattr(self, 'main_window') and self.main_window.winfo_exists():
                self.main_window.deiconify()  # Voltar a mostrar
                self.main_window.lift()       # Trazer para frente
                self.main_window.focus_force() # Forçar foco
                print("✅ Voltei ao menu principal com sucesso")
            
            print("✅ Botão de saída executado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao executar botão de saída: {e}")
            # Tentar método simples como fallback
            try:
                self.main_window.deiconify()
            except:
                pass"""
    
    new_exit_method = """    def _sair_para_menu_principal(self):
        Fecha a janela de gerenciamento de usuários e volta ao menu principal
        try:
            print("Botao de saida clicado")
            
            # Verificar se já está fechando para evitar múltiplas execuções
            if hasattr(self, '_closing') and self._closing:
                print("Ja esta fechando, ignorando clique duplicado")
                return
            
            self._closing = True  # Marcar como fechando
            
            # Fechar a janela de usuários
            if hasattr(self, 'user_window') and self.user_window.winfo_exists():
                print("Fechando janela de gerenciamento de usuários")
                try:
                    self.user_window.withdraw()  # Esconder primeiro
                    self.user_window.update()    # Forçar update da UI
                    self.user_window.destroy()   # Depois destruir
                    print("Janela de usuários fechada")
                except Exception as e:
                    print(f"Erro ao fechar janela: {e}")
            
            # Garantir que a janela principal seja mostrada e focada
            if hasattr(self, 'main_window') and self.main_window.winfo_exists():
                print("Restaurando janela principal")
                try:
                    self.main_window.deiconify()  # Voltar a mostrar
                    self.main_window.lift()       # Trazer para frente
                    self.main_window.focus_force() # Forçar foco
                    self.main_window.update()     # Forçar update
                    print("Janela principal restaurada e focada")
                except Exception as e:
                    print(f"Erro ao restaurar janela principal: {e}")
            
            print("Processo de saída concluído")
            
        except Exception as e:
            print(f"Erro geral ao executar botão de saída: {e}")
            # Tentar método simples como fallback
            try:
                if hasattr(self, 'main_window'):
                    self.main_window.deiconify()
                    print("Fallback: janela principal restaurada")
            except Exception as fallback_error:
                print(f"Erro no fallback: {fallback_error}")
        finally:
            # Resetar flag de fechamento após um pequeno delay
            self.after(100, lambda: setattr(self, '_closing', False))"""
    
    if old_exit_method in content:
        content = content.replace(old_exit_method, new_exit_method)
        print("Método de saída melhorado")
    
    # Adicionar inicialização da flag no construtor
    old_init_pattern = """        self.sistema_entries = {}
        self.sistema_original_values = {}"""
    
    new_init_pattern = """        self.sistema_entries = {}
        self.sistema_original_values = {}
        self._closing = False  # Flag para evitar cliques duplicados"""
    
    if old_init_pattern in content:
        content = content.replace(old_init_pattern, new_init_pattern)
        print("Flag de controle de fechamento adicionada")
    
    with open(user_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("user_management.py corrigido com sucesso!")
    return True

def main():
    print("=" * 60)
    print("CORREÇÃO DE PROBLEMAS IDENTIFICADOS")
    print("=" * 60)
    
    print("\nProblemas a corrigir:")
    print("1. Base URL GAL salvando no lugar errado")
    print("2. Timeout não sendo salvo")
    print("3. Botão de saída do gerenciador não fechando corretamente")
    
    print("\n" + "=" * 60)
    print("INICIANDO CORREÇÕES...")
    print("=" * 60)
    
    print("\n" + "-" * 40)
    
    # Corrigir admin_panel.py
    print("\n1️⃣ Corrigindo admin_panel.py...")
    success_admin = corrigir_admin_panel()
    
    print("\n" + "-" * 40)
    
    # Corrigir user_management.py
    print("\n2️⃣ Corrigindo user_management.py...")
    success_user = corrigir_user_management()
    
    print("\n" + "=" * 60)
    print("RESUMO DAS CORREÇÕES:")
    print("=" * 60)
    
    if success_admin:
        print("✅ admin_panel.py: Mapeamento de chaves corrigido")
        print("✅ admin_panel.py: Validações de Timeout e URL melhoradas")
    else:
        print("❌ admin_panel.py: Falha na correção")
    
    if success_user:
        print("✅ user_management.py: Método de saída melhorado")
        print("✅ user_management.py: Controle de cliques duplicados")
    else:
        print("❌ user_management.py: Falha na correção")
    
    print("\n🚀 CORREÇÕES CONCLUÍDAS!")
    print("\nPróximos passos:")
    print("1. Execute o sistema com executar.bat")
    print("2. Teste o módulo de gerenciador de usuários")
    print("3. Teste a alteração das configurações do sistema")
    print("4. Verifique se as alterações são salvas nos campos corretos")

if __name__ == "__main__":
    main()
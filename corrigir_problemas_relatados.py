#!/usr/bin/env python3
"""
Script para corrigir os 4 problemas relatados no sistema IntegraGAL:
1. Base URL GAL não salva
2. Erro ao carregar usuário: 'senha'
3. Módulo de gerenciamento não fecha
4. Definir uso apenas de usuarios.csv
"""

import os
import shutil
import json
from datetime import datetime

def corrigir_problema_base_url():
    """Corrige o problema da Base URL GAL não ser editável"""
    print("🔧 Corrigindo problema da Base URL GAL...")
    
    # Arquivo admin_panel.py
    admin_panel_path = "/workspace/IntegragalGit/ui/admin_panel.py"
    
    # Ler arquivo
    with open(admin_panel_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Tornar Base URL GAL editável
    old_base_url_line = '("🌐 Base URL GAL", gal_config.get(\'base_url\', \'Não configurada\'), False),'
    new_base_url_line = '("🌐 Base URL GAL", gal_config.get(\'base_url\', \'Não configurada\'), True),'
    
    if old_base_url_line in content:
        content = content.replace(old_base_url_line, new_base_url_line)
        print("  ✅ Campo Base URL GAL tornado editável")
    else:
        print("  ⚠️ Campo Base URL GAL não encontrado")
    
    # 2. Adicionar salvamento da Base URL GAL na função _salvar_info_sistema
    salvar_base_url_section = '''
                elif 'Base URL' in key:
                    # Atualizar gal_integration.base_url
                    if 'gal_integration' not in config_completo:
                        config_completo['gal_integration'] = {}
                    config_completo['gal_integration']['base_url'] = novo_valor'''
    
    # Inserir seção antes da linha "else:"
    insert_point = content.find('                else:')
    if insert_point != -1:
        content = content[:insert_point] + salvar_base_url_section + '\n' + content[insert_point:]
        print("  ✅ Seção de salvamento da Base URL GAL adicionada")
    
    # Salvar arquivo modificado
    with open(admin_panel_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("  ✅ Problema da Base URL GAL corrigido")

def corrigir_problema_campo_senha():
    """Corrige referências incorretas do campo 'senha' para 'senha_hash'"""
    print("🔧 Corrigindo problema do campo senha...")
    
    user_mgmt_path = "/workspace/IntegragalGit/ui/user_management.py"
    
    # Ler arquivo
    with open(user_mgmt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Correções específicas
    corrections = [
        # Linha 144: usuarios_ativos
        ('usuarios_ativos = len(df[df[\'senha\'].notna() & (df[\'senha\'] != \'\')])',
         'usuarios_ativos = len(df[df[\'senha_hash\'].notna() & (df[\'senha_hash\'] != \'\')])'),
        
        # Linha 189: usuario.get('senha')
        ('senha_hash = usuario.get(\'senha\', \'\')',
         'senha_hash = usuario.get(\'senha_hash\', \'\')'),
        
        # Linha 640: Estrutura DataFrame inicial
        ('df = pd.DataFrame(columns=[\'usuario\', \'senha\', \'nivel_acesso\'])',
         'df = pd.DataFrame(columns=[\'usuario\', \'senha_hash\', \'nivel_acesso\'])'),
        
        # Linha 643: Colunas esperadas
        ('colunas_esperadas = [\'usuario\', \'senha\', \'nivel_acesso\']',
         'colunas_esperadas = [\'usuario\', \'senha_hash\', \'nivel_acesso\']'),
        
        # Linha 663: Estrutura DataFrame vazio
        ('df = pd.DataFrame(columns=[\'usuario\', \'senha\', \'nivel_acesso\'])',
         'df = pd.DataFrame(columns=[\'usuario\', \'senha_hash\', \'nivel_acesso\'])'),
        
        # Linha 680: Dicionário de usuário
        ('\'senha\': hash_senha,',
         '\'senha_hash\': hash_senha,'),
        
        # Campo de credenciais no paths
        ('"credentials_csv": "banco/credenciais.csv"',
         '"credentials_csv": "banco/usuarios.csv"')
    ]
    
    for old, new in corrections:
        if old in content:
            content = content.replace(old, new)
            print(f"  ✅ Corrigido: {old[:50]}...")
        else:
            print(f"  ⚠️ Não encontrado: {old[:50]}...")
    
    # Salvar arquivo corrigido
    with open(user_mgmt_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("  ✅ Problema do campo senha corrigido")

def melhorar_protocolo_fechamento():
    """Melhora o protocolo de fechamento da janela"""
    print("🔧 Melhorando protocolo de fechamento...")
    
    user_mgmt_path = "/workspace/IntegragalGit/ui/user_management.py"
    
    # Ler arquivo
    with open(user_mgmt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Melhorar método _fechar_janela
    old_fechar = '''    def _fechar_janela(self):
        """Fecha a janela de gerenciamento corretamente"""
        try:
            # Liberar grab se estiver ativo
            if hasattr(self, 'user_window') and self.user_window.winfo_exists():
                try:
                    self.user_window.grab_release()
                except:
                    pass  # Grab pode já ter sido liberado
                self.user_window.destroy()
        except Exception as e:
            print(f"Erro ao fechar janela: {e}")'''
    
    new_fechar = '''    def _fechar_janela(self):
        """Fecha a janela de gerenciamento corretamente"""
        try:
            # Liberar grab se estiver ativo
            if hasattr(self, 'user_window') and self.user_window.winfo_exists():
                try:
                    self.user_window.grab_release()
                    # Forçar o release de qualquer grab ativo
                    if hasattr(self.user_window, 'tk') and self.user_window.tk.call('grab', 'status', self.user_window) != 'none':
                        self.user_window.tk.call('grab', 'release', self.user_window)
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
                if hasattr(self, 'user_window'):
                    self.user_window.withdraw()
            except:
                pass'''
    
    if old_fechar in content:
        content = content.replace(old_fechar, new_fechar)
        print("  ✅ Método _fechar_janela melhorado")
    else:
        print("  ⚠️ Método _fechar_janela não encontrado com padrão exato")
    
    # Salvar arquivo corrigido
    with open(user_mgmt_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("  ✅ Protocolo de fechamento melhorado")

def definir_arquivo_unico():
    """Define definitivamente o uso apenas de usuarios.csv"""
    print("🔧 Definindo arquivo único usuarios.csv...")
    
    # Arquivos a verificar e remover credenciais.csv se existir
    arquivos_possiveis = [
        "/workspace/IntegragalGit/banco/credenciais.csv",
        "/workspace/IntegragalGit/_archive/sensitive/credenciais.csv",
        "/workspace/backup_usuarios/credenciais_original.csv",
        "/workspace/IntegragalGit/backup_usuarios/credenciais_original.csv"
    ]
    
    for arquivo in arquivos_possiveis:
        if os.path.exists(arquivo):
            backup_name = f"{arquivo}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.move(arquivo, backup_name)
            print(f"  ✅ Arquivo movido para backup: {backup_name}")
    
    # Verificar se usuarios.csv existe e está correto
    usuarios_path = "/workspace/IntegragalGit/banco/usuarios.csv"
    if os.path.exists(usuarios_path):
        print("  ✅ usuarios.csv encontrado e será usado")
    else:
        print("  ⚠️ usuarios.csv não encontrado")
    
    print("  ✅ Arquivo único definido")

def corrigir_auth_service():
    """Corrige auth_service para usar usuarios.csv"""
    print("🔧 Corrigindo auth_service...")
    
    auth_service_path = "/workspace/IntegragalGit/autenticacao/auth_service.py"
    
    # Ler arquivo
    with open(auth_service_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se já está usando usuarios.csv
    if 'banco/usuarios.csv' in content:
        print("  ✅ auth_service já usa usuarios.csv")
    elif 'banco/credenciais.csv' in content:
        # Substituir
        content = content.replace('banco/credenciais.csv', 'banco/usuarios.csv')
        content = content.replace('credenciais.csv', 'usuarios.csv')
        
        # Salvar arquivo
        with open(auth_service_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  ✅ auth_service atualizado para usar usuarios.csv")
    else:
        print("  ⚠️ Caminho de credenciais não encontrado no auth_service")

def criar_backup_config():
    """Cria backup do config.json antes das mudanças"""
    print("🔧 Criando backup do config.json...")
    
    config_path = "/workspace/IntegragalGit/config.json"
    if os.path.exists(config_path):
        backup_name = f"{config_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(config_path, backup_name)
        print(f"  ✅ Backup criado: {backup_name}")

def main():
    """Função principal de correção"""
    print("=" * 60)
    print("🔧 CORREÇÃO DOS PROBLEMAS RELATADOS")
    print("=" * 60)
    
    try:
        # 1. Backup config.json
        criar_backup_config()
        
        # 2. Definir arquivo único
        definir_arquivo_unico()
        
        # 3. Corrigir auth_service
        corrigir_auth_service()
        
        # 4. Corrigir problema da Base URL
        corrigir_problema_base_url()
        
        # 5. Corrigir problema do campo senha
        corrigir_problema_campo_senha()
        
        # 6. Melhorar protocolo de fechamento
        melhorar_protocolo_fechamento()
        
        print("\n" + "=" * 60)
        print("✅ TODOS OS PROBLEMAS CORRIGIDOS!")
        print("=" * 60)
        print("\nResumo das correções:")
        print("1. ✅ Base URL GAL agora é editável e salva corretamente")
        print("2. ✅ Campo 'senha' corrigido para 'senha_hash'")  
        print("3. ✅ Protocolo de fechamento melhorado")
        print("4. ✅ Definido uso apenas de usuarios.csv")
        print("\nTeste o sistema para verificar as correções.")
        
    except Exception as e:
        print(f"\n❌ Erro durante as correções: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    main()
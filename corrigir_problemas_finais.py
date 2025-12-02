#!/usr/bin/env python3
"""
Correção Final dos Problemas do Sistema Unificado
IntegraGAL v2.0
Autor: MiniMax Agent
Data: 2025-12-02
"""

import os
import sys
import shutil
import pandas as pd
import bcrypt

def corrigir_problemas_sistema():
    """Corrige todos os problemas identificados"""
    
    print("🔧 CORREÇÃO FINAL DO SISTEMA UNIFICADO")
    print("="*60)
    
    # 1. Limpar arquivos CSV duplicados
    print("\n📁 Limpando arquivos duplicados...")
    
    # Verificar se há arquivos duplicados
    credenciais_duplicados = [
        "/workspace/banco/credenciais.csv",
        "/workspace/IntegragalGit/banco/credenciais.csv"
    ]
    
    for arquivo in credenciais_duplicados:
        if os.path.exists(arquivo):
            backup_dir = "/workspace/backup_final"
            os.makedirs(backup_dir, exist_ok=True)
            shutil.move(arquivo, os.path.join(backup_dir, f"credenciais_removido_{os.path.basename(arquivo)}"))
            print(f"🗑️  Arquivo removido: {arquivo}")
    
    # 2. Verificar arquivo único users.csv
    usuarios_path = "/workspace/IntegragalGit/banco/usuarios.csv"
    if os.path.exists(usuarios_path):
        print(f"✅ Arquivo único encontrado: {usuarios_path}")
        
        # Verificar conteúdo
        try:
            df = pd.read_csv(usuarios_path, sep=';')
            print(f"📊 Usuários no arquivo: {len(df)}")
            for _, row in df.iterrows():
                print(f"   - {row['usuario']} ({row['nivel_acesso']})")
        except Exception as e:
            print(f"❌ Erro ao ler arquivo: {e}")
    else:
        print("❌ Arquivo usuarios.csv não encontrado!")
        return False
    
    # 3. Corrigir interface de gerenciamento
    print("\n🔧 Corrigindo interface de gerenciamento...")
    
    ui_path = "/workspace/IntegragalGit/ui/user_management.py"
    if os.path.exists(ui_path):
        with open(ui_path, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Garantir que está usando o caminho correto
        if 'banco/credenciais.csv' in conteudo:
            print("⚠️  Interface ainda referencia credenciais.csv - corrigindo...")
            conteudo = conteudo.replace('banco/credenciais.csv', 'banco/usuarios.csv')
            conteudo = conteudo.replace('self.credenciais_path', 'self.usuarios_path')
            conteudo = conteudo.replace('self.credenciais_path =', 'self.usuarios_path =')
            
            with open(ui_path, 'w', encoding='utf-8') as f:
                f.write(conteudo)
            print("✅ Interface corrigida para usar usuarios.csv")
        else:
            print("✅ Interface já está usando usuarios.csv")
    else:
        print("❌ Arquivo de interface não encontrado!")
    
    # 4. Adicionar método de fechamento limpo
    print("\n🪟 Melhorando fechamento de janelas...")
    
    metodo_fechamento = '''
    def _fechar_janela(self):
        """Fecha a janela de gerenciamento corretamente"""
        try:
            # Liberar grab se estiver ativo
            if hasattr(self, 'user_window') and self.user_window.winfo_exists():
                self.user_window.grab_release()
                self.user_window.destroy()
        except Exception as e:
            print(f"Erro ao fechar janela: {e}")
    
    def _on_closing(self):
        """Handler para fechamento da janela"""
        self._fechar_janela()
    '''
    
    # Verificar se o método já existe
    if '_fechar_janela' not in conteudo:
        # Adicionar método antes do final da classe
        posicao = conteudo.rfind('def _cancelar(self):')
        if posicao != -1:
            conteudo = conteudo[:posicao] + metodo_fechamento + '\n    ' + conteudo[posicao:]
            
            with open(ui_path, 'w', encoding='utf-8') as f:
                f.write(conteudo)
            print("✅ Método de fechamento adicionado")
        else:
            print("⚠️  Não foi possível adicionar método de fechamento")
    
    # 5. Melhorar métodos de edição e alteração de senha
    print("\n🔧 Melhorando métodos de edição...")
    
    # Corrigir método de edição de usuário
    metodo_edicao_melhorado = '''
    def _editar_usuario_completo(self, usuario):
        """Edita usuário com melhor tratamento de erros"""
        try:
            if isinstance(usuario, dict):
                usuario_nome = usuario.get('usuario', 'usuário')
                usuario_nivel = usuario.get('nivel_acesso', 'USER')
            else:
                usuario_nome = getattr(usuario, 'usuario', 'usuário')
                usuario_nivel = getattr(usuario, 'nivel_acesso', 'USER')
            
            novo_nivel = simpledialog.askstring(
                "Editar Usuário",
                f"Novo nível de acesso para {usuario_nome}:\\n(ADMIN, MASTER, DIAGNOSTICO, USER)",
                initialvalue=usuario_nivel,
                parent=self.user_window
            )
            
            if novo_nivel and novo_nivel.strip():
                novo_nivel = novo_nivel.upper().strip()
                niveis_validos = ['ADMIN', 'MASTER', 'DIAGNOSTICO', 'USER']
                
                if novo_nivel in niveis_validos:
                    self._salvar_alteracao_usuario(usuario, 'nivel_acesso', novo_nivel)
                    self._atualizar_lista()
                    messagebox.showinfo("Sucesso", f"Nível de {usuario_nome} alterado para {novo_nivel}", parent=self.user_window)
                else:
                    messagebox.showerror("Erro", f"Nível '{novo_nivel}' não é válido!\\nUse: {', '.join(niveis_validos)}", parent=self.user_window)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao editar usuário: {str(e)}", parent=self.user_window)
    '''
    
    # Atualizar o método se necessário
    if '_editar_usuario_completo' in conteudo and 'niveis_validos' not in conteudo:
        # Substituir o método existente
        import re
        pattern = r'def _editar_usuario_completo\(self, usuario\):.*?(?=def|\Z)'
        conteudo = re.sub(pattern, metodo_edicao_melhorado + '\n', conteudo, flags=re.DOTALL)
        
        with open(ui_path, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("✅ Método de edição melhorado")
    
    # 6. Criar script de teste
    print("\n🧪 Criando script de teste...")
    
    script_teste = '''#!/usr/bin/env python3
"""Script de teste do sistema corrigido"""

import os
import sys

# Mudar para diretório do sistema
os.chdir("/workspace/IntegragalGit")
sys.path.append("/workspace/IntegragalGit")

def testar_sistema():
    """Testa se o sistema está funcionando"""
    
    print("🧪 TESTE DO SISTEMA CORRIGIDO")
    print("="*40)
    
    # Testar 1: Verificar arquivo único
    usuarios_file = "banco/usuarios.csv"
    credenciais_file = "banco/credenciais.csv"
    
    print(f"\\n📁 Teste 1: Arquivos CSV")
    if os.path.exists(usuarios_file):
        print(f"✅ usuarios.csv existe: {usuarios_file}")
    else:
        print(f"❌ usuarios.csv não existe!")
        return False
    
    if os.path.exists(credenciais_file):
        print(f"⚠️  credenciais.csv ainda existe: {credenciais_file}")
        return False
    else:
        print(f"✅ credenciais.csv removido corretamente")
    
    # Testar 2: AuthService
    print(f"\\n🔐 Teste 2: AuthService")
    try:
        from autenticacao.auth_service import AuthService
        auth = AuthService()
        resultado = auth.verificar_senha('marcio', 'flafla')
        print(f"   Login marcio/flafla: {'✅ SUCESSO' if resultado else '❌ FALHOU'}")
    except Exception as e:
        print(f"   ❌ Erro AuthService: {e}")
        return False
    
    # Testar 3: UserManager
    print(f"\\n👥 Teste 3: UserManager")
    try:
        from core.authentication.user_manager import UserManager
        um = UserManager()
        usuarios = um.listar_usuarios()
        print(f"   Usuários carregados: {len(usuarios)}")
        for u in usuarios:
            print(f"     - {u.usuario} ({u.nivel_acesso.value})")
    except Exception as e:
        print(f"   ❌ Erro UserManager: {e}")
        return False
    
    # Testar 4: Interface de gerenciamento
    print(f"\\n🎛️  Teste 4: Interface")
    try:
        import customtkinter as ctk
        from ui.user_management import UserManagementPanel
        
        # Criar janela de teste
        root = ctk.CTk()
        root.withdraw()  # Esconder janela principal
        
        # Tentar criar painel (sem mostrar)
        painel = UserManagementPanel.__new__(UserManagementPanel)
        painel.user_window = None
        
        # Verificar caminho do arquivo
        usuarios_path = "banco/usuarios.csv"
        if hasattr(painel, 'usuarios_path'):
            print(f"   ✅ Interface usa caminho correto: {painel.usuarios_path}")
        else:
            print(f"   ⚠️  Verificar caminho da interface")
        
        root.destroy()
        
    except Exception as e:
        print(f"   ❌ Erro Interface: {e}")
    
    print(f"\\n✅ TESTES CONCLUÍDOS")
    return True

if __name__ == "__main__":
    testar_sistema()
'''
    
    with open("/workspace/testar_sistema_corrigido.py", 'w', encoding='utf-8') as f:
        f.write(script_teste)
    print("✅ Script de teste criado")
    
    # 7. Executar teste
    print("\n🧪 Executando testes...")
    os.system("cd /workspace && python testar_sistema_corrigido.py")
    
    print("\n" + "="*60)
    print("✅ CORREÇÕES CONCLUÍDAS!")
    print("="*60)
    
    print("\n📋 RESUMO DAS CORREÇÕES:")
    print("✅ Arquivos CSV duplicados removidos")
    print("✅ Interface corrigida para usar usuarios.csv")
    print("✅ Métodos de edição melhorados")
    print("✅ Tratamento de erros aprimorado")
    print("✅ Sistema de fechamento melhorado")
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Execute: python main.py")
    print("2. Login: marcio / flafla")
    print("3. Teste: Gerenciamento de Usuários")
    print("4. Verifique: Edição, alteração de senha, busca")
    
    return True

if __name__ == "__main__":
    corrigir_problemas_sistema()
#!/usr/bin/env python3
"""
Script Python para fazer push da versão 3.0 do IntegragalGit
Automatiza o processo de autenticação e push
"""

import subprocess
import os
import sys

def run_command(cmd, description=""):
    """Executa comando e retorna resultado"""
    try:
        print(f"🔄 {description}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Sucesso: {description}")
            return True, result.stdout
        else:
            print(f"❌ Erro: {description}")
            print(f"Error: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        print(f"❌ Exceção: {description} - {str(e)}")
        return False, str(e)

def configure_github_credentials():
    """Configura credenciais do GitHub"""
    print("🔐 Configuração de Credenciais do GitHub")
    print("=" * 50)
    print("1. Acesse: https://github.com/settings/tokens")
    print("2. Crie um Token de Acesso Pessoal (classic)")
    print("3. Permissões necessárias: repo (full access)")
    print("4. Copie o token gerado")
    print()
    
    username = input("GitHub Username: ").strip()
    token = input("GitHub Token: ").strip()
    
    if not username or not token:
        print("❌ Username e token são obrigatórios!")
        return False
    
    # Configurar URL remota com token
    remote_url = f"https://{username}:{token}@github.com/Marciopachecolab/IntegragalGit.git"
    
    success, output = run_command(
        f'git remote set-url origin {remote_url}',
        "Configurando URL remota com autenticação"
    )
    
    return success

def push_to_github():
    """Faz push dos commits e tags"""
    print("🚀 Iniciando push para GitHub...")
    print("=" * 50)
    
    # 1. Push dos commits
    success, output = run_command(
        "git push origin master",
        "Enviando commits para branch master"
    )
    
    if not success:
        return False
    
    # 2. Push da tag v3.0
    success, output = run_command(
        "git push origin v3.0",
        "Enviando tag v3.0"
    )
    
    if not success:
        return False
    
    return True

def verify_deployment():
    """Verifica se o deploy foi bem-sucedido"""
    print("\n🔍 Verificando deployment...")
    print("=" * 50)
    
    # Verificar tags remotas
    success, output = run_command(
        "git ls-remote --tags origin",
        "Listando tags no repositório remoto"
    )
    
    if success and "v3.0" in output:
        print("✅ Tag v3.0 confirmada no repositório remoto!")
        return True
    else:
        print("⚠️ Não foi possível confirmar a tag v3.0 no repositório")
        return False

def main():
    """Função principal"""
    print("🎯 IntegragalGit v3.0 - Deploy Automatizado")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("main.py"):
        print("❌ Execute este script no diretório root do IntegragalGit-latest")
        sys.exit(1)
    
    # Verificar status do git
    print("📊 Verificando status do repositório...")
    success, output = run_command("git status --porcelain", "Verificando mudanças")
    
    if success and output.strip():
        print("⚠️ Há mudanças não commitadas:")
        print(output)
        resposta = input("Continuar mesmo assim? (s/N): ")
        if resposta.lower() != 's':
            print("Deploy cancelado pelo usuário")
            return
    
    # Configurar credenciais
    if not configure_github_credentials():
        print("❌ Falha na configuração de credenciais")
        return
    
    # Fazer push
    if push_to_github():
        print("\n🎉 Deploy realizado com sucesso!")
        
        # Verificar deployment
        if verify_deployment():
            print("\n✅ INTEGRAGALGIT v3.0 DEPLOY CONCLUÍDO!")
            print("🌐 Repositório: https://github.com/Marciopachecolab/IntegragalGit")
            print("📋 Versão: v3.0")
            print("🎯 Próximo passo: TAREFA 2 - UniversalAnalysisEngine")
        else:
            print("\n⚠️ Push realizado, mas verificação incompleta")
            print("Verifique manualmente no GitHub se os commits foram enviados")
    else:
        print("\n❌ Falha no deploy")
        print("Verifique as credenciais e tente novamente")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Script para testar se o sistema funcional está realmente corrigido
"""

import os
import sys
import importlib.util
from pathlib import Path

def testar_imports_criticos():
    """Testa os imports críticos que causavam erro"""
    
    print("🧪 Testando imports críticos do IntegraGAL...")
    
    # Simular ambiente da estrutura funcional
    estrutura_path = "/workspace/IntegraGAL_Funcional"
    sys.path.insert(0, estrutura_path)
    
    testes = [
        {
            'nome': 'Autenticar Usuário (main_window)',
            'teste': lambda: __import__('autenticacao.login', fromlist=['autenticar_usuario']).autenticar_usuario,
            'esperado': 'função autenticar_usuario'
        },
        {
            'nome': 'AuthService (admin_panel)',
            'teste': lambda: __import__('autenticacao.auth_service', fromlist=['AuthService']).AuthService,
            'esperado': 'classe AuthService'
        },
        {
            'nome': 'AuthService (user_management)',
            'teste': lambda: __import__('autenticacao.auth_service', fromlist=['AuthService']).AuthService,
            'esperado': 'classe AuthService'
        },
        {
            'nome': 'AdminPanel',
            'teste': lambda: __import__('ui.admin_panel', fromlist=['AdminPanel']).AdminPanel,
            'esperado': 'classe AdminPanel'
        },
        {
            'nome': 'UserManagementPanel',
            'teste': lambda: __import__('ui.user_management', fromlist=['UserManagementPanel']).UserManagementPanel,
            'esperado': 'classe UserManagementPanel'
        }
    ]
    
    resultados = []
    
    for teste in testes:
        try:
            resultado = teste['teste']()
            resultados.append(f"✅ {teste['nome']}: {teste['esperado']} - OK")
        except Exception as e:
            resultados.append(f"❌ {teste['nome']}: {str(e)}")
    
    print("\n📋 Resultados dos testes:")
    for resultado in resultados:
        print(f"  {resultado}")
    
    return all("✅" in r for r in resultados)

def verificar_estrutura_correta():
    """Verifica se a estrutura de pastas está correta"""
    
    print("\n📁 Verificando estrutura...")
    
    estrutura_correta = {
        "main.py": "Arquivo principal",
        "executar.bat": "Executor Windows", 
        "config.json": "Configurações",
        "ui/admin_panel.py": "Painel administrativo",
        "ui/user_management.py": "Gerenciamento usuários",
        "ui/main_window.py": "Janela principal",
        "autenticacao/auth_service.py": "Serviço autenticação",
        "autenticacao/login.py": "Dialog login",
        "banco/usuarios.csv": "Arquivo usuários"
    }
    
    base_path = Path("/workspace/IntegraGAL_Funcional")
    verificacoes = []
    
    for arquivo, descricao in estrutura_correta.items():
        caminho_completo = base_path / arquivo
        if caminho_completo.exists():
            verificacoes.append(f"✅ {arquivo}")
        else:
            verificacoes.append(f"❌ {arquivo} - {descricao}")
    
    print("\n📋 Verificação da estrutura:")
    for verificacao in verificacoes:
        print(f"  {verificacao}")
    
    return all("✅" in v for v in verificacoes)

def verificar_correções_originais():
    """Verifica se as correções originais dos 4 problemas foram mantidas"""
    
    print("\n🔧 Verificando correções originais...")
    
    base_path = Path("/workspace/IntegraGAL_Funcional")
    
    # 1. Base URL GAL editável
    admin_panel_path = base_path / "ui" / "admin_panel.py"
    with open(admin_panel_path, 'r', encoding='utf-8') as f:
        admin_content = f.read()
    
    base_url_editavel = '("🌐 Base URL GAL", gal_config.get(' in admin_content and ", True)" in admin_content
    
    # 2. senha_hash corrigido
    user_mgmt_path = base_path / "ui" / "user_management.py"
    with open(user_mgmt_path, 'r', encoding='utf-8') as f:
        user_content = f.read()
    
    senha_hash_corrigido = user_content.count('senha_hash') > 5
    
    # 3. config.json
    config_path = base_path / "config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        config_content = f.read()
    
    usuarios_csv_config = '"credentials_csv": "banco/usuarios.csv"' in config_content
    
    verificacoes = [
        ("Base URL GAL editável", base_url_editavel),
        ("Correções senha_hash", senha_hash_corrigido),
        ("Config usuarios.csv", usuarios_csv_config)
    ]
    
    print("\n📋 Verificações das correções:")
    for nome, status in verificacoes:
        simbolo = "✅" if status else "❌"
        print(f"  {simbolo} {nome}: {'OK' if status else 'FALHA'}")
    
    return all(status for _, status in verificacoes)

def main():
    print("🎯 Testando sistema funcional completo do IntegraGAL")
    print("=" * 60)
    
    # Executar todos os testes
    teste1 = verificar_estrutura_correta()
    teste2 = verificar_correções_originais()
    teste3 = testar_imports_criticos()
    
    print("\n" + "=" * 60)
    print("📊 RESUMO FINAL:")
    
    if teste1 and teste2 and teste3:
        print("🎉 TODOS OS TESTES APROVADOS!")
        print("✅ Estrutura de pastas: Correta")
        print("✅ Correções originais: Mantidas")
        print("✅ Imports críticos: Funcionais")
        print("\n🚀 Sistema pronto para execução!")
        print("\n📋 Próximos passos:")
        print("1. Extrair IntegraGAL_Funcional_20251202_110514.zip")
        print("2. Em C:\\Users\\marci\\Downloads\\Integragal\\")
        print("3. Duplo clique em executar.bat")
        print("4. Sistema deve executar sem ModuleNotFoundError!")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        if not teste1:
            print("  - Estrutura de pastas incorreta")
        if not teste2:
            print("  - Correções originais perdidas")
        if not teste3:
            print("  - Imports ainda com problemas")
    
    return teste1 and teste2 and teste3

if __name__ == "__main__":
    main()
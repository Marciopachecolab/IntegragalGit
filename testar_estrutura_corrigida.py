#!/usr/bin/env python3
"""
Script para testar se a estrutura corrigida funciona adequadamente
"""

import os
import sys
import importlib.util
from pathlib import Path

def testar_imports():
    """Testa se os imports estão funcionando na estrutura corrigida"""
    
    print("🧪 Testando imports na estrutura corrigida...")
    
    # Simular ambiente da estrutura corrigida
    estrutura_path = "/workspace/IntegraGAL_EstruturaCorreta"
    sys.path.insert(0, estrutura_path)
    
    testes = [
        {
            'nome': 'AuthService',
            'modulo': 'auth_service',
            'classe': 'AuthService'
        },
        {
            'nome': 'AdminPanel',
            'modulo': 'ui.admin_panel',
            'classe': 'AdminPanel'
        },
        {
            'nome': 'UserManagementPanel',
            'modulo': 'ui.user_management',
            'classe': 'UserManagementPanel'
        }
    ]
    
    resultados = []
    
    for teste in testes:
        try:
            modulo = importlib.import_module(teste['modulo'])
            classe = getattr(modulo, teste['classe'])
            resultados.append(f"✅ {teste['nome']}: Import OK")
        except Exception as e:
            resultados.append(f"❌ {teste['nome']}: {str(e)}")
    
    print("\n📋 Resultados dos testes:")
    for resultado in resultados:
        print(f"  {resultado}")
    
    return all("✅" in r for r in resultados)

def verificar_estrutura_pastas():
    """Verifica se a estrutura de pastas está correta"""
    
    print("\n📁 Verificando estrutura de pastas...")
    
    estrutura_correta = [
        "main.py",
        "executar.bat", 
        "config.json",
        "ui/admin_panel.py",
        "ui/user_management.py",
        "autenticacao/auth_service.py",
        "banco/usuarios.csv"
    ]
    
    base_path = Path("/workspace/IntegraGAL_EstruturaCorreta")
    verificacoes = []
    
    for arquivo in estrutura_correta:
        caminho_completo = base_path / arquivo
        if caminho_completo.exists():
            verificacoes.append(f"✅ {arquivo}")
        else:
            verificacoes.append(f"❌ {arquivo} - NÃO ENCONTRADO")
    
    print("\n📋 Verificação da estrutura:")
    for verificacao in verificacoes:
        print(f"  {verificacao}")
    
    return all("✅" in v for v in verificacoes)

def verificar_correções_especificas():
    """Verifica se as correções específicas foram aplicadas"""
    
    print("\n🔧 Verificando correções específicas...")
    
    base_path = Path("/workspace/IntegraGAL_EstruturaCorreta")
    
    # 1. Verificar campo Base URL GAL editável
    admin_panel_path = base_path / "ui" / "admin_panel.py"
    with open(admin_panel_path, 'r', encoding='utf-8') as f:
        admin_content = f.read()
    
    base_url_editavel = '("🌐 Base URL GAL", gal_config.get(' in admin_content and ", True)" in admin_content
    
    # 2. Verificar correções senha_hash
    user_mgmt_path = base_path / "ui" / "user_management.py"
    with open(user_mgmt_path, 'r', encoding='utf-8') as f:
        user_content = f.read()
    
    senha_hash_corrigido = user_content.count('senha_hash') > 5  # Deve ter várias ocorrências
    sem_senha_indevida = "'senha'" not in user_content or user_content.count("'senha'") < 3
    
    # 3. Verificar config.json
    config_path = base_path / "config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        config_content = f.read()
    
    usuarios_csv_config = '"credentials_csv": "banco/usuarios.csv"' in config_content
    
    verificacoes = [
        ("Base URL GAL editável", base_url_editavel),
        ("Correções senha_hash", senha_hash_corrigido),
        ("Config usuarios.csv", usuarios_csv_config),
        ("Imports corrigidos", sem_senha_indevida)
    ]
    
    print("\n📋 Verificações técnicas:")
    for nome, status in verificacoes:
        simbolo = "✅" if status else "❌"
        print(f"  {simbolo} {nome}: {'OK' if status else 'FALHA'}")
    
    return all(status for _, status in verificacoes)

def main():
    print("🎯 Testando estrutura corrigida do IntegraGAL")
    print("=" * 50)
    
    # Executar todos os testes
    teste1 = verificar_estrutura_pastas()
    teste2 = verificar_correções_especificas()
    teste3 = testar_imports()
    
    print("\n" + "=" * 50)
    print("📊 RESUMO FINAL:")
    
    if teste1 and teste2 and teste3:
        print("🎉 TODOS OS TESTES APROVADOS!")
        print("✅ Estrutura de pastas: Correta")
        print("✅ Correções implementadas: OK")
        print("✅ Imports funcionando: OK")
        print("\n🚀 Package pronto para uso!")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        if not teste1:
            print("  - Estrutura de pastas incorreta")
        if not teste2:
            print("  - Correções não implementadas")
        if not teste3:
            print("  - Imports com problemas")
    
    return teste1 and teste2 and teste3

if __name__ == "__main__":
    main()
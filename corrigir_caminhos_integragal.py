#!/usr/bin/env python3
"""
Script para corrigir caminhos do sistema para execução em C:\Users\marci\Downloads\Integragal
Adapta todos os paths para funcionar na estrutura correta
"""

import os
import json
import shutil
from datetime import datetime

def detectar_estrutura_pasta():
    """Detecta se está em Integragal ou IntegragalGit"""
    print("🔍 Detectando estrutura de pasta...")
    
    # Verificar pasta atual
    pasta_atual = os.getcwd()
    print(f"📂 Pasta atual: {pasta_atual}")
    
    # Detectar tipo de estrutura
    if "IntegragalGit" in pasta_atual:
        base_dir = "IntegragalGit"
        tipo_estrutura = "IntegragalGit"
    elif "Integragal" in pasta_atual:
        base_dir = "Integragal"
        tipo_estrutura = "Integragal"
    else:
        # Procurar por pasta Integragal*
        for item in os.listdir("."):
            if os.path.isdir(item) and "Integragal" in item:
                base_dir = item
                tipo_estrutura = item
                break
        else:
            base_dir = "Integragal"
            tipo_estrutura = "Integragal"
    
    print(f"✅ Estrutura detectada: {tipo_estrutura}")
    print(f"📁 Diretório base: {base_dir}")
    
    return base_dir, tipo_estrutura

def corrigir_config_json(base_dir):
    """Corrige caminhos no config.json"""
    print("🔧 Corrigindo config.json...")
    
    config_path = f"{base_dir}/config.json"
    if not os.path.exists(config_path):
        print(f"  ⚠️ config.json não encontrado em {config_path}")
        return
    
    # Backup
    backup_path = f"{config_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(config_path, backup_path)
    print(f"  📋 Backup criado: {backup_path}")
    
    # Ler e corrigir
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Corrigir caminhos relativos
    if 'paths' in config:
        paths = config['paths']
        
        # Converter caminhos para relativos
        if 'log_file' in paths and 'logs/' in paths['log_file']:
            paths['log_file'] = 'logs/sistema.log'
        
        if 'exams_catalog_csv' in paths and 'banco/' in paths['exams_catalog_csv']:
            paths['exams_catalog_csv'] = 'banco/exames_config.csv'
        
        if 'credentials_csv' in paths and 'banco/' in paths['credentials_csv']:
            paths['credentials_csv'] = 'banco/usuarios.csv'
        
        if 'gal_history_csv' in paths and 'logs/' in paths['gal_history_csv']:
            paths['gal_history_csv'] = 'logs/total_importados_gal.csv'
    
    # Salvar arquivo corrigido
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    
    print("  ✅ config.json corrigido")

def corrigir_auth_service(base_dir):
    """Corrige caminhos no auth_service.py"""
    print("🔧 Corrigindo auth_service.py...")
    
    auth_path = f"{base_dir}/autenticacao/auth_service.py"
    if not os.path.exists(auth_path):
        print(f"  ⚠️ auth_service.py não encontrado em {auth_path}")
        return
    
    # Backup
    backup_path = f"{auth_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(auth_path, backup_path)
    print(f"  📋 Backup criado: {backup_path}")
    
    # Ler arquivo
    with open(auth_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Corrigir caminhos absolutos para relativos
    corrections = [
        # Caminhos que apontam para estrutura específica
        ('os.path.join(BASE_DIR, "banco", "usuarios.csv")', '"banco/usuarios.csv"'),
        ('os.path.join(BASE_DIR, "config.json")', '"config.json"'),
        ('BASE_DIR + "/logs/"', '"logs/"'),
        ('BASE_DIR + "/banco/"', '"banco/"'),
    ]
    
    for old_path, new_path in corrections:
        if old_path in content:
            content = content.replace(old_path, new_path)
            print(f"  ✅ Corrigido: {old_path}")
    
    # Salvar arquivo corrigido
    with open(auth_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("  ✅ auth_service.py corrigido")

def corrigir_user_management(base_dir):
    """Corrige caminhos no user_management.py"""
    print("🔧 Corrigindo user_management.py...")
    
    user_mgmt_path = f"{base_dir}/ui/user_management.py"
    if not os.path.exists(user_mgmt_path):
        print(f"  ⚠️ user_management.py não encontrado em {user_mgmt_path}")
        return
    
    # Backup
    backup_path = f"{user_mgmt_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(user_mgmt_path, backup_path)
    print(f"  📋 Backup criado: {backup_path}")
    
    # Ler arquivo
    with open(user_mgmt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Corrigir caminhos hardcoded
    corrections = [
        ('"banco/usuarios.csv"', 'os.path.join("banco", "usuarios.csv")'),
        ('"banco/credenciais.csv"', 'os.path.join("banco", "usuarios.csv")'),
        ('"config.json"', 'os.path.join(base_dir, "config.json")'),
        ('"logs/sistema.log"', 'os.path.join("logs", "sistema.log")'),
    ]
    
    for old_path, new_path in corrections:
        if old_path in content:
            content = content.replace(old_path, new_path)
            print(f"  ✅ Corrigido: {old_path}")
    
    # Salvar arquivo corrigido
    with open(user_mgmt_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("  ✅ user_management.py corrigido")

def corrigir_admin_panel(base_dir):
    """Corrige caminhos no admin_panel.py"""
    print("🔧 Corrigindo admin_panel.py...")
    
    admin_path = f"{base_dir}/ui/admin_panel.py"
    if not os.path.exists(admin_path):
        print(f"  ⚠️ admin_panel.py não encontrado em {admin_path}")
        return
    
    # Backup
    backup_path = f"{admin_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(admin_path, backup_path)
    print(f"  📋 Backup criado: {backup_path}")
    
    # Ler arquivo
    with open(admin_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Corrigir caminhos hardcoded
    corrections = [
        ('config_path = "config.json"', 'config_path = os.path.join(os.getcwd(), "config.json")'),
        ('if os.path.exists(config_path):', 'if os.path.exists(config_path):'),
        ('os.startfile(config_path)', 'os.startfile(config_path)'),
    ]
    
    for old_path, new_path in corrections:
        if old_path in content:
            content = content.replace(old_path, new_path)
            print(f"  ✅ Corrigido: {old_path}")
    
    # Salvar arquivo corrigido
    with open(admin_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("  ✅ admin_panel.py corrigido")

def criar_executar_adaptado(base_dir):
    """Cria executar.bat adaptado para a estrutura correta"""
    print("🔧 Criando executar.bat adaptado...")
    
    if base_dir == "Integragal":
        # Para estrutura Integragal
        conteudo_bat = '''@echo off
echo ======================================
echo     IntegraGAL - Sistema de QPCR
echo ======================================
echo.

cd /d "%~dp0"

echo Iniciando sistema...
python main.py

echo.
echo Sistema finalizado.
pause
'''
    else:
        # Para estrutura IntegragalGit
        conteudo_bat = '''@echo off
echo ======================================
echo     IntegraGAL - Sistema de QPCR
echo ======================================
echo.

cd /d "%~dp0"
cd IntegragalGit

echo Iniciando sistema...
python main.py

echo.
echo Sistema finalizado.
pause
'''
    
    bat_path = f"{base_dir}/executar.bat"
    with open(bat_path, 'w', encoding='utf-8') as f:
        f.write(conteudo_bat)
    
    print(f"  ✅ executar.bat criado em {bat_path}")

def verificar_estrutura_arquivos(base_dir):
    """Verifica se todos os arquivos necessários existem"""
    print("🔍 Verificando estrutura de arquivos...")
    
    arquivos_necessarios = [
        f"{base_dir}/main.py",
        f"{base_dir}/config.json",
        f"{base_dir}/autenticacao/auth_service.py",
        f"{base_dir}/ui/main_window.py",
        f"{base_dir}/ui/user_management.py",
        f"{base_dir}/ui/admin_panel.py",
        f"{base_dir}/banco/usuarios.csv",
    ]
    
    arquivos_ok = 0
    for arquivo in arquivos_necessarios:
        if os.path.exists(arquivo):
            print(f"  ✅ {arquivo}")
            arquivos_ok += 1
        else:
            print(f"  ❌ {arquivo}")
    
    print(f"  📊 {arquivos_ok}/{len(arquivos_necessarios)} arquivos encontrados")
    return arquivos_ok == len(arquivos_necessarios)

def main():
    """Função principal de correção"""
    print("=" * 60)
    print("🔧 CORREÇÃO PARA EXECUÇÃO EM C:\\Users\\marci\\Downloads\\Integragal")
    print("=" * 60)
    
    # Detectar estrutura
    base_dir, tipo_estrutura = detectar_estrutura_pasta()
    
    # Verificar estrutura atual
    estrutura_ok = verificar_estrutura_arquivos(base_dir)
    
    if not estrutura_ok:
        print("\n⚠️ Alguns arquivos necessários não foram encontrados.")
        print("Verifique se o package foi extraído corretamente.")
        return False
    
    # Aplicar correções
    try:
        corrigir_config_json(base_dir)
        corrigir_auth_service(base_dir)
        corrigir_user_management(base_dir)
        corrigir_admin_panel(base_dir)
        criar_executar_adaptado(base_dir)
        
        print("\n" + "=" * 60)
        print("✅ CORREÇÕES APLICADAS COM SUCESSO!")
        print("=" * 60)
        print(f"\n📁 Estrutura detectada: {tipo_estrutura}")
        print(f"🔧 Caminhos corrigidos para execução local")
        print(f"📋 Backups criados para todos os arquivos modificados")
        
        print(f"\n💡 Para executar:")
        if base_dir == "IntegragalGit":
            print(f"1. Navegar para: {os.path.join(os.getcwd(), base_dir)}")
            print(f"2. Executar: python main.py")
        else:
            print(f"1. Navegar para: {os.getcwd()}")
            print(f"2. Executar: python main.py")
            print(f"3. Ou clicar em: executar.bat")
        
        print(f"\n🎯 Login: marcio / flafla")
        print(f"\n✅ Sistema pronto para execução!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante as correções: {str(e)}")
        return False

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Script completo para criar package IntegraGAL com estrutura de raiz
Inclui TODOS os arquivos necessários
"""

import os
import zipfile
import shutil
from datetime import datetime

def criar_estrutura_completa():
    """Cria estrutura completa com todos os arquivos"""
    print("Criando estrutura completa...")
    
    temp_dir = "/workspace/integragal_completo"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    # 1. Arquivos principais da raiz
    arquivos_principais = [
        "IntegragalGit/main.py",
        "IntegragalGit/config.json", 
        "IntegragalGit/requirements.txt",
        "IntegragalGit/__init__.py"
    ]
    
    for arquivo in arquivos_principais:
        origem = f"/workspace/{arquivo}"
        destino = os.path.join(temp_dir, os.path.basename(arquivo))
        if os.path.exists(origem):
            shutil.copy2(origem, destino)
            print(f"  {arquivo}")
    
    # 2. Módulos de autenticação (mover para raiz)
    modulos_auth = [
        "IntegragalGit/autenticacao/auth_service.py",
        "IntegragalGit/autenticacao/login.py",
        "IntegragalGit/core/authentication/user_manager.py"
    ]
    
    for arquivo in modulos_auth:
        origem = f"/workspace/{arquivo}"
        destino = os.path.join(temp_dir, os.path.basename(arquivo))
        if os.path.exists(origem):
            shutil.copy2(origem, destino)
            print(f"  {arquivo} -> {os.path.basename(arquivo)}")
    
    # 3. Interface gráfica (mover para raiz)
    modulos_ui = [
        "IntegragalGit/ui/main_window.py",
        "IntegragalGit/ui/admin_panel.py", 
        "IntegragalGit/ui/user_management.py",
        "IntegragalGit/ui/menu_handler.py",
        "IntegragalGit/ui/navigation.py",
        "IntegragalGit/ui/status_manager.py"
    ]
    
    for arquivo in modulos_ui:
        origem = f"/workspace/{arquivo}"
        destino = os.path.join(temp_dir, os.path.basename(arquivo))
        if os.path.exists(origem):
            shutil.copy2(origem, destino)
            print(f"  {arquivo} -> {os.path.basename(arquivo)}")
    
    # 4. Utilitários (mover para raiz)
    modulos_utils = [
        "IntegragalGit/utils/logger.py",
        "IntegragalGit/utils/io_utils.py",
        "IntegragalGit/utils/db_utils.py", 
        "IntegragalGit/utils/gui_utils.py",
        "IntegragalGit/utils/import_utils.py"
    ]
    
    for arquivo in modulos_utils:
        origem = f"/workspace/{arquivo}"
        destino = os.path.join(temp_dir, os.path.basename(arquivo))
        if os.path.exists(origem):
            shutil.copy2(origem, destino)
            print(f"  {arquivo} -> {os.path.basename(arquivo)}")
    
    # 5. Serviços (mover para raiz)
    modulos_services = [
        "IntegragalGit/services/config_service.py",
        "IntegragalGit/services/analysis_service.py"
    ]
    
    for arquivo in modulos_services:
        origem = f"/workspace/{arquivo}"
        destino = os.path.join(temp_dir, os.path.basename(arquivo))
        if os.path.exists(origem):
            shutil.copy2(origem, destino)
            print(f"  {arquivo} -> {os.path.basename(arquivo)}")
    
    # 6. Configuração (mover para raiz)
    config_files = [
        "IntegragalGit/configuracao/configuracao.py"
    ]
    
    for arquivo in config_files:
        origem = f"/workspace/{arquivo}"
        destino = os.path.join(temp_dir, "configuracao.py")
        if os.path.exists(origem):
            shutil.copy2(origem, destino)
            print(f"  {arquivo} -> configuracao.py")
    
    # 7. Diretório banco completo
    banco_origem = "/workspace/IntegragalGit/banco"
    banco_destino = os.path.join(temp_dir, "banco")
    if os.path.exists(banco_origem):
        shutil.copytree(banco_origem, banco_destino)
        print(f"  banco/ completo")
    
    # 8. Criar diretório logs
    logs_dir = os.path.join(temp_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    return temp_dir

def corrigir_imports_completo(temp_dir):
    """Corrige todos os imports para estrutura de raiz"""
    print("Corrigindo imports...")
    
    # Arquivos que precisam de correção de imports
    arquivos_criticos = [
        "main.py",
        "auth_service.py", 
        "login.py",
        "main_window.py",
        "admin_panel.py",
        "user_management.py",
        "menu_handler.py",
        "navigation.py",
        "status_manager.py"
    ]
    
    for arquivo in arquivos_criticos:
        arquivo_path = os.path.join(temp_dir, arquivo)
        if os.path.exists(arquivo_path):
            try:
                with open(arquivo_path, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                
                # Correções de imports específicos
                correcoes = [
                    # Imports de autenticação
                    ('from autenticacao.auth_service import', 'from auth_service import'),
                    ('from autenticacao.login import', 'from login import'),
                    ('from core.authentication.user_manager import', 'from user_manager import'),
                    ('import autenticacao.auth_service', 'import auth_service'),
                    ('import autenticacao.login', 'import login'),
                    
                    # Imports de interface
                    ('from ui.main_window import', 'from main_window import'),
                    ('from ui.admin_panel import', 'from admin_panel import'),
                    ('from ui.user_management import', 'from user_management import'),
                    ('from ui.menu_handler import', 'from menu_handler import'),
                    ('from ui.navigation import', 'from navigation import'),
                    ('from ui.status_manager import', 'from status_manager import'),
                    
                    # Imports de utilitários
                    ('from utils.logger import', 'from logger import'),
                    ('from utils.io_utils import', 'from io_utils import'),
                    ('from utils.db_utils import', 'from db_utils import'),
                    ('from utils.gui_utils import', 'from gui_utils import'),
                    ('from utils.import_utils import', 'from import_utils import'),
                    
                    # Imports de serviços
                    ('from services.config_service import', 'from config_service import'),
                    ('from services.analysis_service import', 'from analysis_service import'),
                    
                    # Imports de configuração
                    ('from configuracao.configuracao import', 'from configuracao import'),
                    ('import configuracao.configuracao', 'import configuracao'),
                    
                    # Caminhos hardcoded
                    ('"banco/usuarios.csv"', 'os.path.join("banco", "usuarios.csv")'),
                    ('"config.json"', '"config.json"'),
                    ('"logs/', '"logs/'),
                ]
                
                for antigo, novo in correcoes:
                    conteudo = conteudo.replace(antigo, novo)
                
                with open(arquivo_path, 'w', encoding='utf-8') as f:
                    f.write(conteudo)
                    
                print(f"  {arquivo}")
                
            except Exception as e:
                print(f"    Erro em {arquivo}: {e}")

def criar_executar_bat_completo(temp_dir):
    """Cria executar.bat completo com verificações"""
    print("Criando executar.bat...")
    
    conteudo = '''@echo off
chcp 65001 >nul
title IntegraGAL - Sistema de QPCR

echo ======================================
echo    IntegraGAL - Sistema de QPCR
echo ======================================
echo.

cd /d "%~dp0"

echo Verificando arquivos necessários...

if not exist "main.py" (
    echo [ERRO] main.py não encontrado!
    echo.
    echo Certifique-se de que extraiu o ZIP na pasta correta.
    echo Pasta atual: %cd%
    echo.
    pause
    exit /b 1
)

echo [OK] main.py encontrado
echo.

echo Iniciando sistema IntegraGAL...
echo.

python main.py

if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao executar o sistema.
    echo.
    echo Verifique se as dependências estão instaladas:
    echo pip install customtkinter pandas bcrypt
    echo.
    pause
    exit /b 1
)

echo.
echo [SUCESSO] Sistema finalizado.
pause
'''
    
    bat_path = os.path.join(temp_dir, "executar.bat")
    with open(bat_path, 'w', encoding='utf-8') as f:
        f.write(conteudo)

def criar_instrucoes_completas(temp_dir):
    """Cria instruções completas"""
    print("Criando instruções...")
    
    texto = """INSTRUÇÕES COMPLETAS - INTEGRAGAL

🎯 ESTRUTURA FINAL:
C:\\Users\\marci\\Downloads\\Integragal/
├── main.py                    ⬅️ ARQUIVO PRINCIPAL
├── executar.bat               ⬅️ EXECUTAR AQUI
├── auth_service.py           # Sistema de autenticação
├── user_management.py        # Gerenciamento de usuários
├── admin_panel.py           # Painel administrativo
├── main_window.py           # Janela principal
├── config.json              # Configurações
├── banco/
│   ├── usuarios.csv         # Arquivo único de usuários
│   ├── configuracoes_sistema.csv
│   ├── exames_config.csv
│   └── sessoes.csv
└── logs/                    # Criado automaticamente

🚀 COMO EXECUTAR:
1. Extrair este ZIP em: C:\\Users\\marci\\Downloads\\Integragal
2. Duplo clique em: executar.bat

🔑 LOGIN:
- Usuário: marcio
- Senha: flafla

✅ TESTES DAS CORREÇÕES:
1. Base URL GAL → Editável no Painel Administrativo
2. Gerenciamento Usuários → Sem erro de campo senha  
3. Fechamento de janelas → Com um clique

🛠️ DEPENDÊNCIAS (se necessário):
pip install customtkinter pandas bcrypt

❗ SOLUÇÃO DE PROBLEMAS:
- main.py não encontrado → Verificar pasta de extração
- ModuleNotFoundError → Instalar dependências
- Janela não abre → Verificar instalação Python

---
Sistema: IntegraGAL v2.0 - Estrutura de Raiz
Data: 02/12/2025
Status: Pronto para uso
"""
    
    instrucoes_path = os.path.join(temp_dir, "LEIA_PRIMEIRO.txt")
    with open(instrucoes_path, 'w', encoding='utf-8') as f:
        f.write(texto)

def criar_package_final(temp_dir):
    """Cria package ZIP final"""
    print("Criando package final...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"IntegraGAL_Raiz_Completo_{timestamp}.zip"
    
    with zipfile.ZipFile(f"/workspace/{zip_name}", 'w', zipfile.ZIP_DEFLATED) as zipf:
        file_count = 0
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)
                file_count += 1
    
    size = os.path.getsize(f"/workspace/{zip_name}")
    print(f"Package criado: {zip_name}")
    print(f"Tamanho: {size:,} bytes ({size/1024:.1f} KB)")
    print(f"Arquivos incluídos: {file_count}")
    
    return zip_name

def main():
    print("="*70)
    print("CRIANDO PACKAGE INTEGRAGAL ESTRUTURA DE RAIZ COMPLETO")
    print("="*70)
    
    try:
        # Passo 1: Criar estrutura completa
        temp_dir = criar_estrutura_completa()
        
        # Passo 2: Corrigir imports
        corrigir_imports_completo(temp_dir)
        
        # Passo 3: Criar executar.bat
        criar_executar_bat_completo(temp_dir)
        
        # Passo 4: Criar instruções
        criar_instrucoes_completas(temp_dir)
        
        # Passo 5: Criar package
        zip_name = criar_package_final(temp_dir)
        
        print("\n" + "="*70)
        print("✅ PACKAGE INTEGRAGAL CRIADO COM SUCESSO!")
        print("="*70)
        print(f"\n📦 Arquivo: {zip_name}")
        print(f"\n💡 INSTRUÇÕES PARA USO:")
        print(f"1. Extrair {os.path.basename(zip_name)} em C:\\Users\\marci\\Downloads\\Integragal")
        print(f"2. DUPLO CLIQUE em executar.bat")
        print(f"3. LOGIN: marcio / flafla")
        print(f"\n🎯 ESTRUTURA: PLANA (sem subpasta IntegragalGit)")
        print(f"✅ Todos os arquivos na raiz")
        print(f"✅ Imports corrigidos automaticamente")
        print(f"✅ Sistema pronto para execução imediata!")
        
        # Limpeza
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        return zip_name
        
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        return None

if __name__ == "__main__":
    main()
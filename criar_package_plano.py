#!/usr/bin/env python3
"""
Cria package com estrutura plana na raiz - sem subpasta IntegragalGit
"""

import os
import zipfile
import shutil
from datetime import datetime

def preparar_estrutura_raiz():
    """Prepara arquivos na estrutura de raiz"""
    print("Preparando estrutura de raiz...")
    
    temp_dir = "/workspace/integragal_plano"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    # Arquivos principais copiados diretamente para raiz
    arquivos_raiz = {
        "IntegragalGit/main.py": "main.py",
        "IntegragalGit/config.json": "config.json", 
        "IntegragalGit/requirements.txt": "requirements.txt",
        "IntegragalGit/__init__.py": "__init__.py",
    }
    
    for origem, destino in arquivos_raiz.items():
        origem_path = f"/workspace/{origem}"
        destino_path = os.path.join(temp_dir, destino)
        if os.path.exists(origem_path):
            shutil.copy2(origem_path, destino_path)
            print(f"  {origem} -> {destino}")
    
    # Diretório banco completo
    banco_origem = "/workspace/IntegragalGit/banco"
    banco_destino = os.path.join(temp_dir, "banco")
    if os.path.exists(banco_origem):
        shutil.copytree(banco_origem, banco_destino)
        print(f"  banco/ completo copiado")
    
    # Criar logs
    os.makedirs(os.path.join(temp_dir, "logs"), exist_ok=True)
    
    return temp_dir

def corrigir_imports_e_caminhos(temp_dir):
    """Corrige imports e caminhos para estrutura plana"""
    print("Corrigindo imports e caminhos...")
    
    # Listar todos os arquivos Python para corrigir
    arquivos_python = []
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            if file.endswith('.py'):
                arquivos_python.append(os.path.join(root, file))
    
    for arquivo_py in arquivos_python:
        try:
            with open(arquivo_py, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Corrigir imports problemáticos
            correcoes_import = [
                ('from autenticacao.auth_service import', 'from auth_service import'),
                ('from ui.user_management import', 'from user_management import'),
                ('from ui.admin_panel import', 'from admin_panel import'),
                ('from utils.', 'from '),
                ('from services.', 'from '),
                ('from configuracao.', 'from configuracao_'),
                ('import autenticacao.auth_service', 'import auth_service'),
                ('import ui.user_management', 'import user_management'),
                ('import ui.admin_panel', 'import admin_panel'),
            ]
            
            for antigo, novo in correcoes_import:
                conteudo = conteudo.replace(antigo, novo)
            
            # Corrigir caminhos hardcoded
            correcoes_caminho = [
                ('"banco/usuarios.csv"', 'os.path.join("banco", "usuarios.csv")'),
                ('"config.json"', '"config.json"'),
                ('"logs/', '"logs/'),
            ]
            
            for antigo, novo in correcoes_caminho:
                conteudo = conteudo.replace(antigo, novo)
            
            with open(arquivo_py, 'w', encoding='utf-8') as f:
                f.write(conteudo)
                
        except Exception as e:
            print(f"    Erro em {arquivo_py}: {e}")

def criar_executar_bat(temp_dir):
    """Cria arquivo executar.bat"""
    print("Criando executar.bat...")
    
    conteudo = '''@echo off
chcp 65001 >nul
echo ======================================
echo    IntegraGAL - Sistema de QPCR  
echo ======================================
echo.

cd /d "%~dp0"

echo Verificando arquivos...
if not exist "main.py" (
    echo main.py não encontrado!
    pause
    exit /b 1
)

echo Arquivos OK
echo.
echo Iniciando sistema...
python main.py
echo.
echo Finalizado.
pause
'''
    
    bat_path = os.path.join(temp_dir, "executar.bat")
    with open(bat_path, 'w', encoding='utf-8') as f:
        f.write(conteudo)

def criar_instrucoes_simples(temp_dir):
    """Cria instruções simples"""
    print("Criando instruções...")
    
    texto = """INSTRUÇÕES DE EXECUÇÃO

1. Extrair este arquivo ZIP em:
   C:\\Users\\marci\\Downloads\\Integragal

2. Duplo clique em:
   executar.bat

3. Login:
   Usuário: marcio
   Senha: flafla

TESTES:
- Base URL GAL deve ser editável
- Gerenciamento usuários sem erro de campo senha
- Janelas devem fechar com um clique

DEPENDÊNCIAS (se necessário):
pip install customtkinter pandas bcrypt
"""
    
    instrucoes_path = os.path.join(temp_dir, "INSTRUCOES.txt")
    with open(instrucoes_path, 'w', encoding='utf-8') as f:
        f.write(texto)

def criar_package_zip(temp_dir):
    """Cria o arquivo ZIP final"""
    print("Criando package ZIP...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"IntegraGAL_Raiz_{timestamp}.zip"
    
    with zipfile.ZipFile(f"/workspace/{zip_name}", 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)
    
    size = os.path.getsize(f"/workspace/{zip_name}")
    print(f"Package criado: {zip_name} ({size} bytes)")
    return zip_name

def main():
    print("="*60)
    print("CRIANDO PACKAGE ESTRUTURA DE RAIZ")
    print("="*60)
    
    temp_dir = preparar_estrutura_raiz()
    corrigir_imports_e_caminhos(temp_dir)
    criar_executar_bat(temp_dir)
    criar_instrucoes_simples(temp_dir)
    
    zip_name = criar_package_zip(temp_dir)
    
    print("="*60)
    print("PACKAGE CRIADO COM SUCESSO!")
    print("="*60)
    print(f"Arquivo: {zip_name}")
    print("Para usar:")
    print("1. Extrair em C:\\Users\\marci\\Downloads\\Integragal")
    print("2. Duplo clique em executar.bat")
    print("3. Login: marcio / flafla")
    
    # Limpeza
    shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()
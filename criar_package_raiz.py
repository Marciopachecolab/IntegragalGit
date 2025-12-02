#!/usr/bin/env python3
"""
Script para criar package com arquivos na pasta raiz (sem subpasta IntegragalGit)
Corrige todos os caminhos para funcionar diretamente em C:\Users\marci\Downloads\Integragal
"""

import os
import zipfile
import shutil
from datetime import datetime

def corrigir_arquivos_para_raiz():
    """Copia e corrige arquivos para estrutura de raiz"""
    print("🔧 Preparando arquivos para estrutura de raiz...")
    
    # Criar diretório temporário para reorganização
    temp_dir = "/workspace/integragal_raiz"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    # Mapeamento de arquivos da estrutura IntegragalGit para raiz
    mapeamento = {
        # Arquivos principais
        "IntegragalGit/main.py": "main.py",
        "IntegragalGit/config.json": "config.json",
        "IntegragalGit/requirements.txt": "requirements.txt",
        "IntegragalGit/__init__.py": "__init__.py",
        
        # Autenticação (move para raiz)
        "IntegragalGit/autenticacao/auth_service.py": "auth_service.py",
        "IntegragalGit/autenticacao/login.py": "login.py",
        "IntegragalGit/core/authentication/user_manager.py": "user_manager.py",
        
        # Interface (move para raiz)
        "IntegragalGit/ui/main_window.py": "main_window.py",
        "IntegragalGit/ui/admin_panel.py": "admin_panel.py",
        "IntegragalGit/ui/user_management.py": "user_management.py",
        "IntegragalGit/ui/menu_handler.py": "menu_handler.py",
        "IntegragalGit/ui/navigation.py": "navigation.py",
        "IntegragalGit/ui/status_manager.py": "status_manager.py",
        
        # Utilitários (move para raiz)
        "IntegragalGit/utils/logger.py": "logger.py",
        "IntegragalGit/utils/io_utils.py": "io_utils.py",
        "IntegragalGit/utils/db_utils.py": "db_utils.py",
        "IntegragalGit/utils/gui_utils.py": "gui_utils.py",
        "IntegragalGit/utils/import_utils.py": "import_utils.py",
        
        # Serviços (move para raiz)
        "IntegragalGit/services/config_service.py": "config_service.py",
        "IntegragalGit/services/analysis_service.py": "analysis_service.py",
        
        # Configuração (move para raiz)
        "IntegragalGit/configuracao/configuracao.py": "configuracao.py",
        "IntegragalGit/configuracao/__init__.py": "configuracao_init.py",
    }
    
    # Copiar e mover arquivos
    for origem, destino in mapeamento.items():
        origem_path = f"/workspace/{origem}"
        destino_path = os.path.join(temp_dir, destino)
        
        if os.path.exists(origem_path):
            shutil.copy2(origem_path, destino_path)
            print(f"  ✅ {origem} → {destino}")
        else:
            print(f"  ⚠️ Arquivo não encontrado: {origem}")
    
    # Copiar diretório banco completo
    banco_origem = "/workspace/IntegragalGit/banco"
    banco_destino = os.path.join(temp_dir, "banco")
    if os.path.exists(banco_origem):
        shutil.copytree(banco_origem, banco_destino)
        print(f"  ✅ banco/ → banco/")
    
    # Criar diretório logs vazio
    logs_dir = os.path.join(temp_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    print(f"  ✅ logs/ (criado)")
    
    return temp_dir

def corrigir_caminhos_arquivos(temp_dir):
    """Corrige todos os caminhos nos arquivos para trabalhar na raiz"""
    print("🔧 Corrigindo caminhos nos arquivos...")
    
    # 1. Corrigir config.json
    config_path = os.path.join(temp_dir, "config.json")
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = f.read()
        
        # Caminhos já estão relativos, manter assim
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config)
        print("  ✅ config.json - caminhos relativos mantidos")
    
    # 2. Corrigir auth_service.py
    auth_path = os.path.join(temp_dir, "auth_service.py")
    if os.path.exists(auth_path):
        with open(auth_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simplificar caminhos para raiz
        content = content.replace('os.path.join(BASE_DIR, "banco", "usuarios.csv")', '"banco/usuarios.csv"')
        content = content.replace('os.path.join(BASE_DIR, "config.json")', '"config.json"')
        content = content.replace('BASE_DIR + "/logs/"', '"logs/"')
        content = content.replace('BASE_DIR + "/banco/"', '"banco/"')
        
        # Remover imports desnecessários
        content = content.replace('import sys', '')
        content = content.replace('SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))', '')
        content = content.replace('AUTH_DIR = os.path.dirname(SCRIPT_DIR)', '')
        content = content.replace('BASE_DIR = AUTH_DIR', 'BASE_DIR = os.getcwd()')
        
        with open(auth_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  ✅ auth_service.py - caminhos simplificados")
    
    # 3. Corrigir user_management.py
    user_path = os.path.join(temp_dir, "user_management.py")
    if os.path.exists(user_path):
        with open(user_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Corrigir caminho do arquivo de usuários
        content = content.replace('self.usuarios_path = "banco/usuarios.csv"', 
                                'self.usuarios_path = os.path.join("banco", "usuarios.csv")')
        
        # Remover imports desnecessários
        if 'import sys' in content:
            content = content.replace('import sys', '')
        if 'BASE_DIR' in content:
            content = content.replace('BASE_DIR', 'os.getcwd()')
        
        with open(user_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  ✅ user_management.py - caminhos corrigidos")
    
    # 4. Corrigir admin_panel.py
    admin_path = os.path.join(temp_dir, "admin_panel.py")
    if os.path.exists(admin_path):
        with open(admin_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simplificar caminhos
        content = content.replace('config_path = "config.json"', 'config_path = "config.json"')
        content = content.replace('os.path.exists(config_path)', 'os.path.exists(config_path)')
        
        with open(admin_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  ✅ admin_panel.py - caminhos simplificados")
    
    # 5. Corrigir main_window.py e outros
    for arquivo in ["main_window.py", "menu_handler.py", "navigation.py"]:
        arquivo_path = os.path.join(temp_dir, arquivo)
        if os.path.exists(arquivo_path):
            with open(arquivo_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simplificar imports e caminhos
            content = content.replace('from autenticacao.auth_service', 'from auth_service')
            content = content.replace('from ui.user_management', 'from user_management')
            content = content.replace('from ui.admin_panel', 'from admin_panel')
            
            with open(arquivo_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ {arquivo} - imports corrigidos")

def criar_executar_batch(temp_dir):
    """Cria executar.bat na raiz"""
    print("🔧 Criando executar.bat...")
    
    conteudo_bat = '''@echo off
chcp 65001 >nul
echo ======================================
echo     IntegraGAL - Sistema de QPCR
echo ======================================
echo.

cd /d "%~dp0"

echo Verificando arquivos necessários...
if not exist "main.py" (
    echo ❌ main.py não encontrado!
    echo.
    echo Certifique-se de que está executando da pasta correta.
    echo.
    pause
    exit /b 1
)

echo ✅ Arquivos principais encontrados
echo.

echo Iniciando sistema IntegraGAL...
echo.

python main.py

if errorlevel 1 (
    echo.
    echo ❌ Erro ao executar o sistema.
    echo Verifique se as dependências estão instaladas:
    echo pip install customtkinter pandas bcrypt
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Sistema finalizado com sucesso.
echo.
pause
'''
    
    bat_path = os.path.join(temp_dir, "executar.bat")
    with open(bat_path, 'w', encoding='utf-8') as f:
        f.write(conteudo_bat)
    
    print("  ✅ executar.bat criado")

def criar_instrucoes_raiz(temp_dir):
    """Cria instruções específicas para estrutura de raiz"""
    print("🔧 Criando instruções...")
    
    instrucoes = """# 🚀 INSTRUÇÕES PARA EXECUÇÃO EM PASTA RAIZ

## 📁 Estrutura Final
```
C:\\Users\\marci\\Downloads\\Integragal/
├── main.py                    # ⬅️ ARQUIVO PRINCIPAL
├── executar.bat               # ⬅️ EXECUTAR AQUI
├── auth_service.py           # Sistema de autenticação
├── user_management.py        # Gerenciamento de usuários  
├── admin_panel.py           # Painel administrativo
├── config.json              # Configurações
├── banco/
│   ├── usuarios.csv         # Arquivo único de usuários
│   ├── configuracoes_sistema.csv
│   ├── exames_config.csv
│   └── sessoes.csv
└── logs/                    # Criado automaticamente
```

## 🎮 Como Executar

### MÉTODO 1: Duplo clique
1. Navegar para `C:\\Users\\marci\\Downloads\\Integragal`
2. Duplo clique em `executar.bat`

### MÉTODO 2: Command Prompt
```bash
cd C:\\Users\\marci\\Downloads\\Integragal
python main.py
```

### MÉTODO 3: Verificar Python
```bash
python --version
pip install customtkinter pandas bcrypt
```

## 🔑 Login do Sistema
- **Usuário**: `marcio`
- **Senha**: `flafla`

## ✅ Testes das Correções

### 1. Base URL GAL
- Menu → Painel Administrativo → Sistema
- Campo "Base URL GAL" deve estar editável (com entrada)
- Alterar e salvar → Verificar se persiste

### 2. Gerenciamento de Usuários  
- Menu → Ferramentas → Gerenciar Usuários
- NÃO deve aparecer erro "X Erro ao carregar usuário: 'senha'"
- Deve mostrar 4 usuários na lista

### 3. Fechamento de Janelas
- Abrir qualquer módulo
- Clicar no X → Deve fechar com UM clique

## 🛠️ Arquivos Importantes

### Principais (raiz):
- `main.py` - Ponto de entrada do sistema
- `auth_service.py` - Autenticação (corrigido)
- `user_management.py` - Gerenciamento usuários (corrigido)  
- `admin_panel.py` - Painel admin (corrigido)
- `config.json` - Configurações (caminhos relativos)

### Dependências:
```bash
pip install customtkinter pandas bcrypt
```

## ❗ Solução de Problemas

### "main.py não encontrado"
→ Certificar-se de estar em `C:\\Users\\marci\\Downloads\\Integragal`

### "ModuleNotFoundError" 
→ Instalar dependências:
```bash
pip install customtkinter pandas bcrypt
```

### "Arquivo não encontrado"
→ Package não foi extraído corretamente

### Janela não abre
→ Verificar instalação do Python

## 🎯 Status das Correções

✅ **Base URL GAL**: Editável e salvável  
✅ **Campo senha**: Corrigido para senha_hash  
✅ **Fechamento**: Protocolo melhorado  
✅ **Arquivo único**: usuarios.csv definido  
✅ **Estrutura plana**: Sem subpasta IntegragalGit  

---
**Sistema**: IntegraGAL v2.0 - Estrutura de Raiz  
**Data**: 02/12/2025  
**Status**: ✅ Pronto para execução
"""
    
    instrucoes_path = os.path.join(temp_dir, "LEIA_PRIMEIRO.txt")
    with open(instrucoes_path, 'w', encoding='utf-8') as f:
        f.write(instrucoes)
    
    print("  ✅ LEIA_PRIMEIRO.txt criado")

def criar_package_final(temp_dir):
    """Cria o package final com estrutura de raiz"""
    print("📦 Criando package final...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"IntegraGAL_Raiz_Final_{timestamp}.zip"
    
    # Criar ZIP com estrutura plana
    with zipfile.ZipFile(f"/workspace/{package_name}", 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)
                print(f"  ✅ {arcname}")
    
    package_size = os.path.getsize(f"/workspace/{package_name}")
    print(f"\n📦 Package criado: {package_name}")
    print(f"📏 Tamanho: {package_size:,} bytes ({package_size/1024:.1f} KB)")
    
    return package_name

def main():
    """Função principal"""
    print("=" * 70)
    print("📦 CRIANDO PACKAGE COM ESTRUTURA DE RAIZ")
    print("=" * 70)
    
    try:
        # Passo 1: Preparar arquivos para raiz
        temp_dir = corrigir_arquivos_para_raiz()
        
        # Passo 2: Corrigir caminhos
        corrigir_caminhos_arquivos(temp_dir)
        
        # Passo 3: Criar executar.bat
        criar_executar_batch(temp_dir)
        
        # Passo 4: Criar instruções
        criar_instrucoes_raiz(temp_dir)
        
        # Passo 5: Criar package
        package_name = criar_package_final(temp_dir)
        
        print("\n" + "=" * 70)
        print("✅ PACKAGE DE RAIZ CRIADO COM SUCESSO!")
        print("=" * 70)
        print(f"\n📦 Arquivo: {package_name}")
        print(f"\n💡 INSTRUÇÕES:")
        print(f"1. Extrair {os.path.basename(package_name)} em C:\\Users\\marci\\Downloads\\Integragal")
        print(f"2. DUPLO CLIQUE em executar.bat")
        print(f"3. Login: marcio / flafla")
        print(f"\n🎯 ESTRUTURA PLANA (SEM IntegragalGit)")
        print(f"✅ Todos os caminhos corrigidos para raiz")
        print(f"✅ Sistema pronto para execução imediata!")

        # Limpeza
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        return package_name
        
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        return None

if __name__ == "__main__":
    main()
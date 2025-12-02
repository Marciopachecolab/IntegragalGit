#!/usr/bin/env python3
"""
Criar package completo do IntegraGAL adaptado para estrutura Windows do usuário
"""

import os
import shutil
import zipfile

def criar_estrutura_windows():
    """Cria a estrutura completa adaptada para C:\\Users\\marci\\Downloads\\Integragal"""
    
    # Estrutura base
    estrutura = {
        # Arquivos principais
        "main.py": None,
        
        # Subdiretórios
        "banco/": ["credenciais.csv"],
        "autenticacao/": ["auth_service.py", "login.py", "__init__.py"],
        "utils/": ["io_utils.py", "logger.py", "after_mixin.py", "__init__.py"],
        "ui/": ["main_window.py", "admin_panel.py", "user_management.py", "__init__.py"],
        "logs/": [],
        "config/": ["configuracao.py", "__init__.py"],
        "analise/": [],
        "exportacao/": [],
        "extracao/": [],
        "inclusao_testes/": [],
        "relatorios/": [],
        "services/": [],
        "db/": [],
        "core/": [],
        "reports/": [],
        "scripts/": [],
        "sql/": [],
        "tests/": [],
        "interface/": [],
        "configuracao/": ["configuracao.py", "config.json", "__init__.py"],
    }
    
    # Conteúdo do main.py adaptado
    main_py_content = '''"""
Ponto de entrada principal da aplicação IntegraGAL v2.0 - ADAPTADO PARA WINDOWS
"""

import os
import sys

# Garante BASE_DIR no sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Importações dos módulos
from autenticacao.login import autenticar_usuario
from ui.main_window import criar_aplicacao_principal
from utils.logger import registrar_log

if __name__ == "__main__":
    """Ponto de entrada principal da aplicação"""
    os.chdir(BASE_DIR)
    
    # Autenticação
    usuario = autenticar_usuario()
    if not usuario:
        sys.exit(1)
    
    # Carrega aplicação principal
    app = criar_aplicacao_principal()
    if app:
        app.mainloop()
'''
    
    # Conteúdo do auth_service.py adaptado para estrutura
    auth_service_content = '''# autenticacao/auth_service.py
import os
import sys
import pandas as pd
import bcrypt

# --- Configuração de Paths para Windows ---
# Tenta múltiplas formas de encontrar o diretório base
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # .../autenticacao
BASE_DIR = os.path.dirname(SCRIPT_DIR)  # Raiz do projeto

# Fallback: Se a estrutura não for a esperada
if not os.path.exists(os.path.join(BASE_DIR, "banco")):
    # Procura por credenciais.csv no diretório atual
    for item in os.listdir('.'):
        if os.path.isfile(item) and item == "credenciais.csv":
            BASE_DIR = os.getcwd()
            break
    else:
        # Como último recurso, cria um arquivo de exemplo
        BASE_DIR = os.getcwd()

try:
    from utils.logger import registrar_log
    from utils.io_utils import read_data_with_auto_detection
except ImportError:
    # Fallback se não conseguir importar
    def registrar_log(modulo, mensagem, nivel="INFO"):
        print(f"[{nivel}] {modulo}: {mensagem}")
    
    def read_data_with_auto_detection(filepath):
        try:
            return pd.read_csv(filepath, sep=';', encoding='utf-8-sig')
        except:
            return None

# --- Constantes ---
CAMINHO_CREDENCIAIS = os.path.join(BASE_DIR, "banco", "credenciais.csv")

class AuthService:
    """
    Encapsula toda a lógica de autenticação e gestão de credenciais.
    """
    def __init__(self):
        self._criar_arquivo_se_nao_existir()

    def _criar_arquivo_se_nao_existir(self):
        """Garante que o arquivo de credenciais CSV exista."""
        if not os.path.exists(CAMINHO_CREDENCIAIS):
            try:
                # Cria diretório se não existir
                os.makedirs(os.path.dirname(CAMINHO_CREDENCIAIS), exist_ok=True)
                pd.DataFrame(columns=['usuario', 'senha_hash']).to_csv(CAMINHO_CREDENCIAIS, index=False, sep=';')
                registrar_log("AuthService", f"Arquivo de credenciais criado em: {CAMINHO_CREDENCIAIS}", "INFO")
            except Exception as e:
                registrar_log("AuthService", f"Falha ao criar arquivo de credenciais: {e}", "CRITICAL")
                
    def gerar_hash_bcrypt(self, senha: str) -> str:
        """Gera um hash seguro para a senha usando bcrypt."""
        senha_bytes = senha.encode('utf-8')
        hashed_bytes = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())
        return hashed_bytes.decode('utf-8')

    def verificar_senha(self, usuario: str, senha_fornecida: str) -> bool:
        """Verifica se a senha fornecida corresponde ao hash armazenado."""
        try:
            registrar_log("AuthService", f"Tentativa de login para usuário: {usuario}", "DEBUG")
            
            # Método 1: Usar o leitor automático
            df = read_data_with_auto_detection(CAMINHO_CREDENCIAIS)
            
            # Método 2: Fallback manual
            if df is None:
                try:
                    df = pd.read_csv(CAMINHO_CREDENCIAIS, sep=';', encoding='utf-8-sig')
                except:
                    try:
                        df = pd.read_csv(CAMINHO_CREDENCIAIS, sep=';', encoding='utf-8')
                    except:
                        try:
                            df = pd.read_csv(CAMINHO_CREDENCIAIS, sep=';', encoding='latin-1')
                        except Exception as e:
                            registrar_log("AuthService", f"Falha em todas as tentativas de leitura: {e}", "ERROR")
                            return False
            
            if df is None or df.empty:
                registrar_log("AuthService", "Arquivo de credenciais está vazio ou não pôde ser lido.", "ERROR")
                return False
            
            if 'usuario' not in df.columns or 'senha_hash' not in df.columns:
                registrar_log("AuthService", f"Colunas necessárias não encontradas. Colunas presentes: {list(df.columns)}", "ERROR")
                return False

            credenciais_usuario = df[df['usuario'].str.strip().str.lower() == usuario.strip().lower()]
            if credenciais_usuario.empty:
                registrar_log("AuthService", f"Usuário '{usuario}' não encontrado", "WARNING")
                return False

            hash_armazenado_str = credenciais_usuario.iloc[0]['senha_hash']
            hash_armazenado_bytes = hash_armazenado_str.encode('utf-8')
            senha_fornecida_bytes = senha_fornecida.encode('utf-8')
            
            resultado = bcrypt.checkpw(senha_fornecida_bytes, hash_armazenado_bytes)
            registrar_log("AuthService", f"Resultado da autenticação: {'Sucesso' if resultado else 'Falha'}", "INFO")
            return resultado

        except Exception as e:
            registrar_log("AuthService", f"Erro ao verificar credenciais: {e}", "CRITICAL")
            return False'''
    
    return {
        "main.py": main_py_content,
        "autenticacao/auth_service.py": auth_service_content
    }

def copiar_arquivos_existentes():
    """Copia os arquivos existentes adaptados"""
    
    arquivos_origem = {
        "/workspace/IntegragalGit/banco/credenciais.csv": "banco/credenciais.csv",
        "/workspace/IntegragalGit/autenticacao/login.py": "autenticacao/login.py",
        "/workspace/IntegragalGit/autenticacao/__init__.py": "autenticacao/__init__.py",
        "/workspace/IntegragalGit/utils/io_utils.py": "utils/io_utils.py",
        "/workspace/IntegragalGit/utils/logger.py": "utils/logger.py",
        "/workspace/IntegragalGit/utils/after_mixin.py": "utils/after_mixin.py",
        "/workspace/IntegragalGit/utils/__init__.py": "utils/__init__.py",
        "/workspace/IntegragalGit/configuracao/configuracao.py": "configuracao/configuracao.py",
        "/workspace/IntegragalGit/configuracao/__init__.py": "configuracao/__init__.py",
        "/workspace/IntegragalGit/ui/main_window.py": "ui/main_window.py",
        "/workspace/IntegragalGit/ui/admin_panel.py": "ui/admin_panel.py",
        "/workspace/IntegragalGit/ui/user_management.py": "ui/user_management.py",
        "/workspace/IntegragalGit/ui/__init__.py": "ui/__init__.py",
    }
    
    return arquivos_origem

def criar_arquivo_credenciais():
    """Cria arquivo de credenciais com usuário marcio/flafla"""
    import bcrypt
    
    conteudo = "usuario;senha_hash\n"
    hash_senha = bcrypt.hashpw("flafla".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    conteudo += f"marcio;{hash_senha}"
    
    return {"banco/credenciais.csv": conteudo}

def criar_scripts_executar():
    """Cria scripts de execução para Windows"""
    
    # Script batch principal
    batch_content = '''@echo off
chcp 65001 >nul
title IntegraGAL - Sistema de Análise Laboratorial

echo ================================================
echo           INTEGRAFAL v2.0 - WINDOWS
echo ================================================
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python não encontrado no PATH
    echo Por favor, instale Python 3.8+ e adicione ao PATH
    echo.
    echo Tentativa de instalação automática...
    pip install pandas customtkinter bcrypt
    echo.
    echo Tentando executar novamente...
)

echo Executando IntegraGAL...
echo Diretório atual: %CD%
echo.

REM Executa o programa
python main.py

if errorlevel 1 (
    echo.
    echo ERRO: O programa encontrou problemas
    echo Verifique se todas as dependências estão instaladas:
    echo pip install pandas customtkinter bcrypt
)

echo.
echo Programa finalizado.
pause
'''
    
    # Validador de credenciais
    validador_content = '''#!/usr/bin/env python3
"""
Validador Simples de Credenciais para Windows
"""

import os
import sys
import pandas as pd
import bcrypt

def main():
    print("=== VALIDADOR DE CREDENCIAIS ===")
    
    # Procura pelo arquivo de credenciais
    credenciais_paths = [
        "banco/credenciais.csv",
        "credenciais.csv"
    ]
    
    credenciais_path = None
    for path in credenciais_paths:
        if os.path.exists(path):
            credenciais_path = path
            break
    
    if not credenciais_path:
        print("❌ Arquivo de credenciais não encontrado!")
        print("Tentei os seguintes caminhos:")
        for path in credenciais_paths:
            print(f"  - {path}")
        input("Pressione Enter para sair...")
        return
    
    print(f"✅ Arquivo encontrado: {credenciais_path}")
    
    # Testa leitura do arquivo
    try:
        df = pd.read_csv(credenciais_path, sep=';', encoding='utf-8-sig')
        print(f"✅ Arquivo lido: {len(df)} linha(s)")
        print(f"📋 Colunas: {list(df.columns)}")
        
        if 'usuario' in df.columns and 'senha_hash' in df.columns:
            usuarios = df['usuario'].tolist()
            print(f"👤 Usuários encontrados: {usuarios}")
            
            # Testa o usuário marcio
            if 'marcio' in df['usuario'].values:
                hash_armazenado = df[df['usuario'] == 'marcio']['senha_hash'].iloc[0]
                senha_valida = bcrypt.checkpw("flafla".encode('utf-8'), hash_armazenado.encode('utf-8'))
                
                if senha_valida:
                    print("✅ CREDENCIAIS VÁLIDAS: marcio/flafla")
                    print("🎉 Sistema funcionando corretamente!")
                else:
                    print("❌ Senha incorreta para usuário marcio")
            else:
                print("❌ Usuário 'marcio' não encontrado")
        else:
            print("❌ Colunas necessárias não encontradas")
    
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
    
    print("\\nValidação concluída.")
    input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()
'''
    
    # Instruções
    instrucoes = '''# IntegraGAL - Instruções de Uso

## Como Executar

### Opção 1: Script Automático (Recomendado)
1. Execute: `executar_integragal.bat`
2. Faça login com: **marcio** / **flafla**

### Opção 2: Linha de Comando
1. Abra Command Prompt ou PowerShell
2. Execute: `python main.py`
3. Faça login com: **marcio** / **flafla**

### Opção 3: Validação Primeiro
1. Execute: `python validar_credenciais.py`
2. Se der sucesso, execute: `python main.py`

## Requisitos

- Python 3.8 ou superior
- pip install pandas customtkinter bcrypt

## Estrutura de Arquivos

- `main.py` - Programa principal
- `banco/credenciais.csv` - Arquivo de usuários
- `autenticacao/` - Módulos de autenticação
- `ui/` - Interface gráfica
- `utils/` - Utilitários

## Login

- Usuário: marcio
- Senha: flafla

## Troubleshooting

Se houver erro "credential inválidas":
1. Execute: `python validar_credenciais.py`
2. Verifique se está no diretório correto
3. Instale dependências: `pip install pandas customtkinter bcrypt`

## Logs

Os logs são salvos em `logs/sistema.log`
'''
    
    return {
        "executar_integragal.bat": batch_content,
        "validar_credenciais.py": validador_content,
        "LEIA-ME.txt": instrucoes
    }

def criar_zip_completo():
    """Cria o arquivo ZIP com tudo pronto para usar"""
    
    print("=== CRIANDO PACKAGE COMPLETO DO INTEGRAFAL ===\n")
    
    # Estrutura de conteúdo
    conteudo_arquivos = {}
    
    # Adiciona arquivos principais
    conteudo_arquivos.update(criar_estrutura_windows())
    
    # Adiciona arquivo de credenciais
    conteudo_arquivos.update(criar_arquivo_credenciais())
    
    # Adiciona scripts
    conteudo_arquivos.update(criar_scripts_executar())
    
    # Adiciona __init__.py para todos os diretórios
    init_content = ""
    for dir_name in ["autenticacao", "utils", "ui", "banco", "logs", "config", "configuracao", "analise", "exportacao", "extracao", "inclusao_testes", "relatorios", "services", "db", "core", "reports", "scripts", "sql", "tests", "interface"]:
        if f"{dir_name}/__init__.py" not in conteudo_arquivos:
            conteudo_arquivos[f"{dir_name}/__init__.py"] = init_content
    
    # Copia arquivos existentes
    arquivos_existentes = copiar_arquivos_existentes()
    
    print("📁 Estrutura que será criada:")
    for path in conteudo_arquivos.keys():
        print(f"   - {path}")
    
    for src, dst in arquivos_existentes.items():
        if os.path.exists(src):
            print(f"   - {dst} (copiado)")
            conteudo_arquivos[dst] = "COPY_FROM_ORIGINAL"
        else:
            print(f"   ⚠️ {dst} (origem não encontrada: {src})")
    
    # Cria o ZIP
    zip_path = "/workspace/IntegraGAL_Windows_COMPLETO.zip"
    
    print(f"\n📦 Criando ZIP: {zip_path}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Adiciona todos os arquivos
        for path, conteudo in conteudo_arquivos.items():
            print(f"   Adicionando: {path}")
            
            if conteudo == "COPY_FROM_ORIGINAL":
                # Copia arquivo original
                src_path = None
                for src, dst in arquivos_existentes.items():
                    if dst == path:
                        src_path = src
                        break
                
                if src_path and os.path.exists(src_path):
                    zipf.write(src_path, path)
                else:
                    print(f"   ⚠️ Falha ao copiar {path}")
                    # Cria arquivo vazio como fallback
                    zipf.writestr(path, "# Arquivo vazio - falhou na cópia", zipfile.ZIP_DEFLATED)
            else:
                # Adiciona conteúdo de string
                zipf.writestr(path, conteudo, zipfile.ZIP_DEFLATED)
    
    print(f"\n✅ ZIP criado com sucesso: {zip_path}")
    
    # Mostra informações do ZIP
    if os.path.exists(zip_path):
        size = os.path.getsize(zip_path)
        print(f"📏 Tamanho: {size:,} bytes ({size/1024/1024:.1f} MB)")
        
        # Lista conteúdo do ZIP
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            files = zipf.namelist()
            print(f"📁 Total de arquivos: {len(files)}")
            print("\n📋 Conteúdo do ZIP:")
            for file in sorted(files)[:20]:  # Mostra primeiros 20
                print(f"   - {file}")
            if len(files) > 20:
                print(f"   ... e mais {len(files) - 20} arquivos")
    
    return zip_path

def main():
    zip_path = criar_zip_completo()
    
    print("\n" + "="*60)
    print("✅ PACKAGE INTEGRAFAL CRIADO COM SUCESSO!")
    print("="*60)
    print(f"📦 Arquivo: {zip_path}")
    print(f"📍 Localização: /workspace/")
    print(f"\n🔧 Para usar:")
    print(f"1. Extraia o ZIP em: C:\\Users\\marci\\Downloads\\")
    print(f"2. Execute: executar_integragal.bat")
    print(f"3. Login: marcio / flafla")

if __name__ == "__main__":
    main()
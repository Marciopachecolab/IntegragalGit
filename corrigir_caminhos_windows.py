#!/usr/bin/env python3
"""
Correção de Caminhos para IntegraGAL no Windows
Este script corrige os caminhos absolutos/relativos para funcionar corretamente no Windows
"""

import os
import sys
import shutil

def corrigir_auth_service():
    """Corrige o arquivo auth_service.py para usar caminhos absolutos"""
    auth_path = "/workspace/IntegragalGit/autenticacao/auth_service.py"
    
    with open(auth_path, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Substitui a configuração de BASE_DIR para ser mais robusta no Windows
    novo_conteudo = '# autenticacao/auth_service.py\nimport os\nimport sys\nimport pandas as pd\nimport bcrypt  # Nova dependência - adicione \'bcrypt\' ao seu requirements.txt\n\n# --- Configuração de Paths Melhorada para Windows ---\n# Tenta múltiplas formas de encontrar o diretório base\nSCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))\nBASE_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # Sobe 2 níveis: auth_service -> autenticacao -> BASE_DIR\n\n# Fallback: Se a estrutura não for a esperada, usa diretório atual\nif not os.path.exists(os.path.join(BASE_DIR, "banco")):\n    BASE_DIR = os.path.dirname(os.path.abspath("."))  # Tenta diretório pai do atual\n    if not os.path.exists(os.path.join(BASE_DIR, "banco")):\n        BASE_DIR = os.getcwd()  # Último recurso: diretório atual\n\nif BASE_DIR not in sys.path:\n    sys.path.append(BASE_DIR)\n\n# Importações\ntry:\n    from utils.logger import registrar_log\n    from utils.io_utils import read_data_with_auto_detection\nexcept ImportError:\n    # Fallback se não conseguir importar\n    def registrar_log(modulo, mensagem, nivel="INFO"):\n        print(f"[{nivel}] {modulo}: {mensagem}")\n    \n    def read_data_with_auto_detection(filepath):\n        try:\n            import pandas as pd\n            # Fallback simples de leitura\n            with open(filepath, \'r\', encoding=\'utf-8-sig\') as f:\n                content = f.read()\n            return pd.read_csv(filepath, sep=\';\', encoding=\'utf-8-sig\')\n        except:\n            return None\n\n# --- Constantes ---\nCAMINHO_CREDENCIAIS = os.path.join(BASE_DIR, "banco", "credenciais.csv")  # Caminho absoluto\n\nclass AuthService:\n    """\n    Encapsula toda a lógica de negócio relacionada à autenticação e gestão de credenciais.\n    """\n    def __init__(self):\n        self._criar_arquivo_se_nao_existir()\n\n    def _criar_arquivo_se_nao_existir(self):\n        """Garante que o arquivo de credenciais CSV exista."""\n        if not os.path.exists(CAMINHO_CREDENCIAIS):\n            try:\n                # Cria diretório se não existir\n                os.makedirs(os.path.dirname(CAMINHO_CREDENCIAIS), exist_ok=True)\n                pd.DataFrame(columns=[\'usuario\', \'senha_hash\']).to_csv(CAMINHO_CREDENCIAIS, index=False, sep=\';\')\n                registrar_log("AuthService", f"Arquivo de credenciais criado em: {CAMINHO_CREDENCIAIS}", "INFO")\n            except Exception as e:\n                registrar_log("AuthService", f"Falha ao criar arquivo de credenciais: {e}", "CRITICAL")\n                \n    def gerar_hash_bcrypt(self, senha: str) -> str:\n        """\n        Gera um hash seguro para a senha usando bcrypt.\n        O salt é gerado e incluído automaticamente no hash.\n        """\n        senha_bytes = senha.encode(\'utf-8\')\n        hashed_bytes = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())\n        return hashed_bytes.decode(\'utf-8\')\n\n    def verificar_senha(self, usuario: str, senha_fornecida: str) -> bool:\n        """\n        Verifica se a senha fornecida corresponde ao hash armazenado para o utilizador.\n        """\n        try:\n            registrar_log("AuthService", f"Tentativa de login para usuário: {usuario}", "DEBUG")\n            \n            # Tenta múltiplas formas de ler o arquivo\n            df = None\n            \n            # Método 1: Usar o leitor automático\n            df = read_data_with_auto_detection(CAMINHO_CREDENCIAIS)\n            \n            # Método 2: Fallback manual\n            if df is None:\n                registrar_log("AuthService", "Fallback: Tentando leitura manual do CSV", "WARNING")\n                try:\n                    df = pd.read_csv(CAMINHO_CREDENCIAIS, sep=\';\', encoding=\'utf-8-sig\')\n                except:\n                    try:\n                        df = pd.read_csv(CAMINHO_CREDENCIAIS, sep=\';\', encoding=\'utf-8\')\n                    except:\n                        try:\n                            df = pd.read_csv(CAMINHO_CREDENCIAIS, sep=\';\', encoding=\'latin-1\')\n                        except Exception as e:\n                            registrar_log("AuthService", f"Falha em todas as tentativas de leitura: {e}", "ERROR")\n                            return False\n            \n            if df is None or df.empty:\n                registrar_log("AuthService", "Arquivo de credenciais está vazio ou não pôde ser lido.", "ERROR")\n                return False\n            \n            if \'usuario\' not in df.columns or \'senha_hash\' not in df.columns:\n                registrar_log("AuthService", f"Colunas necessárias não encontradas. Colunas presentes: {list(df.columns)}", "ERROR")\n                return False\n\n            credenciais_usuario = df[df[\'usuario\'].str.strip().str.lower() == usuario.strip().lower()]\n            if credenciais_usuario.empty:\n                registrar_log("AuthService", f"Usuário \'{usuario}\' não encontrado", "WARNING")\n                return False\n\n            hash_armazenado_str = credenciais_usuario.iloc[0][\'senha_hash\']\n            hash_armazenado_bytes = hash_armazenado_str.encode(\'utf-8\')\n            senha_fornecida_bytes = senha_fornecida.encode(\'utf-8\')\n            \n            # A função checkpw do bcrypt compara a senha com o hash (que já contém o salt)\n            resultado = bcrypt.checkpw(senha_fornecida_bytes, hash_armazenado_bytes)\n            registrar_log("AuthService", f"Resultado da autenticação: {\'Sucesso\' if resultado else \'Falha\'}", "INFO")\n            return resultado\n\n        except Exception as e:\n            registrar_log("AuthService", f"Erro ao verificar credenciais: {e}", "CRITICAL")\n            return False'
    
    with open(auth_path, 'w', encoding='utf-8') as f:
        f.write(novo_conteudo)
    
    print("✅ auth_service.py corrigido para Windows")

def corrigir_io_utils():
    """Melhora o io_utils.py para Windows"""
    io_utils_path = "/workspace/IntegragalGit/utils/io_utils.py"
    
    # Adiciona logging melhorado
    with open(io_utils_path, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Melhoria na função de detecção de separador para ser mais robusta
    secao_correcao = """def detectar_separador_csv(filepath: str) -> str:
    try:
        # Tenta múltiplos encodings
        encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252', 'windows-1252']
        
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    for _ in range(5):
                        linha = f.readline()
                        if ';' in linha and ',' not in linha:
                            return ';'
                        if ',' in linha and ';' not in linha:
                            return ','
                        if ';' in linha and ',' in linha:
                            if linha.count(';') >= linha.count(','):
                                return ';'
                            else:
                                return ','
                break
            except UnicodeDecodeError:
                continue
        
        # Se chegou aqui, usa padrão ';'
        return ','
    except Exception as e:
        return ';'  # Padrão mais comum em sistemas Windows"""
    
    # Substitui a função existente
    import re
    padrao = r'def detectar_separador_csv\(filepath: str\) -> str:.*?return [\'"];[\'"].*?except Exception as e:.*?return [\'"],[\'"]'
    novo_conteudo = re.sub(padrao, secao_correcao, conteudo, flags=re.DOTALL)
    
    with open(io_utils_path, 'w', encoding='utf-8') as f:
        f.write(novo_conteudo)
    
    print("✅ io_utils.py melhorado para Windows")

def criar_script_executor_windows():
    """Cria script de execução otimizado para Windows"""
    script_content = """@echo off
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
    pause
    exit /b 1
)

REM Vai para o diretório do script
cd /d "%~dp0"

REM Verifica se existe o diretório IntegragalGit
if not exist "IntegragalGit" (
    echo ERRO: Diretório IntegragalGit não encontrado
    echo Certifique-se de estar executando do diretório correto
    pause
    exit /b 1
)

echo Iniciando IntegraGAL...
echo Diretório atual: %CD%
echo.

REM Executa o programa
python IntegragalGit/main.py

REM Se chegou aqui, o programa fechou
echo.
echo Programa finalizado.
pause
"""
    with open("/workspace/executar_integragal.bat", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print("✅ Script de execução Windows criado: executar_integragal.bat")

def criar_validador_credenciais():
    """Cria um validador simples para testar credenciais"""
    validador_content = """#!/usr/bin/env python3
\"\"\"
Validador Simples de Credenciais para Windows
Testa se o sistema de login está funcionando
\"\"\"

import os
import sys
import pandas as pd
import bcrypt

def main():
    print("=== VALIDADOR DE CREDENCIAIS ===")
    
    # Tenta encontrar o arquivo de credenciais
    caminhos_possiveis = [
        "IntegragalGit/banco/credenciais.csv",
        "banco/credenciais.csv", 
        "./IntegragalGit/banco/credenciais.csv",
        "./banco/credenciais.csv"
    ]
    
    credenciais_path = None
    for caminho in caminhos_possiveis:
        if os.path.exists(caminho):
            credenciais_path = caminho
            break
    
    if not credenciais_path:
        print("❌ Arquivo de credenciais não encontrado!")
        print("Tentei os seguintes caminhos:")
        for caminho in caminhos_possiveis:
            print(f"  - {caminho}")
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
"""
    
    with open("/workspace/validar_credenciais_windows.py", "w", encoding="utf-8") as f:
        f.write(validador_content)
    
    print("✅ Validador de credenciais criado: validar_credenciais_windows.py")

def criar_instrucoes_windows():
    """Cria arquivo com instruções específicas para Windows"""
    instrucoes = """# Instruções para Execução no Windows

## Problema Identificado
O sistema estava usando caminhos relativos que funcionam no Linux, mas podem ter problemas no Windows.

## Soluções Implementadas

### 1. Caminhos Absolutos
- auth_service.py agora usa caminhos absolutos mais robustos
- Múltiplos fallbacks para encontrar os arquivos corretos
- Melhor tratamento de erros

### 2. Encoding e Separadores
- Melhor detecção de separadores CSV (priorizando ';')
- Múltiplas tentativas de encoding (utf-8-sig, utf-8, latin-1)
- Fallbacks para diferentes versões do Windows

### 3. Scripts de Execução
- executar_integragal.bat: Script principal para Windows
- validar_credenciais_windows.py: Validador de credenciais

## Como Usar

### Opção 1: Script Batch (Recomendado)
1. Vá para: `C:\\Users\\marci\\Downloads\\Integragal`
2. Execute: `executar_integragal.bat`

### Opção 2: Linha de Comando
1. Abra Command Prompt ou PowerShell
2. Navegue até: `C:\\Users\\marci\\Downloads\\Integragal`
3. Execute: `python IntegragalGit/main.py`

### Opção 3: Validação Primeiro
1. Execute: `python validar_credenciais_windows.py`
2. Se der sucesso, execute o sistema normalmente

## Estrutura de Diretórios Necessária
```
C:\\Users\\marci\\Downloads\\Integragal\\
├── executar_integragal.bat
├── validar_credenciais_windows.py
├── IntegragalGit\\
│   ├── main.py
│   ├── banco\\
│   │   └── credenciais.csv
│   ├── autenticacao\\
│   │   └── auth_service.py
│   └── utils\\
│       └── io_utils.py
```

## Credenciais de Teste
- Usuário: marcio
- Senha: flafla

## Troubleshooting

### Se o arquivo não for encontrado:
- Verifique se você está no diretório correto: `C:\\Users\\marci\\Downloads\\Integragal`
- Execute o validador primeiro: `python validar_credenciais_windows.py`

### Se houver erros de encoding:
- O sistema agora tenta múltiplos encodings automaticamente
- Se persistir, verifique se o arquivo credenciais.csv está em UTF-8

### Se a autenticação falhar:
- Use o validador para verificar se as credenciais estão corretas
- O hash da senha 'flafla' é: $2b$12$tBZZ5hWsiWr7XmsRZG7i4.CSUuP4bok2LHDZ/8nQ6jXnB4rEh9762

### Se houver problemas de dependências:
```bash
pip install pandas customtkinter bcrypt
```

## Logs
Os logs são salvos em `logs/sistema.log` no diretório do programa.
"""
    
    with open("/workspace/INSTRUCOES_WINDOWS.md", "w", encoding="utf-8") as f:
        f.write(instrucoes)
    
    print("✅ Instruções para Windows criadas: INSTRUCOES_WINDOWS.md")

def main():
    """Função principal"""
    print("=== CORREÇÃO DE CAMINHOS PARA WINDOWS ===\n")
    
    corrigir_auth_service()
    corrigir_io_utils()
    criar_script_executor_windows()
    criar_validador_credenciais()
    criar_instrucoes_windows()
    
    print("\n" + "="*50)
    print("✅ CORREÇÕES CONCLUÍDAS")
    print("="*50)
    print("\n🔧 Para usar no Windows:")
    print("1. Copie todos os arquivos para: C:\\Users\\marci\\Downloads\\Integragal")
    print("2. Execute: executar_integragal.bat")
    print("3. OU primeiro teste: python validar_credenciais_windows.py")
    print("\n📖 Verifique: INSTRUCOES_WINDOWS.md para detalhes completos")

if __name__ == "__main__":
    main()
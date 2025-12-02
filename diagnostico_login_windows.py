#!/usr/bin/env python3
"""
Script de Diagnóstico para Problemas de Login no Windows
Este script verifica se todos os arquivos estão sendo encontrados corretamente
e se os caminhos estão configurados adequadamente para o Windows.
"""

import os
import sys
import pandas as pd
import bcrypt

def setup_paths():
    """Configura os paths base para funcionar no Windows"""
    # Pega o diretório atual (onde está o main.py)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Adiciona ao sys.path se necessário
    if BASE_DIR not in sys.path:
        sys.path.append(BASE_DIR)
    
    return BASE_DIR

def diagnosticar_sistema():
    """Realiza diagnóstico completo do sistema"""
    print("=== DIAGNÓSTICO DO SISTEMA DE LOGIN ===\n")
    
    # Configura paths
    BASE_DIR = setup_paths()
    print(f"1. Diretório Base: {BASE_DIR}")
    print(f"   Diretório Atual: {os.getcwd()}")
    
    # Verifica estrutura de arquivos
    arquivos_necessarios = [
        "IntegragalGit/autenticacao/auth_service.py",
        "IntegragalGit/banco/credenciais.csv", 
        "IntegragalGit/config.json"
    ]
    
    print(f"\n2. VERIFICAÇÃO DE ARQUIVOS:")
    for arquivo in arquivos_necessarios:
        caminho_completo = os.path.join(BASE_DIR, arquivo)
        existe = os.path.exists(caminho_completo)
        print(f"   {arquivo}: {'✅ EXISTE' if existe else '❌ NÃO EXISTE'}")
        if not existe:
            print(f"      Caminho completo tentado: {caminho_completo}")
    
    # Testa leitura do arquivo de credenciais
    print(f"\n3. TESTE DE LEITURA DO ARQUIVO DE CREDENCIAIS:")
    credenciais_path = os.path.join(BASE_DIR, "IntegragalGit/banco/credenciais.csv")
    
    if os.path.exists(credenciais_path):
        try:
            # Testa diferentes separadores e encodings
            separadores = [';', ',']
            encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
            
            for sep in separadores:
                for encoding in encodings:
                    try:
                        df = pd.read_csv(credenciais_path, encoding=encoding, sep=sep)
                        print(f"   ✅ Sucesso com sep='{sep}' e encoding='{encoding}'")
                        print(f"   📊 DataFrame lido: {len(df)} linhas, {len(df.columns)} colunas")
                        print(f"   📋 Colunas: {list(df.columns)}")
                        if not df.empty:
                            print(f"   👤 Usuários encontrados: {list(df['usuario'].values) if 'usuario' in df.columns else 'N/A'}")
                        break
                    except Exception as e:
                        print(f"   ❌ Falha com sep='{sep}' e encoding='{encoding}': {str(e)[:100]}...")
                else:
                    continue
                break
                
        except Exception as e:
            print(f"   ❌ Erro geral ao ler credenciais: {e}")
    else:
        print(f"   ❌ Arquivo não encontrado: {credenciais_path}")
    
    # Teste de autenticação direta
    print(f"\n4. TESTE DE AUTENTICAÇÃO DIRETA:")
    try:
        # Importa o serviço de autenticação
        sys.path.append(os.path.join(BASE_DIR, "IntegragalGit"))
        from autenticacao.auth_service import AuthService
        
        auth = AuthService()
        
        # Testa com usuário marcio e senha flafla
        resultado = auth.verificar_senha("marcio", "flafla")
        print(f"   🔐 Teste de login marcio/flafla: {'✅ SUCESSO' if resultado else '❌ FALHA'}")
        
        if not resultado:
            print(f"   💡 Possíveis causas:")
            print(f"      - Hash da senha incorreto")
            print(f"      - Arquivo não encontrado")
            print(f"      - Separador/encoding incorreto")
            
    except Exception as e:
        print(f"   ❌ Erro ao importar/testar AuthService: {e}")
    
    # Gera hash da senha esperada
    print(f"\n5. VERIFICAÇÃO DO HASH DA SENHA:")
    try:
        hash_esperado = "$2b$12$tBZZ5hWsiWr7XmsRZG7i4.CSUuP4bok2LHDZ/8nQ6jXnB4rEh9762"
        senha_test = "flafla"
        
        hash_gerado = bcrypt.hashpw(senha_test.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        bcrypt_resultado = bcrypt.checkpw(senha_test.encode('utf-8'), hash_esperado.encode('utf-8'))
        
        print(f"   🔑 Hash esperado: {hash_esperado}")
        print(f"   🔑 Hash de teste: {hash_gerado}")
        print(f"   ✅ Hash válido para 'flafla': {'SIM' if bcrypt_resultado else 'NÃO'}")
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar hash: {e}")
    
    # Verifica permissões de arquivo
    print(f"\n6. VERIFICAÇÃO DE PERMISSÕES:")
    try:
        credenciais_path = os.path.join(BASE_DIR, "IntegragalGit/banco/credenciais.csv")
        if os.path.exists(credenciais_path):
            print(f"   📁 Pode ler: {'SIM' if os.access(credenciais_path, os.R_OK) else 'NÃO'}")
            print(f"   ✏️  Pode escrever: {'SIM' if os.access(credenciais_path, os.W_OK) else 'NÃO'}")
            print(f"   📊 Tamanho do arquivo: {os.path.getsize(credenciais_path)} bytes")
    except Exception as e:
        print(f"   ❌ Erro ao verificar permissões: {e}")
    
    # Soluções recomendadas
    print(f"\n7. SOLUÇÕES RECOMENDADAS:")
    print(f"   🔧 Se os arquivos não estão sendo encontrados:")
    print(f"      - Execute o script do diretório: C:\\Users\\marci\\Downloads\\Integragal")
    print(f"      - Certifique-se que toda a estrutura de pastas esteja presente")
    print(f"   🔧 Se o separador estiver incorreto:")
    print(f"      - O arquivo deve usar ';' como separador")
    print(f"   🔧 Se o encoding estiver incorreto:")
    print(f"      - Use UTF-8 com BOM (utf-8-sig)")
    print(f"   🔧 Para testar login:")
    print(f"      - Execute: python IntegragalGit/main.py")
    
    print(f"\n=== FIM DO DIAGNÓSTICO ===")

def criar_script_windows():
    """Cria um script batch para executar no Windows"""
    script_content = """@echo off
echo Executando IntegraGAL...
cd /d "%~dp0"
python IntegragalGit/main.py
pause
"""
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "executar_integragal.bat"), "w", encoding="utf-8") as f:
        f.write(script_content)
    print("✅ Script de execução criado: executar_integragal.bat")

if __name__ == "__main__":
    diagnosticar_sistema()
    criar_script_windows()
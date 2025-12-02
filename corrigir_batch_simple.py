#!/usr/bin/env python3
"""
Script para criar um arquivo .bat simples e compatível
"""

import os
import shutil
import zipfile
from datetime import datetime

# Caminhos
DESTINO_TEMP = "/workspace/IntegraGAL_Funcional"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
PACKAGE_FINAL = f"/workspace/IntegraGAL_BatchCorrigido_{TIMESTAMP}.zip"

def criar_batch_simples():
    """Cria arquivo .bat simples e compatível"""
    
    # Conteúdo do arquivo .bat simplificado (apenas ASCII)
    batch_content = '''@echo off
echo ========================================
echo          IntegraGAL v2.0
echo    Sistema de Gestao de Exames
echo ========================================
echo.
echo Iniciando sistema...
echo.

cd /d "%~dp0"
python main.py

if errorlevel 1 (
    echo.
    echo Erro ao executar o sistema!
    echo Verifique se o Python esta instalado.
    pause
)
'''
    
    # Salvar arquivo .bat
    batch_path = os.path.join(DESTINO_TEMP, "executar.bat")
    with open(batch_path, 'w', encoding='ascii') as f:
        f.write(batch_content)
    
    print("✅ Criado arquivo executar.bat simples (ASCII)")
    
    # Também criar versão alternativa ainda mais simples
    batch_simples = '''@echo off
python main.py
pause
'''
    
    batch_alt_path = os.path.join(DESTINO_TEMP, "executar_simples.bat")
    with open(batch_alt_path, 'w', encoding='ascii') as f:
        f.write(batch_simples)
    
    print("✅ Criado executar_simples.bat (versao ultra simples)")
    
    return batch_path, batch_alt_path

def criar_manual_explicacao():
    """Cria manual explicando como executar"""
    
    manual_content = '''# Manual de Execucao - IntegraGAL v2.0

## Metodo 1: Arquivo .bat (Recomendado)

### executar.bat
- Duplo clique para executar o sistema
- Versao com mensagens

### executar_simples.bat  
- Duplo clique para executar o sistema
- Versao ultra simples

## Metodo 2: Linha de Comando

### Abrir Prompt de Comando:
1. Pressionar Win + R
2. Digitar: cmd
3. Pressionar Enter

### Navegar para pasta:
cd "C:\\Users\\marci\\Downloads\\Integragal"

### Executar sistema:
python main.py

## Requisitos:
- Python instalado (versao 3.7 ou superior)
- Bibliotecas: customtkinter, pandas, bcrypt, matplotlib

## Credenciais de Acesso:
- Usuario: marcio
- Senha: flafla

## Arquivos Importantes:
- main.py - Arquivo principal
- config.json - Configuracoes
- banco/usuarios.csv - Base de usuarios

## Solucao de Problemas:

### Erro "python nao reconhecido":
- Instalar Python do site: https://python.org
- Marcar opcao "Add to PATH" durante instalacao

### Erro "modulo nao encontrado":
- Instalar bibliotecas: pip install customtkinter pandas bcrypt matplotlib

### Erro de permissao:
- Executar como administrador
- Ou mover pasta para C:\\Users\\marci\\Downloads\\

---
IntegraGAL v2.0 - Sistema Funcional
'''
    
    manual_path = os.path.join(DESTINO_TEMP, "MANUAL_EXECUCAO.md")
    with open(manual_path, 'w', encoding='utf-8') as f:
        f.write(manual_content)
    
    print("✅ Criado manual: MANUAL_EXECUCAO.md")

def criar_package_final():
    """Cria o package final com .bat corrigido"""
    
    with zipfile.ZipFile(PACKAGE_FINAL, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(DESTINO_TEMP):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, DESTINO_TEMP)
                zipf.write(file_path, arc_path)
    
    # Calcular tamanho
    tamanho_kb = os.path.getsize(PACKAGE_FINAL) / 1024
    
    # Contar arquivos
    total_arquivos = sum(len(files) for r, d, files in os.walk(DESTINO_TEMP))
    
    print(f"\n🎁 Package com .bat corrigido:")
    print(f"📁 Arquivo: {PACKAGE_FINAL}")
    print(f"📊 Tamanho: {tamanho_kb:.1f} KB")
    print(f"📄 Total de arquivos: {total_arquivos}")
    
    return PACKAGE_FINAL

def main():
    print("🔧 Corrigindo arquivo .bat para compatibility maxima...")
    print("=" * 60)
    
    # Criar .bats simples
    batch_path, batch_alt_path = criar_batch_simples()
    
    # Criar manual
    criar_manual_explicacao()
    
    # Criar package final
    package = criar_package_final()
    
    print("\n" + "=" * 60)
    print("✅ BATCH CORRIGIDO!")
    print(f"\n📦 Package final: {package}")
    print(f"\n📋 O que foi corrigido:")
    print("  1. Removidos caracteres especiais (Gestão → Gestao)")
    print("  2. Removidos emojis (❌ → sem emoji)")
    print("  3. Usado encoding ASCII puro")
    print("  4. Criado executar_simples.bat como alternativa")
    print("  5. Adicionado manual de execucao")
    print("\n🚀 Opcoes de execucao:")
    print("  - executar.bat (versao com mensagens)")
    print("  - executar_simples.bat (versao ultra simples)")
    print("  - Linha de comando: python main.py")
    
    return package

if __name__ == "__main__":
    main()
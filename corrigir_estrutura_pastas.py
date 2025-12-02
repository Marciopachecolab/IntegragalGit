#!/usr/bin/env python3
"""
Script para corrigir a estrutura de pastas do IntegraGAL
Mantém as subpastas necessárias mas ajusta os imports para funcionar na raiz
"""

import os
import shutil
import re
import zipfile
from pathlib import Path
from datetime import datetime

# Diretórios de origem e destino
ORIGEM = "/workspace/IntegragalGit"
DESTINO_TEMP = "/workspace/IntegraGAL_EstruturaCorreta"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
PACKAGE_FINAL = f"/workspace/IntegraGAL_EstruturaCorreta_{TIMESTAMP}.zip"

def copiar_estrutura_com_correções():
    """Copia toda a estrutura mantendo pastas e corrige imports"""
    
    # Remove destino se existir
    if os.path.exists(DESTINO_TEMP):
        shutil.rmtree(DESTINO_TEMP)
    
    # Lista de diretórios para incluir
    pastas_incluir = [
        'analise', 'autenticacao', 'banco', 'configuracao', 
        'core', 'db', 'exportacao', 'extracao', 'inclusao_testes',
        'interface', 'logs', 'relatorios', 'reports', 'scripts',
        'services', 'sql', 'tests', 'ui', 'utils'
    ]
    
    # Criar diretório destino
    os.makedirs(DESTINO_TEMP, exist_ok=True)
    
    # 1. Copiar arquivos da raiz (exceto os desnecessários)
    arquivos_raiz = ['main.py', 'config.json', 'requirements.txt', 'models.py', '__init__.py']
    
    for arquivo in arquivos_raiz:
        origem_arquivo = os.path.join(ORIGEM, arquivo)
        if os.path.exists(origem_arquivo):
            shutil.copy2(origem_arquivo, DESTINO_TEMP)
            print(f"✅ Copiado: {arquivo}")
    
    # 2. Copiar subpastas e ajustar imports
    for pasta in pastas_incluir:
        origem_pasta = os.path.join(ORIGEM, pasta)
        if os.path.exists(origem_pasta):
            destino_pasta = os.path.join(DESTINO_TEMP, pasta)
            
            # Copiar pasta inteira
            shutil.copytree(origem_pasta, destino_pasta)
            
            # Corrigir imports em todos os arquivos Python da pasta
            for root, dirs, files in os.walk(destino_pasta):
                for file in files:
                    if file.endswith('.py'):
                        arquivo_path = os.path.join(root, file)
                        corrigir_imports_arquivo(arquivo_path)
            
            print(f"✅ Copiada e corrigida pasta: {pasta}")
    
    # 3. Criar arquivo executar.bat na raiz
    criar_batch_executor()
    
    # 4. Criar documentação da correção
    criar_documentacao_correção()
    
    print(f"\n🎯 Estrutura corrigida criada em: {DESTINO_TEMP}")
    return DESTINO_TEMP

def corrigir_imports_arquivo(arquivo_path):
    """Corrige imports em um arquivo específico"""
    
    with open(arquivo_path, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    conteudo_original = conteudo
    
    # Mapeamento de correções de imports
    correcoes = [
        # Substituir imports de 'autenticacao.X' para 'X'
        (r'from autenticacao\.(\w+)', r'from \1'),
        
        # Substituir imports de 'core.authentication.X' para 'core.authentication.X' (manter)
        (r'from core\.authentication\.(\w+)', r'from core.authentication.\1'),
        
        # Imports de ui.X para ui.X (manter estrutura)
        (r'from ui\.(\w+)', r'from ui.\1'),
        
        # Imports diretos (manter como estão)
        # Outros imports relativos que precisam ajuste...
        (r'from (\.\w+)', r'from \1'),  # Imports relativos problemáticos
    ]
    
    for padrao, substituicao in correcoes:
        conteudo = re.sub(padrao, substituicao, conteudo)
    
    # Salvar se houve mudanças
    if conteudo != conteudo_original:
        with open(arquivo_path, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print(f"  📝 Corrigido imports em: {os.path.relpath(arquivo_path, DESTINO_TEMP)}")

def criar_batch_executor():
    """Cria arquivo executar.bat para Windows"""
    
    batch_content = '''@echo off
echo ========================================
echo          IntegraGAL v2.0
echo    Sistema de Gestão de Exames
echo ========================================
echo.
echo Iniciando sistema...
echo.

cd /d "%~dp0"
python main.py

if errorlevel 1 (
    echo.
    echo ❌ Erro ao executar o sistema!
    echo Verifique se o Python está instalado.
    pause
)
'''
    
    with open(os.path.join(DESTINO_TEMP, "executar.bat"), 'w', encoding='utf-8') as f:
        f.write(batch_content)
    
    print("✅ Criado arquivo executar.bat")

def criar_documentacao_correção():
    """Cria documentação das correções"""
    
    doc_content = f'''# IntegraGAL - Estrutura de Pastas Corrigida

## Data da Correção: {TIMESTAMP}

### Problema Identificado
O package anterior tinha todos os arquivos na raiz, mas a estrutura correta deveria manter as subpastas específicas.

### Estrutura Corrigida
A nova estrutura mantém as subpastas originais mas ajusta os imports para funcionar em:
`C:\\Users\\marci\\Downloads\\Integragal\\`

### Estrutura de Pastas:
```
C:\\Users\\marci\\Downloads\\Integragal\\
├── main.py                    (arquivo principal)
├── config.json               (configurações)
├── executar.bat              (script para executar)
├── ui\\                       (interfaces gráficas)
│   ├── admin_panel.py
│   ├── user_management.py
│   └── main_window.py
├── autenticacao\\             (serviços de autenticação)
│   └── auth_service.py
├── banco\\                    (arquivos de dados)
│   └── usuarios.csv
├── core\\                     (funcionalidades centrais)
│   └── authentication\\
├── configuracao\\             (configurações do sistema)
├── exportacao\\               (módulos de exportação)
├── extracao\\                 (módulos de extração)
├── relatorios\\               (geração de relatórios)
└── [outras subpastas...]      (módulos especializados)
```

### Correções de Imports Aplicadas:
1. `from autenticacao.X` → `from X` (simplificado para raiz)
2. `from core.authentication.X` → mantido (estrutura correta)
3. `from ui.X` → mantido (estrutura de pastas preservada)

### Como Usar:
1. Extrair este ZIP em `C:\\Users\\marci\\Downloads\\Integragal\\`
2. Duplo clique em `executar.bat`
3. Sistema funcionará com estrutura de pastas correta

### Teste de Funcionalidade:
Após extrair e executar, teste:
1. ✅ Painel Admin → Base URL GAL (editável)
2. ✅ Gerenciamento Usuários → Sem erro 'senha'
3. ✅ Fechamento de módulos → Um clique
4. ✅ Estrutura de pastas → Subpastas corretas

### Arquivos Corrigidos:
- `ui/admin_panel.py`: Campo Base URL GAL editável
- `ui/user_management.py`: Campo 'senha_hash' corrigido (7 localizações)
- `config.json`: Path configurado para usuarios.csv
- `autenticacao/auth_service.py`: Caminho atualizado
- Protocolos de fechamento melhorados

---
Sistema IntegraGAL v2.0 - Correção de Estrutura de Pastas
'''
    
    with open(os.path.join(DESTINO_TEMP, "ESTRUTURA_CORRIGIDA.md"), 'w', encoding='utf-8') as f:
        f.write(doc_content)
    
    print("✅ Criada documentação: ESTRUTURA_CORRIGIDA.md")

def criar_package_zip():
    """Cria o arquivo ZIP final"""
    
    with zipfile.ZipFile(PACKAGE_FINAL, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(DESTINO_TEMP):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, DESTINO_TEMP)
                zipf.write(file_path, arc_path)
    
    # Calcular tamanho
    tamanho_kb = os.path.getsize(PACKAGE_FINAL) / 1024
    
    print(f"\n🎁 Package final criado:")
    print(f"📁 Arquivo: {PACKAGE_FINAL}")
    print(f"📊 Tamanho: {tamanho_kb:.1f} KB")
    
    # Contar arquivos
    total_arquivos = sum(len(files) for r, d, files in os.walk(DESTINO_TEMP))
    print(f"📄 Total de arquivos: {total_arquivos}")
    
    return PACKAGE_FINAL

def main():
    print("🔧 Iniciando correção da estrutura de pastas do IntegraGAL...")
    print("=" * 60)
    
    # Criar estrutura corrigida
    destino = copiar_estrutura_com_correções()
    
    # Criar package ZIP
    package = criar_package_zip()
    
    print("\n" + "=" * 60)
    print("✅ CORREÇÃO CONCLUÍDA!")
    print(f"\n📦 Package corrigido: {package}")
    print(f"\n📋 Próximos passos:")
    print("1. Extrair em C:\\Users\\marci\\Downloads\\Integragal\\")
    print("2. Duplo clique em executar.bat")
    print("3. Testar funcionalidades")
    
    return package

if __name__ == "__main__":
    main()
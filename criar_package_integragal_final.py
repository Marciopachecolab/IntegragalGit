#!/usr/bin/env python3
"""
Cria package específico para execução em pasta Integragal
Com script de correção automática e instruções específicas
"""

import os
import zipfile
import shutil
from datetime import datetime

def criar_package_integragal():
    """Cria package específico para Integragal"""
    print("📦 Criando package para execução em pasta Integragal...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"IntegraGAL_Integragal_Completo_{timestamp}.zip"
    
    # Arquivos essenciais para o sistema
    arquivos_essenciais = [
        # Arquivos principais
        "IntegragalGit/main.py",
        "IntegragalGit/config.json",
        "IntegragalGit/requirements.txt",
        "IntegragalGit/__init__.py",
        
        # Autenticação
        "IntegragalGit/autenticacao/auth_service.py",
        "IntegragalGit/autenticacao/login.py",
        "IntegragalGit/core/authentication/user_manager.py",
        
        # Interface
        "IntegragalGit/ui/main_window.py",
        "IntegragalGit/ui/admin_panel.py",
        "IntegragalGit/ui/user_management.py",
        "IntegragalGit/ui/menu_handler.py",
        "IntegragalGit/ui/navigation.py",
        "IntegragalGit/ui/status_manager.py",
        
        # Banco de dados
        "IntegragalGit/banco/usuarios.csv",
        "IntegragalGit/banco/configuracoes_sistema.csv",
        "IntegragalGit/banco/exames_config.csv",
        "IntegragalGit/banco/sessoes.csv",
        
        # Utilitários
        "IntegragalGit/utils/logger.py",
        "IntegragalGit/utils/io_utils.py",
        "IntegragalGit/utils/db_utils.py",
        "IntegragalGit/utils/gui_utils.py",
        "IntegragalGit/utils/import_utils.py",
        
        # Serviços
        "IntegragalGit/services/config_service.py",
        "IntegragalGit/services/analysis_service.py",
        
        # Configuração
        "IntegragalGit/configuracao/configuracao.py",
        "IntegragalGit/configuracao/__init__.py",
        
        # Scripts e ferramentas de correção
        "corrigir_caminhos_integragal.py",
        "executar_integragal_v2.bat"
    ]
    
    # Criar arquivo ZIP
    with zipfile.ZipFile(f"/workspace/{package_name}", 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Adicionar arquivos essenciais
        for arquivo in arquivos_essenciais:
            arquivo_path = f"/workspace/{arquivo}"
            if os.path.exists(arquivo_path):
                # Para arquivos principais, colocar na raiz do ZIP
                if arquivo in ["IntegragalGit/main.py", "IntegragalGit/config.json", "IntegragalGit/requirements.txt", "IntegragalGit/__init__.py"]:
                    arcname = os.path.basename(arquivo)
                elif arquivo.startswith("corrigir_caminhos_integragal.py"):
                    arcname = "corrigir_caminhos_integragal.py"
                elif arquivo.startswith("executar_integragal_v2.bat"):
                    arcname = "executar.bat"
                else:
                    arcname = arquivo
                
                zipf.write(arquivo_path, arcname)
                print(f"  ✅ {arcname}")
            else:
                print(f"  ⚠️ Arquivo não encontrado: {arquivo}")
        
        # Adicionar diretório completo de banco
        for root, dirs, files in os.walk("/workspace/IntegragalGit/banco"):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.join("banco", file)
                zipf.write(file_path, arcname)
        
        # Adicionar diretório de logs (se existir)
        logs_path = "/workspace/IntegragalGit/logs"
        if os.path.exists(logs_path):
            for root, dirs, files in os.walk(logs_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, "/workspace")
                    zipf.write(file_path, arcname)
        
        # Adicionar guia específico
        guia_path = "/workspace/GUIA_EXECUCAO_INTEGRAGAL.md"
        if os.path.exists(guia_path):
            zipf.write(guia_path, "LEIA_PRIMEIRO.md")
            print(f"  ✅ LEIA_PRIMEIRO.md")
    
    package_size = os.path.getsize(f"/workspace/{package_name}")
    print(f"\n📦 Package criado: {package_name}")
    print(f"📏 Tamanho: {package_size:,} bytes ({package_size/1024:.1f} KB)")
    
    return package_name

def criar_instrucoes_especificas():
    """Cria instruções específicas para o package"""
    instrucoes = """# 📋 INSTRUÇÕES DE INSTALAÇÃO E EXECUÇÃO

## 🎯 Para executar em: C:\\Users\\marci\\Downloads\\Integragal

### PASSO 1: Extrair o Package
1. Baixar o arquivo: `IntegraGAL_Integragal_Completo_YYYYMMDD_HHMMSS.zip`
2. Extrair em: `C:\\Users\\marci\\Downloads\\Integragal`
3. Verificar se os arquivos ficaram na pasta `Integragal`

### PASSO 2: Executar Correção Automática
```bash
cd C:\\Users\\marci\\Downloads\\Integragal
python corrigir_caminhos_integragal.py
```

### PASSO 3: Iniciar o Sistema
```bash
python main.py
```
OU
```bash
executar.bat
```

## 🎮 Login do Sistema
- **Usuário**: `marcio`
- **Senha**: `flafla`

## ✅ Testes das Correções Implementadas

### 1. Base URL GAL
- Ir para: Painel Administrativo → Sistema
- Verificar se "Base URL GAL" é editável (campo editável)
- Alterar valor e clicar "Salvar Alterações"
- Sair e entrar novamente para verificar se salvou

### 2. Gerenciamento de Usuários
- Ir para: Ferramentas → Gerenciar Usuários
- Verificar se NÃO aparece erro "X Erro ao carregar usuário: 'senha'"
- Lista deve mostrar 4 usuários

### 3. Fechamento de Janelas
- Abrir qualquer módulo (Admin ou Usuários)
- Clicar no X de fechar
- Verificar se fecha com um clique (não múltiplos)

## 🛠️ Arquivos Importantes

### Arquivos Principais (raiz):
- `main.py` - Arquivo principal do sistema
- `config.json` - Configurações do sistema
- `executar.bat` - Script de execução
- `corrigir_caminhos_integragal.py` - Script de correção

### Pastas Importantes:
- `banco/` - Arquivos CSV (usuarios.csv, configuracoes, etc.)
- `autenticacao/` - Sistema de login
- `ui/` - Interface gráfica
- `logs/` - Logs do sistema (será criada automaticamente)

## ❗ Solução de Problemas

### "main.py não encontrado"
→ Verificar se extraiu corretamente em `C:\\Users\\marci\\Downloads\\Integragal`

### "ModuleNotFoundError"
→ Instalar dependências:
```bash
pip install customtkinter pandas bcrypt
```

### "Arquivo não encontrado"
→ Executar o script de correção:
```bash
python corrigir_caminhos_integragal.py
```

### Janela não abre
→ Verificar se tem Python instalado:
```bash
python --version
```

## 📞 Contato
Em caso de problemas, verificar arquivo `LEIA_PRIMEIRO.md` para mais detalhes.

---
**Data**: 02/12/2025  
**Sistema**: IntegraGAL v2.0 - Correções para Integragal  
**Status**: ✅ Pronto para execução
"""
    
    with open("/workspace/INSTRUCOES_INTEGRAGAL.md", 'w', encoding='utf-8') as f:
        f.write(instrucoes)
    
    return "/workspace/INSTRUCOES_INTEGRAGAL.md"

def main():
    """Função principal"""
    print("=" * 70)
    print("📦 CRIAÇÃO DO PACKAGE ESPECÍFICO PARA INTEGRAGAL")
    print("=" * 70)
    
    # Criar instruções específicas
    instrucoes_path = criar_instrucoes_especificas()
    print(f"\n📋 Instruções criadas: {instrucoes_path}")
    
    # Criar package
    package_name = criar_package_integragal()
    
    print("\n" + "=" * 70)
    print("🎯 PACKAGE INTEGRAGAL CRIADO COM SUCESSO!")
    print("=" * 70)
    print(f"\n📦 Arquivo: {package_name}")
    print(f"📋 Instruções: INSTRUCOES_INTEGRAGAL.md")
    print(f"\n💡 PARA O USUÁRIO:")
    print(f"1. Extrair {os.path.basename(package_name)} em C:\\Users\\marci\\Downloads\\Integragal")
    print(f"2. Executar: python corrigir_caminhos_integragal.py")
    print(f"3. Iniciar: python main.py (ou executar.bat)")
    print(f"4. Login: marcio / flafla")
    print(f"\n✅ Sistema pronto para execução em Integragal!")

if __name__ == "__main__":
    main()
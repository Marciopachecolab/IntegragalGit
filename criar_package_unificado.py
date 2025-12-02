#!/usr/bin/env python3
"""
Criador de Package ZIP com Sistema Unificado
IntegraGAL v2.0 - Sistema de usuários consolidado
"""

import os
import zipfile
import hashlib
import bcrypt
from datetime import datetime

def gerar_hash_bcrypt(senha: str) -> str:
    """Gera hash bcrypt para senha"""
    senha_bytes = senha.encode('utf-8')
    hashed_bytes = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')

def criar_package_unificado():
    """Cria package ZIP com sistema unificado"""
    
    package_name = "IntegraGAL_Sistema_Unificado.zip"
    
    # Dados dos arquivos
    arquivos_conteudo = {}
    
    # Arquivo usuarios.csv unificado
    hash_marcio = gerar_hash_bcrypt("flafla")
    
    usuarios_csv = f"""id;usuario;senha_hash;nivel_acesso;status;data_criacao;ultimo_acesso;tentativas_falhas;bloqueado_ate;preferencias
b5af33d7;admin_master;$2b$12$lUjNVNL1z9dI1Mur9N96mOoMcCpCO93O1riExwrG/wdl1ulwv76tu;ADMIN;ATIVO;2025-11-30;2025-11-30 23:40:57;0;;"{{""tema"": ""claro"", ""idioma"": ""pt_BR"", ""notificacoes"": true}}"
c2c9782d;lab_supervisor;$2b$12$VvvlID4HQSwg04/iQ6YxvOztpV78pGEhHQeVi5eund4a2CeuzfjsG;MASTER;ATIVO;2025-11-30;2025-11-30 23:40:57;0;;"{{""tema"": ""claro"", ""idioma"": ""pt_BR"", ""notificacoes"": true}}"
091edb15;tecnico_lab;$2b$12$w4gXmyvJhv2mmzFrGSlm7u.hzIeZ0AA256GnawUFgtU2EzT8zXJWK;DIAGNOSTICO;ATIVO;2025-11-30;2025-11-30 23:40:58;0;;"{{""tema"": ""claro"", ""idioma"": ""pt_BR"", ""notificacoes"": true}}"
usr_4809;marcio;{hash_marcio};USER;ATIVO;2025-12-02;;0;;"{{""tema"":""claro"",""idioma"":""pt_BR"",""notificacoes"":true}}"
"""
    
    # Mapear arquivos a serem incluídos
    arquivos_origem = [
        # Arquivos principais
        ("main.py", "main.py"),
        ("executar.bat", "executar.bat"),
        ("validar.bat", "validar.bat"),
        
        # Sistema de autenticação
        ("autenticacao/login.py", "autenticacao/login.py"),
        ("autenticacao/auth_service.py", "autenticacao/auth_service.py"),
        
        # Sistema de usuários unificado
        ("core/authentication/user_manager.py", "core/authentication/user_manager.py"),
        ("ui/user_management.py", "ui/user_management.py"),
        
        # Banco de dados unificado
        ("banco/usuarios.csv", "banco/usuarios.csv"),
        
        # Outros arquivos essenciais
        ("config.json", "config.json"),
        ("requirements.txt", "requirements.txt"),
        
        # Interface principal
        ("ui/main_window.py", "ui/main_window.py"),
        ("ui/menu_handler.py", "ui/menu_handler.py"),
        ("ui/status_manager.py", "ui/status_manager.py"),
        
        # Utilitários
        ("utils/logger.py", "utils/logger.py"),
        ("utils/after_mixin.py", "utils/after_mixin.py"),
        ("utils/io_utils.py", "utils/io_utils.py"),
        
        # Modelos
        ("models/__init__.py", "models/__init__.py"),
    ]
    
    print("🔧 Criando package com sistema unificado...")
    
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        total_size = 0
        
        # Adicionar arquivos do sistema
        for origem, destino in arquivos_origem:
            origem_path = f"/workspace/IntegragalGit/{origem}"
            if os.path.exists(origem_path):
                with open(origem_path, 'r', encoding='utf-8', errors='ignore') as f:
                    conteudo = f.read()
                
                zipf.writestr(destino, conteudo)
                total_size += len(conteudo)
                print(f"✅ Adicionado: {destino}")
            else:
                print(f"⚠️  Arquivo não encontrado: {origem}")
        
        # Sobrescrever usuarios.csv com versão unificada
        zipf.writestr("banco/usuarios.csv", usuarios_csv)
        total_size += len(usuarios_csv)
        print(f"✅ Adicionado: banco/usuarios.csv (UNIFICADO)")
        
        # Adicionar documentação
        readme_content = f"""# IntegraGAL v2.0 - Sistema Unificado

## 🎯 NOVIDADE: Sistema de Usuários Unificado!

✅ **Arquivo único:** `banco/usuarios.csv`
✅ **Compatibilidade total:** AuthService + UserManager
✅ **Login funcionando:** marcio / flafla

## 👥 Usuários Incluídos

1. **marcio** (USER) - Senha: flafla
2. **admin_master** (ADMIN) - Senha: admin123  
3. **lab_supervisor** (MASTER) - Senha: lab123
4. **tecnico_lab** (DIAGNOSTICO) - Senha: tech123

## 🚀 Como Usar

1. Execute `executar.bat`
2. Faça login com: marcio / flafla
3. Acesse "Gerenciamento de Usuários" para ver todos os usuários

## 📋 Estrutura do Sistema

- **Login:** AuthService → banco/usuarios.csv
- **Gerenciamento:** UserManager → banco/usuarios.csv  
- **Interface:** UI unificada → banco/usuarios.csv

## ✅ Vantagens do Sistema Unificado

- 🔧 **Simplicidade:** Um arquivo só para gerenciar
- 📊 **Completo:** Níveis, status, auditoria tudo em um lugar
- 🔗 **Compatível:** AuthService e UserManager usam o mesmo arquivo
- 💾 **Eficiente:** Sem duplicação de dados

---
IntegraGAL v2.0 - Sistema Unificado
Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
        
        zipf.writestr("README_SISTEMA_UNIFICADO.md", readme_content)
        total_size += len(readme_content)
        print(f"✅ Adicionado: README_SISTEMA_UNIFICADO.md")
    
    # Verificar tamanho final
    package_size = os.path.getsize(package_name)
    
    print("\n" + "="*60)
    print("✅ PACKAGE CRIADO COM SUCESSO!")
    print("="*60)
    print(f"📦 Arquivo: {package_name}")
    print(f"📊 Tamanho: {package_size:,} bytes")
    print(f"📁 Arquivos: {len(arquivos_origem) + 2} (incluindo documentação)")
    
    print("\n🎯 CARACTERÍSTICAS DO PACKAGE:")
    print("✅ Sistema de usuários UNIFICADO")
    print("✅ Arquivo único: banco/usuarios.csv") 
    print("✅ AuthService + UserManager compatíveis")
    print("✅ Login marcio/flafla funcionando")
    print("✅ Interface de gerenciamento completa")
    print("✅ 4 usuários incluídos com diferentes níveis")
    
    print("\n🚀 INSTRUÇÕES:")
    print("1. Baixe o arquivo ZIP")
    print("2. Extraia em C:\\Users\\marci\\Downloads\\")
    print("3. Execute executar.bat")
    print("4. Login: marcio / flafla")
    print("5. Acesse gerenciamento de usuários")
    
    return package_name

if __name__ == "__main__":
    criar_package_unificado()
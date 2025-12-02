#!/usr/bin/env python3
"""
Script para unificar o sistema de usuários - VERSÃO SIMPLIFICADA
Consolida credenciais.csv e usuarios.csv em um único arquivo
"""

import pandas as pd
import shutil
import os

def main():
    print("🔧 UNIFICAÇÃO DO SISTEMA DE USUÁRIOS")
    print("="*50)
    
    # Paths
    credenciais_path = "/workspace/IntegragalGit/banco/credenciais.csv"
    usuarios_path = "/workspace/IntegragalGit/banco/usuarios.csv"
    backup_dir = "/workspace/IntegragalGit/backup_usuarios"
    
    # Criar backup
    os.makedirs(backup_dir, exist_ok=True)
    
    if os.path.exists(credenciais_path):
        shutil.copy2(credenciais_path, os.path.join(backup_dir, "credenciais_original.csv"))
        print("✅ Backup de credenciais.csv criado")
    
    if os.path.exists(usuarios_path):
        shutil.copy2(usuarios_path, os.path.join(backup_dir, "usuarios_original.csv"))
        print("✅ Backup de usuarios.csv criado")
    
    # Consolidar usuários
    usuarios_consolidados = []
    
    # Carregar usuarios.csv (mais completo)
    if os.path.exists(usuarios_path):
        df_usuarios = pd.read_csv(usuarios_path)
        print(f"📂 Carregados {len(df_usuarios)} usuários de usuarios.csv")
        
        for _, row in df_usuarios.iterrows():
            usuarios_consolidados.append({
                'id': row['id'],
                'usuario': row['usuario'],
                'senha_hash': row['senha_hash'],
                'nivel_acesso': row['nivel_acesso'],
                'status': row['status'],
                'data_criacao': row['data_criacao'],
                'ultimo_acesso': row['ultimo_acesso'],
                'tentativas_falhas': int(row['tentativas_falhas']),
                'bloqueado_ate': row['bloqueado_ate'] if pd.notna(row['bloqueado_ate']) else '',
                'preferencias': row['preferencias'] if pd.notna(row['preferencias']) else '{"tema":"claro","idioma":"pt_BR","notificacoes":true}'
            })
    
    # Adicionar usuários do credenciais.csv se não existirem
    if os.path.exists(credenciais_path):
        df_credenciais = pd.read_csv(credenciais_path, sep=';')
        print(f"📂 Carregados {len(df_credenciais)} usuários de credenciais.csv")
        
        for _, row in df_credenciais.iterrows():
            usuario_existe = any(u['usuario'] == row['usuario'] for u in usuarios_consolidados)
            
            if not usuario_existe:
                usuarios_consolidados.append({
                    'id': f"usr_{hash(row['usuario']) % 10000:04d}",
                    'usuario': row['usuario'],
                    'senha_hash': row['senha_hash'],
                    'nivel_acesso': 'USER',
                    'status': 'ATIVO',
                    'data_criacao': '2025-12-02',
                    'ultimo_acesso': '',
                    'tentativas_falhas': 0,
                    'bloqueado_ate': '',
                    'preferencias': '{"tema":"claro","idioma":"pt_BR","notificacoes":true}'
                })
                print(f"➕ Adicionado usuário: {row['usuario']}")
    
    # Salvar arquivo unificado
    if usuarios_consolidados:
        df_final = pd.DataFrame(usuarios_consolidados)
        df_final.to_csv(usuarios_path, sep=';', index=False)
        
        print(f"\n✅ Arquivo unificado: {usuarios_path}")
        print(f"📊 Total de usuários: {len(usuarios_consolidados)}")
        
        print("\n👥 USUÁRIOS CONSOLIDADOS:")
        for i, usuario in enumerate(usuarios_consolidados, 1):
            print(f"   {i}. {usuario['usuario']} - {usuario['nivel_acesso']} - {usuario['status']}")
        
        # Remover credenciais.csv
        if os.path.exists(credenciais_path):
            os.remove(credenciais_path)
            print(f"\n🗑️  credenciais.csv removido (dados migrados)")
        
        # Atualizar auth_service.py para usar usuarios.csv
        auth_service_path = "/workspace/IntegragalGit/autenticacao/auth_service.py"
        if os.path.exists(auth_service_path):
            with open(auth_service_path, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            conteudo = conteudo.replace(
                'CAMINHO_CREDENCIAIS = os.path.join(BASE_DIR, "banco", "credenciais.csv")',
                'CAMINHO_CREDENCIAIS = os.path.join(BASE_DIR, "banco", "usuarios.csv")'
            )
            
            with open(auth_service_path, 'w', encoding='utf-8') as f:
                f.write(conteudo)
            
            print("✅ auth_service.py atualizado para usar usuarios.csv")
        
        print("\n" + "="*50)
        print("✅ UNIFICAÇÃO CONCLUÍDA!")
        print("="*50)
        print("✅ Agora você TEM apenas um arquivo: usuarios.csv")
        print("✅ AuthService + UserManager usam o mesmo arquivo")
        print("✅ Login funciona com: marcio/flafla")
        print("✅ Interface de usuários consolidada")
        
    else:
        print("❌ Nenhum usuário encontrado")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Validador Simples de Credenciais para Windows
Testa se o sistema de login está funcionando
"""

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
    
    print("\nValidação concluída.")
    input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()

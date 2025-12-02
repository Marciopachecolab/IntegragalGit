#!/usr/bin/env python3
"""
Teste das correções aplicadas para Windows
"""

import os
import sys
import pandas as pd
import bcrypt

def testar_auth_service_corrigido():
    """Testa o auth_service.py com as correções aplicadas"""
    print("=== TESTE DO AUTH_SERVICE CORRIGIDO ===\n")
    
    # Adiciona o diretório ao path
    base_dir = "/workspace/IntegragalGit"
    if base_dir not in sys.path:
        sys.path.append(base_dir)
    
    try:
        from autenticacao.auth_service import AuthService
        print("✅ Importação do AuthService bem-sucedida")
        
        # Instancia o serviço
        auth = AuthService()
        print("✅ Instância do AuthService criada")
        
        # Testa autenticação
        resultado = auth.verificar_senha("marcio", "flafla")
        print(f"🔐 Teste de autenticação marcio/flafla: {'✅ SUCESSO' if resultado else '❌ FALHA'}")
        
        if resultado:
            print("🎉 As correções estão funcionando corretamente!")
        else:
            print("⚠️ Ainda há problemas com a autenticação")
            
    except Exception as e:
        print(f"❌ Erro ao testar AuthService: {e}")
        import traceback
        traceback.print_exc()

def mostrar_caminhos_encontrados():
    """Mostra os caminhos que o sistema está usando"""
    print("\n=== CAMINHOS UTILIZADOS ===")
    
    # Importa o auth_service para ver os caminhos
    sys.path.append("/workspace/IntegragalGit")
    from autenticacao.auth_service import CAMINHO_CREDENCIAIS, BASE_DIR
    
    print(f"📁 BASE_DIR: {BASE_DIR}")
    print(f"🔑 CAMINHO_CREDENCIAIS: {CAMINHO_CREDENCIAIS}")
    print(f"✅ Arquivo existe: {'SIM' if os.path.exists(CAMINHO_CREDENCIAIS) else 'NÃO'}")
    
    if os.path.exists(CAMINHO_CREDENCIAIS):
        try:
            df = pd.read_csv(CAMINHO_CREDENCIAIS, sep=';', encoding='utf-8-sig')
            print(f"📊 Arquivo lido: {len(df)} linha(s)")
            print(f"👤 Usuários: {df['usuario'].tolist()}")
        except Exception as e:
            print(f"❌ Erro ao ler arquivo: {e}")

def main():
    testar_auth_service_corrigido()
    mostrar_caminhos_encontrados()
    
    print("\n" + "="*50)
    print("✅ TESTE CONCLUÍDO")

if __name__ == "__main__":
    main()
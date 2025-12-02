#!/usr/bin/env python3
"""
Script de Verificação - Sistema IntegraGAL
Verifica a consistência entre os arquivos de configuração
"""

import json
import os
import sys

def verificar_configuracoes():
    """Verifica a consistência entre os config.json"""
    
    print("=" * 60)
    print("    VERIFICAÇÃO DE CONFIGURAÇÕES - INTEGRA GAL")
    print("=" * 60)
    
    # Verificar config.json principal
    print("\n📁 CONFIG.JSON PRINCIPAL (raiz):")
    if os.path.exists("config.json"):
        with open("config.json", 'r', encoding='utf-8') as f:
            config_principal = json.load(f)
        
        base_url_principal = config_principal.get('gal_integration', {}).get('base_url', 'NÃO DEFINIDO')
        lab_name_principal = config_principal.get('general', {}).get('lab_name', 'NÃO DEFINIDO')
        
        print(f"   ✅ Base URL: {base_url_principal}")
        print(f"   ✅ Lab Name: {lab_name_principal}")
        print(f"   📊 Estrutura: {list(config_principal.keys())}")
    else:
        print("   ❌ ARQUIVO NÃO ENCONTRADO")
        return False
    
    # Verificar config.json da subpasta
    print("\n📁 CONFIG.JSON DA SUBCONFIGURAÇÃO:")
    configuracao_path = "configuracao/config.json"
    if os.path.exists(configuracao_path):
        with open(configuracao_path, 'r', encoding='utf-8') as f:
            config_subpasta = json.load(f)
        
        base_url_subpasta = config_subpasta.get('gal_integration', {}).get('base_url', 'NÃO DEFINIDO')
        lab_name_subpasta = config_subpasta.get('general', {}).get('lab_name', 'NÃO DEFINIDO')
        
        print(f"   ✅ Base URL: {base_url_subpasta}")
        print(f"   ✅ Lab Name: {lab_name_subpasta}")
        print(f"   📊 Estrutura: {list(config_subpasta.keys())}")
    else:
        print("   ❌ ARQUIVO NÃO ENCONTRADO")
        return False
    
    # Comparar valores
    print("\n🔍 COMPARAÇÃO:")
    consistencia = True
    
    if base_url_principal == base_url_subpasta:
        print("   ✅ Base URLs estão sincronizadas")
    else:
        print(f"   ❌ Base URLs NÃO estão sincronizadas!")
        print(f"      Principal: {base_url_principal}")
        print(f"      Subpasta:  {base_url_subpasta}")
        consistencia = False
    
    if lab_name_principal == lab_name_subpasta:
        print("   ✅ Lab Names estão sincronizados")
    else:
        print(f"   ❌ Lab Names NÃO estão sincronizados!")
        print(f"      Principal: {lab_name_principal}")
        print(f"      Subpasta:  {lab_name_subpasta}")
        consistencia = False
    
    # Verificar arquivos de backup
    print("\n💾 BACKUPS ENCONTRADOS:")
    backup_files = [f for f in os.listdir('.') if f.startswith('config_backup_') and f.endswith('.json')]
    backup_files.sort(reverse=True)
    
    if backup_files:
        print(f"   📁 {len(backup_files)} arquivos de backup encontrados:")
        for i, backup in enumerate(backup_files[:3]):  # Mostrar apenas os 3 mais recentes
            print(f"      {i+1}. {backup}")
        if len(backup_files) > 3:
            print(f"      ... e mais {len(backup_files) - 3} backups")
    else:
        print("   📭 Nenhum backup encontrado")
    
    # Status final
    print("\n" + "=" * 60)
    if consistencia:
        print("✅ SISTEMA DE CONFIGURAÇÃO: CONSISTENTE")
    else:
        print("❌ SISTEMA DE CONFIGURAÇÃO: REQUER SINCRONIZAÇÃO")
    print("=" * 60)
    
    return consistencia

def verificar_arquivo_usuarios():
    """Verifica o arquivo de usuários"""
    print("\n👥 VERIFICAÇÃO DO ARQUIVO DE USUÁRIOS:")
    
    usuarios_path = "banco/usuarios.csv"
    if not os.path.exists(usuarios_path):
        print("   ❌ Arquivo não encontrado")
        return False
    
    try:
        import pandas as pd
        
        # Tentar ler com separador ';' primeiro
        try:
            df = pd.read_csv(usuarios_path, sep=';', encoding='utf-8')
            print(f"   ✅ Lido com separador ';' - {len(df)} usuários")
        except:
            # Se falhar, tentar com ','
            df = pd.read_csv(usuarios_path, sep=',', encoding='utf-8')
            print(f"   ✅ Lido com separador ',' - {len(df)} usuários")
        
        # Verificar se coluna senha_hash existe
        if 'senha_hash' in df.columns:
            print("   ✅ Coluna 'senha_hash' encontrada")
            usuarios_com_senha = len(df[df['senha_hash'].notna() & (df['senha_hash'] != '')])
            print(f"   📊 Usuários com senha: {usuarios_com_senha}/{len(df)}")
        else:
            print("   ❌ Coluna 'senha_hash' NÃO encontrada")
            print(f"   📊 Colunas disponíveis: {list(df.columns)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar arquivo: {str(e)}")
        return False

if __name__ == "__main__":
    print("Script de Verificação IntegraGAL")
    print("Execute este script no diretório principal do sistema\n")
    
    consistencia_config = verificar_configuracoes()
    consistencia_usuarios = verificar_arquivo_usuarios()
    
    print("\n🏁 VERIFICAÇÃO CONCLUÍDA")
    
    if consistencia_config and consistencia_usuarios:
        print("✅ Todos os sistemas estão funcionando corretamente!")
        sys.exit(0)
    else:
        print("❌ Foram encontrados problemas que requerem atenção.")
        sys.exit(1)
#!/usr/bin/env python3
"""
Script para diagnosticar os problemas relatados pelo usuário
"""

import json
import os
import sys
from datetime import datetime

def verificar_arquivos_configuracao():
    """Verifica a estrutura dos arquivos de configuração"""
    print("🔍 DIAGNÓSTICO DOS ARQUIVOS DE CONFIGURAÇÃO")
    print("=" * 60)
    
    # Verificar config.json raiz
    if os.path.exists("config.json"):
        with open("config.json", 'r', encoding='utf-8') as f:
            config_raiz = json.load(f)
        
        print("✅ config.json (raiz) encontrado:")
        print(f"   📋 Seções: {list(config_raiz.keys())}")
        
        # Verificar se tem seções gerais
        if 'general' in config_raiz:
            print(f"   📝 Seção 'general': {config_raiz['general']}")
        else:
            print("   ❌ Seção 'general' NÃO encontrada em config.json")
        
        # Verificar gal_integration
        if 'gal_integration' in config_raiz:
            print(f"   🌐 gal_integration.base_url: {config_raiz['gal_integration'].get('base_url', 'NÃO CONFIGURADO')}")
        else:
            print("   ❌ Seção 'gal_integration' NÃO encontrada em config.json")
    else:
        print("❌ config.json (raiz) NÃO encontrado")
    
    print()
    
    # Verificar configuracao/config.json
    if os.path.exists("configuracao/config.json"):
        with open("configuracao/config.json", 'r', encoding='utf-8') as f:
            config_subpasta = json.load(f)
        
        print("✅ configuracao/config.json encontrado:")
        print(f"   📋 Seções: {list(config_subpasta.keys())}")
        
        # Verificar general
        if 'general' in config_subpasta:
            print(f"   📝 Seção 'general': {config_subpasta['general']}")
            if 'lab_name' in config_subpasta['general']:
                print(f"   🏥 lab_name: {config_subpasta['general']['lab_name']}")
        else:
            print("   ❌ Seção 'general' NÃO encontrada em configuracao/config.json")
        
        # Verificar gal_integration
        if 'gal_integration' in config_subpasta:
            print(f"   🌐 gal_integration.base_url: {config_subpasta['gal_integration'].get('base_url', 'NÃO CONFIGURADO')}")
        else:
            print("   ❌ Seção 'gal_integration' NÃO encontrada em configuracao/config.json")
    else:
        print("❌ configuracao/config.json NÃO encontrado")
    
    print()
    print("🎯 PROBLEMA IDENTIFICADO:")
    if os.path.exists("config.json") and not os.path.exists("configuracao/config.json"):
        print("   ❌ config.json existe mas configuracao/config.json NÃO")
        return "ARQUIVOS_DIFERENTES"
    elif os.path.exists("config.json") and os.path.exists("configuracao/config.json"):
        with open("config.json", 'r') as f1, open("configuracao/config.json", 'r') as f2:
            config1 = json.load(f1)
            config2 = json.load(f2)
            
        tem_general1 = 'general' in config1
        tem_general2 = 'general' in config2
        
        if not tem_general1 and tem_general2:
            print("   ❌ config.json NÃO tem seção 'general' mas configuracao/config.json TEM")
            print("   ➡️  O sistema está salvando lab_name em configuracao/config.json")
            print("   ➡️  Mas o ConfigService salva em config.json que não tem essa seção")
            return "ESTRUTURAS_DIFERENTES"
        elif tem_general1 and tem_general2:
            print("   ✅ Ambos os arquivos têm a seção 'general'")
            return "ESTRUTURAS_SIMILARES"
    
    return "UNKNOWN"

def testar_salvamento():
    """Testa o salvamento das configurações"""
    print("\n🧪 TESTE DE SALVAMENTO")
    print("=" * 30)
    
    # Criar um backup dos arquivos originais
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if os.path.exists("config.json"):
        import shutil
        shutil.copy2("config.json", f"config_backup_teste_{timestamp}.json")
        print("✅ Backup de config.json criado")
    
    if os.path.exists("configuracao/config.json"):
        import shutil
        shutil.copy2("configuracao/config.json", f"configuracao/config_backup_teste_{timestamp}.json")
        print("✅ Backup de configuracao/config.json criado")
    
    # Carregar e modificar
    config_path = "config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Adicionar seção general se não existir
        if 'general' not in config:
            config['general'] = {}
            print("📝 Adicionando seção 'general' ao config.json")
        
        # Testar mudanças
        config['general']['lab_name'] = "LAB TESTE SALVAMENTO"
        config['general']['test_timestamp'] = timestamp
        
        if 'gal_integration' not in config:
            config['gal_integration'] = {}
            print("📝 Adicionando seção 'gal_integration' ao config.json")
        
        config['gal_integration']['base_url'] = "https://teste-salvamento.saude.sc.gov.br"
        
        # Salvar
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        print(f"✅ Salvamento testado em {timestamp}")
        
        # Verificar se foi salvo
        with open(config_path, 'r', encoding='utf-8') as f:
            config_test = json.load(f)
        
        if config_test.get('general', {}).get('lab_name') == "LAB TESTE SALVAMENTO":
            print("✅ Lab_name foi salvo corretamente")
        else:
            print("❌ Lab_name NÃO foi salvo corretamente")
        
        if config_test.get('gal_integration', {}).get('base_url') == "https://teste-salvamento.saude.sc.gov.br":
            print("✅ Base URL foi salva corretamente")
        else:
            print("❌ Base URL NÃO foi salva corretamente")
    
    return config_path

def verificar_botao_saida():
    """Verifica a implementação do botão de saída"""
    print("\n🚪 DIAGNÓSTICO DO BOTÃO DE SAÍDA")
    print("=" * 40)
    
    # Verificar se o arquivo user_management.py tem o método
    if os.path.exists("ui/user_management.py"):
        with open("ui/user_management.py", 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        if 'def _sair_para_menu_principal(self):' in conteudo:
            print("✅ Método _sair_para_menu_principal encontrado")
        else:
            print("❌ Método _sair_para_menu_principal NÃO encontrado")
        
        if 'command=self._sair_para_menu_principal' in conteudo:
            print("✅ Botão configurado para chamar o método correto")
        else:
            print("❌ Botão NÃO está configurado para chamar o método")
        
        if 'self.main_window.deiconify()' in conteudo:
            print("✅ Janela principal configurada para ser mostrada")
        else:
            print("❌ Janela principal NÃO configurada para ser mostrada")
    else:
        print("❌ ui/user_management.py NÃO encontrado")

def main():
    """Função principal de diagnóstico"""
    print("🔧 DIAGNÓSTICO COMPLETO DOS PROBLEMAS")
    print("=" * 60)
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Diretório atual: {os.getcwd()}")
    
    problema_config = verificar_arquivos_configuracao()
    testar_salvamento()
    verificar_botao_saida()
    
    print("\n📋 RESUMO DO DIAGNÓSTICO")
    print("=" * 30)
    if problema_config == "ESTRUTURAS_DIFERENTES":
        print("🎯 PROBLEMA PRINCIPAL IDENTIFICADO:")
        print("   ➡️  Os dois arquivos de configuração têm estruturas diferentes")
        print("   ➡️  ConfigService salva em config.json (sem seção 'general')")
        print("   ➡️  Sistema espera salvar em configuracao/config.json (com seção 'general')")
        print("\n🛠️  SOLUÇÃO:")
        print("   ➡️  Unificar a estrutura dos arquivos de configuração")
        print("   ➡️  Garantir que config.json tenha seção 'general' para lab_name")
        print("   ➡️  Sincronizar automaticamente entre os dois arquivos")
    elif problema_config == "ARQUIVOS_DIFERENTES":
        print("🎯 PROBLEMA: Um arquivo existe e o outro não")

if __name__ == "__main__":
    main()

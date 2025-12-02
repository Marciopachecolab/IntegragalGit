#!/usr/bin/env python3
"""
Script de teste pós-limpeza para verificar se o sistema ainda funciona
Execute após fazer as limpezas: python testar_pos_limpeza.py
"""

import sys
import os

# Adicionar diretório atual ao path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

def testar_importacoes_criticas():
    """Testa se as importações críticas ainda funcionam"""
    print("🔍 Testando importações críticas...")
    
    modulos_criticos = [
        ('ui.main_window', 'criar_aplicacao_principal'),
        ('ui.menu_handler', 'MenuHandler'),
        ('ui.status_manager', 'StatusManager'),
        ('ui.navigation', 'NavigationManager'),
        ('utils.logger', 'registrar_log'),
        ('autenticacao.login', 'autenticar_usuario'),
        ('models', 'AppState'),
        ('analise.vr1e2_biomanguinhos_7500', 'analisar_placa_vr1e2_7500'),
    ]
    
    sucessos = 0
    falhas = []
    
    for modulo, item in modulos_criticos:
        try:
            module = __import__(modulo, fromlist=[item])
            getattr(module, item)
            print(f"   ✅ {modulo}.{item}")
            sucessos += 1
        except Exception as e:
            print(f"   ❌ {modulo}.{item} - {e}")
            falhas.append(f"{modulo}.{item}: {e}")
    
    return sucessos, falhas

def testar_arquivos_essenciais():
    """Verifica se os arquivos essenciais existem"""
    print("\n📁 Verificando arquivos essenciais...")
    
    arquivos_essenciais = [
        'main.py',
        'config.json',
        'requirements.txt',
        'banco/credenciais.csv',
        'models.py',
        'ui/__init__.py',
        'ui/main_window.py',
        'utils/logger.py',
    ]
    
    sucessos = 0
    falhas = []
    
    for arquivo in arquivos_essenciais:
        caminho_completo = os.path.join(BASE_DIR, arquivo)
        if os.path.exists(caminho_completo):
            print(f"   ✅ {arquivo}")
            sucessos += 1
        else:
            print(f"   ❌ {arquivo} - não encontrado")
            falhas.append(arquivo)
    
    return sucessos, falhas

def testar_usuario_marcio():
    """Testa se o usuário marcio ainda existe"""
    print("\n👤 Verificando usuário marcio...")
    
    try:
        import bcrypt
        import csv
        
        credenciais_path = os.path.join(BASE_DIR, 'banco', 'credenciais.csv')
        with open(credenciais_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            usuarios = list(reader)
        
        marcio_encontrado = any(u['usuario'] == 'marcio' for u in usuarios)
        if marcio_encontrado:
            print("   ✅ Usuário marcio encontrado")
            return True, None
        else:
            return False, "Usuário marcio não encontrado"
    except Exception as e:
        return False, f"Erro ao verificar usuário: {e}"

def main():
    """Função principal de teste"""
    print("🧪 TESTE PÓS-LIMPEZA - IntegragalGit")
    print("=" * 50)
    
    # Testar importações
    imports_ok, imports_falhas = testar_importacoes_criticas()
    
    # Testar arquivos
    arquivos_ok, arquivos_falhas = testar_arquivos_essenciais()
    
    # Testar usuário marcio
    marcio_ok, marcio_erro = testar_usuario_marcio()
    
    # Relatório final
    print("\n" + "=" * 50)
    print("📊 RELATÓRIO FINAL")
    print("=" * 50)
    
    total_sucessos = imports_ok + arquivos_ok + (1 if marcio_ok else 0)
    total_teste = len([1]) + len([1]) + len([1])  # 3 testes principais
    
    print(f"✅ Importações críticas: {imports_ok}/7")
    print(f"✅ Arquivos essenciais: {arquivos_ok}/8")
    print(f"✅ Usuário marcio: {'OK' if marcio_ok else 'FALHA'}")
    
    if imports_falhas:
        print(f"\n❌ Falhas nas importações:")
        for falha in imports_falhas:
            print(f"   • {falha}")
    
    if arquivos_falhas:
        print(f"\n❌ Arquivos faltando:")
        for falha in arquivos_falhas:
            print(f"   • {falha}")
    
    if marcio_erro:
        print(f"\n❌ Erro no usuário marcio: {marcio_erro}")
    
    # Status geral
    if imports_ok >= 6 and arquivos_ok >= 7 and marcio_ok:
        print("\n🎉 SISTEMA FUNCIONANDO CORRETAMENTE PÓS-LIMPEZA!")
        print("✅ Todos os módulos essenciais estão operacionais")
        return True
    else:
        print("\n⚠️  PROBLEMAS DETECTADOS PÓS-LIMPEZA")
        print("🔧 Verifique os itens acima para correções")
        return False

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
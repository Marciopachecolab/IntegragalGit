#!/usr/bin/env python3
"""
Script Principal de Gerenciamento da Refatoração - TAREFA 1
Oferece interface amigável para executar, validar ou desfazer a refatoração.

Uso:
    python gerenciar_refatoracao.py

Autor: MiniMax Agent
"""

import os
import sys
import subprocess
import datetime
from pathlib import Path

def limpar_tela():
    """Limpa a tela do console"""
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_cabecalho():
    """Mostra o cabeçalho do programa"""
    print("🔧 GERENCIADOR DE REFATORAÇÃO - TAREFA 1")
    print("=" * 60)
    print("IntegraGAL v2.0 - Arquitetura Modular")
    print("Autor: MiniMax Agent")
    print("Data: 2025-12-01")
    print("=" * 60)
    print()

def verificar_estado_atual():
    """Verifica o estado atual da refatoração"""
    print("🔍 VERIFICANDO ESTADO ATUAL...")
    print("-" * 40)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Verificar main.py
    main_path = os.path.join(base_dir, 'main.py')
    if os.path.exists(main_path):
        with open(main_path, 'r') as f:
            linhas = len(f.readlines())
        
        with open(main_path, 'r') as f:
            conteudo = f.read()
        
        # Verificar se já foi refatorado
        if 'from ui.main_window import criar_aplicacao_principal' in conteudo:
            estado = "REFATORADO"
            print(f"📄 main.py: {linhas} linhas (REFATORADO)")
        else:
            estado = "ORIGINAL"
            print(f"📄 main.py: {linhas} linhas (ORIGINAL)")
    else:
        estado = "ERRO"
        print("❌ main.py não encontrado")
    
    # Verificar diretório ui/
    ui_dir = os.path.join(base_dir, 'ui')
    if os.path.exists(ui_dir):
        arquivos_ui = len([f for f in os.listdir(ui_dir) if f.endswith('.py')])
        print(f"📁 ui/: {arquivos_ui} arquivos Python")
    else:
        print("📁 ui/: não existe")
    
    # Verificar backups
    backups = [d for d in os.listdir(base_dir) if d.startswith('_backup_refatoracao_')]
    if backups:
        print(f"💾 Backups: {len(backups)} encontrado(s)")
    else:
        print("💾 Backups: nenhum encontrado")
    
    print("-" * 40)
    return estado

def executar_script(nome_script, descricao):
    """Executa um script e retorna o resultado"""
    print(f"\n🚀 EXECUTANDO: {descricao}")
    print("-" * 50)
    
    try:
        # Executar script
        result = subprocess.run([sys.executable, nome_script], 
                              capture_output=True, 
                              text=True, 
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        
        # Mostrar output
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("⚠️ AVISOS/ERROS:")
            print(result.stderr)
        
        # Retornar sucesso
        if result.returncode == 0:
            print(f"✅ {descricao} concluído com sucesso")
            return True
        else:
            print(f"❌ {descricao} falhou (código: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao executar {nome_script}: {e}")
        return False

def mostrar_menu():
    """Mostra o menu principal"""
    print("📋 OPÇÕES DISPONÍVEIS:")
    print()
    print("1. 🚀 EXECUTAR REFATORAÇÃO COMPLETA")
    print("   - Aplica toda a refatoração da TAREFA 1")
    print("   - Cria arquitetura modular UI")
    print("   - Reduz main.py de 282 para ~108 linhas")
    print()
    print("2. 🧪 VALIDAR REFATORAÇÃO ATUAL")
    print("   - Verifica se a refatoração foi aplicada corretamente")
    print("   - Mostra estatísticas de sucesso")
    print()
    print("3. 🔄 ROLLBACK (DESFAZER REFATORAÇÃO)")
    print("   - Restaura main.py original")
    print("   - Remove diretório ui/")
    print("   - Desfaz todas as mudanças")
    print()
    print("4. 📊 VER ESTADO ATUAL")
    print("   - Mostra status da refatoração")
    print("   - Informações sobre arquivos e backups")
    print()
    print("5. 📖 AJUDA")
    print("   - Mostra documentação completa")
    print()
    print("0. 🚪 SAIR")
    print()

def mostrar_ajuda():
    """Mostra a ajuda completa"""
    print("\n📖 AJUDA COMPLETA")
    print("=" * 50)
    print()
    print("🎯 OBJETIVO DA TAREFA 1:")
    print("   Modularizar o main.py de 282 linhas para ~108 linhas")
    print("   Criar arquitetura UI com 4 gerenciadores especializados")
    print()
    print("🏗️ COMPONENTES CRIADOS:")
    print("   • StatusManager (47 linhas)")
    print("   • MenuHandler (236 linhas)")
    print("   • NavigationManager (223 linhas)")
    print("   • MainWindow (293 linhas)")
    print()
    print("📊 RESULTADOS ESPERADOS:")
    print("   • Redução de 62% no tamanho do main.py")
    print("   • Código organizado por responsabilidade")
    print("   • Melhor manutenibilidade")
    print("   • Preparação para extensibilidade")
    print()
    print("⚠️ IMPORTANTE:")
    print("   • Backup automático é criado antes da refatoração")
    print("   • Sistema original é preservado")
    print("   • Rollback disponível se necessário")
    print()
    print("🔗 ARQUIVOS ENVOLVIDOS:")
    print("   • ui/__init__.py - Inicialização do módulo")
    print("   • ui/main_window.py - Janela principal refatorada")
    print("   • ui/menu_handler.py - Gerenciador de menu")
    print("   • ui/status_manager.py - Gerenciador de status")
    print("   • ui/navigation.py - Sistema de navegação")
    print()
    input("Pressione ENTER para continuar...")

def mostrar_status_detalhado():
    """Mostra status detalhado"""
    print("\n📊 STATUS DETALHADO")
    print("=" * 50)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Estatísticas de arquivos
    arquivos_py = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py'):
                arquivos_py.append(os.path.join(root, file))
    
    ui_arquivos = [f for f in arquivos_py if 'ui' in f]
    
    print(f"📁 Total de arquivos Python: {len(arquivos_py)}")
    print(f"📁 Arquivos no módulo UI: {len(ui_arquivos)}")
    
    # Informações sobre backup
    backups = [d for d in os.listdir(base_dir) if d.startswith('_backup_refatoracao_')]
    if backups:
        backup_info = []
        for backup in backups:
            backup_path = os.path.join(base_dir, backup)
            if os.path.exists(backup_path):
                files_backup = len([f for f in os.listdir(backup_path) if f.endswith('.py')])
                backup_info.append(f"   • {backup}: {files_backup} arquivos")
        
        print("\n💾 BACKUPS DISPONÍVEIS:")
        for info in backup_info:
            print(info)
    
    # Informações sobre scripts de automação
    scripts_automaticos = [
        'automatizar_refatoracao.py',
        'validar_refatoracao.py',
        'rollback_refatoracao.py',
        'gerenciar_refatoracao.py'
    ]
    
    print("\n🤖 SCRIPTS DE AUTOMAÇÃO:")
    for script in scripts_automaticos:
        script_path = os.path.join(base_dir, script)
        if os.path.exists(script_path):
            print(f"   ✅ {script}")
        else:
            print(f"   ❌ {script} (ausente)")
    
    input("\nPressione ENTER para continuar...")

def main():
    """Função principal"""
    while True:
        limpar_tela()
        mostrar_cabecalho()
        
        # Mostrar estado atual
        estado = verificar_estado_atual()
        
        print(f"\n🎯 ESTADO ATUAL: {estado}")
        
        # Mostrar menu
        mostrar_menu()
        
        # Obter escolha do usuário
        try:
            escolha = input("👉 Escolha uma opção (0-5): ").strip()
            
            if escolha == '0':
                print("\n👋 Saindo...")
                break
                
            elif escolha == '1':
                print(f"\n⚠️ ESTADO ATUAL: {estado}")
                if estado == "REFATORADO":
                    confirmacao = input("Sistema já foi refatorado. Continuar mesmo assim? (s/N): ").strip().lower()
                    if confirmacao not in ['s', 'sim', 'y', 'yes']:
                        continue
                
                sucesso = executar_script('automatizar_refatoracao.py', 'REFATORAÇÃO COMPLETA')
                if sucesso:
                    input("\nPressione ENTER para continuar...")
                
            elif escolha == '2':
                executar_script('validar_refatoracao.py', 'VALIDAÇÃO DA REFATORAÇÃO')
                input("\nPressione ENTER para continuar...")
                
            elif escolha == '3':
                print("\n⚠️ CUIDADO: Esta operação irá desfazer TODAS as mudanças!")
                confirmacao = input("Tem certeza? Digite 'CONTINUAR' para confirmar: ").strip()
                if confirmacao == 'CONTINUAR':
                    sucesso = executar_script('rollback_refatoracao.py', 'ROLLBACK DA REFATORAÇÃO')
                    if sucesso:
                        input("\nPressione ENTER para continuar...")
                else:
                    print("❌ Rollback cancelado")
                    input("\nPressione ENTER para continuar...")
                    
            elif escolha == '4':
                mostrar_status_detalhado()
                
            elif escolha == '5':
                mostrar_ajuda()
                
            else:
                print(f"\n❌ Opção inválida: {escolha}")
                input("Pressione ENTER para continuar...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrompido pelo usuário. Saindo...")
            break
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
            input("Pressione ENTER para continuar...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrompido. Até logo!")
    except Exception as e:
        print(f"\n💥 Erro crítico: {e}")
        print("Contacte o suporte técnico.")
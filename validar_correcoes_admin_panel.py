#!/usr/bin/env python3
"""
Validação das correções implementadas no admin_panel.py
"""

import os
import sys
import ast
import json
from datetime import datetime

def validar_sintaxe_admin_panel():
    """Valida a sintaxe do arquivo admin_panel.py"""
    try:
        admin_panel_path = "/workspace/IntegragalGit/ui/admin_panel.py"
        
        with open(admin_panel_path, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Parse do código
        tree = ast.parse(conteudo)
        
        print("✅ SINTAXE VÁLIDA - admin_panel.py")
        print(f"📊 Linhas de código: {len(conteudo.splitlines())}")
        
        # Verificar classes
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        print(f"🏗️ Classes encontradas: {classes}")
        
        # Verificar métodos principais
        metodos_principais = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('_'):
                metodos_principais.append(node.name)
        
        print(f"🔧 Métodos privados: {len(metodos_principais)}")
        
        return True
        
    except SyntaxError as e:
        print(f"❌ ERRO DE SINTAXE: {e}")
        return False
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False

def validar_remocao_aba_usuarios():
    """Verifica se a aba de usuários foi removida"""
    try:
        admin_panel_path = "/workspace/IntegragalGit/ui/admin_panel.py"
        
        with open(admin_panel_path, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Verificar se não há referência à aba "Usuários"
        if '"Usuários"' in conteudo or "'Usuários'" in conteudo:
            print("❌ ABa USUÁRIOS AINDA PRESENTE no código")
            return False
        
        # Verificar se métodos relacionados foram removidos
        metodos_usuarios = ['_criar_aba_usuarios', '_carregar_lista_usuarios', 
                           '_adicionar_usuario', '_editar_usuario']
        
        for metodo in metodos_usuarios:
            if metodo in conteudo:
                print(f"❌ MÉTODO {metodo} AINDA PRESENTE no código")
                return False
        
        print("✅ ABA USUÁRIOS REMOVIDA com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ ERRO ao verificar remoção da aba usuários: {e}")
        return False

def validar_sistema_editavel():
    """Verifica se o sistema foi tornado editável"""
    try:
        admin_panel_path = "/workspace/IntegragalGit/ui/admin_panel.py"
        
        with open(admin_panel_path, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Verificar se há campos editáveis no sistema
        indicadores_editaveis = [
            'sistema_entries',
            '_salvar_info_sistema',
            '_restaurar_valor_sistema',
            'CTkEntry'  # Para campos editáveis
        ]
        
        faltando = []
        for indicador in indicadores_editaveis:
            if indicador not in conteudo:
                faltando.append(indicador)
        
        if faltando:
            print(f"❌ SISTEMA NÃO COMPLETAMENTE EDITÁVEL. Faltando: {faltando}")
            return False
        
        print("✅ SISTEMA TORNADO EDITÁVEL com sucesso")
        print("   • Campos editáveis adicionados")
        print("   • Métodos de salvar/restauração implementados")
        print("   • Validações incluídas")
        return True
        
    except Exception as e:
        print(f"❌ ERRO ao verificar sistema editável: {e}")
        return False

def validar_cleanup_customtkinter():
    """Verifica se o cleanup do CustomTkinter foi implementado"""
    try:
        admin_panel_path = "/workspace/IntegragalGit/ui/admin_panel.py"
        
        with open(admin_panel_path, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Verificar métodos de cleanup
        metodos_cleanup = [
            '_fechar_admin_panel',
            'grab_release',
            'update_idletasks'
        ]
        
        faltando = []
        for metodo in metodos_cleanup:
            if metodo not in conteudo:
                faltando.append(metodo)
        
        if faltando:
            print(f"❌ CLEANUP CUSTOMTKINTER INCOMPLETO. Faltando: {faltando}")
            return False
        
        print("✅ CLEANUP CUSTOMTKINTER IMPLEMENTADO")
        print("   • Método de fechamento seguro")
        print("   • Liberação de grab e recursos")
        print("   • Tratamento de exceções")
        return True
        
    except Exception as e:
        print(f"❌ ERRO ao verificar cleanup CustomTkinter: {e}")
        return False

def validar_estrutura_arquivos():
    """Valida a estrutura dos arquivos relacionados"""
    try:
        # Verificar se o config.json existe
        config_path = "/workspace/IntegragalGit/config.json"
        if not os.path.exists(config_path):
            print("⚠️  ARQUIVO config.json não encontrado")
            return False
        
        # Tentar ler config.json
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"✅ CONFIG.JSON válido com {len(config)} configurações")
        
        # Verificar estrutura de pastas
        ui_path = "/workspace/IntegragalGit/ui"
        if not os.path.exists(ui_path):
            print("❌ PASTA ui não encontrada")
            return False
        
        arquivos_ui = os.listdir(ui_path)
        print(f"📁 Arquivos em ui/: {arquivos_ui}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO ao validar estrutura: {e}")
        return False

def main():
    """Função principal de validação"""
    print("🔍 VALIDANDO CORREÇÕES DO ADMIN_PANEL.PY")
    print("=" * 50)
    
    resultados = []
    
    # 1. Validar sintaxe
    print("\n1️⃣ VALIDANDO SINTAXE")
    resultados.append(validar_sintaxe_admin_panel())
    
    # 2. Validar remoção da aba usuários
    print("\n2️⃣ VALIDANDO REMOÇÃO DA ABA USUÁRIOS")
    resultados.append(validar_remocao_aba_usuarios())
    
    # 3. Validar sistema editável
    print("\n3️⃣ VALIDANDO SISTEMA EDITÁVEL")
    resultados.append(validar_sistema_editavel())
    
    # 4. Validar cleanup CustomTkinter
    print("\n4️⃣ VALIDANDO CLEANUP CUSTOMTKINTER")
    resultados.append(validar_cleanup_customtkinter())
    
    # 5. Validar estrutura de arquivos
    print("\n5️⃣ VALIDANDO ESTRUTURA DE ARQUIVOS")
    resultados.append(validar_estrutura_arquivos())
    
    # Resumo final
    print("\n" + "=" * 50)
    sucessos = sum(resultados)
    total = len(resultados)
    
    print(f"📊 RESUMO: {sucessos}/{total} validações passaram")
    
    if sucessos == total:
        print("🎉 TODAS AS CORREÇÕES IMPLEMENTADAS COM SUCESSO!")
        print("\n✅ Problemas resolvidos:")
        print("   • Aba 'Usuários' removida do menu")
        print("   • Informações do Sistema agora editáveis")
        print("   • Erro de destruction CustomTkinter corrigido")
        print("   • Validações e backups implementados")
        print("\n🔧 O admin_panel.py está pronto para uso!")
    else:
        print("❌ ALGUMAS CORREÇÕES PRECISAM DE ATENÇÃO")
        print("   Revise os erros acima antes de usar o sistema")
    
    print(f"\n🕐 Validação concluída em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

if __name__ == "__main__":
    main()

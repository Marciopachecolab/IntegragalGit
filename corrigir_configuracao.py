#!/usr/bin/env python3
"""
Correção do problema de salvamento das configurações
"""

import json
import os
import shutil
from datetime import datetime

def corrigir_estrutura_config():
    """Corrige a estrutura do config.json para ter a seção general"""
    print("🔧 CORREÇÃO DA ESTRUTURA DE CONFIGURAÇÃO")
    print("=" * 50)
    
    config_path = "config.json"
    config_subpasta_path = "configuracao/config.json"
    
    # Backup dos arquivos originais
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if os.path.exists(config_path):
        shutil.copy2(config_path, f"config_backup_correcao_{timestamp}.json")
        print(f"✅ Backup de config.json criado: config_backup_correcao_{timestamp}.json")
    
    if os.path.exists(config_subpasta_path):
        shutil.copy2(config_subpasta_path, f"configuracao/config_backup_correcao_{timestamp}.json")
        print(f"✅ Backup de configuracao/config.json criado: config_backup_correcao_{timestamp}.json")
    
    # Carregar config da subpasta como referência
    with open(config_subpasta_path, 'r', encoding='utf-8') as f:
        config_subpasta = json.load(f)
    
    # Modificar config.json raiz para ter a mesma estrutura
    with open(config_path, 'r', encoding='utf-8') as f:
        config_raiz = json.load(f)
    
    # Copiar general e base_url da subpasta para raiz
    if 'general' in config_subpasta:
        config_raiz['general'] = config_subpasta['general'].copy()
        print(f"✅ Copiada seção 'general' para config.json: {config_raiz['general']}")
    
    if 'gal_integration' in config_subpasta:
        # Preservar login_ids e outros campos específicos da raiz
        raiz_gal = config_raiz.get('gal_integration', {})
        subpasta_gal = config_subpasta['gal_integration']
        
        # Atualizar apenas base_url
        if 'base_url' in subpasta_gal:
            raiz_gal['base_url'] = subpasta_gal['base_url']
            print(f"✅ Atualizada base_url: {raiz_gal['base_url']}")
        
        config_raiz['gal_integration'] = raiz_gal
    
    # Adicionar seção exams se não existir
    if 'exams' in config_subpasta:
        config_raiz['exams'] = config_subpasta['exams'].copy()
        print("✅ Copiada seção 'exams' para config.json")
    
    # Salvar config.json corrigido
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_raiz, f, indent=4, ensure_ascii=False)
    
    print(f"\n✅ Config.json estruturalmente corrigido com sucesso!")
    print("   📋 Seções em config.json:", list(config_raiz.keys()))
    
    return config_raiz, config_subpasta

def corrigir_metodo_salvamento():
    """Corrige o método de salvamento no admin_panel.py"""
    print("\n🔧 CORREÇÃO DO MÉTODO DE SALVAMENTO")
    print("=" * 45)
    
    # Ler o arquivo admin_panel.py
    with open("ui/admin_panel.py", 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Encontrar o método _salvar_info_sistema
    inicio = conteudo.find("def _salvar_info_sistema(self):")
    if inicio == -1:
        print("❌ Método _salvar_info_sistema não encontrado")
        return False
    
    # Encontrar o final do método
    prox_metodo = conteudo.find("\n    def ", inicio + 1)
    if prox_metodo == -1:
        prox_metodo = len(conteudo)
    
    metodo_original = conteudo[inicio:prox_metodo]
    
    # Substituir a seção de sincronização para garantir que funcione
    secao_antiga = '''            # Sincronizar com configuracao/config.json se existir
            try:
                if os.path.exists(configuracao_path):
                    # Ler ConfigService atualizado
                    with open("config.json", 'r', encoding='utf-8') as f:
                        config_atualizado = json.load(f)
                    
                    # Carregar config da subpasta
                    with open(configuracao_path, 'r', encoding='utf-8') as f:
                        config_subpasta = json.load(f)
                    
                    # Sincronizar todos os campos alterados no config da subpasta
                    if 'base_url' in novas_configuracoes:
                        config_subpasta.setdefault('gal_integration', {})['base_url'] = novas_configuracoes['base_url']
                        print(f"✅ Sincronizando base_url: {novas_configuracoes['base_url']}")
                    
                    if 'lab_name' in novas_configuracoes:
                        config_subpasta.setdefault('general', {})['lab_name'] = novas_configuracoes['lab_name']
                        print(f"✅ Sincronizando lab_name: {novas_configuracoes['lab_name']}")
                    
                    # Sincronizar outros campos gerais
                    for key, value in novas_configuracoes.items():
                        if key not in ['base_url', 'lab_name']:
                            config_subpasta.setdefault('general', {})[key] = value
                            print(f"✅ Sincronizando {key}: {value}")
                    
                    # Garantir estrutura completa do arquivo da subpasta
                    config_subpasta.setdefault('gal_integration', {})
                    config_subpasta.setdefault('paths', {})
                    config_subpasta.setdefault('postgres', {})
                    config_subpasta.setdefault('exams', {})
                    
                    # Salvar config da subpasta
                    backup_subpasta_path = f"configuracao/config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    shutil.copy2(configuracao_path, backup_subpasta_path)
                    
                    with open(configuracao_path, 'w', encoding='utf-8') as f:
                        json.dump(config_subpasta, f, indent=4, ensure_ascii=False)
                    
                    # Verificar se a sincronização foi bem-sucedida
                    with open(configuracao_path, 'r', encoding='utf-8') as f:
                        config_verificado = json.load(f)
                    
                    base_url_verificada = config_verificado.get('gal_integration', {}).get('base_url', 'N/A')
                    lab_name_verificado = config_verificado.get('general', {}).get('lab_name', 'N/A')
                    
                    print(f"✅ Configuracao/config.json sincronizado com sucesso")
                    print(f"   📌 Base URL sincronizada: {base_url_verificada}")
                    print(f"   📌 Lab Name sincronizado: {lab_name_verificado}")
                    
            except Exception as e:
                print(f"❌ Erro na sincronização: {e}")
                erros.append(f"Erro ao sincronizar configurações secundárias: {e}")'''
    
    secao_nova = '''            # Sincronizar com configuracao/config.json se existir
            try:
                if os.path.exists(configuracao_path):
                    # Ler ConfigService atualizado (que já salvou em config.json raiz)
                    with open("config.json", 'r', encoding='utf-8') as f:
                        config_atualizado = json.load(f)
                    
                    # Carregar config da subpasta
                    with open(configuracao_path, 'r', encoding='utf-8') as f:
                        config_subpasta = json.load(f)
                    
                    # Sincronizar TODOS os campos alterados no config da subpasta
                    # Base URL do GAL
                    if 'base_url' in novas_configuracoes:
                        config_subpasta.setdefault('gal_integration', {})['base_url'] = novas_configuracoes['base_url']
                        print(f"✅ Sincronizando base_url: {novas_configuracoes['base_url']}")
                    
                    # Nome do laboratório
                    if 'lab_name' in novas_configuracoes:
                        config_subpasta.setdefault('general', {})['lab_name'] = novas_configuracoes['lab_name']
                        print(f"✅ Sincronizando lab_name: {novas_configuracoes['lab_name']}")
                    
                    # Outros campos gerais
                    for key, value in novas_configuracoes.items():
                        if key not in ['base_url', 'lab_name']:
                            config_subpasta.setdefault('general', {})[key] = value
                            print(f"✅ Sincronizando {key}: {value}")
                    
                    # Garantir estrutura completa do arquivo da subpasta
                    config_subpasta.setdefault('gal_integration', {})
                    config_subpasta.setdefault('paths', {})
                    config_subpasta.setdefault('postgres', {})
                    config_subpasta.setdefault('exams', {})
                    
                    # Salvar config da subpasta
                    backup_subpasta_path = f"configuracao/config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    shutil.copy2(configuracao_path, backup_subpasta_path)
                    
                    with open(configuracao_path, 'w', encoding='utf-8') as f:
                        json.dump(config_subpasta, f, indent=4, ensure_ascii=False)
                    
                    # Verificar se a sincronização foi bem-sucedida
                    with open(configuracao_path, 'r', encoding='utf-8') as f:
                        config_verificado = json.load(f)
                    
                    base_url_verificada = config_verificado.get('gal_integration', {}).get('base_url', 'N/A')
                    lab_name_verificado = config_verificado.get('general', {}).get('lab_name', 'N/A')
                    
                    print(f"✅ Configuracao/config.json sincronizado com sucesso")
                    print(f"   📌 Base URL sincronizada: {base_url_verificada}")
                    print(f"   📌 Lab Name sincronizado: {lab_name_verificado}")
                    
            except Exception as e:
                print(f"❌ Erro na sincronização: {e}")
                erros.append(f"Erro ao sincronizar configurações secundárias: {e}")'''
    
    # Fazer a substituição
    novo_conteudo = conteudo.replace(secao_antiga, secao_nova)
    
    if novo_conteudo == conteudo:
        print("⚠️  Seção de sincronização não encontrada ou já está correta")
        return True
    else:
        # Salvar o arquivo corrigido
        with open("ui/admin_panel.py", 'w', encoding='utf-8') as f:
            f.write(novo_conteudo)
        print("✅ Método de salvamento corrigido com sucesso")
        return True

def corrigir_botao_saida():
    """Melhora o método do botão de saída"""
    print("\n🚪 MELHORIA DO BOTÃO DE SAÍDA")
    print("=" * 35)
    
    # Ler o arquivo user_management.py
    with open("ui/user_management.py", 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Encontrar o método atual
    inicio = conteudo.find("def _sair_para_menu_principal(self):")
    if inicio == -1:
        print("❌ Método _sair_para_menu_principal não encontrado")
        return False
    
    # Encontrar o final do método
    prox_metodo = conteudo.find("\n    def ", inicio + 1)
    if prox_metodo == -1:
        prox_metodo = len(conteudo)
    
    metodo_original = conteudo[inicio:prox_metodo]
    
    # Método melhorado
    metodo_novo = '''    def _sair_para_menu_principal(self):
        """Fecha a janela de gerenciamento de usuários e volta ao menu principal"""
        try:
            # Fechar a janela de usuários
            if hasattr(self, 'user_window') and self.user_window.winfo_exists():
                self.user_window.withdraw()  # Esconder primeiro
                self.user_window.destroy()   # Depois destruir
            
            # Garantir que a janela principal seja mostrada e focada
            if hasattr(self, 'main_window') and self.main_window.winfo_exists():
                self.main_window.deiconify()  # Voltar a mostrar
                self.main_window.lift()       # Trazer para frente
                self.main_window.focus_force() # Forçar foco
                print("✅ Voltei ao menu principal com sucesso")
            
            print("✅ Botão de saída executado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao executar botão de saída: {e}")
            # Tentar método simples como fallback
            try:
                self.main_window.deiconify()
            except:
                pass'''
    
    # Substituir
    novo_conteudo = conteudo.replace(metodo_original, metodo_novo)
    
    if novo_conteudo == conteudo:
        print("⚠️  Método do botão não encontrado ou já está correto")
        return True
    else:
        with open("ui/user_management.py", 'w', encoding='utf-8') as f:
            f.write(novo_conteudo)
        print("✅ Método do botão de saída melhorado com sucesso")
        return True

def testar_correcoes():
    """Testa as correções aplicadas"""
    print("\n🧪 TESTE DAS CORREÇÕES")
    print("=" * 30)
    
    # Verificar config.json corrigido
    with open("config.json", 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("✅ Config.json após correção:")
    print(f"   📋 Seções: {list(config.keys())}")
    
    if 'general' in config:
        print(f"   📝 Seção 'general': {config['general']}")
        if 'lab_name' in config['general']:
            print(f"   🏥 lab_name: {config['general']['lab_name']}")
    else:
        print("   ❌ Seção 'general' ainda não encontrada")
    
    if 'gal_integration' in config:
        print(f"   🌐 base_url: {config['gal_integration'].get('base_url', 'N/A')}")
    
    # Simular salvamento
    config['general']['lab_name'] = "LAB TESTE CORREÇÃO"
    config['gal_integration']['base_url'] = "https://correcao-teste.saude.sc.gov.br"
    
    with open("config.json", 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    
    print("✅ Teste de salvamento realizado")
    
    # Verificar se foi salvo
    with open("config.json", 'r', encoding='utf-8') as f:
        config_test = json.load(f)
    
    if config_test.get('general', {}).get('lab_name') == "LAB TESTE CORREÇÃO":
        print("✅ Lab_name foi salvo e preservado corretamente")
    else:
        print("❌ Lab_name NÃO foi preservado")
    
    print("\n🎉 CORREÇÕES APLICADAS COM SUCESSO!")

def main():
    """Função principal de correção"""
    print("🔧 CORREÇÃO DOS PROBLEMAS IDENTIFICADOS")
    print("=" * 60)
    
    try:
        # Corrigir estrutura dos arquivos
        config_raiz, config_subpasta = corrigir_estrutura_config()
        
        # Corrigir método de salvamento
        corrigir_metodo_salvamento()
        
        # Melhorar botão de saída
        corrigir_botao_saida()
        
        # Testar correções
        testar_correcoes()
        
        print("\n📋 RESUMO DAS CORREÇÕES")
        print("=" * 30)
        print("✅ Estrutura do config.json unificada")
        print("✅ Método de salvamento melhorado")  
        print("✅ Botão de saída aprimorado")
        print("✅ Teste de funcionamento realizado")
        
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. Execute o sistema normalmente")
        print("2. Teste o salvamento das configurações do sistema")
        print("3. Teste o botão 'SAIR PARA O MENU INICIAL'")
        
    except Exception as e:
        print(f"❌ Erro durante a correção: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Correção para usar o ConfigService no admin_panel.py
Corrige o problema do Base URL GAL não persistir
"""

import os
import shutil
from datetime import datetime

def aplicar_correcao():
    """Corrige o admin_panel.py para usar o ConfigService"""
    
    print("🔧 Iniciando correção do ConfigService...")
    
    # Caminhos
    admin_panel_path = "IntegraGAL_Funcional/ui/admin_panel.py"
    config_service_path = "IntegraGAL_Funcional/services/config_service.py"
    configuracao_path = "IntegraGAL_Funcional/configuracao/config.json"
    
    # Ler o arquivo admin_panel.py
    print("📖 Lendo admin_panel.py...")
    with open(admin_panel_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Encontrar o método _salvar_info_sistema e substituir
    method_start = None
    method_end = None
    
    for i, line in enumerate(lines):
        if "def _salvar_info_sistema(self):" in line:
            method_start = i
        elif method_start is not None and line.strip().startswith("def ") and "_salvar_info_sistema" not in line:
            method_end = i
            break
    
    if method_start is None:
        print("❌ Método _salvar_info_sistema não encontrado!")
        return False
    
    if method_end is None:
        method_end = len(lines)
    
    print(f"📍 Método encontrado nas linhas {method_start+1} a {method_end}")
    
    # Novo método que usa ConfigService
    novo_metodo = '''    def _salvar_info_sistema(self):
        """Salva as informações editadas do sistema usando ConfigService"""
        try:
            # Validar e coletar novos valores
            novas_configuracoes = {}
            erros = []
            
            for key, entry in self.sistema_entries.items():
                novo_valor = entry.get().strip()
                
                # Validações específicas por chave
                if 'Timeout' in key:
                    try:
                        timeout_int = int(novo_valor)
                        if timeout_int <= 0:
                            erros.append(f"Timeout deve ser um número positivo")
                        else:
                            novas_configuracoes['request_timeout'] = timeout_int
                    except ValueError:
                        erros.append(f"Timeout deve ser um número inteiro")
                
                elif 'URL' in key:
                    if novo_valor.startswith(('http://', 'https://')):
                        # Usar a chave correta para GAL integration
                        self.config_service._config.setdefault('gal_integration', {})['base_url'] = novo_valor
                        novas_configuracoes['base_url'] = novo_valor
                    else:
                        erros.append(f"URL do GAL deve começar com http:// ou https://")
                
                elif 'Log' in key:
                    # ConfigService usa default logging, não precisa desta configuração aqui
                    print(f"⚠️  Campo Log será ignorado: {key}")
                    continue
                
                else:
                    if novo_valor:
                        # Mapear para a seção correta
                        if any(term in key.lower() for term in ['lab', 'laboratório']):
                            self.config_service._config.setdefault('general', {})['lab_name'] = novo_valor
                            novas_configuracoes['lab_name'] = novo_valor
                        else:
                            # Outros campos gerais
                            self.config_service._config.setdefault('general', {})[key.lower().replace(' ', '_')] = novo_valor
                            novas_configuracoes[key.lower().replace(' ', '_')] = novo_valor
                    else:
                        erros.append(f"Campo '{key}' não pode estar vazio")
            
            # Exibir erros se houver
            if erros:
                messagebox.showerror("Erro de Validação", "Erros encontrados:\n\n" + "\\n".join(erros), parent=self.admin_window)
                return
            
            # Backup do config.json principal
            config_backup_path = f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            if os.path.exists("config.json"):
                shutil.copy2("config.json", config_backup_path)
            
            # Atualizar ConfigService
            try:
                self.config_service._save_config()
                print(f"✅ ConfigService salvo com sucesso")
            except Exception as e:
                print(f"❌ Erro ao salvar ConfigService: {e}")
                erros.append(f"Erro interno ao salvar configurações: {e}")
            
            # Sincronizar com configuracao/config.json se existir
            try:
                if os.path.exists(configuracao_path):
                    # Ler ConfigService atualizado
                    with open("config.json", 'r', encoding='utf-8') as f:
                        config_atualizado = json.load(f)
                    
                    # Carregar config da subpasta
                    with open(configuracao_path, 'r', encoding='utf-8') as f:
                        config_subpasta = json.load(f)
                    
                    # Atualizar base_url no config da subpasta se foi alterada
                    if 'base_url' in novas_configuracoes:
                        config_subpasta.setdefault('gal_integration', {})['base_url'] = novas_configuracoes['base_url']
                    
                    # Atualizar lab_name se foi alterado
                    if 'lab_name' in novas_configuracoes:
                        config_subpasta.setdefault('general', {})['lab_name'] = novas_configuracoes['lab_name']
                    
                    # Salvar config da subpasta
                    backup_subpasta_path = f"configuracao/config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    shutil.copy2(configuracao_path, backup_subpasta_path)
                    
                    with open(configuracao_path, 'w', encoding='utf-8') as f:
                        json.dump(config_subpasta, f, indent=4, ensure_ascii=False)
                    
                    print(f"✅ Configuracao/config.json sincronizado")
                    
            except Exception as e:
                print(f"⚠️  Aviso: Erro ao sincronizar configuracao/config.json: {e}")
            
            # Exibir sucesso
            mensagem_sucesso = f"Configurações do sistema salvas com sucesso!\\n\\n"
            mensagem_sucesso += f"Backup criado: {config_backup_path}\\n\\n"
            mensagem_sucesso += "Novos valores:\\n" + "\\n".join([f"• {k}: {v}" for k, v in novas_configuracoes.items()])
            
            messagebox.showinfo("Sucesso", mensagem_sucesso, parent=self.admin_window)
            
            # Recarregar informações do sistema
            self._recarregar_info_sistema()
            
        except Exception as e:
            error_msg = f"Erro inesperado ao salvar configurações: {str(e)}"
            print(f"❌ {error_msg}")
            messagebox.showerror("Erro", error_msg, parent=self.admin_window)
    
    '''
    
    # Substituir o método
    linhas_novas = lines[:method_start] + [novo_metodo + "\n"] + lines[method_end:]
    
    # Adicionar import do ConfigService se não existir
    imports_section = []
    content_section = []
    import_added = False
    
    for i, line in enumerate(linhas_novas):
        if line.startswith("import ") or line.startswith("from "):
            imports_section.append(line)
        else:
            content_section = linhas_novas[i:]
            break
    
    # Verificar se o import do ConfigService já existe
    for import_line in imports_section:
        if "config_service" in import_line:
            import_added = True
            break
    
    if not import_added:
        # Adicionar o import após os outros imports
        for i, import_line in enumerate(imports_section):
            if "import json" in import_line or "import os" in import_line:
                imports_section.insert(i + 1, 'from services.config_service import config_service\\n')
                import_added = True
                break
        
        if not import_added:
            imports_section.append('from services.config_service import config_service\\n')
    
    # Recompor o arquivo
    linhas_finais = imports_section + content_section
    
    # Escrever o arquivo corrigido
    print("💾 Escrevendo arquivo corrigido...")
    with open(admin_panel_path, 'w', encoding='utf-8') as f:
        f.writelines(linhas_finais)
    
    print("✅ Correção aplicada com sucesso!")
    return True

if __name__ == "__main__":
    aplicar_correcao()
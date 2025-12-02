#!/usr/bin/env python3
"""
Corrige os imports do admin_panel.py
"""

def corrigir_imports():
    """Corrige os imports danificados"""
    
    admin_panel_path = "IntegraGAL_Funcional/ui/admin_panel.py"
    
    print("📖 Lendo arquivo...")
    with open(admin_panel_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Corrigir o problema do import na linha 1
    if content.startswith("from services.config_service import config_service\\n\"\"\""):
        content = content.replace(
            "from services.config_service import config_service\\n\"\"\"",
            "\"\"\""
        )
    
    print("💾 Escrevendo arquivo corrigido...")
    with open(admin_panel_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Adicionar o import correto
    with open(admin_panel_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Encontrar onde estão os outros imports e adicionar o config_service
    insert_index = -1
    for i, line in enumerate(lines):
        if line.strip().startswith("from utils.logger import registrar_log"):
            insert_index = i + 1
            break
    
    if insert_index != -1:
        lines.insert(insert_index, "from services.config_service import config_service\\n")
    
    with open(admin_panel_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ Imports corrigidos!")

if __name__ == "__main__":
    corrigir_imports()
#!/usr/bin/env python3
"""
Criar o package final com todas as correções aplicadas
"""

import zipfile
from datetime import datetime

# Caminhos
DESTINO_TEMP = "/workspace/IntegraGAL_FinalCorrigido"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
PACKAGE_FINAL = f"/workspace/IntegraGAL_ProblemasResolvidos_{TIMESTAMP}.zip"

def criar_package_final():
    """Cria o package final com todas as correções"""
    
    with zipfile.ZipFile(PACKAGE_FINAL, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(DESTINO_TEMP):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, DESTINO_TEMP)
                zipf.write(file_path, arc_path)
    
    # Calcular tamanho
    import os
    tamanho_kb = os.path.getsize(PACKAGE_FINAL) / 1024
    total_arquivos = sum(len(files) for r, d, files in os.walk(DESTINO_TEMP))
    
    print(f"\n🎁 Package final com problemas resolvidos:")
    print(f"📁 Arquivo: {PACKAGE_FINAL}")
    print(f"📊 Tamanho: {tamanho_kb:.1f} KB")
    print(f"📄 Total de arquivos: {total_arquivos}")
    
    return PACKAGE_FINAL

def main():
    print("📦 Criando package final com todos os problemas resolvidos...")
    
    package = criar_package_final()
    
    print("\n" + "=" * 60)
    print("🎉 PACOTE FINAL CRIADO!")
    print(f"\n📦 {package}")
    print(f"\n✅ Correções implementadas:")
    print("  1. Base URL GAL: Salva corretamente (chave 🌐 Base)")
    print("  2. Erro senha_hash: Removida renomeação incorreta")
    print("  3. Fechamento: Protocolo melhorado")
    print("  4. Estrutura: Subpastas organizadas")
    print("  5. Imports: Todos corrigidos")
    print("  6. Arquivo .bat: ASCII compatível")
    
    return package

if __name__ == "__main__":
    main()
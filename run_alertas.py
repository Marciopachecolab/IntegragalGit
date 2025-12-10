"""
Script para testar Sistema de Alertas

⚠️ DEPRECATED: Use 'python main.py alertas'
"""

import customtkinter as ctk
import warnings

warnings.warn(
    "run_alertas.py está deprecated. Use 'python main.py alertas'.",
    DeprecationWarning
)
from interface.sistema_alertas import GerenciadorAlertas, CentroNotificacoes, gerar_alertas_exemplo


def main():
    """Testa sistema de alertas standalone"""
    print("\n" + "="*60)
    print("TESTANDO SISTEMA DE ALERTAS - INTEGAGAL")
    print("="*60)
    
    print("\n1. Criando gerenciador de alertas...")
    gerenciador = GerenciadorAlertas()
    print("   ✅ Gerenciador criado")
    
    print("\n2. Gerando alertas de exemplo...")
    gerar_alertas_exemplo(gerenciador)
    stats = gerenciador.get_estatisticas()
    print(f"   ✅ {stats['total']} alertas gerados")
    print(f"      - Críticos: {stats['criticos']}")
    print(f"      - Altos: {stats['altos']}")
    print(f"      - Médios: {stats['medios']}")
    print(f"      - Baixos: {stats['baixos']}")
    print(f"      - Não lidos: {stats['nao_lidos']}")
    print(f"      - Não resolvidos: {stats['nao_resolvidos']}")
    
    print("\n3. Abrindo Centro de Notificações...")
    app = ctk.CTk()
    app.withdraw()
    
    centro = CentroNotificacoes(app, gerenciador)
    
    print("   ✅ Centro de Notificações aberto")
    print("\n" + "="*60)
    print("Feche a janela para encerrar o teste.")
    print("="*60 + "\n")
    
    app.mainloop()
    
    print("\n✅ Teste concluído!")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()

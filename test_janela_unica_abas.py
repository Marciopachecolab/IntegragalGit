"""
Teste da nova JanelaAnaliseCompleta com sistema de abas.
Valida que não há mais travamentos após "Salvar e Voltar".
"""

import sys
import pandas as pd
import customtkinter as ctk
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from ui.janela_analise_completa import JanelaAnaliseCompleta

print("=" * 70)
print("🧪 TESTE: Janela Única com Abas (Análise + Mapa)")
print("=" * 70)
print()

# Criar dados de teste
data = {
    "Selecionado": [True, True, False, True],
    "Amostra": ["AMOSTRA-001", "AMOSTRA-002", "CN", "AMOSTRA-003"],
    "Código": ["001", "002", "CN-01", "003"],
    "Poço": ["A01+A02", "B01+B02", "C01", "D01+D02"],
    "Resultado_SC2": ["Det", "ND", "ND", "Det"],
    "CT_SC2": [25.5, 0.0, 0.0, 28.3],
    "Resultado_HMPV": ["ND", "ND", "ND", "ND"],
    "CT_HMPV": [0.0, 0.0, 0.0, 0.0],
}

df_teste = pd.DataFrame(data)

print("📊 DataFrame de teste criado:")
print(df_teste)
print()

# Criar janela principal
root = ctk.CTk()
root.title("Teste - Sistema de Abas")
root.geometry("400x300")

# Label de status
status_label = ctk.CTkLabel(
    root,
    text="Status: Aguardando teste...",
    font=("Segoe UI", 14)
)
status_label.pack(pady=20)

# Variável para rastrear se teste passou
teste_passou = False

def abrir_janela_teste():
    """Abre a janela de análise completa."""
    global teste_passou
    
    try:
        status_label.configure(text="Status: Criando JanelaAnaliseCompleta...")
        root.update()
        
        janela = JanelaAnaliseCompleta(
            root,
            dataframe=df_teste,
            status_corrida="CONCLUÍDA",
            num_placa="TESTE-001",
            data_placa_formatada="10/12/2025",
            agravos=["SC2", "HMPV"],
            usuario_logado="Testador",
            exame="COVID-19 + HMPV",
            lote="LOTE-TESTE",
            arquivo_corrida="teste_corrida.xlsx",
            bloco_tamanho=2,
        )
        
        status_label.configure(text="Status: ✅ Janela criada com sucesso!")
        print("\n✅ TESTE 1 PASSOU: JanelaAnaliseCompleta criada sem erros")
        print()
        print("🔍 INSTRUÇÕES DE TESTE MANUAL:")
        print("  1. Clique em '🧬 Ir para Mapa' na aba Análise")
        print("  2. Navegue pelo mapa, edite algum resultado")
        print("  3. Clique em '💾 Salvar Alterações e Voltar'")
        print("  4. Verifique que:")
        print("     - A janela NÃO trava")
        print("     - Volta automaticamente para aba Análise")
        print("     - Alterações aparecem na tabela")
        print("     - Pode alternar entre abas livremente")
        print()
        print("❌ Se travar ou der erro 'invalid command name': FALHA")
        print("✅ Se tudo funcionar suavemente: SUCESSO")
        
        teste_passou = True
        
    except Exception as e:
        status_label.configure(text=f"Status: ❌ ERRO - {type(e).__name__}")
        print(f"\n❌ TESTE FALHOU: {e}")
        import traceback
        traceback.print_exc()

# Botão para iniciar teste
btn_teste = ctk.CTkButton(
    root,
    text="🚀 Iniciar Teste da Janela com Abas",
    command=abrir_janela_teste,
    font=("Segoe UI", 16, "bold"),
    height=60,
    fg_color="#3498db",
    hover_color="#2980b9"
)
btn_teste.pack(pady=20)

# Instruções
instrucoes = ctk.CTkLabel(
    root,
    text="Este teste valida:\n"
         "• Criação da janela única\n"
         "• Navegação entre abas\n"
         "• Sincronização de dados\n"
         "• Ausência de travamentos",
    font=("Segoe UI", 11),
    justify="left"
)
instrucoes.pack(pady=10)

print("🎯 Objetivo: Verificar que a solução com abas elimina travamentos")
print("📌 A janela de teste está aberta. Clique no botão para começar.")
print()

try:
    root.mainloop()
except KeyboardInterrupt:
    print("\n⚠️ Teste interrompido pelo usuário")

print()
print("=" * 70)
print("📊 RESULTADO DO TESTE AUTOMÁTICO:")
print("=" * 70)
if teste_passou:
    print("✅ Janela criada com sucesso (teste automático passou)")
    print("⚠️ Validação manual necessária para confirmar ausência de travamentos")
else:
    print("❌ Falha na criação da janela")
print("=" * 70)

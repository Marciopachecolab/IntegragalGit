"""
Teste focado para diagnosticar e resolver o problema de "invalid command name"
em TabelaComSelecaoSimulada e PlateWindow.

Este teste:
1. Reproduz o fluxo exato do sistema
2. Monitora callbacks do CustomTkinter
3. Testa diferentes soluções
4. Valida qual abordagem funciona
"""

import customtkinter as ctk
import pandas as pd
import sys
import time
from pathlib import Path

# Adicionar caminho do projeto
sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*80)
print("TESTE DE DIAGNÓSTICO: 'invalid command name' Error")
print("="*80 + "\n")

# =============================================================================
# ANÁLISE DO PROBLEMA
# =============================================================================

print("📋 ANÁLISE DO PROBLEMA:")
print("-" * 80)
print("""
CAUSA RAIZ IDENTIFICADA:
CustomTkinter agenda callbacks internos continuamente:
  - update() a cada 30ms
  - check_dpi_scaling() a cada 100ms
  - _click_animation() ao interagir com widgets

QUANDO O ERRO OCORRE:
1. TabelaComSelecaoSimulada abre com grab_set()
2. Usuário abre PlateWindow (grab é liberado temporariamente)
3. Usuário fecha PlateWindow rapidamente
4. TabelaComSelecaoSimulada restaura grab após 100ms
5. Se janela for fechada antes de 100ms, o callback tenta executar em widget destruído

PROBLEMA ESPECÍFICO:
O after(100, restaurar_grab_seguro) em _gerar_mapa_placa() agenda callback
que pode executar APÓS o destroy() se usuário fechar janela muito rápido.
""")
print("="*80 + "\n")

# =============================================================================
# SOLUÇÕES PROPOSTAS
# =============================================================================

print("💡 SOLUÇÕES PROPOSTAS:")
print("-" * 80)
print("""
SOLUÇÃO 1: Cancelar callback de restaurar_grab no _on_close()
  ✓ Cancela especificamente o after(100) de restaurar_grab
  ✓ Simples e direto
  ✗ Requer rastrear o ID do callback

SOLUÇÃO 2: Verificação mais robusta em restaurar_grab_seguro()
  ✓ Verifica se widget ainda existe antes de grab_set()
  ✗ Já implementado, mas erro persiste (callback já foi destruído)

SOLUÇÃO 3: Não usar after() para restaurar grab
  ✓ Restaurar grab IMEDIATAMENTE após abrir_placa_ctk()
  ✓ Remove a janela de vulnerabilidade de 100ms
  ✗ Pode causar conflito se PlateWindow não terminou __init__

SOLUÇÃO 4: PlateWindow notifica pai quando está pronta
  ✓ Callback explícito quando PlateWindow termina inicialização
  ✓ Mais robusto e previsível
  ✗ Mais complexo de implementar

SOLUÇÃO RECOMENDADA: Combinar Solução 1 + 3
  - Rastrear ID do callback de restaurar_grab
  - Cancelar no _on_close()
  - Reduzir delay de 100ms para 0ms (usar after_idle)
""")
print("="*80 + "\n")

# =============================================================================
# IMPLEMENTAÇÃO DA SOLUÇÃO
# =============================================================================

class TabelaTesteFix(ctk.CTkToplevel):
    """Versão corrigida de TabelaComSelecaoSimulada"""
    
    def __init__(self, root, df):
        super().__init__(root)
        self.title("TESTE - Tabela com Correção")
        self.geometry("600x400")
        
        self._parent = root
        self._restore_grab_callback_id = None  # SOLUÇÃO 1: Rastrear ID do callback
        
        # Criar interface
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        label = ctk.CTkLabel(frame, text=f"DataFrame: {len(df)} linhas", font=("Arial", 14, "bold"))
        label.pack(pady=10)
        
        btn_abrir = ctk.CTkButton(frame, text="🗺️ Abrir Janela Filha (Simula PlateWindow)", 
                                  command=self._abrir_janela_filha, width=300, height=50)
        btn_abrir.pack(pady=20)
        
        self.status_label = ctk.CTkLabel(frame, text="Status: Pronto", font=("Arial", 12))
        self.status_label.pack(pady=10)
        
        # Configurar como no sistema real
        self.transient(root)
        self.grab_set()
        
        self.protocol("WM_DELETE_WINDOW", self._on_close_corrigido)
        
        print("[TESTE] TabelaTesteFix criada com grab_set()")
    
    def _abrir_janela_filha(self):
        """Simula abertura de PlateWindow"""
        print("\n[TESTE] Abrindo janela filha...")
        self.status_label.configure(text="Status: Janela filha aberta")
        
        # SOLUÇÃO: Liberar grab
        try:
            self.grab_release()
            print("[TESTE] grab_release() executado")
        except Exception as e:
            print(f"[TESTE] Erro ao liberar grab: {e}")
        
        # Criar janela filha
        janela_filha = ctk.CTkToplevel(self)
        janela_filha.title("Janela Filha")
        janela_filha.geometry("400x300")
        janela_filha.transient(self)
        
        frame = ctk.CTkFrame(janela_filha)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame, text="Janela Filha\n(Simula PlateWindow)", 
                    font=("Arial", 14)).pack(pady=20)
        
        def fechar_filha():
            print("[TESTE] Fechando janela filha...")
            try:
                janela_filha.destroy()
                print("[TESTE] Janela filha destruída")
            except Exception as e:
                print(f"[TESTE] Erro ao destruir janela filha: {e}")
            
            # SOLUÇÃO 3: Restaurar grab IMEDIATAMENTE com after_idle (não after(100))
            def restaurar_grab_seguro():
                try:
                    if self.winfo_exists():
                        self.grab_set()
                        print("[TESTE] grab_set() restaurado com sucesso")
                except Exception as e:
                    print(f"[TESTE] Erro ao restaurar grab: {e}")
            
            # SOLUÇÃO 1: Rastrear ID do callback para cancelar depois se necessário
            self._restore_grab_callback_id = self.after_idle(restaurar_grab_seguro)
            print(f"[TESTE] grab_set() agendado com after_idle (ID: {self._restore_grab_callback_id})")
            
            self.status_label.configure(text="Status: Janela filha fechada - Testando responsividade")
        
        ctk.CTkButton(frame, text="✅ Fechar e Voltar", command=fechar_filha,
                     width=200, height=50).pack(pady=20)
        
        janela_filha.focus_force()
    
    def _on_close_corrigido(self):
        """Versão corrigida do _on_close que cancela callback pendente"""
        print("\n[TESTE] Fechando TabelaTesteFix...")
        
        # SOLUÇÃO 1: Cancelar callback de restaurar_grab se ainda pendente
        if self._restore_grab_callback_id is not None:
            try:
                self.after_cancel(self._restore_grab_callback_id)
                print(f"[TESTE] ✅ Callback de restaurar_grab cancelado (ID: {self._restore_grab_callback_id})")
                self._restore_grab_callback_id = None
            except Exception as e:
                print(f"[TESTE] Erro ao cancelar callback: {e}")
        
        # Liberar grab
        try:
            self.grab_release()
            print("[TESTE] grab_release() executado")
        except Exception as e:
            print(f"[TESTE] Erro ao liberar grab: {e}")
        
        # Ocultar janela
        try:
            self.withdraw()
            print("[TESTE] withdraw() executado")
        except Exception as e:
            print(f"[TESTE] Erro ao ocultar janela: {e}")
        
        # Destruir após delay
        def destruir_seguro():
            try:
                if self.winfo_exists():
                    self.destroy()
                    print("[TESTE] ✅ Janela destruída com sucesso")
            except Exception as e:
                print(f"[TESTE] Erro ao destruir: {e}")
        
        try:
            self.after(300, destruir_seguro)
            print("[TESTE] destroy() agendado para 300ms")
        except Exception as e:
            print(f"[TESTE] Erro ao agendar destroy: {e}")
            destruir_seguro()


# =============================================================================
# FUNÇÃO DE TESTE
# =============================================================================

def executar_teste():
    """Executa o teste com a solução implementada"""
    
    print("🚀 INICIANDO TESTE...")
    print("-" * 80)
    print("INSTRUÇÕES:")
    print("1. Clique em 'Iniciar Teste com Correção'")
    print("2. Clique em 'Abrir Janela Filha'")
    print("3. Clique em 'Fechar e Voltar'")
    print("4. FECHE A JANELA PRINCIPAL RAPIDAMENTE (< 100ms)")
    print("5. Observe se aparece 'invalid command name' no terminal")
    print("="*80 + "\n")
    
    root = ctk.CTk()
    root.title("Teste de Correção")
    root.geometry("500x350")
    
    df_teste = pd.DataFrame({
        'Coluna1': range(10),
        'Coluna2': ['Teste'] * 10
    })
    
    frame = ctk.CTkFrame(root)
    frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    ctk.CTkLabel(frame, text="Teste de Correção do Erro\n'invalid command name'",
                font=("Arial", 16, "bold")).pack(pady=20)
    
    def iniciar_teste():
        print("\n" + "="*80)
        print("TESTE INICIADO")
        print("="*80)
        janela = TabelaTesteFix(root, df_teste)
        janela.focus_force()
    
    ctk.CTkButton(frame, text="🧪 Iniciar Teste com Correção",
                 command=iniciar_teste, width=300, height=60).pack(pady=20)
    
    ctk.CTkLabel(frame, text="Feche esta janela para encerrar o teste",
                font=("Arial", 10)).pack(pady=10)
    
    print("[TESTE] Aplicação de teste pronta\n")
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n[TESTE] Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n[TESTE] ERRO durante teste: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("TESTE CONCLUÍDO")
    print("="*80)
    print("\n✅ Se não apareceu 'invalid command name', a correção funcionou!")
    print("❌ Se apareceu o erro, precisamos de uma abordagem diferente.\n")


if __name__ == "__main__":
    executar_teste()

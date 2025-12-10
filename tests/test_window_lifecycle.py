"""
Teste isolado para verificar o ciclo de vida das janelas CustomTkinter
sem iniciar o sistema completo.

Testa:
1. Criação e destruição de TabelaComSelecaoSimulada
2. Abertura de PlateWindow a partir de TabelaComSelecaoSimulada
3. Fechamento de PlateWindow e verificação se TabelaComSelecaoSimulada fica responsiva
4. Detecção de "invalid command name" errors
"""

import customtkinter as ctk
import pandas as pd
import sys
import traceback
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestConfig:
    """Configuração do teste"""
    QUICK_DESTROY = False  # True = destruir rapidamente (reproduz erro)
    USE_GRAB_SET = True    # True = usar grab_set (comportamento atual)
    USE_STATE_ZOOMED = True  # True = maximizar janela (comportamento atual)
    DELAY_BEFORE_DESTROY = 500  # ms antes de destruir (ajustar conforme necessário)


def criar_dataframe_teste():
    """Cria DataFrame de teste simulando resultados de análise"""
    data = {
        'Poço': [f'{chr(65+i//12)}{(i%12)+1}' for i in range(36)],
        'Amostra': [f'Amostra_{i+1}' for i in range(36)],
        'Código': [f'COD{i+1:03d}' for i in range(36)],
        'Resultado_SC2': ['DETECTADO' if i % 3 == 0 else 'NÃO DETECTADO' for i in range(36)],
        'CT_SC2': [25.5 + i*0.5 if i % 3 == 0 else '' for i in range(36)],
    }
    return pd.DataFrame(data)


class TabelaTeste(ctk.CTkToplevel):
    """Versão simplificada de TabelaComSelecaoSimulada para teste"""
    
    def __init__(self, root, df, test_config: TestConfig):
        super().__init__(root)
        
        self.test_config = test_config
        self.df = df
        self._closing = False
        self._after_ids = []
        
        self.title("TESTE - Tabela de Resultados")
        self.geometry("800x600")
        
        # Criar interface simples
        self._criar_widgets()
        
        # Aplicar configurações de teste
        self.transient(root)
        
        if self.test_config.USE_GRAB_SET:
            print("[TESTE] Aplicando grab_set()")
            self.grab_set()
        
        if self.test_config.USE_STATE_ZOOMED:
            print("[TESTE] Agendando state('zoomed')")
            # Proteção contra "invalid command name"
            def maximizar_seguro():
                try:
                    if self.winfo_exists():
                        print("[TESTE] Executando state('zoomed')")
                        self.state("zoomed")
                except Exception as e:
                    print(f"[TESTE] Erro ao maximizar: {e}")
            
            aid = self.after(100, maximizar_seguro)
            self._after_ids.append(aid)
        
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        print("[TESTE] TabelaTeste criada")
    
    def _criar_widgets(self):
        """Cria interface simplificada"""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Label de informação
        info_label = ctk.CTkLabel(
            main_frame,
            text=f"DataFrame de Teste: {len(self.df)} linhas",
            font=("Arial", 16, "bold")
        )
        info_label.pack(pady=10)
        
        # Botão para abrir "PlateWindow"
        btn_mapa = ctk.CTkButton(
            main_frame,
            text="🗺️ Abrir Mapa da Placa (Simula PlateWindow)",
            command=self._abrir_mapa_teste,
            width=400,
            height=50
        )
        btn_mapa.pack(pady=20)
        
        # Botão para fechar
        btn_fechar = ctk.CTkButton(
            main_frame,
            text="❌ Fechar Janela",
            command=self._on_close,
            width=200,
            height=40
        )
        btn_fechar.pack(pady=10)
        
        # Label de status
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Status: Aguardando ação...",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=10)
    
    def _abrir_mapa_teste(self):
        """Simula abertura de PlateWindow"""
        print("[TESTE] Abrindo janela de mapa (simulação)...")
        self.status_label.configure(text="Status: Abrindo mapa da placa...")
        
        # Liberar grab antes de abrir janela filha
        if self.test_config.USE_GRAB_SET:
            print("[TESTE] Liberando grab_set() temporariamente")
            try:
                self.grab_release()
            except Exception as e:
                print(f"[TESTE] Erro ao liberar grab: {e}")
        
        # Criar janela filha simples
        janela_mapa = ctk.CTkToplevel(self)
        janela_mapa.title("TESTE - Mapa da Placa")
        janela_mapa.geometry("600x400")
        janela_mapa.transient(self)
        
        frame = ctk.CTkFrame(janela_mapa)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        label = ctk.CTkLabel(
            frame,
            text="Simulação de PlateWindow\n\nEsta janela simula o PlateWindow",
            font=("Arial", 14)
        )
        label.pack(pady=20)
        
        # Botão para "salvar e retornar"
        def salvar_e_retornar():
            print("[TESTE] Executando 'Salvar e Retornar'")
            try:
                janela_mapa.destroy()
                print("[TESTE] Janela de mapa destruída")
            except Exception as e:
                print(f"[TESTE] Erro ao destruir janela de mapa: {e}")
                traceback.print_exc()
            
            # Restaurar grab após fechar janela filha
            if self.test_config.USE_GRAB_SET:
                print("[TESTE] Restaurando grab_set()")
                def restaurar_grab_seguro():
                    try:
                        if self.winfo_exists():
                            self.grab_set()
                            print("[TESTE] grab_set() restaurado com sucesso")
                    except Exception as e:
                        print(f"[TESTE] Erro ao restaurar grab: {e}")
                
                aid = self.after(100, restaurar_grab_seguro)
                self._after_ids.append(aid)
            
            self.status_label.configure(text="Status: Mapa fechado. Janela principal deveria estar responsiva.")
        
        btn_salvar = ctk.CTkButton(
            frame,
            text="💾 Salvar e Retornar",
            command=salvar_e_retornar,
            width=250,
            height=50
        )
        btn_salvar.pack(pady=20)
        
        janela_mapa.focus_force()
        print("[TESTE] Janela de mapa criada")
    
    def _cancelar_callbacks(self):
        """Cancela todos os callbacks pendentes"""
        print(f"[TESTE] Cancelando {len(self._after_ids)} callbacks pendentes")
        for aid in self._after_ids:
            try:
                self.after_cancel(aid)
            except Exception as e:
                print(f"[TESTE] Erro ao cancelar callback {aid}: {e}")
        self._after_ids.clear()
    
    def _on_close(self):
        """Fecha a janela com segurança"""
        if self._closing:
            print("[TESTE] _on_close já foi chamado, ignorando")
            return
        
        print("[TESTE] Iniciando fechamento da janela...")
        self._closing = True
        
        # Cancelar callbacks pendentes
        self._cancelar_callbacks()
        
        # Liberar grab
        if self.test_config.USE_GRAB_SET:
            try:
                print("[TESTE] Liberando grab_set() final")
                self.grab_release()
            except Exception as e:
                print(f"[TESTE] Erro ao liberar grab: {e}")
        
        # Destruir janela
        if self.test_config.QUICK_DESTROY:
            print("[TESTE] Destruindo janela IMEDIATAMENTE (pode causar erro)")
            try:
                if self.winfo_exists():
                    self.destroy()
            except Exception as e:
                print(f"[TESTE] Erro ao destruir: {e}")
                traceback.print_exc()
        else:
            print(f"[TESTE] Destruindo janela com delay de {self.test_config.DELAY_BEFORE_DESTROY}ms")
            def destruir_seguro():
                try:
                    if self.winfo_exists():
                        print("[TESTE] Executando destroy()")
                        self.destroy()
                        print("[TESTE] Janela destruída com sucesso")
                except Exception as e:
                    print(f"[TESTE] Erro ao destruir: {e}")
                    traceback.print_exc()
            
            try:
                self.after_idle(destruir_seguro)
                print("[TESTE] destroy() agendado com after_idle()")
            except Exception as e:
                print(f"[TESTE] Erro ao agendar destroy: {e}")
                destruir_seguro()


def executar_teste(config: TestConfig):
    """Executa o teste com a configuração especificada"""
    print("\n" + "="*80)
    print("TESTE DE CICLO DE VIDA DE JANELAS CUSTOMTKINTER")
    print("="*80)
    print(f"Configuração:")
    print(f"  - Destruição rápida: {config.QUICK_DESTROY}")
    print(f"  - Usar grab_set(): {config.USE_GRAB_SET}")
    print(f"  - Usar state('zoomed'): {config.USE_STATE_ZOOMED}")
    print(f"  - Delay antes de destruir: {config.DELAY_BEFORE_DESTROY}ms")
    print("="*80 + "\n")
    
    # Criar aplicação principal
    root = ctk.CTk()
    root.title("TESTE - Janela Principal")
    root.geometry("400x300")
    
    df_teste = criar_dataframe_teste()
    
    # Frame principal
    main_frame = ctk.CTkFrame(root)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Label de título
    title_label = ctk.CTkLabel(
        main_frame,
        text="Teste de Gerenciamento de Janelas",
        font=("Arial", 18, "bold")
    )
    title_label.pack(pady=20)
    
    # Status label
    status_label = ctk.CTkLabel(
        main_frame,
        text="Status: Pronto para teste",
        font=("Arial", 12)
    )
    status_label.pack(pady=10)
    
    # Botão para abrir janela de teste
    def abrir_janela_teste():
        print("\n[TESTE] Abrindo TabelaTeste...")
        status_label.configure(text="Status: Janela de teste aberta")
        try:
            janela = TabelaTeste(root, df_teste, config)
            janela.focus_force()
        except Exception as e:
            print(f"[TESTE] ERRO ao criar TabelaTeste: {e}")
            traceback.print_exc()
            status_label.configure(text=f"Status: ERRO - {e}")
    
    btn_abrir = ctk.CTkButton(
        main_frame,
        text="🚀 Iniciar Teste",
        command=abrir_janela_teste,
        width=250,
        height=50
    )
    btn_abrir.pack(pady=20)
    
    # Instruções
    instrucoes = ctk.CTkLabel(
        main_frame,
        text="1. Clique em 'Iniciar Teste'\n"
             "2. Clique em 'Abrir Mapa da Placa'\n"
             "3. Clique em 'Salvar e Retornar'\n"
             "4. Verifique se a janela principal fica travada",
        font=("Arial", 10),
        justify="left"
    )
    instrucoes.pack(pady=10)
    
    print("[TESTE] Aplicação principal criada. Aguardando interação do usuário...")
    print("[TESTE] Feche a janela principal para encerrar o teste.\n")
    
    try:
        root.mainloop()
    except Exception as e:
        print(f"\n[TESTE] ERRO durante mainloop: {e}")
        traceback.print_exc()
    
    print("\n[TESTE] Teste encerrado.")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("SELEÇÃO DE CENÁRIO DE TESTE")
    print("="*80)
    print("\nEscolha o cenário a testar:")
    print("1. Configuração ATUAL do sistema (grab_set + state zoomed + after_idle)")
    print("2. Destruição RÁPIDA (reproduz 'invalid command name' error)")
    print("3. SEM grab_set (teste sem modal)")
    print("4. SEM state('zoomed') (teste sem maximizar)")
    print("5. Delay LONGO antes de destruir (2000ms)")
    print()
    
    escolha = input("Digite o número do cenário (1-5) [padrão=1]: ").strip()
    
    config = TestConfig()
    
    if escolha == "2":
        print("\n➡️ Cenário 2: Destruição rápida (reproduz erro)")
        config.QUICK_DESTROY = True
    elif escolha == "3":
        print("\n➡️ Cenário 3: Sem grab_set")
        config.USE_GRAB_SET = False
    elif escolha == "4":
        print("\n➡️ Cenário 4: Sem state('zoomed')")
        config.USE_STATE_ZOOMED = False
    elif escolha == "5":
        print("\n➡️ Cenário 5: Delay longo (2000ms)")
        config.DELAY_BEFORE_DESTROY = 2000
    else:
        print("\n➡️ Cenário 1: Configuração atual (padrão)")
    
    executar_teste(config)

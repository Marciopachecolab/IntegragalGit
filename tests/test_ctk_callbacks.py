"""
Teste focado em identificar e resolver callbacks internos do CustomTkinter
que causam "invalid command name" errors.

Este teste monitora os callbacks agendados pelo CustomTkinter internamente.
"""

import customtkinter as ctk
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def interceptar_after(widget):
    """Intercepta chamadas de after() para monitorar callbacks"""
    original_after = widget.after
    callbacks_pendentes = []
    
    def after_wrapper(ms, func=None, *args):
        if func is None:
            # after() usado como sleep
            return original_after(ms)
        
        # Registrar callback
        aid = original_after(ms, func, *args)
        info = {
            'id': aid,
            'delay': ms,
            'func': func.__name__ if hasattr(func, '__name__') else str(func),
            'cancelado': False
        }
        callbacks_pendentes.append(info)
        print(f"[MONITOR] Callback agendado: {info['func']} em {ms}ms (ID: {aid})")
        return aid
    
    widget.after = after_wrapper
    widget._callbacks_pendentes = callbacks_pendentes
    return widget


def listar_callbacks_pendentes(widget):
    """Lista todos os callbacks ainda pendentes"""
    if hasattr(widget, '_callbacks_pendentes'):
        pendentes = [cb for cb in widget._callbacks_pendentes if not cb['cancelado']]
        if pendentes:
            print(f"\n[MONITOR] ⚠️ {len(pendentes)} callbacks AINDA PENDENTES:")
            for cb in pendentes:
                print(f"  - {cb['func']} (ID: {cb['id']}, delay: {cb['delay']}ms)")
        else:
            print(f"\n[MONITOR] ✅ Nenhum callback pendente")
        return pendentes
    return []


class JanelaTeste(ctk.CTkToplevel):
    """Janela de teste que monitora callbacks"""
    
    def __init__(self, root, usar_grab=True, usar_zoom=True):
        super().__init__(root)
        
        # Interceptar after() para monitorar callbacks
        interceptar_after(self)
        
        self.title("Janela de Teste - Monitoramento de Callbacks")
        self.geometry("600x400")
        
        self.usar_grab = usar_grab
        self.usar_zoom = usar_zoom
        
        # Criar interface
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        label = ctk.CTkLabel(
            frame,
            text="Teste de Callbacks do CustomTkinter",
            font=("Arial", 16, "bold")
        )
        label.pack(pady=20)
        
        info_label = ctk.CTkLabel(
            frame,
            text=f"grab_set: {usar_grab}\nstate('zoomed'): {usar_zoom}",
            font=("Arial", 12)
        )
        info_label.pack(pady=10)
        
        # Botão para listar callbacks
        btn_listar = ctk.CTkButton(
            frame,
            text="📋 Listar Callbacks Pendentes",
            command=lambda: listar_callbacks_pendentes(self),
            width=250
        )
        btn_listar.pack(pady=10)
        
        # Botão para fechar
        btn_fechar = ctk.CTkButton(
            frame,
            text="❌ Fechar Janela",
            command=self._fechar_seguro,
            width=250
        )
        btn_fechar.pack(pady=10)
        
        # Aplicar configurações
        self.transient(root)
        
        if self.usar_grab:
            print("[TESTE] Aplicando grab_set()")
            self.grab_set()
        
        if self.usar_zoom:
            print("[TESTE] Agendando state('zoomed')")
            self.after(100, lambda: self.state("zoomed"))
        
        self.protocol("WM_DELETE_WINDOW", self._fechar_seguro)
        
        print("\n[TESTE] Janela criada. Monitore os callbacks acima.")
    
    def _fechar_seguro(self):
        """Fecha a janela verificando callbacks pendentes"""
        print("\n[TESTE] Iniciando fechamento...")
        
        # Listar callbacks antes de fechar
        pendentes = listar_callbacks_pendentes(self)
        
        if pendentes:
            print("[TESTE] ⚠️ ATENÇÃO: Callbacks pendentes serão cancelados")
            
            # Tentar cancelar todos
            for cb in pendentes:
                try:
                    self.after_cancel(cb['id'])
                    cb['cancelado'] = True
                    print(f"[TESTE] ✓ Callback {cb['func']} cancelado")
                except Exception as e:
                    print(f"[TESTE] ✗ Erro ao cancelar {cb['func']}: {e}")
        
        # Liberar grab
        if self.usar_grab:
            try:
                print("[TESTE] Liberando grab_set()")
                self.grab_release()
            except Exception as e:
                print(f"[TESTE] Erro ao liberar grab: {e}")
        
        # Destruir com after_idle
        print("[TESTE] Agendando destroy() com after_idle()")
        def destruir():
            try:
                print("[TESTE] Executando destroy()")
                if self.winfo_exists():
                    self.destroy()
                print("[TESTE] ✅ Janela destruída com sucesso")
            except Exception as e:
                print(f"[TESTE] ❌ Erro ao destruir: {e}")
        
        try:
            self.after_idle(destruir)
        except Exception as e:
            print(f"[TESTE] Erro ao agendar destroy: {e}")
            destruir()


def executar_teste():
    """Executa teste de monitoramento de callbacks"""
    print("\n" + "="*80)
    print("TESTE DE CALLBACKS INTERNOS DO CUSTOMTKINTER")
    print("="*80)
    print("\nEste teste monitora todos os callbacks agendados pelo CustomTkinter")
    print("e verifica se eles são cancelados corretamente ao fechar a janela.\n")
    print("="*80 + "\n")
    
    root = ctk.CTk()
    root.title("TESTE - Janela Principal")
    root.geometry("400x250")
    
    # Interceptar after() da janela principal também
    interceptar_after(root)
    
    frame = ctk.CTkFrame(root)
    frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    title = ctk.CTkLabel(
        frame,
        text="Teste de Callbacks",
        font=("Arial", 18, "bold")
    )
    title.pack(pady=20)
    
    def abrir_janela(usar_grab, usar_zoom):
        config_text = []
        if usar_grab:
            config_text.append("grab_set")
        if usar_zoom:
            config_text.append("state('zoomed')")
        
        config_str = " + ".join(config_text) if config_text else "padrão"
        print(f"\n[TESTE] Abrindo janela com: {config_str}")
        
        janela = JanelaTeste(root, usar_grab, usar_zoom)
        janela.focus_force()
    
    # Botões para diferentes configurações
    btn1 = ctk.CTkButton(
        frame,
        text="Teste COM grab_set + zoomed",
        command=lambda: abrir_janela(True, True),
        width=250
    )
    btn1.pack(pady=5)
    
    btn2 = ctk.CTkButton(
        frame,
        text="Teste SEM grab_set",
        command=lambda: abrir_janela(False, True),
        width=250
    )
    btn2.pack(pady=5)
    
    btn3 = ctk.CTkButton(
        frame,
        text="Teste SEM zoomed",
        command=lambda: abrir_janela(True, False),
        width=250
    )
    btn3.pack(pady=5)
    
    print("[TESTE] Aplicação pronta. Clique nos botões para testar.\n")
    
    root.mainloop()
    
    print("\n[TESTE] Teste encerrado.")


if __name__ == "__main__":
    executar_teste()

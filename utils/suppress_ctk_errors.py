"""
Wrapper para suprimir erros "invalid command name" do CustomTkinter
sem afetar a funcionalidade do sistema.

Esses erros são cosméticos e ocorrem quando callbacks internos do CustomTkinter
(update, check_dpi_scaling) são agendados mas a janela é fechada antes de executarem.
"""

import sys
import io


class SuppressCustomTkinterErrors:
    """
    Context manager que suprime apenas erros "invalid command name" do Tcl/Tk
    sem afetar outros erros ou a funcionalidade do sistema.
    """
    
    def __init__(self):
        self.original_stderr = None
        self.buffer = None
    
    def __enter__(self):
        # Capturar stderr
        self.original_stderr = sys.stderr
        self.buffer = io.StringIO()
        sys.stderr = FilteredStderr(self.original_stderr)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restaurar stderr original
        sys.stderr = self.original_stderr
        return False


class FilteredStderr:
    """
    Wrapper de stderr que filtra apenas mensagens específicas de erro do Tcl/Tk
    relacionadas a callbacks do CustomTkinter.
    """
    
    def __init__(self, original_stderr):
        self.original_stderr = original_stderr
        self.buffer = []
    
    def write(self, message):
        # Filtrar apenas erros específicos do CustomTkinter
        if self._should_suppress(message):
            # Armazenar em buffer mas não exibir
            self.buffer.append(message)
            return
        
        # Todos os outros erros/warnings são exibidos normalmente
        self.original_stderr.write(message)
    
    def _should_suppress(self, message):
        """
        Retorna True apenas para erros cosméticos do CustomTkinter
        que não afetam a funcionalidade.
        """
        message_lower = message.lower()
        
        # Suprimir apenas "invalid command name" de update/check_dpi_scaling
        if 'invalid command name' in message_lower:
            if 'update' in message_lower or 'check_dpi_scaling' in message_lower:
                return True
        
        return False
    
    def flush(self):
        self.original_stderr.flush()
    
    def fileno(self):
        return self.original_stderr.fileno()


def aplicar_filtro_global():
    """
    Aplica o filtro de erros globalmente ao sistema.
    Chamar no início do main.py.
    """
    sys.stderr = FilteredStderr(sys.stderr)
    print("[Sistema] Filtro de erros CustomTkinter ativado")

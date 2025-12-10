"""
Error Handler - Sistema Centralizado de Tratamento de Erros
Fornece error handling consistente e mensagens amigáveis ao usuário
"""

import traceback
import functools
from typing import Optional, Callable, Any
from tkinter import messagebox
import customtkinter as ctk


class ErrorHandler:
    """Classe centralizada para tratamento de erros"""
    
    # Mapeamento de tipos de erro para mensagens amigáveis
    ERROR_MESSAGES = {
        FileNotFoundError: {
            'title': 'Arquivo Não Encontrado',
            'message': 'O arquivo especificado não foi encontrado.',
            'suggestion': 'Verifique se o arquivo existe e o caminho está correto.'
        },
        PermissionError: {
            'title': 'Sem Permissão',
            'message': 'Você não tem permissão para acessar este recurso.',
            'suggestion': 'Verifique as permissões ou execute como administrador.'
        },
        IOError: {
            'title': 'Erro de Entrada/Saída',
            'message': 'Erro ao ler ou escrever arquivo.',
            'suggestion': 'Verifique se há espaço em disco e se o arquivo não está em uso.'
        },
        ValueError: {
            'title': 'Valor Inválido',
            'message': 'Um valor inválido foi fornecido.',
            'suggestion': 'Verifique os dados inseridos e tente novamente.'
        },
        KeyError: {
            'title': 'Chave Não Encontrada',
            'message': 'Um campo esperado não foi encontrado nos dados.',
            'suggestion': 'Verifique se o arquivo possui todos os campos necessários.'
        },
        AttributeError: {
            'title': 'Atributo Não Encontrado',
            'message': 'Um atributo necessário não existe.',
            'suggestion': 'Pode ser um problema de compatibilidade. Reporte ao suporte.'
        },
        TypeError: {
            'title': 'Tipo Inválido',
            'message': 'Um dado possui tipo incorreto.',
            'suggestion': 'Verifique o formato dos dados fornecidos.'
        },
        Exception: {
            'title': 'Erro Inesperado',
            'message': 'Ocorreu um erro inesperado.',
            'suggestion': 'Tente novamente. Se persistir, reporte ao suporte.'
        }
    }
    
    @staticmethod
    def get_friendly_message(exception: Exception) -> dict:
        """
        Converte exceção em mensagem amigável
        
        Args:
            exception: Exceção capturada
            
        Returns:
            Dict com title, message e suggestion
        """
        exc_type = type(exception)
        
        # Buscar mensagem específica para o tipo de erro
        for error_type, msg_data in ErrorHandler.ERROR_MESSAGES.items():
            if isinstance(exception, error_type):
                return msg_data.copy()
        
        # Fallback para erro genérico
        return ErrorHandler.ERROR_MESSAGES[Exception].copy()
    
    @staticmethod
    def show_error(title: str = None, 
                   message: str = None, 
                   details: str = None,
                   suggestion: str = None,
                   exception: Exception = None):
        """
        Mostra diálogo de erro amigável ao usuário
        
        Args:
            title: Título do erro (se None, usa do exception)
            message: Mensagem principal (se None, usa do exception)
            details: Detalhes técnicos (opcional)
            suggestion: Sugestão de solução (se None, usa do exception)
            exception: Exceção original (opcional)
        """
        # Se exception fornecida, extrair mensagens
        if exception and (not title or not message):
            friendly = ErrorHandler.get_friendly_message(exception)
            title = title or friendly['title']
            message = message or friendly['message']
            suggestion = suggestion or friendly['suggestion']
            if not details and hasattr(exception, 'args') and exception.args:
                details = str(exception.args[0])
        
        # Construir mensagem completa
        full_message = message
        
        if suggestion:
            full_message += f"\n\n💡 Sugestão:\n{suggestion}"
        
        if details:
            full_message += f"\n\n🔍 Detalhes:\n{details}"
        
        # Mostrar diálogo
        messagebox.showerror(title or "Erro", full_message)
    
    @staticmethod
    def show_warning(title: str, message: str, suggestion: str = None):
        """
        Mostra diálogo de aviso ao usuário
        
        Args:
            title: Título do aviso
            message: Mensagem principal
            suggestion: Sugestão de ação (opcional)
        """
        full_message = message
        
        if suggestion:
            full_message += f"\n\n💡 Sugestão:\n{suggestion}"
        
        messagebox.showwarning(title, full_message)
    
    @staticmethod
    def show_info(title: str, message: str):
        """
        Mostra diálogo informativo ao usuário
        
        Args:
            title: Título da mensagem
            message: Mensagem informativa
        """
        messagebox.showinfo(title, message)
    
    @staticmethod
    def log_exception(exception: Exception, context: str = ""):
        """
        Loga exceção com traceback completo
        
        Args:
            exception: Exceção capturada
            context: Contexto onde ocorreu (nome da função, etc)
        """
        error_msg = f"ERRO{' em ' + context if context else ''}: {type(exception).__name__}: {str(exception)}"
        print(error_msg)
        print("Traceback:")
        traceback.print_exc()
    
    @staticmethod
    def handle_exception(exception: Exception, 
                        context: str = "",
                        show_dialog: bool = True,
                        re_raise: bool = False):
        """
        Tratamento completo de exceção (log + dialog + re-raise opcional)
        
        Args:
            exception: Exceção capturada
            context: Contexto onde ocorreu
            show_dialog: Se deve mostrar diálogo ao usuário
            re_raise: Se deve re-lançar a exceção após tratamento
        """
        # Logar
        ErrorHandler.log_exception(exception, context)
        
        # Mostrar diálogo se solicitado
        if show_dialog:
            ErrorHandler.show_error(exception=exception)
        
        # Re-lançar se solicitado
        if re_raise:
            raise exception


def safe_operation(fallback_value: Any = None,
                   fallback_msg: str = None,
                   show_error: bool = True,
                   context: str = None):
    """
    Decorador para operações seguras com tratamento de erro automático
    
    Args:
        fallback_value: Valor a retornar em caso de erro
        fallback_msg: Mensagem customizada de erro
        show_error: Se deve mostrar diálogo de erro
        context: Contexto da operação (se None, usa nome da função)
    
    Example:
        @safe_operation(fallback_value=[], show_error=True)
        def carregar_dados():
            return pd.read_csv('dados.csv')
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Determinar contexto
                op_context = context or func.__name__
                
                # Logar erro
                ErrorHandler.log_exception(e, op_context)
                
                # Mostrar erro se solicitado
                if show_error:
                    if fallback_msg:
                        ErrorHandler.show_error(
                            title="Erro",
                            message=fallback_msg,
                            exception=e
                        )
                    else:
                        ErrorHandler.show_error(exception=e)
                
                # Retornar fallback
                return fallback_value
        
        return wrapper
    return decorator


class ErrorContext:
    """
    Context manager para tratamento de erros
    
    Example:
        with ErrorContext("Carregar Dados"):
            df = pd.read_csv('dados.csv')
    """
    
    def __init__(self, 
                 context: str,
                 show_error: bool = True,
                 re_raise: bool = False):
        """
        Args:
            context: Nome da operação
            show_error: Se deve mostrar diálogo
            re_raise: Se deve re-lançar exceção
        """
        self.context = context
        self.show_error = show_error
        self.re_raise = re_raise
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type is not None:
            # Tratamento completo da exceção
            ErrorHandler.handle_exception(
                exc_value,
                context=self.context,
                show_dialog=self.show_error,
                re_raise=self.re_raise
            )
            
            # Suprime a exceção se não for para re-lançar
            return not self.re_raise
        
        return True


# Funções de conveniência
def show_error(message: str, title: str = "Erro", suggestion: str = None):
    """Atalho para mostrar erro simples"""
    ErrorHandler.show_error(title=title, message=message, suggestion=suggestion)


def show_warning(message: str, title: str = "Aviso", suggestion: str = None):
    """Atalho para mostrar aviso"""
    ErrorHandler.show_warning(title=title, message=message, suggestion=suggestion)


def show_info(message: str, title: str = "Informação"):
    """Atalho para mostrar informação"""
    ErrorHandler.show_info(title=title, message=message)

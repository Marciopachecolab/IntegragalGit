"""
Gerenciador de Navegação para a aplicação IntegraGAL.
Responsável por controlar a navegação e estado entre diferentes módulos.
"""

from typing import Callable, Optional

from utils.logger import registrar_log


class NavigationManager:
    """Gerenciador de navegação entre módulos"""

    def __init__(self, main_window):
        """
        Inicializa o gerenciador de navegação

        Args:
            main_window: Instância da janela principal (App)
        """
        self.main_window = main_window
        self.current_module: Optional[str] = None
        self.navigation_history = []
        self.module_states = {}

    def navigate_to(self, module_name: str, callback: Optional[Callable] = None):
        """
        Navega para um módulo específico

        Args:
            module_name: Nome do módulo de destino
            callback: Função a ser executada durante a navegação
        """
        try:
            # Registrar navegação no histórico
            self.navigation_history.append(
                {
                    "from": self.current_module,
                    "to": module_name,
                    "timestamp": self._get_current_timestamp(),
                }
            )

            # Atualizar módulo atual
            old_module = self.current_module
            self.current_module = module_name

            # Salvar estado do módulo anterior se existir
            if old_module:
                self._save_module_state(old_module)

            # Registrar log de navegação
            registrar_log(
                "Navegação", f"Navegação de '{old_module}' para '{module_name}'", "INFO"
            )

            # Executar callback se fornecido
            if callback:
                callback()

            # Atualizar interface
            self._update_ui_for_module(module_name)

        except Exception as e:
            registrar_log(
                "Navegação", f"Erro na navegação para '{module_name}': {e}", "ERROR"
            )

    def _get_current_timestamp(self) -> str:
        """Retorna timestamp atual"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _save_module_state(self, module_name: str):
        """
        Salva o estado do módulo atual

        Args:
            module_name: Nome do módulo
        """
        if hasattr(self.main_window, "app_state"):
            self.module_states[module_name] = {
                "app_state": self.main_window.app_state,
                "timestamp": self._get_current_timestamp(),
            }

    def _update_ui_for_module(self, module_name: str):
        """
        Atualiza a interface para o módulo específico

        Args:
            module_name: Nome do módulo
        """
        # Mapear módulos para títulos e ações específicas
        module_configs = {
            "main": {"title": "IntegraGAL - Menu Principal", "actions": []},
            "extracao": {"title": "IntegraGAL - Mapeamento da Placa", "actions": []},
            "analise": {"title": "IntegraGAL - Análise", "actions": []},
            "resultados": {"title": "IntegraGAL - Resultados", "actions": []},
            "gal": {"title": "IntegraGAL - Envio GAL", "actions": []},
            "admin": {"title": "IntegraGAL - Administração", "actions": []},
            "usuarios": {"title": "IntegraGAL - Gerenciar Usuários", "actions": []},
        }

        config = module_configs.get(module_name, module_configs["main"])

        # Atualizar título da janela
        if hasattr(self.main_window, "title"):
            self.main_window.title(config["title"])

        # Executar ações específicas do módulo
        for action in config["actions"]:
            try:
                action()
            except Exception as e:
                registrar_log(
                    "Navegação",
                    f"Erro ao executar ação do módulo '{module_name}': {e}",
                    "ERROR",
                )

    def go_back(self) -> bool:
        """
        Volta para o módulo anterior no histórico

        Returns:
            True se foi possível voltar, False caso contrário
        """
        try:
            if len(self.navigation_history) > 1:
                # Remover navegação atual
                self.navigation_history.pop()

                # Obter navegação anterior
                previous_nav = self.navigation_history[-1]
                target_module = previous_nav["from"]

                # Navegar para o módulo anterior
                if target_module:
                    self.navigate_to(target_module)
                    return True

        except Exception as e:
            registrar_log("Navegação", f"Erro ao voltar no histórico: {e}", "ERROR")

        return False

    def get_current_module(self) -> Optional[str]:
        """
        Retorna o módulo atual

        Returns:
            Nome do módulo atual ou None
        """
        return self.current_module

    def get_navigation_history(self) -> list:
        """
        Retorna o histórico de navegações

        Returns:
            Lista do histórico de navegações
        """
        return self.navigation_history.copy()

    def clear_history(self):
        """Limpa o histórico de navegações"""
        self.navigation_history.clear()
        registrar_log("Navegação", "Histórico de navegações limpo", "INFO")

    def get_module_info(self, module_name: str) -> dict:
        """
        Retorna informações sobre um módulo específico

        Args:
            module_name: Nome do módulo

        Returns:
            Dicionário com informações do módulo
        """
        info = {
            "name": module_name,
            "current": self.current_module == module_name,
            "has_saved_state": module_name in self.module_states,
            "navigation_count": len(
                [h for h in self.navigation_history if h["to"] == module_name]
            ),
        }

        if module_name in self.module_states:
            info["last_access"] = self.module_states[module_name]["timestamp"]

        return info

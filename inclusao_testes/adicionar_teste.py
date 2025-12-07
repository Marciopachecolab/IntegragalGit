"""
Módulo de interface para inclusão e manutenção de exames, equipamentos,
placas e regras ("Cadastros Diversos") no IntegraGAL.

Este módulo expõe a classe `AdicionarTesteApp`, que é utilizada pelo
`MenuHandler` da UI através de:

    from inclusao_testes.adicionar_teste import AdicionarTesteApp
    AdicionarTesteApp(self.main_window)

Em vez de reimplementar toda a lógica de cadastros, esta classe atua
como uma *fachada* para `services.cadastros_diversos.CadastrosDiversosWindow`,
garantindo:

- reutilização da tela já existente em `services/cadastros_diversos.py`;
- leitura/escrita diretamente nos CSVs configurados pelo `config_service`;
- integração suave com o `AppState`, quando disponível na `main_window`.
"""

from __future__ import annotations

from typing import Optional, Any

import customtkinter as ctk

from services.cadastros_diversos import CadastrosDiversosWindow
from models import AppState


class AdicionarTesteApp:
    """
    Fachada simples para abrir a janela de *Cadastros Diversos*.

    Esta classe mantém a assinatura esperada pelo `MenuHandler`
    e encapsula a criação da `CadastrosDiversosWindow`, que é a
    janela real responsável por gerenciar:

    - Exames (banco/exames_config.csv)
    - Equipamentos (banco/equipamentos.csv)
    - Placas (banco/placas.csv)
    - Regras (banco/regras.csv)
    """

    def __init__(self, main_window: ctk.CTk | Any) -> None:
        """
        Cria a janela de cadastros diversos a partir da `main_window`.

        Parameters
        ----------
        main_window:
            Janela principal da aplicação (instância de `MainWindow`),
            que normalmente possui o atributo `app_state`.
        """
        self.main_window = main_window
        self.app_state: Optional[AppState] = getattr(
            main_window, "app_state", None
        )

        # Instancia e exibe a janela unificada de cadastros.
        # Toda a lógica de leitura/escrita de CSV e validações
        # mínimas já está implementada em `CadastrosDiversosWindow`.
        self.window = CadastrosDiversosWindow(main_window)

    def focus(self) -> None:
        """
        Método auxiliar opcional para dar foco à janela de cadastros.

        Não é utilizado diretamente pelo sistema hoje, mas pode ser
        útil em cenários futuros onde seja necessário recuperar o
        foco da janela sem recriá-la.
        """
        try:
            self.window.window.lift()
            self.window.window.focus_force()
        except Exception:
            # Se por algum motivo a janela já foi destruída, ignoramos.
            pass

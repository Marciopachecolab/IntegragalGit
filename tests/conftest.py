import pytest

def pytest_configure(config):
    """Registra marcadores customizados usados na suíte de testes."""
    config.addinivalue_line(
        "markers",
        "gui: testes que exercitam componentes de interface gráfica (Tkinter/CustomTkinter).",
    )

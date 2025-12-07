import sys
import pathlib

# Garante que o diretório do projeto esteja no PYTHONPATH para imports relativos (analise, services, etc.).
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def pytest_configure(config):
    """Registra marcadores customizados usados na suíte de testes."""
    config.addinivalue_line(
        "markers",
        "gui: testes que exercitam componentes de interface gráfica (Tkinter/CustomTkinter).",
    )

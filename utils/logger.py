# utils/logger.py
import csv
import getpass
import os
import socket
from datetime import datetime

# --- Bloco de Configuração Inicial ---
# Define o diretório base do projeto de forma robusta
from services.system_paths import BASE_DIR

# --- MELHORIA: Quebra da Importação Circular ---
# O caminho do log é definido aqui, de forma autônoma, sem depender do ConfigService.
# Isto resolve o erro de importação circular.
LOG_FILE_PATH = os.path.join(BASE_DIR, "logs", "sistema.log")


def registrar_log(acao: str, detalhes: str, level: str = "INFO"):
    """
    Regista uma entrada de log no ficheiro CSV centralizado.
    Cria o diretório do log se ele não existir.

    Args:
        acao (str): Ação que está a ser logada (ex: "Login", "Análise").
        detalhes (str): Detalhes específicos sobre a ação.
        level (str): Nível do log (INFO, WARNING, ERROR, CRITICAL, DEBUG).
    """
    try:
        # Garante que o diretório do log exista
        log_dir = os.path.dirname(LOG_FILE_PATH)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            # Log para a consola na primeira criação do diretório
            print(f"[LOGGER] Diretório de log criado: {log_dir}")

        # Abre o ficheiro em modo de adição ('a') com codificação UTF-8
        with open(LOG_FILE_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(
                [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    getpass.getuser(),
                    socket.gethostbyname(socket.gethostname()),
                    acao,
                    detalhes,
                    level.upper(),
                ]
            )
    except Exception as e:
        # Se o logging falhar, imprime o erro na consola para não passar despercebido.
        print("--- ERRO CRÍTICO NO LOGGER ---")
        print("Não foi possível registar o log:")
        print(f"Ação: {acao}, Detalhes: {detalhes}, Nível: {level}")
        print(f"Erro: {e}")
        print("--- FIM DO ERRO DO LOGGER ---")

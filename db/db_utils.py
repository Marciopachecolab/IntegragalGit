# db/db_utils.py

import psycopg2

# --- MELHORIA: Importa o novo serviço de configuração e o logger ---
from services.config_service import config_service
# --- Configuração de Paths e Imports ---
from utils.logger import registrar_log


def get_postgres_connection():
    """
    Estabelece e retorna uma conexão com o banco de dados PostgreSQL.
    As configurações são obtidas exclusivamente do ConfigService.
    Retorna None se a conexão estiver desabilitada ou falhar.
    """
    # --- MELHORIA: Obtém a configuração do DB a partir do serviço ---
    db_config = config_service.get_db_config()

    if not db_config.get("enabled", False):
        # Apenas retorna None, não regista log aqui para evitar poluir o log
        # se o DB estiver intencionalmente desabilitado.
        return None

    try:
        conn = psycopg2.connect(
            dbname=db_config.get("dbname"),
            user=db_config.get("user"),
            password=db_config.get("password"),
            host=db_config.get("host"),
            port=int(db_config.get("port", 5432)),
        )
        return conn
    except psycopg2.OperationalError as e:
        registrar_log("DB Utils", f"Erro de conexão com o PostgreSQL: {e}", "CRITICAL")
        return None
    except Exception as e:
        registrar_log(
            "DB Utils", f"Erro inesperado ao conectar ao PostgreSQL: {e}", "CRITICAL"
        )
        return None


def salvar_historico_processamento(
    analista: str, exame: str, status: str, detalhes: str
):
    """
    Salva um registo na tabela 'historico_processos' do PostgreSQL.
    
    ⚠️ FONTE DE VERDADE: Esta função salva no PostgreSQL que é a ÚNICA fonte oficial.
    O arquivo logs/historico_analises.csv é apenas uma visão auxiliar gerada do banco.
    Sempre use esta função para salvar histórico, NUNCA escreva diretamente no CSV.
    
    Ver: scripts/consolidate_history.py para exportar CSV do banco.
    """
    conn = get_postgres_connection()
    if conn is None:
        # Se a conexão estiver desabilitada ou falhar, regista e continua sem erro.
        registrar_log(
            "DB Utils",
            "Salvamento de histórico ignorado (conexão com DB indisponível ou desabilitada).",
            "INFO",
        )
        return

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO historico_processos (analista, exame, status, detalhes, data_hora)
                VALUES (%s, %s, %s, %s, NOW())
            """,
                (analista, exame, status, detalhes),
            )
        conn.commit()
    except psycopg2.Error as e:
        registrar_log(
            "DB Utils", f"Falha ao salvar histórico no PostgreSQL: {e}", "ERROR"
        )
        # Opcional: poderia relançar uma exceção se a gravação for crítica
    finally:
        if conn:
            conn.close()

#!/usr/bin/env python3
"""
CSV Lock Manager - Sincronização segura de arquivos CSV em rede local

Fornece lock baseado em arquivo para evitar corrupção de dados quando
múltiplos usuários/máquinas acessam o mesmo CSV simultaneamente.

Uso:
    from services.csv_lock import csv_lock
    
    with csv_lock("logs/historico_analises.csv", timeout=30):
        df = pd.read_csv("logs/historico_analises.csv")
        # ... processa ...
        df.to_csv("logs/historico_analises.csv")
"""

import time
import logging
from pathlib import Path
from contextlib import contextmanager
from typing import Optional

logger = logging.getLogger(__name__)


class CsvLockError(Exception):
    """Exceção para erros de lock CSV"""
    pass


@contextmanager
def csv_lock(
    filepath: str,
    timeout: int = 30,
    lock_suffix: str = ".lock",
    retry_interval: float = 0.05
):
    """
    Context manager para lock seguro de arquivo CSV em rede local.
    
    Usa um arquivo .lock para sincronização entre processos/máquinas.
    Ideal para ambientes com NFS/SMB (rede local).
    
    Args:
        filepath: Caminho do arquivo CSV a proteger
        timeout: Tempo máximo de espera pelo lock (segundos)
        lock_suffix: Sufixo do arquivo de lock (padrão: .lock)
        retry_interval: Intervalo entre verificações de lock (segundos)
    
    Raises:
        CsvLockError: Se não conseguir adquirir lock no tempo limite
    
    Exemplo:
        >>> with csv_lock("logs/historico_analises.csv", timeout=30):
        ...     df = pd.read_csv("logs/historico_analises.csv")
        ...     df["nova_coluna"] = "valor"
        ...     df.to_csv("logs/historico_analises.csv")
    
    """
    lock_path = Path(filepath).with_suffix(lock_suffix)
    start_time = time.time()
    filename = Path(filepath).name
    
    # Aguarda lock ficar disponível
    while lock_path.exists():
        elapsed = time.time() - start_time
        if elapsed > timeout:
            msg = f"Timeout ({timeout}s) esperando lock para {filename}"
            logger.error(f"❌ {msg}")
            raise CsvLockError(msg)
        
        remaining = timeout - elapsed
        logger.debug(f"⏳ Esperando lock {filename} ({remaining:.1f}s restantes)...")
        time.sleep(retry_interval)
    
    try:
        # Adquire lock criando arquivo
        lock_path.touch()
        logger.info(f"✅ Lock adquirido: {filename}")
        yield
        
    except Exception as e:
        logger.error(f"❌ Erro dentro do lock {filename}: {e}")
        raise
        
    finally:
        # Libera lock removendo arquivo
        try:
            lock_path.unlink(missing_ok=True)
            logger.info(f"🔓 Lock liberado: {filename}")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao liberar lock {filename}: {e}")


def obter_info_lock(filepath: str, lock_suffix: str = ".lock") -> Optional[dict]:
    """
    Obtém informações sobre lock de um arquivo (para debug).
    
    Args:
        filepath: Caminho do arquivo CSV
        lock_suffix: Sufixo do arquivo de lock
    
    Returns:
        Dict com informações do lock ou None se não existir
        
    Exemplo:
        >>> info = obter_info_lock("logs/historico_analises.csv")
        >>> if info:
        ...     print(f"Bloqueado desde: {info['tempo_espera']}s atrás")
    """
    lock_path = Path(filepath).with_suffix(lock_suffix)
    
    if not lock_path.exists():
        return None
    
    try:
        stat = lock_path.stat()
        tempo_atrás = time.time() - stat.st_mtime
        
        return {
            "arquivo": str(lock_path),
            "existe": True,
            "tempo_espera": f"{tempo_atrás:.1f}s",
            "modificado_em": stat.st_mtime
        }
    except Exception as e:
        logger.error(f"Erro ao verificar lock: {e}")
        return None


def limpar_locks_antigos(timeout: int = 300) -> int:
    """
    Remove locks antigos (possivelmente deixados por crash).
    
    CUIDADO: Use apenas se NENHUM processo está usando o lock!
    
    Args:
        timeout: Considerar lock antigo se > X segundos (padrão: 5 min)
    
    Returns:
        Número de locks removidos
        
    Exemplo:
        >>> removidos = limpar_locks_antigos(timeout=600)
        >>> print(f"Removidos {removidos} locks antigos")
    """
    banco_dir = Path("banco")
    logs_dir = Path("logs")
    
    removidos = 0
    agora = time.time()
    
    for diretorio in [banco_dir, logs_dir]:
        if not diretorio.exists():
            continue
        
        for lock_file in diretorio.glob("*.lock"):
            try:
                idade = agora - lock_file.stat().st_mtime
                if idade > timeout:
                    lock_file.unlink()
                    logger.warning(f"🗑️  Lock antigo removido: {lock_file.name} ({idade:.0f}s)")
                    removidos += 1
            except Exception as e:
                logger.error(f"Erro removendo lock antigo {lock_file}: {e}")
    
    return removidos


# Configuração de logging
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

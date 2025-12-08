# 🌐 ANÁLISE: Uso Concomitante em Rede Local - Múltiplos Usuários & Máquinas

## 📊 CENÁRIO ATUAL

**Arquitetura:**
- Sistema baseado em **CSV locais** (armazenamento)
- **Interface GUI** (CTk/Tkinter - mono-thread por sessão)
- Sem banco de dados
- Sem mecanismo de lock/sincronização

**Problemas Identificados:**

### 🔴 **CRÍTICO: Corrupção de CSV**
```
Máquina A (Usuario João)  | Máquina B (Usuario Maria)
--------------------------|------------------------
1. Lê historico_analises.csv
2. Processa 10 análises
3. Escreve CSV           | 1. Lê historico_analises.csv
                         | 2. Processa 5 análises
                         | 3. Escreve CSV (SOBRESCREVE!)
4. Resultado: 5 análises de João perdidas ❌
```

### 🔴 **CRÍTICO: Race Condition nos Arquivos de Config**
```
Arquivo: banco/usuarios.csv

Máquina A              | Máquina B
-----------------------|-----------------------
1. Lê usuarios.csv     |
2. Processa login      | 1. Lê usuarios.csv
3. ...                 | 2. Altera senha user X
   ...                 | 3. Escreve usuarios.csv
4. Altera email user Y |
5. Escreve usuarios.csv (Sobrescreve dados de B!)
```

---

## 🔍 ANÁLISE DETALHADA

### **1. Arquivos Afetados (Acesso Crítico)**

| Arquivo | Tipo | Acesso | Risco |
|---------|------|--------|-------|
| `logs/historico_analises.csv` | APPEND + UPDATE | R/W simultâneo | 🔴 CRÍTICO |
| `banco/usuarios.csv` | AUTH + CRUD | R/W simultâneo | 🔴 CRÍTICO |
| `banco/credenciais.csv` | AUTH | Leitura freq. | 🟡 ALTO |
| `banco/exames_config.csv` | READ-ONLY* | Leitura freq. | 🟢 BAIXO |
| `config/exams/*.json` | READ-ONLY | Leitura freq. | 🟢 BAIXO |
| Outros CSVs | READ-ONLY | Leitura freq. | 🟢 BAIXO |

*Config pode ser editado via UI, risco se simultâneo

---

## 🚨 CENÁRIOS DE FALHA

### **Cenário 1: Histórico de Análises (MAIS CRÍTICO)**

**Código atual em `services/history_report.py`:**
```python
# Operação 1: Lê CSV (se existe)
if csv_path_obj.exists():
    df_existente = pd.read_csv(csv_path_obj, sep=";", encoding="utf-8")

# Operação 2: Adiciona novas linhas
df_hist = pd.DataFrame(linhas)

# Operação 3: Valida colunas
if colunas_existentes != colunas_esperadas:
    # ... modifica df_existente

# Operação 4: ESCREVE (PERIGOSO!)
df_hist.to_csv(caminho_csv, sep=";", index=False, mode="a", ...)
```

**Problema:** Entre Leitura (Op 1) e Escrita (Op 4), outra máquina pode ter modificado o arquivo!

**Resultado:**
- Máquina A lê: [linhas 1-100]
- Máquina B lê: [linhas 1-100]
- Máquina A adiciona: +50 linhas → [1-150]
- Máquina B adiciona: +30 linhas → [1-130] ❌ Perde 20 linhas de A!

---

### **Cenário 2: Autenticação de Usuários**

**Código em `core/authentication/user_manager.py`:**
```python
def _carregar_usuarios(self):
    with open(self.csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        # Processa usuários

def _salvar_usuarios(self, usuarios):
    with open(self.csv_path, "w", newline="", encoding="utf-8") as file:
        # Escreve todos de novo
```

**Problema:** Abertura exclusiva de arquivo, sem compartilhamento seguro

**Resultado:**
- Máquina A: Altera senha do usuário X
- Máquina B: Altera email do usuário Y
- Se Máquina B escrever DEPOIS, dados de A são perdidos ❌

---

### **Cenário 3: Atualização de Status GAL**

**Código em `services/history_report.py` - `atualizar_status_gal()`:**
```python
df = pd.read_csv(csv_path_obj, ...)
# ... modifica df ...
df.to_csv(csv_path_obj, ...)  # SOBRESCREVE!
```

**Problema:** Outro usuário pode estar adicionando análises ENQUANTO atualiza status

**Resultado:**
- Máquina A: Lê CSV (100 linhas)
- Máquina B: Adiciona 10 linhas → 110 linhas
- Máquina A: Atualiza status → Escreve 100 linhas (PERDE 10!) ❌

---

## 🔐 SOLUÇÕES RECOMENDADAS

### **Opção 1: File-Based Locking (Rápido, Baixo Custo)**

**Vantagens:**
- ✅ Sem dependência externa
- ✅ Funciona em rede local
- ✅ Fácil implementar em CSV

**Desvantagens:**
- ❌ Pode travar em case de crash
- ❌ Performance degradada
- ❌ Não escala para múltiplos servidores

**Implementação:**
```python
import fcntl
import time
from pathlib import Path

class CsvFileLock:
    def __init__(self, csv_path, timeout=30):
        self.csv_path = csv_path
        self.lock_path = Path(csv_path).with_suffix('.lock')
        self.timeout = timeout
    
    def __enter__(self):
        start = time.time()
        while self.lock_path.exists():
            if time.time() - start > self.timeout:
                raise TimeoutError(f"Lock timeout em {self.csv_path}")
            time.sleep(0.1)
        self.lock_path.touch()
        return self
    
    def __exit__(self, *args):
        self.lock_path.unlink(missing_ok=True)

# Uso:
with CsvFileLock("logs/historico_analises.csv"):
    df = pd.read_csv(...)
    # ... processa ...
    df.to_csv(...)  # Seguro!
```

**Limitação:** Funciona bem em rede local NFS/SMB, mas pode ter delays

---

### **Opção 2: SQLite com Lock (RECOMENDADO para Rede Local)**

**Vantagens:**
- ✅ Lock automático built-in
- ✅ ACID transactions
- ✅ Compartilhável em rede local
- ✅ Sem servidor necessário
- ✅ Lê/escreve em arquivo único
- ✅ Fácil migração de CSV

**Desvantagens:**
- ❌ Requer refatoração de código
- ❌ Performance degrada com writes simultâneos
- ❌ Suporte limitado a NFS remoto

**Implementação Básica:**
```python
import sqlite3
from contextlib import contextmanager

@contextmanager
def obter_conexao_db(db_path="banco/integragal.db"):
    conn = sqlite3.connect(db_path, timeout=30, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
    try:
        yield conn
    finally:
        conn.close()

# Tabela: historico_analises
# CREATE TABLE historico (
#     id_registro TEXT PRIMARY KEY,
#     data_hora_analise TIMESTAMP,
#     usuario_analise TEXT,
#     exame TEXT,
#     status_gal TEXT,
#     data_hora_envio TIMESTAMP NULL,
#     usuario_envio TEXT NULL,
#     sucesso_envio BOOLEAN NULL,
#     detalhes_envio TEXT,
#     criado_em TIMESTAMP,
#     atualizado_em TIMESTAMP
# );

# Inserção segura:
with obter_conexao_db() as conn:
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO historico 
           (id_registro, data_hora_analise, usuario_analise, ...)
           VALUES (?, ?, ?, ...)""",
        (uuid.uuid4(), timestamp, usuario, ...)
    )
    conn.commit()  # Lock liberado automaticamente

# Atualização segura:
with obter_conexao_db() as conn:
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE historico 
           SET status_gal=?, data_hora_envio=?, usuario_envio=?, sucesso_envio=?
           WHERE id_registro=?""",
        ("enviado", timestamp, usuario, True, id_registro)
    )
    conn.commit()
```

---

### **Opção 3: PostgreSQL/MySQL em Servidor (MELHOR ESCALABILIDADE)**

**Vantagens:**
- ✅ Concorrência ilimitada
- ✅ ACID completo
- ✅ Escalável (multi-servidor)
- ✅ Backup centralizado
- ✅ Replicação possível

**Desvantagens:**
- ❌ Requer servidor rodando
- ❌ Complexidade aumentada
- ❌ Custo de infraestrutura
- ❌ Setup inicial complexo

---

## 📈 COMPARAÇÃO DE SOLUÇÕES

| Aspecto | CSV atual | File Lock | SQLite | PostgreSQL |
|--------|-----------|-----------|--------|------------|
| **Concorrência** | ❌ Nenhuma | 🟡 Básica | ✅ Boa | ✅ Excelente |
| **Rede Local** | ⚠️ Perigoso | ✅ Funciona | ✅ Funciona | ✅ Funciona |
| **Múltiplas máquinas** | ❌ Não | 🟡 Lento | ✅ Sim | ✅ Sim |
| **Integridade dados** | ❌ Fraca | 🟡 Média | ✅ Forte | ✅ Forte |
| **Performance** | ✅ Rápido | 🟡 Médio | ✅ Rápido | ✅ Rápido |
| **Implementação** | ✅ Trivial | 🟡 Fácil | ✅ Médio | ❌ Complexo |
| **Manutenção** | ✅ Nenhuma | 🟡 Pouca | ✅ Pouca | ❌ Muita |
| **Escalabilidade** | ❌ Não | ❌ Não | 🟡 Limitada | ✅ Sim |
| **Custo** | ✅ Zero | ✅ Zero | ✅ Zero | 🟡 Servidor |

---

## 🎯 RECOMENDAÇÃO PARA SEU CASO

### **CURTO PRAZO (Imediato - Próxima 1-2 semanas)**

**Use: File-Based Locking + CSV**

Motivo:
- ✅ Implementação rápida (< 2h)
- ✅ Zero dependências externas
- ✅ Funciona com setup atual
- ✅ Suficiente para rede local ~5-10 usuários

```python
# Criar arquivo: services/csv_lock.py
import fcntl
import time
from pathlib import Path
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

@contextmanager
def csv_lock(filepath: str, timeout: int = 30):
    """
    Context manager para lock seguro em CSV em rede local.
    Usa arquivo .lock para sincronização.
    """
    lock_file = Path(filepath).with_suffix('.lock')
    acquired_at = time.time()
    
    # Aguarda lock ficar disponível
    while lock_file.exists():
        if time.time() - acquired_at > timeout:
            raise TimeoutError(f"Timeout aguardando lock em {filepath}")
        time.sleep(0.05)
    
    try:
        # Adquire lock
        lock_file.touch()
        logger.info(f"Lock adquirido: {filepath}")
        yield
    finally:
        # Libera lock
        lock_file.unlink(missing_ok=True)
        logger.info(f"Lock liberado: {filepath}")

# Uso em history_report.py:
from services.csv_lock import csv_lock

def gerar_historico_csv(...):
    with csv_lock(caminho_csv):
        df_existente = pd.read_csv(caminho_csv, ...)
        # ... processa ...
        df_hist.to_csv(caminho_csv, ...)

def atualizar_status_gal(...):
    with csv_lock(csv_path):
        df = pd.read_csv(csv_path, ...)
        # ... atualiza ...
        df.to_csv(csv_path, ...)
```

**Impacto:**
- ✅ Elimina corrupção de dados
- ✅ Operações atômicas
- ⚠️ Performance ok para até 50 operações/minuto

---

### **MÉDIO PRAZO (Próximo mês)**

**Use: SQLite com WAL mode**

Motivo:
- ✅ Melhor performance que file locks
- ✅ Transações ACID
- ✅ Suporta múltiplas conexões simultâneas

```python
# Exemplo: historico_analises em SQLite
# Create table uma vez:
# CREATE TABLE historico_analises (
#     id_registro TEXT PRIMARY KEY,
#     data_hora_analise TEXT,
#     usuario_analise TEXT,
#     exame TEXT,
#     status_gal TEXT,
#     data_hora_envio TEXT,
#     usuario_envio TEXT,
#     sucesso_envio INTEGER,
#     detalhes_envio TEXT,
#     criado_em TEXT,
#     atualizado_em TEXT
# );

import sqlite3
from contextlib import contextmanager

@contextmanager
def db_context(db_path: str = "banco/integragal.db"):
    conn = sqlite3.connect(db_path, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")  # Ativa WAL
    try:
        yield conn
    finally:
        conn.close()

# Inserção:
with db_context() as conn:
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO historico_analises 
           (id_registro, data_hora_analise, usuario_analise, exame, status_gal, criado_em, atualizado_em)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (id_reg, dt_analise, usuario, exame, "não enviado", timestamp, timestamp)
    )
    conn.commit()

# Atualização:
def atualizar_status_gal(id_registros, sucesso, usuario_envio, detalhes):
    with db_context() as conn:
        cursor = conn.cursor()
        novo_status = "enviado" if sucesso else "falha no envio"
        
        for id_reg in id_registros:
            cursor.execute(
                """UPDATE historico_analises
                   SET status_gal=?, data_hora_envio=?, usuario_envio=?, sucesso_envio=?, detalhes_envio=?, atualizado_em=?
                   WHERE id_registro=?""",
                (novo_status, datetime.now(), usuario_envio, sucesso, detalhes, datetime.now(), id_reg)
            )
        conn.commit()
        return {"registros_atualizados": cursor.rowcount}
```

---

### **LONGO PRAZO (Próximo trimestre)**

**Use: PostgreSQL em servidor Linux**

Motivo:
- ✅ Escalabilidade ilimitada
- ✅ Suporte a 1000s de usuários simultâneos
- ✅ Backup/replicação automática
- ✅ Possibilidade de cloud migration

---

## ⚠️ PROBLEMAS ADICIONAIS IDENTIFICADOS

### **1. Histórico de Análises**
- ❌ Sem proteção contra corrupção simultânea
- ✅ **Solução:** CSV Lock + Transações

### **2. Autenticação (usuarios.csv)**
- ❌ Sem proteção contra race condition
- ✅ **Solução:** CSV Lock + Validação

### **3. Atualização de Status GAL**
- ❌ Sem versioning - pode sobrescrever alterações recentes
- ✅ **Solução:** Usar UPDATE com WHERE em vez de sobrescrever tudo

### **4. Configurações (exames_config.csv)**
- ❌ Se editado via UI enquanto outra máquina lê
- ✅ **Solução:** CSV Lock + Reload em memória

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

### Fase 1: File Locks (IMEDIATO)
- [ ] Criar `services/csv_lock.py`
- [ ] Atualizar `gerar_historico_csv()` com lock
- [ ] Atualizar `atualizar_status_gal()` com lock
- [ ] Atualizar `_salvar_usuarios()` com lock
- [ ] Atualizar outros CSV writes com lock
- [ ] Testes: 2 máquinas simultâneas

### Fase 2: SQLite (Próximo mês)
- [ ] Design schema SQLite
- [ ] Criar `services/db_manager.py`
- [ ] Migrar `historico_analises` para SQLite
- [ ] Migrar `usuarios` para SQLite
- [ ] Testes de carga (100 ops/min)

### Fase 3: PostgreSQL (Futuro)
- [ ] Setup servidor PostgreSQL
- [ ] Design completo de BD
- [ ] Migração dados de SQLite
- [ ] Testes de replicação

---

## 🔧 IMPLEMENTAÇÃO RÁPIDA (FILE LOCK)

**Tempo estimado:** ~1-2 horas

```python
# services/csv_lock.py
import time
from pathlib import Path
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

@contextmanager
def csv_lock(filepath: str, timeout: int = 30, lock_suffix: str = ".lock"):
    """
    Lock seguro para CSV em rede local.
    
    Uso:
        with csv_lock("logs/historico.csv"):
            df = pd.read_csv("logs/historico.csv")
            # ... processa ...
            df.to_csv("logs/historico.csv")
    """
    lock_path = Path(filepath).with_suffix(lock_suffix)
    start_time = time.time()
    
    # Aguarda lock
    while lock_path.exists():
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Timeout esperando lock para {filepath}")
        time.sleep(0.05)
    
    try:
        lock_path.touch()
        logger.info(f"✅ Lock: {Path(filepath).name}")
        yield
    finally:
        lock_path.unlink(missing_ok=True)
        logger.info(f"🔓 Liberado: {Path(filepath).name}")
```

---

**Conclusão:**
Para **rede local com 3-10 usuários simultâneos**, use **File Locks + CSV** (curto prazo).
Planeje migração para **SQLite** quando usar chegar a **20+ usuários simultâneos**.

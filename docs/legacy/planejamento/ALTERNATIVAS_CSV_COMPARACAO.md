# 🗄️ ALTERNATIVAS PARA CSV (Além de PostgreSQL)

## 📊 COMPARAÇÃO COMPLETA DE SOLUÇÕES

| Solução | Escalabilidade | Concorrência | Performance | Setup | Custo | Recomendação |
|---------|----------------|--------------|-------------|-------|-------|--------------|
| **CSV + Lock** | 🟢 ~10 usuários | 🟡 Básica | 🟡 Lento | 🟢 1-2h | 💰 $0 | ✅ **Agora** |
| **SQLite** | 🟡 ~50 usuários | 🟡 Boa | 🟢 Rápido | 🟡 2-4h | 💰 $0 | ✅ **Próx mês** |
| **SQLite + Pool** | 🟡 ~100 usuários | 🟢 Excelente | 🟢 Rápido | 🔴 6-8h | 💰 $0 | 🟡 Complexo |
| **MongoDB** | 🟢 Ilimitada | 🟢 Excelente | 🟢 Rápido | 🟡 4-6h | 💰 Grátis/Pago | 🔴 Cloud |
| **PostgreSQL** | 🟢 Ilimitada | 🟢 Excelente | 🟢 Rápido | 🔴 8-16h | 💰 $0-$$ | ✅ **Futuro** |
| **MySQL** | 🟢 Ilimitada | 🟢 Excelente | 🟢 Rápido | 🔴 8-16h | 💰 $0-$$ | 🟡 Similar PG |
| **MariaDB** | 🟢 Ilimitada | 🟢 Excelente | 🟢 Rápido | 🔴 8-16h | 💰 $0 | 🟡 Similar PG |

---

## 1️⃣ **SQLite (RECOMENDADO - Curto/Médio Prazo)**

### 🎯 O QUE É?
Banco de dados **SQL embutido** (não precisa servidor separado)
- ✅ Um arquivo único (`banco.db`)
- ✅ Acesso multi-processo/máquina
- ✅ Transações ACID
- ✅ Sem servidor externo
- ✅ Zero configuração

### ✅ VANTAGENS

```
1. IMPLEMENTAÇÃO
   ├─ Usa Python nativo (sqlite3)
   ├─ Sem dependências externas
   ├─ Documentação excelente
   └─ Comunidade grande

2. PERFORMANCE
   ├─ Leitura: 10-50x mais rápido que CSV Lock
   ├─ Escrita: 5-10x mais rápido que CSV Lock
   ├─ Sem overhead de lock
   └─ Índices para busca rápida

3. ESCALABILIDADE
   ├─ Até ~50 usuários simultâneos
   ├─ Até ~1 milhão de registros
   ├─ Até ~100GB de dados
   └─ Suficiente para 5 anos de dados

4. SEGURANÇA
   ├─ Transações ACID
   ├─ Foreign keys
   ├─ Constraints
   └─ Backup simples (copiar .db)

5. CUSTO
   ├─ $0 (código aberto)
   ├─ Sem licença
   ├─ Sem servidor
   └─ Sem manutenção
```

### ❌ DESVANTAGENS

```
1. SCALABILIDADE LIMITADA
   ├─ Máximo ~100 conexões simultâneas
   ├─ Escreve sequencial (mais lento que PG)
   └─ Acima 50 usuários → considerar PG

2. REDE REMOTA
   ├─ Acesso remoto limitado
   ├─ NFS pode ter deadlock
   └─ Não é ideal para cloud

3. RECURSOS
   ├─ Usa lock em nível de arquivo
   ├─ Escreve ficam em fila
   └─ Pode travar com muitas escritas

4. ADMIN
   ├─ Sem user/senha nativo
   ├─ Sem replicação built-in
   └─ Backup manual (não automático)
```

### 📈 COMPARAÇÃO: CSV Lock vs SQLite

```
OPERAÇÃO: Adicionar 100 análises simultâneas

CSV Lock:
├─ Tempo: ~3.5 segundos (fila de 10 usuários)
├─ Throughput: 28 análises/seg
├─ Latência: 350ms por operação
└─ Status: Aceitável

SQLite:
├─ Tempo: ~1.2 segundos
├─ Throughput: 83 análises/seg
├─ Latência: 120ms por operação
└─ Status: Muito bom
```

### 💻 EXEMPLO DE USO

```python
# Instalação: já vem com Python

import sqlite3
from contextlib import contextmanager

@contextmanager
def db_connection(db_path="banco/integragal.db"):
    """Context manager para conexão segura"""
    conn = sqlite3.connect(db_path, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")  # Ativa WAL (melhor concorrência)
    try:
        yield conn
    finally:
        conn.close()

# Usar:
with db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO historico_analises 
           (id_registro, data_hora, usuario, status_gal)
           VALUES (?, ?, ?, ?)""",
        (uuid.uuid4(), datetime.now(), "joao", "não enviado")
    )
    conn.commit()

# Atualizar:
with db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE historico_analises
           SET status_gal=?, data_hora_envio=?, usuario_envio=?
           WHERE id_registro=?""",
        ("enviado", datetime.now(), "admin", id_registro)
    )
    conn.commit()
```

### 📋 QUANDO USAR SQLite

✅ Usar se:
- Você tem 10-50 usuários
- Máquina Linux/Windows com compartilhamento NFS/SMB
- Quer melhor performance que CSV Lock
- Quer transações ACID
- Não precisa de replicação
- Orçamento $0

❌ Não usar se:
- 100+ usuários simultâneos
- Precisa acesso remoto via Internet
- Precisa replicação/backup automático
- Múltiplos datacenters

---

## 2️⃣ **MongoDB (Sem Servidor - Alternativa Moderna)**

### 🎯 O QUE É?
Banco de dados **NoSQL** baseado em documentos JSON
- ✅ Pode rodar localmente ou cloud
- ✅ Escalável horizontalmente
- ✅ Sem schema rígido
- ✅ JSON como formato nativo

### ✅ VANTAGENS

```
1. FLEXIBILIDADE
   ├─ Sem schema fixo
   ├─ Campos opcionais
   ├─ Fácil adicionar campos novos
   └─ Perfeito para dados não-estruturados

2. ESCALABILIDADE
   ├─ Sharding automático
   ├─ Replicação built-in
   ├─ Ilimitado em quantidade de dados
   └─ Crescimento sem redesign

3. PERFORMANCE
   ├─ Otimizado para reads
   ├─ Escrita rápida
   ├─ Índices eficientes
   └─ Aggregation pipeline

4. CLOUD
   ├─ MongoDB Atlas (serverless)
   ├─ Sem manutenção de servidor
   ├─ Backup automático
   └─ Replicação automática

5. DESENVOLVIMENTO
   ├─ Python driver excelente
   ├─ Comunidade grande
   └─ Muitos exemplos
```

### ❌ DESVANTAGENS

```
1. COMPLEXIDADE
   ├─ Sem transações ACID nativas (MongoDB 4.0+ tem)
   ├─ Sem foreign keys
   ├─ Denormalização necessária
   └─ Aprendizado mais alto

2. ARMAZENAMENTO
   ├─ JSON ocupa mais espaço
   ├─ Overhead de estrutura
   └─ Arquivo .db maior que SQL

3. CONSISTÊNCIA
   ├─ Eventual consistency no cluster
   ├─ Pode ter dados desincronizados
   └─ Precisa cuidado em concorrência

4. CUSTO
   ├─ MongoDB Atlas: $0-$999+/mês
   ├─ Self-hosted: máquina própria
   └─ Não é tão cheap quanto SQLite

5. TOOLING
   ├─ Menos ferramentas GUI
   ├─ Backup mais complexo
   └─ Admin manual
```

### 💻 EXEMPLO DE USO

```python
from pymongo import MongoClient

# Conexão local ou cloud
client = MongoClient("mongodb://localhost:27017")
# ou cloud: MongoClient("mongodb+srv://user:pass@cluster.mongodb.net/")

db = client["integragal"]
collection = db["historico_analises"]

# Inserir:
collection.insert_one({
    "_id": str(uuid.uuid4()),
    "data_hora_analise": datetime.now(),
    "usuario_analise": "joao",
    "exame": "VR1e2",
    "status_gal": "não enviado",
    "alvos": [
        {"nome": "EX200", "resultado": 1, "ct": 15.5},
        {"nome": "EX220", "resultado": 2, "ct": None}
    ]
})

# Atualizar:
collection.update_one(
    {"_id": id_registro},
    {"$set": {
        "status_gal": "enviado",
        "data_hora_envio": datetime.now(),
        "usuario_envio": "admin"
    }}
)

# Buscar:
registros = collection.find({"status_gal": "não enviado"})
```

### 📋 QUANDO USAR MONGODB

✅ Usar se:
- Dados não-estruturados ou semi-estruturados
- Precisa escalabilidade horizontal
- Quer cloud serverless (MongoDB Atlas)
- Flexibilidade no schema
- Crescimento exponencial esperado

❌ Não usar se:
- Orçamento muito limitado
- Precisa ACID garantido
- Dados estruturados (CSV natural)
- Quer administração mínima

---

## 3️⃣ **MariaDB / MySQL (Open-Source SQL)**

### 🎯 O QUE É?
Bancos de dados **SQL** full-featured
- ✅ Open-source (grátis)
- ✅ Similar PostgreSQL
- ✅ Escalável
- ✅ Transações ACID

### ✅ VANTAGENS

```
1. COMPATIBILIDADE
   ├─ Compatível com SQL padrão
   ├─ Mesmas queries PostgreSQL (80%)
   ├─ Fácil migração
   └─ Ferramenta amplo suporte

2. PERFORMANCE
   ├─ Rápido em leitura
   ├─ Índices eficientes
   ├─ Replicação nativa
   └─ Cluster possível

3. CUSTO
   ├─ $0 (open-source)
   ├─ Sem licença
   ├─ Comunidade grande
   └─ Suporte comunitário

4. FEATURES
   ├─ Transações ACID
   ├─ Foreign keys
   ├─ Stored procedures
   └─ Triggers
```

### ❌ DESVANTAGENS

```
1. SETUP
   ├─ Precisa servidor separado
   ├─ Mais complexo que SQLite
   ├─ Configuração necessária
   └─ Admin requerido

2. RECURSOS
   ├─ Usa mais RAM que SQLite
   ├─ Overhead de processo
   ├─ Não é "embarcado"
   └─ Máquina dedicada recomendada

3. CONHECIMENTO
   ├─ Requer sysadmin
   ├─ Conhecimento SQL
   ├─ Troubleshooting complexo
   └─ Backup/restore manual

4. COMPARAÇÃO PG
   ├─ Menos features que PostgreSQL
   ├─ PostgreSQL é mais robusto
   └─ Use MariaDB se não quer PG
```

### 💻 EXEMPLO DE USO

```python
import mysql.connector

conn = mysql.connector.connect(
    host="192.168.1.100",
    user="integragal_user",
    password="senha_forte",
    database="integragal"
)

cursor = conn.cursor()

# Insertar:
cursor.execute(
    """INSERT INTO historico_analises 
       (id_registro, data_hora_analise, usuario_analise, exame, status_gal)
       VALUES (%s, %s, %s, %s, %s)""",
    (str(uuid.uuid4()), datetime.now(), "joao", "VR1e2", "não enviado")
)
conn.commit()

# Atualizar:
cursor.execute(
    """UPDATE historico_analises
       SET status_gal=%s, data_hora_envio=%s, usuario_envio=%s
       WHERE id_registro=%s""",
    ("enviado", datetime.now(), "admin", id_registro)
)
conn.commit()
```

### 📋 QUANDO USAR MARIADB/MYSQL

✅ Usar se:
- 50-500 usuários simultâneos
- Quer open-source tipo PostgreSQL
- Infraestrutura Linux/Windows disponível
- Admin com conhecimento BD
- Orçamento $0 (software)

❌ Não usar se:
- Quer simplicidade (use SQLite)
- Sem equipe admin
- PostgreSQL já é opção

---

## 4️⃣ **SQLite + Connection Pool (Avançado)**

### 🎯 O QUE É?
SQLite com **pool de conexões** para melhor concorrência
- ✅ Múltiplas conexões ao SQLite
- ✅ Gerenciador automático
- ✅ Até ~100 usuários
- ✅ Melhor que SQLite puro

### ✅ VANTAGENS

```
1. PERFORMANCE
   ├─ Até 3-5x mais rápido
   ├─ Menos contenção
   ├─ Parallelismo melhor
   └─ WAL mode otimizado

2. ESCALABILIDADE
   ├─ De 50 para ~100 usuários
   ├─ Ainda sem servidor externo
   ├─ Configuração simples
   └─ Custo $0

3. COMPATIBILIDADE
   ├─ Mesmas queries SQLite
   ├─ Sem mudanças grandes
   ├─ Transição suave CSV → SQLite Pool
   └─ Fácil upgrade depois

4. RESILÊNCIA
   ├─ Failover automático
   ├─ Reconexão automática
   ├─ Health checks
   └─ Logging detalhado
```

### ❌ DESVANTAGENS

```
1. COMPLEXIDADE
   ├─ Setup mais complexo
   ├─ Gerenciamento de conexões
   ├─ Debug mais difícil
   └─ Requer conhecimento pool

2. OVERHEAD
   ├─ Mais memória RAM
   ├─ Mais conexões abertas
   ├─ Sincronização adicional
   └─ CPU overhead

3. LIMITE
   ├─ Ainda máximo ~100 usuários
   ├─ Depois precisa PG
   └─ Solução temporária

4. APRENDIZADO
   ├─ Conceito de pool novo
   ├─ Debugging mais complexo
   ├─ Troubleshooting específico
   └─ Documentação espalhada
```

### 💻 EXEMPLO DE USO

```python
from sqlite3 import connect
import threading
from queue import Queue

class SQLiteConnectionPool:
    def __init__(self, db_path, pool_size=5, timeout=30):
        self.db_path = db_path
        self.pool = Queue(maxsize=pool_size)
        self.timeout = timeout
        
        # Pré-aloca conexões
        for _ in range(pool_size):
            conn = connect(db_path, timeout=timeout, check_same_thread=False)
            conn.execute("PRAGMA journal_mode=WAL")
            self.pool.put(conn)
    
    def get_connection(self):
        """Obtém conexão do pool"""
        return self.pool.get(timeout=self.timeout)
    
    def return_connection(self, conn):
        """Devolve conexão ao pool"""
        self.pool.put(conn)
    
    def close_all(self):
        """Fecha todas as conexões"""
        while not self.pool.empty():
            conn = self.pool.get()
            conn.close()

# Usar:
pool = SQLiteConnectionPool("banco.db", pool_size=10)

try:
    conn = pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ...")
    conn.commit()
finally:
    pool.return_connection(conn)
```

### 📋 QUANDO USAR SQLite Pool

✅ Usar se:
- 50-100 usuários simultâneos
- Quer performance melhor que SQLite puro
- Sem servidor externo
- Equipe Python competente
- Transição PostgreSQL não urgente

❌ Não usar se:
- Quer simplicidade (use SQLite base)
- 10-50 usuários (overkill)
- 100+ usuários (use PG)

---

## 5️⃣ **Redis (Cache + Sessões)**

### 🎯 O QUE É?
Banco de dados **em-memória** ultra-rápido
- ✅ Cache distribuído
- ✅ Ultra-rápido (microsegundos)
- ✅ Não é para dados primários
- ✅ Complementa outros BDs

### ✅ VANTAGENS

```
1. VELOCIDADE
   ├─ 1000x mais rápido que BD
   ├─ Microsegundos
   ├─ Real-time analytics
   └─ Cache perfeito

2. CASOS DE USO
   ├─ Sessões de usuário
   ├─ Cache de análises
   ├─ Queues de jobs
   ├─ Contadores real-time
   └─ Pub/Sub messaging

3. ESCALABILIDADE
   ├─ Cluster distribuído
   ├─ Replicação automática
   ├─ Crescimento horizontal
   └─ Ilimitado

4. SEGURANÇA
   ├─ Password auth
   ├─ SSL/TLS
   ├─ ACL por comando
   └─ Criptografia dados
```

### ❌ DESVANTAGENS

```
1. TIPO DE DADOS
   ├─ NÃO é para dados primários
   ├─ Dados em-memória = volátil
   ├─ Se cair, perde dados
   ├─ Precisa backup to BD

2. LIMITE DE TAMANHO
   ├─ Limitado à RAM disponível
   ├─ Típico: 64GB
   ├─ Caro expandir RAM
   └─ Não é para histórico grande

3. COMPLEXIDADE
   ├─ Precisa BD principal + Redis
   ├─ Sincronização necessária
   ├─ Invalidação de cache
   └─ Mais pontos de falha

4. NÃO É SUBSTITUTO
   ├─ Deve usar com CSV/SQLite/PG
   ├─ Não substitui BD relacional
   └─ Arquitetura mais complexa
```

### 💻 EXEMPLO DE USO

```python
import redis

# Conexão
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Cache de análise (válido 1 hora)
r.setex(f"analise:{id_registro}", 3600, json.dumps({
    "status": "processando",
    "progresso": 45
}))

# Obter
analise = json.loads(r.get(f"analise:{id_registro}"))

# Sessão de usuário
r.hset(f"sessao:{user_id}", mapping={
    "usuario": "joao",
    "login_em": datetime.now().isoformat(),
    "ip": "192.168.1.100"
})

# Obter dados sessão
sessao = r.hgetall(f"sessao:{user_id}")
```

### 📋 QUANDO USAR REDIS

✅ Usar se:
- Precisa cache ultra-rápido
- Gerenciar sessões de usuários
- Queue de jobs/tarefas
- Real-time analytics
- Complementando BD principal

❌ Não usar se:
- Para dados primários
- Sem BD relacional backup
- Dados devem ser duráveis
- Quer simplicidade

---

## 📊 MATRIZ DE DECISÃO

```
DECISÃO BASEADA EM CRITÉRIO:

1. QUANTO USUÁRIOS SIMULTÂNEOS?
   ├─ 1-10: CSV Lock + ✅ (agora)
   ├─ 10-50: SQLite ✅ (próximo mês)
   ├─ 50-100: SQLite Pool 🟡 (opcional)
   ├─ 100-500: MariaDB/PostgreSQL ✅ (depois)
   └─ 500+: PostgreSQL cluster (futuro)

2. QUAL ORÇAMENTO?
   ├─ $0: CSV Lock → SQLite → PostgreSQL
   ├─ $0-100/mês: MongoDB Atlas
   ├─ $100+/mês: Cloud managed (AWS RDS)
   └─ Custom: Self-hosted cualquer

3. QUAL INFRAESTRUTURA?
   ├─ Rede local: CSV Lock → SQLite → MariaDB
   ├─ Servidor próprio: SQLite → PostgreSQL
   ├─ Cloud: MongoDB Atlas → PostgreSQL AWS RDS
   └─ Híbrido: Redis Cache + BD principal

4. QUAL CONHECIMENTO TÉCNICO?
   ├─ Básico: CSV Lock → SQLite
   ├─ Intermediário: SQLite → SQLite Pool → MariaDB
   ├─ Avançado: PostgreSQL cluster → Redis
   └─ Expert: Arquitetura microservices

5. QUAL HORIZONTE DE TEMPO?
   ├─ Semana 1: CSV Lock ✅
   ├─ Mês 1: Migrar SQLite 🟡
   ├─ Trimestre 1: Avaliar PostgreSQL
   ├─ Ano 1: PostgreSQL cluster se 100+ usuários
   └─ Futuro: Microservices conforme crescer
```

---

## 🎯 ROADMAP RECOMENDADO

```
AGORA (Semana 1-2):
├─ Implementar CSV Lock
├─ Testar com 5-10 usuários
└─ Status: ✅ Funcionando

PRÓXIMO MÊS (Semana 3-6):
├─ Implementar SQLite
├─ Migrar dados CSV → SQLite
├─ Testar com 20-30 usuários
└─ Status: ✅ Performance melhor

PRÓXIMO TRIMESTRE (Mês 2-3):
├─ Avaliar carga
├─ Se >50 usuários: Considerar SQLite Pool
├─ Se <50 usuários: Continuar SQLite
└─ Status: 🟡 Avaliação

FINAL DO ANO (Mês 6+):
├─ Se 100+ usuários: Iniciar PostgreSQL
├─ Se 50-100 usuários: SQLite suficiente
├─ Se <50 usuários: SQLite ideal
└─ Status: 🟡 Decisão por demanda

FUTURO (Ano 2+):
├─ Se 500+ usuários: PostgreSQL cluster
├─ Se analytics: Adicionar Redis
├─ Se real-time: Adicionar WebSocket
└─ Status: 📈 Escala produção
```

---

## 💡 MINHA RECOMENDAÇÃO FINAL

### **Melhor estratégia (custo-benefício):**

```
FASE 1 (Imediato): CSV Lock ✅
├─ Tempo: 1-2 horas
├─ Custo: $0
├─ Usuários: ~10
└─ Reason: Rápido, sem dependências, funciona agora

FASE 2 (Próximo mês): SQLite ✅
├─ Tempo: 4-6 horas
├─ Custo: $0
├─ Usuários: ~50
├─ Reason: Melhor performance, ACID, escalável
└─ Migration: Simples (SQL similar)

FASE 3 (Se necessário): PostgreSQL ✅
├─ Tempo: 8-16 horas
├─ Custo: $0 (self-hosted) ou $20-500/mês (cloud)
├─ Usuários: Ilimitado
├─ Reason: Production-grade, cluster, backup
└─ Migration: Queries SQL quase idênticas

COMPLEMENTAR (Opcional): Redis 🟡
├─ Quando: Se >100 usuários
├─ Custo: $0 (self-hosted) ou $15+/mês (cloud)
├─ Uso: Cache + sessões
└─ Benefício: 10x performance em cache
```

### **Por que essa ordem:**

1. ✅ **CSV Lock primeiro** - Resolve problema HOJE sem overhead
2. ✅ **SQLite depois** - Melhor performance com zero custo
3. ✅ **PostgreSQL no final** - Apenas se realmente necessário

**Não pule etapas!** PostgreSQL é overkill para 10 usuários.

---

## 📋 PRÓXIMOS PASSOS

```
☐ 1. Implementar CSV Lock (esta semana)
☐ 2. Testar com múltiplas máquinas
☐ 3. Documentar em produção
☐ 4. Monitorar performance por 1 mês
☐ 5. Avaliar: Mais rápido necessário?
     ├─ SIM → Iniciar migração SQLite
     └─ NÃO → Continuar CSV Lock
☐ 6. Se necessário, migrar para SQLite
☐ 7. Monitorar por 6 meses
☐ 8. Se 100+ usuários → Planejar PostgreSQL
```

---

**Data:** 2025-12-07  
**Status:** ✅ Análise Completa  
**Recomendação:** CSV Lock (agora) → SQLite (próx mês) → PostgreSQL (futuro)

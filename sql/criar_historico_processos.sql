-- Criação da tabela para histórico de processos (análises, exportações, etc)
CREATE TABLE IF NOT EXISTS historico_processos (
    id SERIAL PRIMARY KEY,
    analista TEXT NOT NULL,
    exame TEXT NOT NULL,
    status TEXT NOT NULL,
    detalhes TEXT,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criação de uma tabela de log caso queira também armazenar os logs do sistema em banco (Opcional)
CREATE TABLE IF NOT EXISTS log_sistema (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acao TEXT NOT NULL,
    detalhes TEXT
);

-- Criação de uma tabela para armazenar configurações persistentes em banco (Opcional - pode expandir futuramente)
CREATE TABLE IF NOT EXISTS configuracoes (
    id SERIAL PRIMARY KEY,
    chave TEXT UNIQUE NOT NULL,
    valor TEXT
);

-- Exemplo: Registro de novos testes criados (se desejar versionar no futuro)
CREATE TABLE IF NOT EXISTS exames_personalizados (
    id SERIAL PRIMARY KEY,
    nome_exame TEXT NOT NULL,
    kit_codigo INTEGER NOT NULL,
    export_fields TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Script SQL para criar a tabela de sorteios da Mega Sena
-- Execute este script no seu banco PostgreSQL no Easypanel

-- Criar tabela de sorteios
CREATE TABLE IF NOT EXISTS sorteios_megasena (
    id SERIAL PRIMARY KEY,
    concurso INTEGER UNIQUE NOT NULL,
    data_sorteio DATE NOT NULL,
    dezena_1 INTEGER NOT NULL CHECK (dezena_1 >= 1 AND dezena_1 <= 60),
    dezena_2 INTEGER NOT NULL CHECK (dezena_2 >= 1 AND dezena_2 <= 60),
    dezena_3 INTEGER NOT NULL CHECK (dezena_3 >= 1 AND dezena_3 <= 60),
    dezena_4 INTEGER NOT NULL CHECK (dezena_4 >= 1 AND dezena_4 <= 60),
    dezena_5 INTEGER NOT NULL CHECK (dezena_5 >= 1 AND dezena_5 <= 60),
    dezena_6 INTEGER NOT NULL CHECK (dezena_6 >= 1 AND dezena_6 <= 60),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar índices para melhorar performance
CREATE INDEX idx_sorteios_concurso ON sorteios_megasena(concurso);
CREATE INDEX idx_sorteios_data ON sorteios_megasena(data_sorteio);

-- Criar função para atualizar timestamp automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Criar trigger para atualizar automaticamente o campo updated_at
CREATE TRIGGER update_sorteios_megasena_updated_at
BEFORE UPDATE ON sorteios_megasena
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Exemplo de inserção de dados (opcional - remover após testar)
INSERT INTO sorteios_megasena (concurso, data_sorteio, dezena_1, dezena_2, dezena_3, dezena_4, dezena_5, dezena_6)
VALUES 
    (1, '1996-03-11', 4, 5, 30, 33, 41, 52),
    (2, '1996-03-18', 9, 37, 39, 41, 43, 49),
    (3, '1996-03-25', 10, 11, 29, 30, 36, 47)
ON CONFLICT (concurso) DO NOTHING;

-- Verificar se a tabela foi criada corretamente
SELECT COUNT(*) as total_sorteios FROM sorteios_megasena;

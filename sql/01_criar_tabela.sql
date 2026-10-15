
CREATE TABLE IF NOT EXISTS leituras_temperatura (
    id_registro BIGSERIAL PRIMARY KEY,
    id_original TEXT,
    room_id TEXT,
    noted_date TIMESTAMP NOT NULL,
    temp INTEGER NOT NULL,
    local_leitura TEXT NOT NULL,
    data_leitura DATE NOT NULL,
    hora_leitura SMALLINT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_leituras_data
    ON leituras_temperatura (data_leitura);

CREATE INDEX IF NOT EXISTS idx_leituras_hora
    ON leituras_temperatura (hora_leitura);

CREATE INDEX IF NOT EXISTS idx_leituras_local
    ON leituras_temperatura (local_leitura);

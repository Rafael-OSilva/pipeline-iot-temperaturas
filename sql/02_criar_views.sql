
-- VIEW 1: Estatísticas de temperatura por classificação
CREATE OR REPLACE VIEW vw_temperatura_por_local AS
SELECT
    local_leitura,
    COUNT(*) AS total_leituras,
    ROUND(AVG(temp)::numeric, 2) AS temperatura_media,
    MIN(temp) AS temperatura_minima,
    MAX(temp) AS temperatura_maxima
FROM leituras_temperatura
GROUP BY local_leitura;


-- VIEW 2: Quantidade de leituras por hora
CREATE OR REPLACE VIEW vw_leituras_por_hora AS
SELECT
    hora_leitura,
    COUNT(*) AS total_leituras,
    ROUND(AVG(temp)::numeric, 2) AS temperatura_media
FROM leituras_temperatura
GROUP BY hora_leitura
ORDER BY hora_leitura;


-- VIEW 3: Temperaturas mínimas e máximas por dia
CREATE OR REPLACE VIEW vw_temperaturas_por_dia AS
SELECT
    data_leitura,
    COUNT(*) AS total_leituras,
    ROUND(AVG(temp)::numeric, 2) AS temperatura_media,
    MIN(temp) AS temperatura_minima,
    MAX(temp) AS temperatura_maxima
FROM leituras_temperatura
GROUP BY data_leitura
ORDER BY data_leitura;

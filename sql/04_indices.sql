-- =====================================================================
-- Arquivo 04: Índices — cada um responde a uma consulta real da oficina
-- (PK e UNIQUE já criam índices automaticamente: placa, chassi, cpf...)
-- A justificativa e a medição antes/depois estão em
-- evidencias/resultados/indices_antes_depois.csv
-- =====================================================================
SET search_path TO oficina;
CREATE EXTENSION IF NOT EXISTS pg_trgm SCHEMA public;

-- I1. Histórico do veículo (recepção digita a placa) -> OS do veículo, mais recentes primeiro
CREATE INDEX ix_os_veiculo_data   ON ordem_servico (id_veiculo, data_abertura DESC);

-- I2. Painel de OS pendentes: índice PARCIAL, só com as ~3 mil OS não finalizadas
CREATE INDEX ix_os_pendentes      ON ordem_servico (data_abertura)
       WHERE status IN ('ABERTA', 'EM_EXECUCAO', 'AGUARDANDO_PECA');

-- I3. Produtividade do mecânico por período
CREATE INDEX ix_os_mecanico_data  ON ordem_servico (id_mecanico, data_abertura);

-- I4. Faturamento por período (data de conclusão)
CREATE INDEX ix_os_conclusao      ON ordem_servico (data_conclusao);

-- I5. FK os_peca.id_peca: consumo de uma peça / exclusão de peça (a PK começa por id_os)
CREATE INDEX ix_os_peca_peca      ON os_peca (id_peca);

-- I6. FK veiculo.id_cliente: veículos de um cliente
CREATE INDEX ix_veiculo_cliente   ON veiculo (id_cliente);

-- I7. Busca de cliente por parte do nome (ILIKE '%...%') com trigramas
CREATE INDEX ix_cliente_nome_trgm ON cliente USING gin (nome public.gin_trgm_ops);

-- I8. (CONTRAEXEMPLO) índice em coluna de baixa seletividade — o teste mostra
--     que o otimizador o IGNORA para status = 'CONCLUIDA' (95% das linhas).
CREATE INDEX ix_os_status         ON ordem_servico (status);

ANALYZE;

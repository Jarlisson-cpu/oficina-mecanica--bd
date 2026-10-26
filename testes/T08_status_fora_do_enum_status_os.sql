-- T08 [Tipo] Status fora do ENUM status_os
-- Esperado: ERRO 22P02
UPDATE ordem_servico SET status = 'FINALIZADA' WHERE id_os = 1;

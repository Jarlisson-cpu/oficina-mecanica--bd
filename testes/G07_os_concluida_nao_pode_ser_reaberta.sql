-- G07 [Regra] OS CONCLUIDA não pode ser reaberta
-- Esperado: ERRO P0001
UPDATE ordem_servico SET status = 'ABERTA', data_conclusao = NULL
 WHERE id_os = (SELECT min(id_os) FROM ordem_servico WHERE status = 'CONCLUIDA');

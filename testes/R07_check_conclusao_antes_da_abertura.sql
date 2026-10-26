-- R07 [Restrição] CHECK: conclusão antes da abertura
-- Esperado: ERRO 23514
UPDATE ordem_servico SET data_conclusao = data_abertura - INTERVAL '1 day'
 WHERE id_os = (SELECT min(id_os) FROM ordem_servico WHERE status = 'CONCLUIDA');

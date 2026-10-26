-- R09 [Restrição] CHECK: desconto maior que a mão de obra
-- Esperado: ERRO 23514
UPDATE ordem_servico SET desconto = valor_mao_obra + 1
 WHERE id_os = (SELECT min(id_os) FROM ordem_servico WHERE status = 'CONCLUIDA');

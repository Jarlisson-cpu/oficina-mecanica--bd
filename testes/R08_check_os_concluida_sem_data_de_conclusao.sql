-- R08 [Restrição] CHECK: OS CONCLUIDA sem data de conclusão
-- Esperado: ERRO 23514
INSERT INTO ordem_servico (id_veiculo, id_mecanico, km_entrada, descricao_problema)
VALUES (1, 1, (SELECT km_atual + 500 FROM veiculo WHERE id_veiculo = 1), 'Teste de bancada')
RETURNING id_os AS os \gset
UPDATE ordem_servico SET status = 'CONCLUIDA' WHERE id_os = :os;

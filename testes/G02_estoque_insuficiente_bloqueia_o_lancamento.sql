-- G02 [Regra] Estoque insuficiente bloqueia o lançamento
-- Esperado: ERRO 23514
INSERT INTO ordem_servico (id_veiculo, id_mecanico, km_entrada, descricao_problema)
VALUES (1, 1, (SELECT km_atual + 500 FROM veiculo WHERE id_veiculo = 1), 'Teste de bancada')
RETURNING id_os AS os \gset
UPDATE peca SET qtd_estoque = 1 WHERE id_peca = 20;
INSERT INTO os_peca (id_os, id_peca, quantidade) VALUES (:os, 20, 3);

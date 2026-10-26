-- G01 [Regra] Lançar peça na OS baixa o estoque automaticamente
-- Esperado: OK
SELECT qtd_estoque AS estoque_antes FROM peca WHERE id_peca = 20 \gset
INSERT INTO ordem_servico (id_veiculo, id_mecanico, km_entrada, descricao_problema)
VALUES (1, 1, (SELECT km_atual + 500 FROM veiculo WHERE id_veiculo = 1), 'Teste de bancada')
RETURNING id_os AS os \gset
INSERT INTO os_peca (id_os, id_peca, quantidade) VALUES (:os, 20, 2);
SELECT :estoque_antes AS antes, qtd_estoque AS depois,
       CASE WHEN qtd_estoque = :estoque_antes - 2 THEN 'PASSOU' ELSE 'FALHOU' END AS verificacao
  FROM peca WHERE id_peca = 20;

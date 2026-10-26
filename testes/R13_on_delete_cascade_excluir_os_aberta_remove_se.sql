-- R13 [Restrição] ON DELETE CASCADE: excluir OS aberta remove seus itens
-- Esperado: OK
INSERT INTO ordem_servico (id_veiculo, id_mecanico, km_entrada, descricao_problema)
VALUES (1, 1, (SELECT km_atual + 500 FROM veiculo WHERE id_veiculo = 1), 'Teste de bancada')
RETURNING id_os AS os \gset
INSERT INTO os_peca (id_os, id_peca, quantidade) VALUES (:os, 10, 1), (:os, 11, 2);
SELECT count(*) AS itens_antes FROM os_peca WHERE id_os = :os;
DELETE FROM ordem_servico WHERE id_os = :os;
SELECT count(*) AS itens_depois,
       CASE WHEN count(*) = 0 THEN 'PASSOU' ELSE 'FALHOU' END AS verificacao
  FROM os_peca WHERE id_os = :os;

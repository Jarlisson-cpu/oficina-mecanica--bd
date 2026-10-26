-- R10 [Restrição] PRIMARY KEY composta: mesma peça duas vezes na OS
-- Esperado: ERRO 23505
INSERT INTO ordem_servico (id_veiculo, id_mecanico, km_entrada, descricao_problema)
VALUES (1, 1, (SELECT km_atual + 500 FROM veiculo WHERE id_veiculo = 1), 'Teste de bancada')
RETURNING id_os AS os \gset
INSERT INTO os_peca (id_os, id_peca, quantidade) VALUES (:os, 10, 1);
INSERT INTO os_peca (id_os, id_peca, quantidade) VALUES (:os, 10, 1);

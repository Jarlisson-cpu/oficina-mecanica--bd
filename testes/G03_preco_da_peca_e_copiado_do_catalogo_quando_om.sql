-- G03 [Regra] Preço da peça é copiado do catálogo quando omitido
-- Esperado: OK
INSERT INTO ordem_servico (id_veiculo, id_mecanico, km_entrada, descricao_problema)
VALUES (1, 1, (SELECT km_atual + 500 FROM veiculo WHERE id_veiculo = 1), 'Teste de bancada')
RETURNING id_os AS os \gset
INSERT INTO os_peca (id_os, id_peca, quantidade) VALUES (:os, 30, 1);
SELECT op.preco_unitario, p.preco_venda,
       CASE WHEN op.preco_unitario = p.preco_venda THEN 'PASSOU' ELSE 'FALHOU' END AS verificacao
  FROM os_peca op JOIN peca p USING (id_peca) WHERE op.id_os = :os;

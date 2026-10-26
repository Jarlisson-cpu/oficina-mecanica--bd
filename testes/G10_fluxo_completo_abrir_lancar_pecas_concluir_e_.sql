-- G10 [Regra] Fluxo completo: abrir, lançar peças, concluir e faturar
-- Esperado: OK
INSERT INTO ordem_servico (id_veiculo, id_mecanico, km_entrada, descricao_problema)
VALUES (1, 1, (SELECT km_atual + 500 FROM veiculo WHERE id_veiculo = 1), 'Teste de bancada')
RETURNING id_os AS os \gset
INSERT INTO os_peca (id_os, id_peca, quantidade, preco_unitario) VALUES (:os, 50, 2, 100.00), (:os, 51, 1, 45.90);
UPDATE ordem_servico SET horas_trabalhadas = 1.5, status = 'EM_EXECUCAO' WHERE id_os = :os;
UPDATE ordem_servico SET desconto = 10, status = 'CONCLUIDA', data_conclusao = now() WHERE id_os = :os;
SELECT id_os, status, total_pecas, valor_mao_obra, desconto, valor_total,
       CASE WHEN valor_total = 245.90 + valor_mao_obra - 10 THEN 'PASSOU' ELSE 'FALHOU' END AS verificacao
  FROM vw_os_total WHERE id_os = :os;

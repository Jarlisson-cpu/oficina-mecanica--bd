-- G09 [Regra] Mão de obra = horas trabalhadas x valor/hora do mecânico
-- Esperado: OK
INSERT INTO ordem_servico (id_veiculo, id_mecanico, km_entrada, descricao_problema)
VALUES (1, 1, (SELECT km_atual + 500 FROM veiculo WHERE id_veiculo = 1), 'Teste de bancada')
RETURNING id_os AS os \gset
UPDATE ordem_servico SET horas_trabalhadas = 2.5 WHERE id_os = :os;
SELECT os.horas_trabalhadas, m.valor_hora, os.valor_mao_obra,
       CASE WHEN os.valor_mao_obra = 2.5 * m.valor_hora THEN 'PASSOU' ELSE 'FALHOU' END AS verificacao
  FROM ordem_servico os JOIN mecanico m USING (id_mecanico) WHERE os.id_os = :os;

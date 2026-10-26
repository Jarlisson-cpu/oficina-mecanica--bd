-- G05 [Regra] Mecânico inativo não pode assumir OS
-- Esperado: ERRO P0001
INSERT INTO ordem_servico (id_veiculo, id_mecanico, km_entrada, descricao_problema)
VALUES (1, (SELECT min(id_mecanico) FROM mecanico WHERE NOT ativo),
        (SELECT km_atual + 10 FROM veiculo WHERE id_veiculo = 1), 'Revisão geral');

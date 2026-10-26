-- G06 [Regra] Hodômetro não pode voltar (km_entrada < km_atual)
-- Esperado: ERRO P0001
INSERT INTO ordem_servico (id_veiculo, id_mecanico, km_entrada, descricao_problema)
VALUES (1, 1, (SELECT km_atual - 1000 FROM veiculo WHERE id_veiculo = 1), 'Revisão geral');

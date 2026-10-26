-- R06 [Restrição] CHECK: km do veículo negativo
-- Esperado: ERRO 23514
UPDATE veiculo SET km_atual = -10 WHERE id_veiculo = 1;

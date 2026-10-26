-- R03 [Restrição] UNIQUE: placa repetida
-- Esperado: ERRO 23505
INSERT INTO veiculo (id_cliente, placa, chassi, marca, modelo, ano)
SELECT 2, placa, '9BWZZZ00000099906', 'Fiat', 'Uno', 2015 FROM veiculo WHERE id_veiculo = 1;

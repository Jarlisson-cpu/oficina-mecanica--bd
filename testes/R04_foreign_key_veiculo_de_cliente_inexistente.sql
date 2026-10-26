-- R04 [Restrição] FOREIGN KEY: veículo de cliente inexistente
-- Esperado: ERRO 23503
INSERT INTO veiculo (id_cliente, placa, chassi, marca, modelo, ano)
VALUES (999999, 'ZZZ9Z99', '9BWZZZ00000099907', 'Fiat', 'Uno', 2015);

-- T04 [Tipo] Texto em coluna SMALLINT (ano)
-- Esperado: ERRO 22P02
INSERT INTO veiculo (id_cliente, placa, chassi, marca, modelo, ano)
VALUES (1, 'QWE1234', '9BWZZZ00000099904', 'Fiat', 'Uno', 'dois mil');

-- T01 [Tipo] Placa com 8 caracteres não cabe em CHAR(7)
-- Esperado: ERRO 22001
INSERT INTO veiculo (id_cliente, placa, chassi, marca, modelo, ano)
VALUES (1, 'ABC12345', '9BWZZZ00000099901', 'Fiat', 'Uno', 2015);

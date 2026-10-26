-- T05 [Tipo] Ano 40000 estoura o limite de SMALLINT
-- Esperado: ERRO 22003
INSERT INTO veiculo (id_cliente, placa, chassi, marca, modelo, ano)
VALUES (1, 'QWE1235', '9BWZZZ00000099905', 'Fiat', 'Uno', 40000);

-- T02 [Tipo] Placa fora do padrão (domínio dm_placa)
-- Esperado: ERRO 23514
INSERT INTO veiculo (id_cliente, placa, chassi, marca, modelo, ano)
VALUES (1, 'AB-1234', '9BWZZZ00000099902', 'Fiat', 'Uno', 2015);

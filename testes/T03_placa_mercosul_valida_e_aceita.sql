-- T03 [Tipo] Placa Mercosul válida é aceita
-- Esperado: OK
INSERT INTO veiculo (id_cliente, placa, chassi, marca, modelo, ano)
VALUES (1, 'RIO2A18', '9BWZZZ00000099903', 'Fiat', 'Uno', 2015);
SELECT CASE WHEN count(*) = 1 THEN 'PASSOU' ELSE 'FALHOU' END AS verificacao
  FROM veiculo WHERE placa = 'RIO2A18';

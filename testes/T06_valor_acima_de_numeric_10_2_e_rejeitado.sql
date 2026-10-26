-- T06 [Tipo] Valor acima de NUMERIC(10,2) é rejeitado
-- Esperado: ERRO 22003
UPDATE peca SET preco_venda = 123456789.00 WHERE id_peca = 1;

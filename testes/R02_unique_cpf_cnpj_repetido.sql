-- R02 [Restrição] UNIQUE: CPF/CNPJ repetido
-- Esperado: ERRO 23505
INSERT INTO cliente (nome, cpf_cnpj, telefone)
SELECT 'Clone do cliente 1', cpf_cnpj, '79999990000' FROM cliente WHERE id_cliente = 1;

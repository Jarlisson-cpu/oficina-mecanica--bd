-- R01 [Restrição] NOT NULL: cliente sem nome
-- Esperado: ERRO 23502
INSERT INTO cliente (nome, cpf_cnpj, telefone)
VALUES (NULL, '98765432100', '79999990000');

-- T11 [Tipo] Telefone com letras viola o domínio dm_telefone
-- Esperado: ERRO 23514
INSERT INTO cliente (nome, cpf_cnpj, telefone)
VALUES ('Maria Teste', '98765432100', '79-ABC-0000');

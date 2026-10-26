-- T10 [Tipo] CPF com pontuação viola o domínio dm_doc
-- Esperado: ERRO 23514
INSERT INTO cliente (nome, cpf_cnpj, telefone)
VALUES ('Maria Teste', '123.456.789-0', '79999990000');

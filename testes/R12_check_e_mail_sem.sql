-- R12 [Restrição] CHECK: e-mail sem @
-- Esperado: ERRO 23514
UPDATE cliente SET email = 'cliente.email.com' WHERE id_cliente = 1;

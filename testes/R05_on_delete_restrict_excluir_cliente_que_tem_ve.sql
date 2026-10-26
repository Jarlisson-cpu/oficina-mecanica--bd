-- R05 [Restrição] ON DELETE RESTRICT: excluir cliente que tem veículos
-- Esperado: ERRO 23503
DELETE FROM cliente WHERE id_cliente = 1;

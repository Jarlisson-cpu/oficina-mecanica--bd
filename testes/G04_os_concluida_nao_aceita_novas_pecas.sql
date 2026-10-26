-- G04 [Regra] OS CONCLUIDA não aceita novas peças
-- Esperado: ERRO P0001
INSERT INTO os_peca (id_os, id_peca, quantidade)
VALUES ((SELECT min(id_os) FROM ordem_servico WHERE status = 'CONCLUIDA'), 499, 1);

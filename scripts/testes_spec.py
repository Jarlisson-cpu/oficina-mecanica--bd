"""Especificação dos testes de TIPOS, RESTRIÇÕES e REGRAS (triggers).

Cada teste vira um arquivo testes/<ID>_<slug>.sql e é executado pelo
scripts/executar_testes.py dentro de BEGIN ... ROLLBACK (o banco volta
ao estado original depois de cada teste).

esperado = "ERRO <SQLSTATE>"  -> o banco PRECISA rejeitar o comando
esperado = "OK"               -> o comando passa e a última consulta
                                 precisa devolver 'PASSOU'
"""

# Abre uma OS nova (status ABERTA) no veículo 1 e guarda o id em :os
NOVA_OS = """INSERT INTO ordem_servico (id_veiculo, id_mecanico, km_entrada, descricao_problema)
VALUES (1, 1, (SELECT km_atual + 500 FROM veiculo WHERE id_veiculo = 1), 'Teste de bancada')
RETURNING id_os AS os \\gset"""

TESTES = [
    # ------------------------------------------------------------ TIPOS
    ("T01", "Tipo", "Placa com 8 caracteres não cabe em CHAR(7)", "ERRO 22001",
     "INSERT INTO veiculo (id_cliente, placa, chassi, marca, modelo, ano)\n"
     "VALUES (1, 'ABC12345', '9BWZZZ00000099901', 'Fiat', 'Uno', 2015);"),
    ("T02", "Tipo", "Placa fora do padrão (domínio dm_placa)", "ERRO 23514",
     "INSERT INTO veiculo (id_cliente, placa, chassi, marca, modelo, ano)\n"
     "VALUES (1, 'AB-1234', '9BWZZZ00000099902', 'Fiat', 'Uno', 2015);"),
    ("T03", "Tipo", "Placa Mercosul válida é aceita", "OK",
     "INSERT INTO veiculo (id_cliente, placa, chassi, marca, modelo, ano)\n"
     "VALUES (1, 'RIO2A18', '9BWZZZ00000099903', 'Fiat', 'Uno', 2015);\n"
     "SELECT CASE WHEN count(*) = 1 THEN 'PASSOU' ELSE 'FALHOU' END AS verificacao\n"
     "  FROM veiculo WHERE placa = 'RIO2A18';"),
    ("T04", "Tipo", "Texto em coluna SMALLINT (ano)", "ERRO 22P02",
     "INSERT INTO veiculo (id_cliente, placa, chassi, marca, modelo, ano)\n"
     "VALUES (1, 'QWE1234', '9BWZZZ00000099904', 'Fiat', 'Uno', 'dois mil');"),
    ("T05", "Tipo", "Ano 40000 estoura o limite de SMALLINT", "ERRO 22003",
     "INSERT INTO veiculo (id_cliente, placa, chassi, marca, modelo, ano)\n"
     "VALUES (1, 'QWE1235', '9BWZZZ00000099905', 'Fiat', 'Uno', 40000);"),
    ("T06", "Tipo", "Valor acima de NUMERIC(10,2) é rejeitado", "ERRO 22003",
     "UPDATE peca SET preco_venda = 123456789.00 WHERE id_peca = 1;"),
    ("T07", "Tipo", "NUMERIC(10,2) arredonda 10,555 para 10,56 (sem erro de ponto flutuante)", "OK",
     "UPDATE peca SET preco_venda = 10.555 WHERE id_peca = 1;\n"
     "SELECT preco_venda,\n"
     "       0.1::float8 + 0.2::float8 AS soma_float,\n"
     "       0.1::numeric + 0.2::numeric AS soma_numeric,\n"
     "       CASE WHEN preco_venda = 10.56 AND 0.1::numeric + 0.2 = 0.3 THEN 'PASSOU' ELSE 'FALHOU' END AS verificacao\n"
     "  FROM peca WHERE id_peca = 1;"),
    ("T08", "Tipo", "Status fora do ENUM status_os", "ERRO 22P02",
     "UPDATE ordem_servico SET status = 'FINALIZADA' WHERE id_os = 1;"),
    ("T09", "Tipo", "Data inexistente (30/02) em TIMESTAMP", "ERRO 22008",
     "UPDATE ordem_servico SET data_abertura = '2026-02-30 10:00' WHERE id_os = 1;"),
    ("T10", "Tipo", "CPF com pontuação viola o domínio dm_doc", "ERRO 23514",
     "INSERT INTO cliente (nome, cpf_cnpj, telefone)\n"
     "VALUES ('Maria Teste', '123.456.789-0', '79999990000');"),
    ("T11", "Tipo", "Telefone com letras viola o domínio dm_telefone", "ERRO 23514",
     "INSERT INTO cliente (nome, cpf_cnpj, telefone)\n"
     "VALUES ('Maria Teste', '98765432100', '79-ABC-0000');"),

    # ------------------------------------------------------- RESTRIÇÕES
    ("R01", "Restrição", "NOT NULL: cliente sem nome", "ERRO 23502",
     "INSERT INTO cliente (nome, cpf_cnpj, telefone)\n"
     "VALUES (NULL, '98765432100', '79999990000');"),
    ("R02", "Restrição", "UNIQUE: CPF/CNPJ repetido", "ERRO 23505",
     "INSERT INTO cliente (nome, cpf_cnpj, telefone)\n"
     "SELECT 'Clone do cliente 1', cpf_cnpj, '79999990000' FROM cliente WHERE id_cliente = 1;"),
    ("R03", "Restrição", "UNIQUE: placa repetida", "ERRO 23505",
     "INSERT INTO veiculo (id_cliente, placa, chassi, marca, modelo, ano)\n"
     "SELECT 2, placa, '9BWZZZ00000099906', 'Fiat', 'Uno', 2015 FROM veiculo WHERE id_veiculo = 1;"),
    ("R04", "Restrição", "FOREIGN KEY: veículo de cliente inexistente", "ERRO 23503",
     "INSERT INTO veiculo (id_cliente, placa, chassi, marca, modelo, ano)\n"
     "VALUES (999999, 'ZZZ9Z99', '9BWZZZ00000099907', 'Fiat', 'Uno', 2015);"),
    ("R05", "Restrição", "ON DELETE RESTRICT: excluir cliente que tem veículos", "ERRO 23503",
     "DELETE FROM cliente WHERE id_cliente = 1;"),
    ("R06", "Restrição", "CHECK: km do veículo negativo", "ERRO 23514",
     "UPDATE veiculo SET km_atual = -10 WHERE id_veiculo = 1;"),
    ("R07", "Restrição", "CHECK: conclusão antes da abertura", "ERRO 23514",
     "UPDATE ordem_servico SET data_conclusao = data_abertura - INTERVAL '1 day'\n"
     " WHERE id_os = (SELECT min(id_os) FROM ordem_servico WHERE status = 'CONCLUIDA');"),
    ("R08", "Restrição", "CHECK: OS CONCLUIDA sem data de conclusão", "ERRO 23514",
     NOVA_OS + "\nUPDATE ordem_servico SET status = 'CONCLUIDA' WHERE id_os = :os;"),
    ("R09", "Restrição", "CHECK: desconto maior que a mão de obra", "ERRO 23514",
     "UPDATE ordem_servico SET desconto = valor_mao_obra + 1\n"
     " WHERE id_os = (SELECT min(id_os) FROM ordem_servico WHERE status = 'CONCLUIDA');"),
    ("R10", "Restrição", "PRIMARY KEY composta: mesma peça duas vezes na OS", "ERRO 23505",
     NOVA_OS + "\nINSERT INTO os_peca (id_os, id_peca, quantidade) VALUES (:os, 10, 1);\n"
     "INSERT INTO os_peca (id_os, id_peca, quantidade) VALUES (:os, 10, 1);"),
    ("R11", "Restrição", "CHECK: quantidade zero de peça", "ERRO 23514",
     NOVA_OS + "\nINSERT INTO os_peca (id_os, id_peca, quantidade) VALUES (:os, 10, 0);"),
    ("R12", "Restrição", "CHECK: e-mail sem @", "ERRO 23514",
     "UPDATE cliente SET email = 'cliente.email.com' WHERE id_cliente = 1;"),
    ("R13", "Restrição", "ON DELETE CASCADE: excluir OS aberta remove seus itens", "OK",
     NOVA_OS + "\nINSERT INTO os_peca (id_os, id_peca, quantidade) VALUES (:os, 10, 1), (:os, 11, 2);\n"
     "SELECT count(*) AS itens_antes FROM os_peca WHERE id_os = :os;\n"
     "DELETE FROM ordem_servico WHERE id_os = :os;\n"
     "SELECT count(*) AS itens_depois,\n"
     "       CASE WHEN count(*) = 0 THEN 'PASSOU' ELSE 'FALHOU' END AS verificacao\n"
     "  FROM os_peca WHERE id_os = :os;"),

    # ------------------------------------------------ REGRAS (TRIGGERS)
    ("G01", "Regra", "Lançar peça na OS baixa o estoque automaticamente", "OK",
     "SELECT qtd_estoque AS estoque_antes FROM peca WHERE id_peca = 20 \\gset\n"
     + NOVA_OS + "\nINSERT INTO os_peca (id_os, id_peca, quantidade) VALUES (:os, 20, 2);\n"
     "SELECT :estoque_antes AS antes, qtd_estoque AS depois,\n"
     "       CASE WHEN qtd_estoque = :estoque_antes - 2 THEN 'PASSOU' ELSE 'FALHOU' END AS verificacao\n"
     "  FROM peca WHERE id_peca = 20;"),
    ("G02", "Regra", "Estoque insuficiente bloqueia o lançamento", "ERRO 23514",
     NOVA_OS + "\nUPDATE peca SET qtd_estoque = 1 WHERE id_peca = 20;\n"
     "INSERT INTO os_peca (id_os, id_peca, quantidade) VALUES (:os, 20, 3);"),
    ("G03", "Regra", "Preço da peça é copiado do catálogo quando omitido", "OK",
     NOVA_OS + "\nINSERT INTO os_peca (id_os, id_peca, quantidade) VALUES (:os, 30, 1);\n"
     "SELECT op.preco_unitario, p.preco_venda,\n"
     "       CASE WHEN op.preco_unitario = p.preco_venda THEN 'PASSOU' ELSE 'FALHOU' END AS verificacao\n"
     "  FROM os_peca op JOIN peca p USING (id_peca) WHERE op.id_os = :os;"),
    ("G04", "Regra", "OS CONCLUIDA não aceita novas peças", "ERRO P0001",
     "INSERT INTO os_peca (id_os, id_peca, quantidade)\n"
     "VALUES ((SELECT min(id_os) FROM ordem_servico WHERE status = 'CONCLUIDA'), 499, 1);"),
    ("G05", "Regra", "Mecânico inativo não pode assumir OS", "ERRO P0001",
     "INSERT INTO ordem_servico (id_veiculo, id_mecanico, km_entrada, descricao_problema)\n"
     "VALUES (1, (SELECT min(id_mecanico) FROM mecanico WHERE NOT ativo),\n"
     "        (SELECT km_atual + 10 FROM veiculo WHERE id_veiculo = 1), 'Revisão geral');"),
    ("G06", "Regra", "Hodômetro não pode voltar (km_entrada < km_atual)", "ERRO P0001",
     "INSERT INTO ordem_servico (id_veiculo, id_mecanico, km_entrada, descricao_problema)\n"
     "VALUES (1, 1, (SELECT km_atual - 1000 FROM veiculo WHERE id_veiculo = 1), 'Revisão geral');"),
    ("G07", "Regra", "OS CONCLUIDA não pode ser reaberta", "ERRO P0001",
     "UPDATE ordem_servico SET status = 'ABERTA', data_conclusao = NULL\n"
     " WHERE id_os = (SELECT min(id_os) FROM ordem_servico WHERE status = 'CONCLUIDA');"),
    ("G08", "Regra", "Cancelar a OS devolve as peças ao estoque", "OK",
     "SELECT qtd_estoque AS estoque_inicial FROM peca WHERE id_peca = 40 \\gset\n"
     + NOVA_OS + "\nINSERT INTO os_peca (id_os, id_peca, quantidade) VALUES (:os, 40, 3);\n"
     "SELECT qtd_estoque AS apos_lancar FROM peca WHERE id_peca = 40;\n"
     "UPDATE ordem_servico SET status = 'CANCELADA' WHERE id_os = :os;\n"
     "SELECT :estoque_inicial AS inicial, qtd_estoque AS apos_cancelar,\n"
     "       CASE WHEN qtd_estoque = :estoque_inicial THEN 'PASSOU' ELSE 'FALHOU' END AS verificacao\n"
     "  FROM peca WHERE id_peca = 40;"),
    ("G09", "Regra", "Mão de obra = horas trabalhadas x valor/hora do mecânico", "OK",
     NOVA_OS + "\nUPDATE ordem_servico SET horas_trabalhadas = 2.5 WHERE id_os = :os;\n"
     "SELECT os.horas_trabalhadas, m.valor_hora, os.valor_mao_obra,\n"
     "       CASE WHEN os.valor_mao_obra = 2.5 * m.valor_hora THEN 'PASSOU' ELSE 'FALHOU' END AS verificacao\n"
     "  FROM ordem_servico os JOIN mecanico m USING (id_mecanico) WHERE os.id_os = :os;"),
    ("G10", "Regra", "Fluxo completo: abrir, lançar peças, concluir e faturar", "OK",
     NOVA_OS + "\nINSERT INTO os_peca (id_os, id_peca, quantidade, preco_unitario) VALUES (:os, 50, 2, 100.00), (:os, 51, 1, 45.90);\n"
     "UPDATE ordem_servico SET horas_trabalhadas = 1.5, status = 'EM_EXECUCAO' WHERE id_os = :os;\n"
     "UPDATE ordem_servico SET desconto = 10, status = 'CONCLUIDA', data_conclusao = now() WHERE id_os = :os;\n"
     "SELECT id_os, status, total_pecas, valor_mao_obra, desconto, valor_total,\n"
     "       CASE WHEN valor_total = 245.90 + valor_mao_obra - 10 THEN 'PASSOU' ELSE 'FALHOU' END AS verificacao\n"
     "  FROM vw_os_total WHERE id_os = :os;"),
]

-- C06 Top 10 clientes por gasto acumulado e participação no faturamento total.
--     Relatório sobre TODAS as OS: agrega direto nas tabelas (a view com LATERAL
--     é ótima para poucas OS, mas mais lenta para varrer tudo — ver view_v1_vs_v2.csv).
WITH pecas AS (
    SELECT id_os, sum(quantidade * preco_unitario) AS total_pecas FROM os_peca GROUP BY id_os
), gasto AS (
    SELECT c.id_cliente, c.nome, count(*) AS visitas,
           sum(COALESCE(p.total_pecas, 0) + os.valor_mao_obra - os.desconto) AS total
      FROM ordem_servico os
      JOIN veiculo v      ON v.id_veiculo = os.id_veiculo
      JOIN cliente c      ON c.id_cliente = v.id_cliente
      LEFT JOIN pecas p   ON p.id_os = os.id_os
     WHERE os.status = 'CONCLUIDA'
     GROUP BY c.id_cliente, c.nome
)
SELECT RANK() OVER (ORDER BY total DESC) AS pos, nome, visitas, total,
       round(100 * total / sum(total) OVER (), 3) AS perc_faturamento
  FROM gasto
 ORDER BY pos
 LIMIT 10;

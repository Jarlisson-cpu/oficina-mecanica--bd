-- C04 Peças para repor: abaixo do mínimo, com o consumo dos últimos 90 dias
SELECT p.codigo, p.descricao, p.qtd_estoque, p.estoque_minimo,
       COALESCE(c.consumo, 0) AS consumo_90d
  FROM peca p
  LEFT JOIN (SELECT op.id_peca, sum(op.quantidade) AS consumo
               FROM os_peca op
               JOIN ordem_servico os ON os.id_os = op.id_os
              WHERE os.data_abertura >= TIMESTAMP '2026-10-26' - INTERVAL '90 days'
                AND os.status <> 'CANCELADA'
              GROUP BY op.id_peca) c ON c.id_peca = p.id_peca
 WHERE p.qtd_estoque < p.estoque_minimo
 ORDER BY consumo_90d DESC, p.codigo
 LIMIT 10;

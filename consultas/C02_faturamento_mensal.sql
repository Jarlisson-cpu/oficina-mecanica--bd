-- C02 Faturamento mensal de 2026 (OS concluídas): peças, mão de obra e ticket médio
SELECT to_char(date_trunc('month', data_conclusao), 'YYYY-MM') AS mes,
       count(*)                          AS os_concluidas,
       sum(total_pecas)                  AS pecas,
       sum(valor_mao_obra - desconto)    AS mao_de_obra,
       sum(valor_total)                  AS faturamento,
       round(avg(valor_total), 2)        AS ticket_medio
  FROM vw_os_total
 WHERE status = 'CONCLUIDA'
   AND data_conclusao >= '2026-01-01' AND data_conclusao < '2026-11-01'
 GROUP BY 1
 ORDER BY 1;

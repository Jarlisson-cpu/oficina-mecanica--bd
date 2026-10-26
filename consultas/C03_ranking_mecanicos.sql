-- C03 Ranking de mecânicos em 2026: OS concluídas, horas, tempo médio e faturamento
SELECT RANK() OVER (ORDER BY sum(os.valor_mao_obra) DESC)                AS pos,
       m.nome, m.especialidade,
       count(*)                                                          AS os_concluidas,
       sum(os.horas_trabalhadas)                                         AS horas,
       round(avg(EXTRACT(EPOCH FROM os.data_conclusao - os.data_abertura) / 86400)::numeric, 1) AS dias_medios,
       sum(os.valor_mao_obra)                                            AS mao_de_obra
  FROM ordem_servico os
  JOIN mecanico m USING (id_mecanico)
 WHERE os.status = 'CONCLUIDA' AND os.data_abertura >= '2026-01-01'
 GROUP BY m.id_mecanico, m.nome, m.especialidade
 ORDER BY pos
 LIMIT 10;

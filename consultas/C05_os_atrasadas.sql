-- C05 OS pendentes há mais de 7 dias (painel da recepção), agrupadas por status
SELECT status, count(*) AS qtd,
       min(data_abertura)::date AS mais_antiga,
       round(avg(EXTRACT(EPOCH FROM TIMESTAMP '2026-10-26 17:00' - data_abertura) / 86400)::numeric, 1) AS dias_em_aberto
  FROM ordem_servico
 WHERE status IN ('ABERTA','EM_EXECUCAO','AGUARDANDO_PECA')
   AND data_abertura < TIMESTAMP '2026-10-26 17:00' - INTERVAL '7 days'
 GROUP BY status
 ORDER BY qtd DESC;

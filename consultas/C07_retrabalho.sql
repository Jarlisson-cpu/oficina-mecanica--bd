-- C07 Retrabalho: veículo que volta com o MESMO problema em até 30 dias após a conclusão.
--     LAG() pega a OS anterior do mesmo veículo; o indicador é atribuído ao mecânico da OS anterior.
WITH seq AS (
    SELECT id_os, id_veiculo, id_mecanico, descricao_problema, data_abertura, data_conclusao, status,
           LAG(id_mecanico)        OVER w AS mec_ant,
           LAG(descricao_problema) OVER w AS prob_ant,
           LAG(data_conclusao)     OVER w AS concl_ant
      FROM ordem_servico
    WINDOW w AS (PARTITION BY id_veiculo ORDER BY data_abertura)
)
SELECT m.nome AS mecanico,
       count(*) FILTER (WHERE s.prob_ant = s.descricao_problema
                          AND s.data_abertura <= s.concl_ant + INTERVAL '30 days') AS retornos_30d,
       count(*)                                                                    AS os_seguintes,
       round(100.0 * count(*) FILTER (WHERE s.prob_ant = s.descricao_problema
                          AND s.data_abertura <= s.concl_ant + INTERVAL '30 days') / count(*), 2) AS taxa_retrabalho_perc
  FROM seq s
  JOIN mecanico m ON m.id_mecanico = s.mec_ant
 GROUP BY m.id_mecanico, m.nome
 ORDER BY taxa_retrabalho_perc DESC
 LIMIT 5;

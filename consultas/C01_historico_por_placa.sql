-- C01 Histórico do veículo pela placa (recepção): últimas 5 OS com valor total
SELECT t.id_os, t.data_abertura::date AS abertura, t.status, t.mecanico,
       t.total_pecas, t.valor_mao_obra, t.valor_total
  FROM vw_os_total t
 WHERE t.placa = 'DAB7E42'
 ORDER BY t.data_abertura DESC
 LIMIT 5;

-- C08 Conferência: o total da view vw_os_total bate com a soma feita direto nas tabelas?
SELECT (SELECT sum(valor_total) FROM vw_os_total WHERE status = 'CONCLUIDA') AS total_pela_view,
       (SELECT sum(op.quantidade * op.preco_unitario)
          FROM os_peca op JOIN ordem_servico os USING (id_os) WHERE os.status = 'CONCLUIDA')
     + (SELECT sum(valor_mao_obra - desconto) FROM ordem_servico WHERE status = 'CONCLUIDA') AS total_pelas_tabelas,
       CASE WHEN (SELECT sum(valor_total) FROM vw_os_total WHERE status = 'CONCLUIDA')
               = (SELECT sum(op.quantidade * op.preco_unitario)
                    FROM os_peca op JOIN ordem_servico os USING (id_os) WHERE os.status = 'CONCLUIDA')
               + (SELECT sum(valor_mao_obra - desconto) FROM ordem_servico WHERE status = 'CONCLUIDA')
            THEN 'PASSOU' ELSE 'FALHOU' END AS verificacao;

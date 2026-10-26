-- =====================================================================
-- Arquivo 03: Carga de dados sintéticos (volume para testar índices)
-- ---------------------------------------------------------------------
-- 20.000 clientes | 30.000 veículos | 25 mecânicos | 500 peças
-- 300.000 ordens de serviço (2021-2026) | ~450.000 itens de peça
-- A carga é determinística (setseed) para que os resultados sejam
-- reproduzíveis. Como é uma carga HISTÓRICA (migração de planilhas),
-- os triggers de regra de negócio são desligados só durante a carga;
-- as chaves estrangeiras continuam ativas.
-- =====================================================================
SET search_path TO oficina;
SELECT setseed(0.42);

ALTER TABLE ordem_servico DISABLE TRIGGER USER;
ALTER TABLE os_peca       DISABLE TRIGGER USER;

-- ---------------- CLIENTE ----------------
INSERT INTO cliente (nome, cpf_cnpj, telefone, email, data_cadastro)
SELECT n.nome || ' ' || s.sob || ' ' || s2.sob,
       CASE WHEN i % 10 = 0 THEN lpad(i::text, 14, '0')        -- 10% pessoa jurídica
            ELSE lpad(i::text, 11, '0') END,
       '79' || (900000000 + i)::text,
       lower(n.nome) || '.' || i || '@email.com',
       DATE '2020-01-01' + (random() * 2100)::int
  FROM generate_series(1, 20000) AS i
  CROSS JOIN LATERAL (SELECT (ARRAY['Ana','Bruno','Carla','Diego','Eduarda','Felipe','Gabriela','Hugo',
        'Isabela','João','Karina','Lucas','Mariana','Natan','Olívia','Paulo','Quésia','Rafael',
        'Sabrina','Tiago','Úrsula','Vitor','Wesley','Yasmin'])[1 + (i % 24)] AS nome) n
  CROSS JOIN LATERAL (SELECT (ARRAY['Santos','Oliveira','Souza','Lima','Almeida','Costa','Ferreira',
        'Rodrigues','Barbosa','Menezes','Prado','Nascimento','Carvalho','Rocha','Teles'])[1 + (i % 15)] AS sob) s
  CROSS JOIN LATERAL (SELECT (ARRAY['Silva','Brito','Andrade','Machado','Dantas','Cardoso','Araújo',
        'Freitas','Gomes'])[1 + ((i / 15) % 9)] AS sob) s2;

-- ---------------- VEICULO ----------------
INSERT INTO veiculo (id_cliente, placa, chassi, marca, modelo, ano, km_atual)
SELECT 1 + (i % 20000),
       chr(65 + ((i/1000 + 2000) / 676) % 26) || chr(65 + ((i/1000 + 2000) / 26) % 26) || chr(65 + (i/1000 + 2000) % 26)
         || ((i / 100) % 10)::text || chr(65 + (i * 7) % 10) || lpad((i % 100)::text, 2, '0'),
       '9BWZZZ' || lpad(i::text, 11, '0'),
       mm.marca, mm.modelo,
       2005 + (i % 21),
       0
  FROM generate_series(1, 30000) AS i
  CROSS JOIN LATERAL (SELECT (ARRAY['Volkswagen','Fiat','Chevrolet','Hyundai','Toyota','Renault','Honda','Ford'])[1 + (i % 8)] AS marca,
                             (ARRAY['Gol','Uno','Onix','HB20','Corolla','Sandero','Civic','Ka'])[1 + (i % 8)] AS modelo) mm;

-- ---------------- MECANICO ----------------
INSERT INTO mecanico (nome, cpf, especialidade, valor_hora, ativo)
SELECT 'Mecânico ' || (ARRAY['Antônio','Benedito','Cícero','Damião','Edvaldo','Francisco','Genivaldo','Heleno',
                             'Ivanildo','José','Jailson','Luiz','Manoel'])[1 + (i % 13)] || ' ' || i,
       lpad((90000000000 + i)::text, 11, '0'),
       (ARRAY['MOTOR','SUSPENSAO','FREIOS','ELETRICA','INJECAO','AR_CONDICIONADO','GERAL'])[1 + (i % 7)],
       60 + (i % 5) * 15,
       i <= 22                                         -- 3 mecânicos desligados
  FROM generate_series(1, 25) AS i;

-- ---------------- PECA ----------------
INSERT INTO peca (codigo, descricao, fabricante, preco_venda, qtd_estoque, estoque_minimo)
SELECT 'PC-' || lpad(i::text, 5, '0'),
       (ARRAY['Filtro de óleo','Pastilha de freio','Disco de freio','Amortecedor','Correia dentada',
              'Vela de ignição','Bateria 60Ah','Filtro de ar','Bomba d''água','Kit embreagem',
              'Óleo 5W30 (litro)','Lâmpada farol','Sensor de oxigênio','Bico injetor','Compressor A/C',
              'Terminal de direção','Bieleta','Junta do cabeçote','Radiador','Fluido de freio'])[1 + (i % 20)]
         || ' mod. ' || i,
       (ARRAY['Bosch','Cofap','Fras-le','Mahle','NGK','Moura','SKF','Valeo','Delphi','Magneti Marelli'])[1 + (i % 10)],
       round((12 + random() * 388)::numeric, 2),         -- R$ 12 a R$ 400
       (random() * 200)::int,
       5 + (i % 16)
  FROM generate_series(1, 500) AS i;

-- ---------------- ORDEM_SERVICO ----------------
INSERT INTO ordem_servico (id_veiculo, id_mecanico, data_abertura, data_conclusao, status,
                           km_entrada, descricao_problema, horas_trabalhadas, valor_mao_obra, desconto)
SELECT x.id_veiculo, x.id_mecanico, x.abertura,
       CASE WHEN x.status = 'CONCLUIDA' THEN
            LEAST(x.abertura + (1 + random() * 9) * INTERVAL '1 day',
                  GREATEST(x.abertura + INTERVAL '2 hours', TIMESTAMP '2026-10-26 08:00')) END,
       x.status, 0, x.problema, x.horas,
       round(x.horas * m.valor_hora, 2),
       CASE WHEN random() < 0.2 THEN round(x.horas * m.valor_hora * 0.05, 2) ELSE 0 END
  FROM (
    SELECT 1 + (random() * 29999)::int AS id_veiculo,
           1 + (random() * 21)::int    AS id_mecanico,             -- só mecânicos ativos (1..22)
           ab.abertura,
           CASE WHEN ab.abertura < TIMESTAMP '2026-10-01' THEN
                     CASE WHEN random() < 0.96 THEN 'CONCLUIDA' ELSE 'CANCELADA' END
                ELSE (ARRAY['ABERTA','EM_EXECUCAO','AGUARDANDO_PECA','CONCLUIDA'])[1 + (random() * 3)::int]
           END::status_os AS status,
           (ARRAY['Barulho na suspensão dianteira','Revisão dos 10.000 km','Troca de óleo e filtros',
                  'Freio rangendo','Motor falhando a frio','Ar-condicionado não gela','Bateria descarregando',
                  'Luz da injeção acesa','Vazamento de óleo','Embreagem patinando'])[1 + (g % 10)] AS problema,
           round((0.5 + random() * 7.5)::numeric, 2) AS horas
      FROM generate_series(1, 300000) AS g
      CROSS JOIN LATERAL (SELECT TIMESTAMP '2021-01-02 08:00'
                                 + (random() * (TIMESTAMP '2026-10-25 18:00' - TIMESTAMP '2021-01-02 08:00')) AS abertura
                           WHERE g > 0) ab
  ) x
  JOIN mecanico m ON m.id_mecanico = x.id_mecanico;

-- Abertas recentes não podem ter data de conclusão; CONCLUIDA de outubro ganha data coerente
UPDATE ordem_servico SET data_conclusao = data_abertura + INTERVAL '1 day'
 WHERE status = 'CONCLUIDA' AND data_conclusao IS NULL;

-- Hodômetro crescente por veículo, na ordem cronológica das OS
UPDATE ordem_servico os SET km_entrada = k.km
  FROM (SELECT id_os,
               (id_veiculo % 50) * 1000
               + 9000 * row_number() OVER (PARTITION BY id_veiculo ORDER BY data_abertura) AS km
          FROM ordem_servico) k
 WHERE k.id_os = os.id_os;

UPDATE veiculo v SET km_atual = k.km
  FROM (SELECT id_veiculo, max(km_entrada) AS km FROM ordem_servico GROUP BY id_veiculo) k
 WHERE k.id_veiculo = v.id_veiculo;

-- ---------------- OS_PECA ----------------
INSERT INTO os_peca (id_os, id_peca, quantidade, preco_unitario)
SELECT DISTINCT ON (os.id_os, pc.id_peca)
       os.id_os, pc.id_peca, CASE WHEN random() < 0.75 THEN 1 ELSE 2 END, pc.preco_venda
  FROM ordem_servico os
  CROSS JOIN LATERAL generate_series(1, abs(hashint4(os.id_os)) % 4) AS n(k)   -- 0 a 3 peças por OS
  JOIN peca pc ON pc.id_peca = 1 + ((os.id_os * 31 + n.k * 97) % 500);

ALTER TABLE ordem_servico ENABLE TRIGGER USER;
ALTER TABLE os_peca       ENABLE TRIGGER USER;

ANALYZE;

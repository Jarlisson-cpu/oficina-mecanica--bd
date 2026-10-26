-- =====================================================================
-- Projeto de Banco de Dados — Tema 07: Oficina Mecânica
-- Arquivo 01: Estrutura (DDL) — PostgreSQL 16
-- =====================================================================
-- Execução:  psql -d oficina -f sql/01_ddl.sql
-- =====================================================================

DROP SCHEMA IF EXISTS oficina CASCADE;
CREATE SCHEMA oficina;
SET search_path TO oficina;

-- ---------------------------------------------------------------------
-- Domínios: regras de formato reaproveitadas em várias tabelas
-- ---------------------------------------------------------------------
CREATE DOMAIN dm_cpf      AS CHAR(11)     CHECK (VALUE ~ '^[0-9]{11}$');
CREATE DOMAIN dm_doc      AS VARCHAR(14)  CHECK (VALUE ~ '^([0-9]{11}|[0-9]{14})$');   -- CPF ou CNPJ, só dígitos
CREATE DOMAIN dm_placa    AS CHAR(7)      CHECK (VALUE ~ '^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$'); -- antiga e Mercosul
CREATE DOMAIN dm_dinheiro AS NUMERIC(10,2) CHECK (VALUE >= 0);
CREATE DOMAIN dm_telefone AS VARCHAR(11)  CHECK (VALUE ~ '^[0-9]{10,11}$');            -- DDD + número

-- Status possíveis de uma ordem de serviço
CREATE TYPE status_os AS ENUM ('ABERTA', 'EM_EXECUCAO', 'AGUARDANDO_PECA', 'CONCLUIDA', 'CANCELADA');

-- ---------------------------------------------------------------------
-- CLIENTE
-- ---------------------------------------------------------------------
CREATE TABLE cliente (
    id_cliente     INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome           VARCHAR(120) NOT NULL CHECK (length(trim(nome)) >= 3),
    cpf_cnpj       dm_doc       NOT NULL,
    telefone       dm_telefone  NOT NULL,
    email          VARCHAR(120)          CHECK (email ~* '^[^@\s]+@[^@\s]+\.[a-z]{2,}$'),
    data_cadastro  DATE         NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT uq_cliente_doc UNIQUE (cpf_cnpj)
);

-- ---------------------------------------------------------------------
-- VEICULO
-- ---------------------------------------------------------------------
CREATE TABLE veiculo (
    id_veiculo  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_cliente  INTEGER     NOT NULL REFERENCES cliente (id_cliente) ON DELETE RESTRICT,
    placa       dm_placa    NOT NULL,
    chassi      CHAR(17)    NOT NULL CHECK (chassi ~ '^[A-HJ-NPR-Z0-9]{17}$'),   -- VIN: sem I, O, Q
    marca       VARCHAR(40) NOT NULL,
    modelo      VARCHAR(60) NOT NULL,
    ano         SMALLINT    NOT NULL CHECK (ano BETWEEN 1950 AND 2100),
    km_atual    INTEGER     NOT NULL DEFAULT 0 CHECK (km_atual >= 0),
    CONSTRAINT uq_veiculo_placa  UNIQUE (placa),
    CONSTRAINT uq_veiculo_chassi UNIQUE (chassi)
);

-- ---------------------------------------------------------------------
-- MECANICO
-- ---------------------------------------------------------------------
CREATE TABLE mecanico (
    id_mecanico    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome           VARCHAR(120) NOT NULL,
    cpf            dm_cpf       NOT NULL UNIQUE,
    especialidade  VARCHAR(30)  NOT NULL
                   CHECK (especialidade IN ('MOTOR','SUSPENSAO','FREIOS','ELETRICA','INJECAO','AR_CONDICIONADO','GERAL')),
    valor_hora     dm_dinheiro  NOT NULL CHECK (valor_hora > 0),
    ativo          BOOLEAN      NOT NULL DEFAULT TRUE
);

-- ---------------------------------------------------------------------
-- PECA (catálogo + estoque)
-- ---------------------------------------------------------------------
CREATE TABLE peca (
    id_peca         INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo          VARCHAR(20)  NOT NULL UNIQUE,
    descricao       VARCHAR(120) NOT NULL,
    fabricante      VARCHAR(60)  NOT NULL,
    preco_venda     dm_dinheiro  NOT NULL CHECK (preco_venda > 0),
    qtd_estoque     INTEGER      NOT NULL DEFAULT 0,
    estoque_minimo  INTEGER      NOT NULL DEFAULT 0 CHECK (estoque_minimo >= 0),
    CONSTRAINT ck_peca_estoque_nao_negativo CHECK (qtd_estoque >= 0)
);

-- ---------------------------------------------------------------------
-- ORDEM_SERVICO
-- ---------------------------------------------------------------------
CREATE TABLE ordem_servico (
    id_os               INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_veiculo          INTEGER     NOT NULL REFERENCES veiculo  (id_veiculo)  ON DELETE RESTRICT,
    id_mecanico         INTEGER     NOT NULL REFERENCES mecanico (id_mecanico) ON DELETE RESTRICT,
    data_abertura       TIMESTAMP   NOT NULL DEFAULT now(),
    data_conclusao      TIMESTAMP,
    status              status_os   NOT NULL DEFAULT 'ABERTA',
    km_entrada          INTEGER     NOT NULL CHECK (km_entrada >= 0),
    descricao_problema  TEXT        NOT NULL CHECK (length(trim(descricao_problema)) >= 5),
    horas_trabalhadas   NUMERIC(5,2) NOT NULL DEFAULT 0 CHECK (horas_trabalhadas BETWEEN 0 AND 200),
    valor_mao_obra      dm_dinheiro NOT NULL DEFAULT 0,
    desconto            dm_dinheiro NOT NULL DEFAULT 0,
    -- Regras de negócio entre colunas
    CONSTRAINT ck_os_datas      CHECK (data_conclusao IS NULL OR data_conclusao >= data_abertura),
    CONSTRAINT ck_os_concluida  CHECK ((status = 'CONCLUIDA') = (data_conclusao IS NOT NULL)),
    CONSTRAINT ck_os_desconto   CHECK (desconto <= valor_mao_obra)
);

-- ---------------------------------------------------------------------
-- OS_PECA (associativa N:N entre ORDEM_SERVICO e PECA)
-- ---------------------------------------------------------------------
CREATE TABLE os_peca (
    id_os           INTEGER     NOT NULL REFERENCES ordem_servico (id_os) ON DELETE CASCADE,
    id_peca         INTEGER     NOT NULL REFERENCES peca (id_peca)        ON DELETE RESTRICT,
    quantidade      INTEGER     NOT NULL CHECK (quantidade > 0),
    preco_unitario  dm_dinheiro NOT NULL CHECK (preco_unitario > 0),     -- preço congelado no momento da venda
    CONSTRAINT pk_os_peca PRIMARY KEY (id_os, id_peca)
);

COMMENT ON TABLE  os_peca IS 'Peças aplicadas em cada OS; o preço é copiado da PECA no momento do lançamento.';
COMMENT ON COLUMN ordem_servico.id_mecanico IS 'Mecânico responsável pela OS (obrigatório).';

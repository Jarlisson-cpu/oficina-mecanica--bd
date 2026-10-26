-- =====================================================================
-- Arquivo 02: Regras de negócio implementadas no banco (funções/triggers)
-- =====================================================================
SET search_path TO oficina;

-- ---------------------------------------------------------------------
-- R1. Preço da peça é copiado do catálogo quando não for informado
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_os_peca_preco() RETURNS trigger AS $$
BEGIN
    IF NEW.preco_unitario IS NULL THEN
        SELECT preco_venda INTO NEW.preco_unitario FROM peca WHERE id_peca = NEW.id_peca;
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER trg_os_peca_preco
BEFORE INSERT ON os_peca
FOR EACH ROW EXECUTE FUNCTION fn_os_peca_preco();

-- ---------------------------------------------------------------------
-- R2. Não se mexe nas peças de uma OS já CONCLUIDA ou CANCELADA
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_os_peca_os_aberta() RETURNS trigger AS $$
DECLARE
    v_status status_os;
BEGIN
    SELECT status INTO v_status
      FROM ordem_servico WHERE id_os = COALESCE(NEW.id_os, OLD.id_os);
    IF v_status IN ('CONCLUIDA', 'CANCELADA') THEN
        RAISE EXCEPTION 'OS % está % e não aceita alteração de peças', COALESCE(NEW.id_os, OLD.id_os), v_status
            USING ERRCODE = 'P0001';
    END IF;
    RETURN COALESCE(NEW, OLD);
END $$ LANGUAGE plpgsql;

CREATE TRIGGER trg_os_peca_os_aberta
BEFORE INSERT OR UPDATE OR DELETE ON os_peca
FOR EACH ROW EXECUTE FUNCTION fn_os_peca_os_aberta();

-- ---------------------------------------------------------------------
-- R3. Baixa e estorno automáticos de estoque.
--     Se não houver saldo, a CHECK ck_peca_estoque_nao_negativo barra.
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_os_peca_estoque() RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE peca SET qtd_estoque = qtd_estoque - NEW.quantidade WHERE id_peca = NEW.id_peca;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE peca SET qtd_estoque = qtd_estoque + OLD.quantidade WHERE id_peca = OLD.id_peca;
    ELSIF TG_OP = 'UPDATE' THEN
        UPDATE peca SET qtd_estoque = qtd_estoque + OLD.quantidade WHERE id_peca = OLD.id_peca;
        UPDATE peca SET qtd_estoque = qtd_estoque - NEW.quantidade WHERE id_peca = NEW.id_peca;
    END IF;
    RETURN NULL;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER trg_os_peca_estoque
AFTER INSERT OR UPDATE OR DELETE ON os_peca
FOR EACH ROW EXECUTE FUNCTION fn_os_peca_estoque();

-- ---------------------------------------------------------------------
-- R4. Abertura de OS: mecânico precisa estar ativo e o hodômetro
--     não pode voltar (km_entrada >= km_atual do veículo).
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_os_abertura() RETURNS trigger AS $$
DECLARE
    v_ativo BOOLEAN;
    v_km    INTEGER;
BEGIN
    SELECT ativo INTO v_ativo FROM mecanico WHERE id_mecanico = NEW.id_mecanico;
    IF v_ativo IS FALSE THEN
        RAISE EXCEPTION 'Mecânico % está inativo e não pode assumir OS', NEW.id_mecanico;
    END IF;

    SELECT km_atual INTO v_km FROM veiculo WHERE id_veiculo = NEW.id_veiculo;
    IF NEW.km_entrada < v_km THEN
        RAISE EXCEPTION 'km_entrada (%) menor que o km já registrado do veículo (%)', NEW.km_entrada, v_km;
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER trg_os_abertura
BEFORE INSERT ON ordem_servico
FOR EACH ROW EXECUTE FUNCTION fn_os_abertura();

-- Atualiza o hodômetro do veículo após abrir a OS
CREATE OR REPLACE FUNCTION fn_os_atualiza_km() RETURNS trigger AS $$
BEGIN
    UPDATE veiculo SET km_atual = NEW.km_entrada
     WHERE id_veiculo = NEW.id_veiculo AND km_atual < NEW.km_entrada;
    RETURN NULL;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER trg_os_atualiza_km
AFTER INSERT ON ordem_servico
FOR EACH ROW EXECUTE FUNCTION fn_os_atualiza_km();

-- ---------------------------------------------------------------------
-- R5. Ciclo de vida da OS: CONCLUIDA/CANCELADA não reabrem.
--     Ao CANCELAR, as peças voltam para o estoque.
--     Mão de obra = horas_trabalhadas x valor_hora do mecânico.
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_os_status() RETURNS trigger AS $$
DECLARE
    v_valor_hora NUMERIC(10,2);
BEGIN
    IF OLD.status IN ('CONCLUIDA', 'CANCELADA') AND NEW.status <> OLD.status THEN
        RAISE EXCEPTION 'OS % já está % e não pode mudar para %', OLD.id_os, OLD.status, NEW.status;
    END IF;

    IF NEW.horas_trabalhadas <> OLD.horas_trabalhadas OR NEW.id_mecanico <> OLD.id_mecanico THEN
        SELECT valor_hora INTO v_valor_hora FROM mecanico WHERE id_mecanico = NEW.id_mecanico;
        NEW.valor_mao_obra := round(NEW.horas_trabalhadas * v_valor_hora, 2);
    END IF;

    IF NEW.status = 'CANCELADA' AND OLD.status <> 'CANCELADA' THEN
        UPDATE peca p SET qtd_estoque = p.qtd_estoque + op.quantidade
          FROM os_peca op
         WHERE op.id_os = NEW.id_os AND op.id_peca = p.id_peca;
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER trg_os_status
BEFORE UPDATE ON ordem_servico
FOR EACH ROW EXECUTE FUNCTION fn_os_status();

-- ---------------------------------------------------------------------
-- Visão de apoio: valor total de cada OS.
-- Versão com LATERAL: a soma das peças é feita só para as OS que
-- passaram no filtro (ver evidencias/resultados/view_v1_vs_v2.csv —
-- a versão com GROUP BY em subconsulta somava os ~450 mil itens sempre).
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_os_total AS
SELECT os.id_os,
       os.status,
       os.data_abertura,
       os.data_conclusao,
       v.id_veiculo,
       v.placa,
       c.id_cliente,
       c.nome                                   AS cliente,
       m.nome                                   AS mecanico,
       p.total_pecas,
       os.valor_mao_obra,
       os.desconto,
       p.total_pecas + os.valor_mao_obra - os.desconto AS valor_total
  FROM ordem_servico os
  JOIN veiculo  v ON v.id_veiculo  = os.id_veiculo
  JOIN cliente  c ON c.id_cliente  = v.id_cliente
  JOIN mecanico m ON m.id_mecanico = os.id_mecanico
  CROSS JOIN LATERAL (SELECT COALESCE(SUM(op.quantidade * op.preco_unitario), 0) AS total_pecas
                        FROM os_peca op WHERE op.id_os = os.id_os) p;

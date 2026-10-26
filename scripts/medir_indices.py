"""Mede o efeito dos índices: EXPLAIN (ANALYZE, BUFFERS) antes e depois.

Uso: python3 scripts/medir_indices.py

1. remove os índices do arquivo 04 (fica só PK/UNIQUE) e roda ANALYZE
2. executa cada consulta N vezes e guarda a MEDIANA do "Execution Time"
3. cria os índices (sql/04_indices.sql) e repete
4. mede também o custo na escrita (inserir 20 mil OS) e o tamanho dos índices
Saídas: evidencias/resultados/indices_antes_depois.csv, planos .txt e capturas .png
"""
import csv, os, re, statistics, subprocess, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
from captura import render

DB = os.environ.get("PGDATABASE", "oficina")
N = 7
RES = os.path.join(RAIZ, "evidencias", "resultados")
CAP = os.path.join(RAIZ, "evidencias", "capturas")
INDICES = ["ix_os_veiculo_data", "ix_os_pendentes", "ix_os_mecanico_data", "ix_os_conclusao",
           "ix_os_peca_peca", "ix_veiculo_cliente", "ix_cliente_nome_trgm", "ix_os_status"]


def psql(sql, extra=()):
    p = subprocess.run(["psql", "-X", "-d", DB, "-v", "ON_ERROR_STOP=1", *extra, "-c",
                        "SET search_path TO oficina, public", "-c", sql],
                       capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(p.stderr)
    return p.stdout


def valor(sql):
    return psql(sql, ("-A", "-t")).strip().split("\n")[-1]


PLACA = valor("SELECT v.placa FROM veiculo v JOIN ordem_servico o USING (id_veiculo) "
              "GROUP BY v.placa ORDER BY count(*) DESC, v.placa LIMIT 1")

CONSULTAS = [
    ("B1", "I1 ix_os_veiculo_data", "Histórico de OS de um veículo pela placa",
     f"SELECT os.id_os, os.data_abertura, os.status, os.km_entrada, os.descricao_problema\n"
     f"  FROM ordem_servico os JOIN veiculo v USING (id_veiculo)\n"
     f" WHERE v.placa = '{PLACA}'\n ORDER BY os.data_abertura DESC"),
    ("B2", "I2 ix_os_pendentes (parcial)", "Painel: 50 OS pendentes mais antigas",
     "SELECT id_os, data_abertura, status FROM ordem_servico\n"
     " WHERE status IN ('ABERTA','EM_EXECUCAO','AGUARDANDO_PECA')\n ORDER BY data_abertura LIMIT 50"),
    ("B3", "I3 ix_os_mecanico_data", "Produção de um mecânico em set/2026",
     "SELECT count(*), sum(horas_trabalhadas) FROM ordem_servico\n"
     " WHERE id_mecanico = 5 AND data_abertura >= '2026-09-01' AND data_abertura < '2026-10-01'"),
    ("B4", "I4 ix_os_conclusao", "Faturamento de mão de obra em set/2026",
     "SELECT sum(valor_mao_obra - desconto) FROM ordem_servico\n"
     " WHERE data_conclusao >= '2026-09-01' AND data_conclusao < '2026-10-01'"),
    ("B5", "I5 ix_os_peca_peca", "Consumo total de uma peça",
     "SELECT count(*), sum(quantidade) FROM os_peca WHERE id_peca = 137"),
    ("B6", "I6 ix_veiculo_cliente", "Veículos de um cliente",
     "SELECT placa, marca, modelo FROM veiculo WHERE id_cliente = 4321"),
    ("B7", "I7 ix_cliente_nome_trgm (GIN)", "Busca de cliente por parte do nome",
     "SELECT id_cliente, nome FROM cliente WHERE nome ILIKE '%teles dantas%'"),
    ("B8", "I8 ix_os_status (contraexemplo)", "Somar mão de obra das OS CONCLUIDAS (95% da tabela)",
     "SELECT sum(valor_mao_obra) FROM ordem_servico WHERE status = 'CONCLUIDA'"),
    ("B9", "I8 ix_os_status", "Somar mão de obra das OS ABERTAS (0,2% da tabela)",
     "SELECT sum(valor_mao_obra) FROM ordem_servico WHERE status = 'ABERTA'"),
]

ESCRITA = ("INSERT INTO ordem_servico (id_veiculo, id_mecanico, km_entrada, descricao_problema)\n"
           "SELECT 1 + (g % 30000), 1 + (g % 22), 9999999, 'Carga de teste de escrita'\n"
           "  FROM generate_series(1, 20000) g")


def vacuum():
    for t in ("ordem_servico", "os_peca", "cliente", "veiculo", "peca", "mecanico"):
        psql(f"VACUUM ANALYZE {t}")


def plano(sql):
    return psql("EXPLAIN (ANALYZE, BUFFERS, COSTS OFF) " + sql)


def acesso(p):
    m = re.findall(r"(Index Only Scan using \w+|Index Scan(?: Backward)? using \w+|Bitmap Index Scan on \w+|Seq Scan on \w+)", p)
    vistos = []
    for x in m:
        x = re.sub(r" using | on ", " ", x)
        if x not in vistos:
            vistos.append(x)
    return "; ".join(vistos)


def mede(sql):
    tempos, p = [], ""
    for _ in range(N):
        p = plano(sql)
        tempos.append(float(re.search(r"Execution Time: ([\d.]+) ms", p).group(1)))
    buf = re.search(r"Buffers: shared hit=(\d+)(?: read=(\d+))?", p)
    paginas = int(buf.group(1)) + int(buf.group(2) or 0) if buf else 0
    return statistics.median(tempos), paginas, p


def mede_escrita():
    t = []
    for _ in range(3):
        out = psql("BEGIN; EXPLAIN (ANALYZE, COSTS OFF) " + ESCRITA + "; ROLLBACK;")
        t.append(float(re.search(r"Execution Time: ([\d.]+) ms", out).group(1)))
    return statistics.median(t)


def fase(nome):
    linhas = {}
    for cid, idx, desc, sql in CONSULTAS:
        med, pag, p = mede(sql)
        linhas[cid] = (med, pag, acesso(p))
        with open(os.path.join(RES, f"plano_{cid}_{nome}.txt"), "w") as fh:
            fh.write(f"-- {cid} {desc} ({nome} dos índices)\nEXPLAIN (ANALYZE, BUFFERS, COSTS OFF)\n{sql};\n\n{p}")
        print(f"  {cid} {nome:6} {med:9.3f} ms  {pag:6} pág.  {acesso(p)}")
    return linhas


def main():
    os.makedirs(RES, exist_ok=True); os.makedirs(CAP, exist_ok=True)
    print("placa usada no B1:", PLACA)
    psql("; ".join(f"DROP INDEX IF EXISTS {i}" for i in INDICES) + "; ANALYZE")
    vacuum()
    print("ANTES (só PK/UNIQUE):")
    antes = fase("antes")
    esc_antes = mede_escrita()

    subprocess.run(["psql", "-X", "-q", "-d", DB, "-v", "ON_ERROR_STOP=1", "-f",
                    os.path.join(RAIZ, "sql", "04_indices.sql")], check=True, capture_output=True)
    vacuum()
    print("DEPOIS (com sql/04_indices.sql):")
    depois = fase("depois")
    esc_depois = mede_escrita()

    tamanhos = psql("SELECT indexrelname, pg_size_pretty(pg_relation_size(indexrelid)) FROM pg_stat_user_indexes "
                    "WHERE indexrelname LIKE 'ix_%' ORDER BY 1", ("-A", "-t", "-F", ";"))
    with open(os.path.join(RES, "indices_tamanho.csv"), "w") as fh:
        fh.write("indice;tamanho\n" + "\n".join(l for l in tamanhos.strip().split("\n") if ";" in l) + "\n")

    with open(os.path.join(RES, "indices_antes_depois.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "indice", "consulta", "ms_antes", "ms_depois", "ganho_x",
                    "paginas_antes", "paginas_depois", "acesso_antes", "acesso_depois"])
        for cid, idx, desc, _ in CONSULTAS:
            a, d = antes[cid], depois[cid]
            w.writerow([cid, idx, desc, f"{a[0]:.3f}", f"{d[0]:.3f}", f"{a[0]/d[0]:.1f}",
                        a[1], d[1], a[2], d[2]])
        w.writerow(["W1", "todos", "INSERT de 20.000 OS (custo de escrita)", f"{esc_antes:.1f}",
                    f"{esc_depois:.1f}", f"{esc_antes/esc_depois:.2f}", "", "", "", ""])
    print(f"Escrita 20k OS: antes {esc_antes:.1f} ms, depois {esc_depois:.1f} ms")

    # capturas lado a lado das consultas principais
    for cid in ("B1", "B2", "B4", "B8", "B9"):
        for f in ("antes", "depois"):
            txt = open(os.path.join(RES, f"plano_{cid}_{f}.txt")).read()
            render(txt, os.path.join(CAP, f"plano_{cid}_{f}.png"),
                   titulo=f"psql — EXPLAIN ANALYZE {cid} ({f} dos índices)", max_col=110)


if __name__ == "__main__":
    main()

"""Compara a view antiga (GROUP BY em subconsulta) com a nova (LATERAL)."""
import csv, os, re, statistics, subprocess, sys
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
from captura import render
DB = os.environ.get("PGDATABASE", "oficina")
V1 = """CREATE OR REPLACE TEMP VIEW vw_os_total_v1 AS
SELECT os.id_os, os.status, os.data_abertura, os.data_conclusao, v.placa, c.id_cliente,
       COALESCE(p.total_pecas, 0) + os.valor_mao_obra - os.desconto AS valor_total
  FROM oficina.ordem_servico os
  JOIN oficina.veiculo v ON v.id_veiculo = os.id_veiculo
  JOIN oficina.cliente c ON c.id_cliente = v.id_cliente
  LEFT JOIN (SELECT id_os, SUM(quantidade * preco_unitario) AS total_pecas
               FROM oficina.os_peca GROUP BY id_os) p ON p.id_os = os.id_os"""
CONSULTAS = [
    ("histórico de 1 placa", "SELECT id_os, valor_total FROM {v} WHERE placa = 'DAB7E42'"),
    ("faturamento set/2026", "SELECT sum(valor_total) FROM {v} WHERE status = 'CONCLUIDA' "
                             "AND data_conclusao >= '2026-09-01' AND data_conclusao < '2026-10-01'"),
    ("faturamento total (todas as OS)", "SELECT sum(valor_total) FROM {v} WHERE status = 'CONCLUIDA'"),
]
def mede(sql):
    t, plano = [], ""
    for _ in range(7):
        p = subprocess.run(["psql", "-X", "-d", DB, "-v", "ON_ERROR_STOP=1", "-c", V1, "-c",
                            "SET search_path TO oficina", "-c", "EXPLAIN (ANALYZE, COSTS OFF) " + sql],
                           capture_output=True, text=True, check=True)
        plano = p.stdout
        t.append(float(re.search(r"Execution Time: ([\d.]+) ms", plano).group(1)))
    return statistics.median(t), plano
linhas, txt = [], []
for nome, sql in CONSULTAS:
    a, pa = mede(sql.format(v="vw_os_total_v1")); b, pb = mede(sql.format(v="vw_os_total"))
    linhas.append([nome, f"{a:.2f}", f"{b:.2f}", f"{a/b:.1f}"])
    txt.append(f"{nome:34} v1 (GROUP BY) {a:9.2f} ms | v2 (LATERAL) {b:9.2f} ms | {a/b:6.1f}x")
with open(os.path.join(RAIZ, "evidencias/resultados/view_v1_vs_v2.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["consulta", "ms_v1_groupby", "ms_v2_lateral", "razao_v1_v2"]); w.writerows(linhas)
print("\n".join(txt))

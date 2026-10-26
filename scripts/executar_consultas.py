"""Executa as consultas de negócio (consultas/*.sql) e salva saída + captura."""
import glob, os, subprocess, sys
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
from captura import render
DB = os.environ.get("PGDATABASE", "oficina")
for arq in sorted(glob.glob(os.path.join(RAIZ, "consultas", "C*.sql"))):
    nome = os.path.basename(arq)[:-4]
    p = subprocess.run(["psql", "-X", "-d", DB, "-a", "-v", "ON_ERROR_STOP=1", "-c",
                        "SET search_path TO oficina", "-c", "\\timing on", "-f", arq],
                       capture_output=True, text=True)
    saida = "\n".join(l for l in (p.stdout + p.stderr).split("\n")
                      if l.strip() not in ("SET", "Timing is on.")).strip() + "\n"
    open(os.path.join(RAIZ, "evidencias", "resultados", nome + ".txt"), "w").write(saida)
    render(saida, os.path.join(RAIZ, "evidencias", "capturas", nome + ".png"), max_col=125)
    print("=" * 30, nome, "(erro)" if p.returncode else ""); print(saida)

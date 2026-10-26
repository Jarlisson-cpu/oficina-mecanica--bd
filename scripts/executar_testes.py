"""Executa os testes de tipos, restrições e regras no PostgreSQL.

Uso:  python3 scripts/executar_testes.py   (banco 'oficina' já criado e carregado)

Para cada teste:
  1. grava testes/<ID>_<slug>.sql
  2. roda no psql dentro de BEGIN ... ROLLBACK
  3. compara o resultado com o esperado (ERRO <SQLSTATE> ou OK/PASSOU)
  4. salva o log em evidencias/resultados/ e a captura em evidencias/capturas/
"""
import csv, os, re, subprocess, sys, unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
from testes_spec import TESTES
from captura import render

DB = os.environ.get("PGDATABASE", "oficina")


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", t).strip("_")[:45]


def roda(arq):
    cmd = ["psql", "-X", "-d", DB, "-a", "-v", "ON_ERROR_STOP=0",
           "-c", "\\set VERBOSITY verbose", "-c", "\\set SHOW_CONTEXT never",
           "-c", "SET search_path TO oficina", "-c", "BEGIN",
           "-f", os.path.relpath(arq, RAIZ), "-c", "ROLLBACK"]
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=RAIZ)
    saida = p.stdout + p.stderr
    # retira só as linhas de "LOCATION" (arquivo-fonte do PostgreSQL) e o eco dos comandos de controle
    linhas = [l for l in saida.split("\n")
              if not l.startswith(("LOCATION:", "set VERBOSITY", "set SHOW_CONTEXT", "SET search_path"))
              and l.strip() not in ("SET", "BEGIN", "ROLLBACK")]
    return "\n".join(linhas).strip() + "\n"


def main():
    os.makedirs(os.path.join(RAIZ, "testes"), exist_ok=True)
    res_dir = os.path.join(RAIZ, "evidencias", "resultados")
    cap_dir = os.path.join(RAIZ, "evidencias", "capturas")
    os.makedirs(res_dir, exist_ok=True); os.makedirs(cap_dir, exist_ok=True)
    linhas_csv = []
    for tid, cat, desc, esperado, sql in TESTES:
        nome = f"{tid}_{slug(desc)}"
        arq = os.path.join(RAIZ, "testes", nome + ".sql")
        with open(arq, "w") as fh:
            fh.write(f"-- {tid} [{cat}] {desc}\n-- Esperado: {esperado}\n{sql}\n")
        saida = roda(arq)
        erros = re.findall(r"ERROR:\s+([0-9A-Z]{5}):\s*(.*)", saida)
        if esperado.startswith("ERRO"):
            cod = esperado.split()[1]
            obtido = f"ERRO {erros[0][0]}" if erros else "OK"
            passou = bool(erros) and erros[0][0] == cod
            msg = erros[0][1] if erros else ""
        else:
            obtido = f"ERRO {erros[0][0]}" if erros else "OK"
            passou = not erros and "PASSOU" in saida
            msg = "verificação = PASSOU" if passou else (erros[0][1] if erros else "verificação = FALHOU")
        with open(os.path.join(res_dir, nome + ".txt"), "w") as fh:
            fh.write(saida)
        render(saida, os.path.join(cap_dir, nome + ".png"))
        linhas_csv.append([tid, cat, desc, esperado, obtido, msg, "PASSOU" if passou else "FALHOU"])
        print(f"{tid:4} {'PASSOU' if passou else 'FALHOU':7} {esperado:11} -> {obtido:11} {desc}")

    with open(os.path.join(res_dir, "resumo_testes.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "categoria", "descricao", "esperado", "obtido", "mensagem_do_banco", "resultado"])
        w.writerows(linhas_csv)
    with open(os.path.join(res_dir, "resumo_testes.md"), "w") as fh:
        fh.write("| ID | Categoria | Teste | Esperado | Obtido | Resultado |\n|---|---|---|---|---|---|\n")
        for r in linhas_csv:
            fh.write(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {'✅' if r[6]=='PASSOU' else '❌'} {r[6]} |\n")
    total = len(linhas_csv); ok = sum(r[6] == "PASSOU" for r in linhas_csv)
    print(f"\n{ok}/{total} testes passaram")
    return 0 if ok == total else 1


if __name__ == "__main__":
    sys.exit(main())

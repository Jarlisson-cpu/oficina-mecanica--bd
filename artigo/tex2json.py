"""Converte o artigo-oficina-sbc.tex (estrutura conhecida) em blocos JSON
para o gerador de .docx (gerar_docx.js). Assim o .docx tem exatamente o
mesmo texto do PDF."""
import json, re, sys

src = open(sys.argv[1], encoding="utf-8").read()
body = src[src.index("\\begin{document}"):src.index("\\end{document}")]

# ---------- numeração de figuras/tabelas/citações ----------
labels, nfig, ntab = {}, 0, 0
for m in re.finditer(r"\\begin\{(figure|table|longtable)\}|\\label\{([^}]+)\}", body):
    if m.group(1) in ("figure",):
        nfig += 1; cur = nfig
    elif m.group(1) in ("table", "longtable"):
        ntab += 1; cur = ntab
    elif m.group(2):
        labels[m.group(2)] = str(cur)
cites = {k: str(i + 1) for i, k in enumerate(re.findall(r"\\bibitem\{([^}]+)\}", body))}


def arg(s, i):
    """lê {...} a partir de s[i]=='{'; devolve (conteúdo, posição após)"""
    assert s[i] == "{", s[i:i + 30]
    d, j = 0, i
    while True:
        if s[j] == "\\":
            j += 2; continue
        if s[j] == "{": d += 1
        elif s[j] == "}":
            d -= 1
            if d == 0: return s[i + 1:j], j + 1
        j += 1


SIMPLE = [("\\%", "%"), ("\\_", "_"), ("\\&", "&"), ("\\#", "#"), ("\\$", "$"), ("~", "\u00a0"),
          ("``", "\u201c"), ("''", "\u201d"), ("---", "\u2014"), ("--", "\u2013"),
          ("\\dots{}", "\u2026"), ("\\dots", "\u2026"), ("\\\\", " "), ("\\hfill", ""), ("\\,", "\u202f")]


def math(m):
    m = m.replace("{,}", ",").replace("\\rightarrow", "\u2192").replace("\\ ", " ")
    return m.replace("{", "").replace("}", "")


def runs(s, fmt=None):
    """converte LaTeX inline em lista de runs {t, b, i, code}"""
    fmt = fmt or {}
    out, i, buf = [], 0, ""

    def flush():
        nonlocal buf
        if buf:
            t = buf
            for a, b in SIMPLE: t = t.replace(a, b)
            t = re.sub(r"\s+", " ", t)
            out.append(dict(fmt, t=t))
        buf = ""
    while i < len(s):
        if s.startswith("\\verb", i):
            raise ValueError("verb")
        m = re.match(r"\\(textbf|emph|textit|cod|texttt|cite|ref|url|small|footnotesize|label|textbackslash)\b", s[i:])
        if s[i] == "\\" and i + 1 < len(s) and s[i + 1] in "{}$%&_#":
            buf += s[i + 1]; i += 2; continue
        if s[i] == "$":
            j = s.index("$", i + 1); buf += math(s[i + 1:j]); i = j + 1; continue
        if m:
            cmd = m.group(1); i += len(m.group(0))
            if cmd in ("small", "footnotesize"):
                continue
            if cmd == "textbackslash":
                buf += "\\"; i += 2 if s[i:i + 2] == "{}" else 0; continue
            while i < len(s) and s[i] == " ": i += 1
            c, i = arg(s, i)
            flush()
            if cmd == "textbf": out += runs(c, dict(fmt, b=True))
            elif cmd in ("emph", "textit"): out += runs(c, dict(fmt, i=not fmt.get("i")))
            elif cmd in ("cod", "texttt", "url"): out += runs(c, dict(fmt, code=True))
            elif cmd == "cite": out.append(dict(fmt, t="[" + ",".join(cites[k.strip()] for k in c.split(",")) + "]"))
            elif cmd == "ref": out.append(dict(fmt, t=labels[c]))
            continue
        if s[i] == "{":
            c, i = arg(s, i); flush(); out += runs(c, fmt); continue
        buf += s[i]; i += 1
    flush()
    return [r for r in out if r["t"]]


def tabular_rows(t):
    t = re.sub(r"\\(hline|endfirsthead|endhead|endfoot)", "", t)
    rows = []
    for r in re.split(r"\\\\", t):
        r = r.strip()
        if not r: continue
        rows.append([runs(c.strip()) for c in r.split("&")])
    return rows


blocks = []
# ---------- cabeçalho ----------
center = body[body.index("\\begin{center}"):body.index("\\end{center}")]
linhas = [l for l in re.findall(r"\\bfseries ([^}]*)\}", center)]
blocks.append({"type": "title", "runs": runs(linhas[0])})
blocks.append({"type": "title2", "runs": runs(linhas[1])})
autores = re.search(r"\\normalsize\\bfseries (.*?)\}\\\\", center).group(1)
blocks.append({"type": "authors", "runs": runs(autores.replace("$^{1}$", "\u00b9"))})
prof = re.search(r"\\itshape (.*?)\}\\\\", center).group(1)
blocks.append({"type": "center", "runs": runs(prof, {"i": True}), "size": 20})
aff = re.search(r"\$\^\{1\}\$(.*?)\\\\\{\}", center).group(1)
blocks.append({"type": "center", "runs": [{"t": "\u00b9"}] + runs(aff)})
blocks.append({"type": "center", "runs": runs("Aracaju, Sergipe -- SE")})
email = re.search(r"\\texttt\{(.*)\}\s*\n\s*\}", center).group(1)
blocks.append({"type": "center", "runs": runs(email, {"code": True}), "size": 18})

resto = body[body.index("\\end{center}"):]


def env(name, s):
    a = s.index("\\begin{%s}" % name); b = s.index("\\end{%s}" % name)
    return s[a + len(name) + 8:b], s[b + len(name) + 6:]


res, _ = env("resumo", resto)
blocks.append({"type": "abstract", "label": "Resumo.", "runs": runs(res.strip(), {"i": True})})
kw = re.search(r"\\textbf\{Palavras-chave:\} (.*)", resto).group(1)
blocks.append({"type": "keywords", "runs": [{"t": "Palavras-chave: ", "b": True}] + runs(kw)})
ab, _ = env("abstract", resto)
blocks.append({"type": "abstract", "label": "Abstract.", "runs": runs(ab.strip(), {"i": True})})
kw = re.search(r"\\textbf\{Keywords:\} (.*)", resto).group(1)
blocks.append({"type": "keywords", "runs": [{"t": "Keywords: ", "b": True}] + runs(kw)})

corpo = resto[resto.index("\\section{Introdução}"):resto.index("\\begin{thebibliography}")]
corpo = re.sub(r"(?m)^%.*$", "", corpo)
sec = sub = 0
pos = 0
pat = re.compile(r"\\section\*?\{|\\subsection\{|\\begin\{(figure|table|itemize)\}(\[[^\]]*\])?|\{\\footnotesize[^\n]*\n\\begin\{longtable\}|\n\s*\n")


def para(txt):
    txt = txt.strip()
    if txt:
        blocks.append({"type": "p", "runs": runs(txt)})


while True:
    m = pat.search(corpo, pos)
    if not m:
        para(corpo[pos:]); break
    para(corpo[pos:m.start()])
    g = m.group(0)
    if g.startswith("\\section"):
        t, pos = arg(corpo, m.end() - 1)
        if "*" in g:
            blocks.append({"type": "h1", "runs": runs(t)})
        else:
            sec += 1; sub = 0
            blocks.append({"type": "h1", "runs": [{"t": f"{sec}. "}] + runs(t)})
    elif g.startswith("\\subsection"):
        t, pos = arg(corpo, m.end() - 1); sub += 1
        blocks.append({"type": "h2", "runs": [{"t": f"{sec}.{sub}. "}] + runs(t)})
    elif m.group(1) == "figure":
        e = corpo.index("\\end{figure}", m.end()); f = corpo[m.end():e]; pos = e + 12
        imgs = re.findall(r"\\includegraphics\[width=([.\d]*)\\linewidth\]\{([^}]+)\}", f)
        subcaps = re.findall(r"\{\\footnotesize (.*?)\}\n", f)
        cap = arg(f, f.index("\\caption{") + 8)[0]
        lab = re.search(r"\\label\{([^}]+)\}", f).group(1)
        blocks.append({"type": "figure", "imgs": [(float(w or 1), p) for w, p in imgs],
                       "subcaps": [runs(x) for x in subcaps],
                       "caption": [{"t": f"Figura {labels[lab]}. ", "b": True}] + runs(cap)})
    elif m.group(1) == "table":
        e = corpo.index("\\end{table}", m.end()); f = corpo[m.end():e]; pos = e + 11
        cap = arg(f, f.index("\\caption{") + 8)[0]
        lab = re.search(r"\\label\{([^}]+)\}", f).group(1)
        tb = f[f.index("\\begin{tabular}"):f.index("\\end{tabular}")]
        spec, k = arg(tb, tb.index("}") + 1)
        blocks.append({"type": "table", "caption": [{"t": f"Tabela {labels[lab]}. ", "b": True}] + runs(cap),
                       "spec": spec, "rows": tabular_rows(tb[k:])})
    elif m.group(1) == "itemize":
        e = corpo.index("\\end{itemize}", m.end()); f = corpo[m.end():e]; pos = e + 13
        for it in f.split("\\item")[1:]:
            blocks.append({"type": "bullet", "runs": runs(it.strip())})
    elif "longtable" in g:
        e = corpo.index("\\end{longtable}", m.end()); f = corpo[m.end():e]; pos = corpo.index("}", e + 15) + 1
        spec, k = arg(f, 0)
        cap = arg(f, f.index("\\caption{") + 8)[0]
        lab = re.search(r"\\label\{([^}]+)\}", f).group(1)
        rest = f[f.index("\\endfoot") + 8:]
        hdr = tabular_rows(f[f.index("\\hline"):f.index("\\endfirsthead")])
        blocks.append({"type": "table", "caption": [{"t": f"Tabela {labels[lab]}. ", "b": True}] + runs(cap),
                       "spec": spec, "rows": hdr + tabular_rows(rest)})
    else:
        pos = m.end()

blocks.append({"type": "h1", "runs": [{"t": "Referências"}]})
bib = resto[resto.index("\\begin{thebibliography}"):resto.index("\\end{thebibliography}")]
for n, item in enumerate(bib.split("\\bibitem")[1:], 1):
    item = re.sub(r"^\{[^}]+\}", "", item.strip()).replace("\\newblock", " ")
    blocks.append({"type": "ref", "runs": [{"t": f"[{n}] "}] + runs(item.strip())})

json.dump(blocks, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(blocks), "blocos;", "figuras", nfig, "tabelas", ntab)

"""Gera os PDFs do roteiro da apresentação (completo + um por integrante)."""
import os, subprocess

AQUI = os.path.dirname(os.path.abspath(__file__))

P = {"J": ("Jarlisson Brito Santos", "1B4F8A"), "B": ("Brunno Passos", "2E7D4F"), "C": ("Caio Vinicius", "B4541A")}

SLIDES = [
 ("J", 1, "Capa", "0:00 -- 0:20", "20 s",
  [r"Boa tarde, professor e turma. Nosso tema é a \textbf{oficina mecânica}: o controle das ordens de serviço, das peças usadas e dos mecânicos responsáveis.",
   r"A gente montou o banco em PostgreSQL e provou cada regra com teste."], None, None),
 ("J", 2, "O problema", "0:20 -- 1:20", "1 min",
  [r"Numa oficina que controla tudo em papel ou planilha, seis erros se repetem: placa ou CPF cadastrado duas vezes, peça que sai sem baixa no estoque, ordem de serviço sem mecânico responsável, hodômetro que ``volta'' por erro de digitação, OS já paga sendo alterada depois e o histórico do carro demorando para aparecer.",
   r"O ponto em comum: as regras existem na cabeça das pessoas, mas nada obriga que sejam cumpridas. A nossa ideia foi \textbf{colocar cada regra dentro do banco}. Embaixo de cada card está o recurso que resolve."], None, None),
 ("J", 3, "Arquitetura", "1:20 -- 2:20", "1 min",
  [r"A solução tem três camadas. \textbf{Os usuários}: recepção, mecânico e gerência usam o mesmo banco. \textbf{O PostgreSQL}: os formatos, as seis tabelas, os cinco gatilhos com as regras, uma view que calcula o valor de cada OS e oito índices. \textbf{O GitHub}: cria o banco do zero e roda os 34 testes sozinho a cada atualização."],
  r"Agora o Brunno vai mostrar como o banco foi montado.", None),
 ("B", 4, "Modelo de dados", "2:20 -- 3:20", "1 min",
  [r"São seis tabelas, e a ordem de serviço fica no centro. O cliente tem veículos, o veículo recebe ordens de serviço, e cada OS tem \textbf{um mecânico responsável obrigatório}.",
   r"Três decisões importantes: (1) uma OS tem várias peças e uma peça aparece em várias OS, então criamos a tabela \texttt{os\_peca}, onde a mesma peça não entra duas vezes na mesma OS; (2) o preço da peça é \textbf{copiado} para a OS na hora, então se o catálogo mudar as OS antigas não mudam; (3) o banco não deixa apagar um cliente que tem carro cadastrado."], None, None),
 ("B", 5, "Tipos de dados", "3:20 -- 4:10", "50 s",
  [r"Cada tipo de dado foi escolhido por um motivo e tem um teste. O exemplo mais importante é o dinheiro, que \textbf{nunca} fica em FLOAT. Olhem o duelo: em FLOAT, 0,1 + 0,2 dá \textbf{0,30000000000000004}; em NUMERIC dá \textbf{0,3}, exato.",
   r"Embaixo estão os outros: a placa aceita o padrão antigo e o Mercosul, o status só aceita cinco valores, e CPF e telefone só aceitam números. Cada um tem o código do teste que prova."], None, None),
 ("B", 6, "Regras (gatilhos)", "4:10 -- 5:30", "1 min 20 s",
  [r"Algumas regras dependem de outra tabela, então viraram cinco gatilhos, que são regras automáticas do banco: copiar o preço, bloquear peça em OS fechada, baixar o estoque, aceitar só mecânico ativo sem km voltando, e não reabrir OS fechada.",
   r"O destaque é o estoque. Nesse teste tinha \textbf{1 unidade} e tentamos lançar \textbf{3}. O saldo ficaria \textbf{$-2$}, e o banco recusou com erro. Essa regra vale até para quem mexer no estoque à mão."],
  r"Agora o Caio mostra as provas de que tudo isso funciona.", None),
 ("C", 7, "Testes", "5:30 -- 6:30", "1 min",
  [r"Toda afirmação que fizemos tem teste. São \textbf{34 testes}: 11 de tipos, 13 de restrições e 10 de regras, e \textbf{todos passaram}.",
   r"Nos 26 testes que deveriam dar erro, a gente conferiu o \textbf{código exato} do erro, não só se deu erro. Assim o teste só passa se falhar pelo motivo certo.",
   r"Esse da direita testa o fluxo completo: abre a OS, lança as peças, registra as horas, dá desconto, conclui, e o total sai certinho em \textbf{R\$ 348,40}."],
  None, r"Opcional, se der tempo (30 s): mostrar o GitHub com o selo verde dos testes."),
 ("C", 8, "Índices", "6:30 -- 8:00", "1 min 30 s",
  [r"Índice é como o índice de um livro: em vez de ler o livro inteiro, você vai direto na página. A gente mediu cada consulta antes e depois, rodando sete vezes cada uma, sobre 300 mil ordens de serviço.",
   r"A barra cinza é antes e a laranja é depois. Na busca do histórico pela placa, o tempo caiu de \textbf{30 para 0,25 milissegundo}, cerca de \textbf{120 vezes mais rápido}. Em vez de ler 8.323 páginas, o banco lê só 31.",
   r"Quase todas as barras laranjas somem. A exceção é a B8, e é isso que o próximo slide explica."], None, None),
 ("C", 9, "O que não saiu como esperávamos", "8:00 -- 9:00", "1 min",
  [r"Os resultados mais interessantes foram os que nos surpreenderam:",
   r"\textbf{95\%}: quando a busca pega quase a tabela inteira, o banco \textbf{ignora o índice}, porque ler tudo direto é mais rápido. \textbf{+26\%}: índice tem custo, e cadastrar ficou um pouco mais lento. \textbf{633 vezes}: uma mesma consulta ficou muito mais rápida num caso e mais lenta em outro. \textbf{3.000 $\rightarrow$ 61}: os testes acharam um \textbf{erro nosso} na consulta de estoque, e a gente corrigiu.",
   r"Nenhum desses resultados teria aparecido sem teste."],
  r"Volto com o Jarlisson.", None),
 ("J", 10, "Conclusão", "9:00 -- 9:40", "40 s",
  [r"O trabalho foi organizado em \textbf{cinco sprints semanais} no GitHub, com tarefas, prazos e um quadro de acompanhamento que o professor pode abrir.",
   r"Para concluir, três pontos: as regras da oficina agora estão \textbf{dentro do banco}; \textbf{toda afirmação tem teste}, 34 de 34; e \textbf{índice só entra com medição}."], None, None),
 ("J", 11, "Encerramento", "9:40 -- 10:00", "20 s",
  [r"Esse é o nosso grupo: Jarlisson, Brunno e Caio. Pelo QR code vocês abrem o repositório completo, com o banco, os testes, as evidências e o artigo.",
   r"\textbf{Obrigado! Ficamos à disposição para perguntas.}"], None, None),
]

PERGUNTAS = [
 ("B", "Por que NUMERIC e não FLOAT?", "FLOAT erra a conta; o teste mostra que 0,1 + 0,2 não dá 0,3."),
 ("B", "Por que gatilho e não só CHECK?", "CHECK só olha a própria linha; estoque e km dependem de outra tabela."),
 ("C", "Por que o índice foi ignorado?", "Com 95\\% das linhas, ler a tabela inteira em sequência é mais barato."),
 ("C", "Os dados são reais?", "São fictícios, gerados por script; são 300 mil para o índice fazer diferença."),
 ("C", "Como sabem que o teste está certo?", "Conferimos o código exato do erro, não só se deu erro."),
 ("J", "Como o grupo se organizou?", "Cinco sprints no GitHub, com tarefas, prazos e quadro Kanban."),
 ("J", "E se dois mecânicos usarem a mesma peça ao mesmo tempo?", "Não testamos isso; está nas limitações e nos trabalhos futuros."),
]

DICAS = [r"\textbf{Ensaiem pelo menos 2 vezes com cronômetro.} Se passar de 10 minutos, corte a parte opcional do GitHub no slide 7.",
         r"\textbf{Cada um passa a vez} com a frase de transição (``Agora o Brunno\dots'', ``Agora o Caio\dots'').",
         r"\textbf{Não precisa decorar:} as falas também estão nas anotações de cada slide (modo apresentador).",
         r"Deixem \textbf{o GitHub aberto numa aba} e \textbf{o PDF do artigo} à mão, caso o professor peça um detalhe."]

PREAMBULO = r"""\documentclass[a4paper,11pt]{article}
\usepackage[utf8]{inputenc}\usepackage[T1]{fontenc}
\usepackage{helvet}\renewcommand{\familydefault}{\sfdefault}
\usepackage[a4paper,top=2cm,bottom=2cm,left=2.2cm,right=2.2cm]{geometry}
\usepackage[table]{xcolor}\usepackage{array}\usepackage{enumitem}\usepackage{fancyhdr}
\usepackage{amssymb}\usepackage[most]{tcolorbox}
\definecolor{grafite}{HTML}{1B2130}\definecolor{laranja}{HTML}{E57A2E}\definecolor{cinza}{HTML}{5A5F6B}
\definecolor{cJ}{HTML}{1B4F8A}\definecolor{cB}{HTML}{2E7D4F}\definecolor{cC}{HTML}{B4541A}
\setlength{\parindent}{0pt}\setlength{\parskip}{4pt}
\setlist{itemsep=3pt,topsep=3pt}
\pagestyle{fancy}\fancyhf{}\renewcommand{\headrulewidth}{0pt}
\cfoot{\small\color{cinza}Oficina Mecânica -- Roteiro da apresentação -- \thepage}
\newtcolorbox{slidebox}[3]{enhanced,breakable,colback=#3!4,colframe=#3,boxrule=0.8pt,arc=3pt,
  left=8pt,right=8pt,top=6pt,bottom=6pt,
  title={\bfseries #1\hfill #2},fonttitle=\large,coltitle=white,colbacktitle=#3}
\newtcolorbox{fala}{enhanced,breakable,colback=white,colframe=white,borderline west={3pt}{0pt}{laranja},left=10pt,right=4pt,top=2pt,bottom=2pt}
\newcommand{\passa}[1]{\par\smallskip{\color{laranja}\bfseries $\blacktriangleright$ Passa a vez:} \emph{``#1''}}
\newcommand{\nota}[1]{\par\smallskip{\color{cinza}\small\itshape #1}}
\begin{document}
"""


def bloco(s):
    k, n, tit, tempo, dur, falas, passa, nota = s
    nome = P[k][0]
    out = [r"\begin{slidebox}{Slide %d -- %s}{%s \textbullet{} %s}{c%s}" % (n, tit, tempo, dur, k),
           r"{\small\color{cinza}Apresenta: \textbf{%s}}\par" % nome, r"\begin{fala}"]
    out += [f + r"\par\smallskip" for f in falas]
    out.append(r"\end{fala}")
    if nota:
        out.append(r"\nota{%s}" % nota)
    if passa:
        out.append(r"\passa{%s}" % passa)
    out.append(r"\end{slidebox}")
    return "\n".join(out)


def tabela_divisao(destaque=None):
    linhas = [("J", "1, 2, 3", "0:00 -- 2:20", "Abertura, problema e arquitetura"),
              ("B", "4, 5, 6", "2:20 -- 5:30", "Modelo, tipos e regras"),
              ("C", "7, 8, 9", "5:30 -- 9:00", "Testes, índices e aprendizados"),
              ("J", "10, 11", "9:00 -- 10:00", "Conclusão e encerramento")]
    t = [r"\renewcommand{\arraystretch}{1.5}",
         r"\begin{tabular}{>{\bfseries}p{4.3cm}p{1.8cm}p{2.6cm}p{6cm}}",
         r"\rowcolor{grafite}\textcolor{white}{Quem} & \textcolor{white}{\bfseries Slides} & \textcolor{white}{\bfseries Tempo} & \textcolor{white}{\bfseries Parte}\\"]
    for k, sl, tp, pt in linhas:
        cor = r"\rowcolor{c%s!12}" % k if destaque in (None, k) else ""
        t.append(r"%s\textcolor{c%s}{%s} & %s & %s & %s\\" % (cor, k, P[k][0], sl, tp, pt))
    t.append(r"\end{tabular}")
    return "\n".join(t)


def tabela_perguntas(filtro=None):
    t = [r"\renewcommand{\arraystretch}{1.45}",
         r"\begin{tabular}{p{5.6cm}p{2.9cm}p{6.2cm}}",
         r"\rowcolor{grafite}\textcolor{white}{\bfseries Pergunta} & \textcolor{white}{\bfseries Responde} & \textcolor{white}{\bfseries Resposta curta}\\"]
    for k, q, a in PERGUNTAS:
        if filtro and k != filtro:
            continue
        t.append(r"%s & \textcolor{c%s}{\bfseries %s} & %s\\" % (q, k, P[k][0].split()[0], a))
    t.append(r"\end{tabular}")
    return "\n".join(t)


def cabecalho(titulo, sub, cor="laranja"):
    return (r"\begin{tcolorbox}[colback=grafite,colframe=grafite,arc=4pt,left=14pt,right=14pt,top=12pt,bottom=12pt]"
            r"{\color{%s}\small\bfseries PROJETO DE BANCO DE DADOS \textbullet{} TEMA 07}\\[2pt]"
            r"{\color{white}\fontsize{26}{30}\selectfont\bfseries %s}\\[4pt]"
            r"{\color{white!80!grafite}\large %s}\end{tcolorbox}" % (cor, titulo, sub))


def dicas():
    return r"\section*{\color{grafite}Dicas para o ensaio}" + r"\begin{itemize}" + "".join(r"\item " + d for d in DICAS) + r"\end{itemize}"


def compila(nome, corpo):
    tex = os.path.join(AQUI, nome + ".tex")
    open(tex, "w").write(PREAMBULO + corpo + "\n\\end{document}\n")
    for _ in range(2):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", nome + ".tex"], cwd=AQUI,
                       capture_output=True, check=True)
    for ext in ("aux", "log", "out"):
        p = os.path.join(AQUI, f"{nome}.{ext}")
        if os.path.exists(p):
            os.remove(p)
    print("ok", nome)


# ---------- roteiro completo ----------
corpo = [cabecalho("Roteiro da apresentação", "Oficina Mecânica \\textbullet{} 11 slides \\textbullet{} 10 minutos \\textbullet{} 3 apresentadores"),
         r"\section*{\color{grafite}Divisão}", tabela_divisao(), r"\bigskip"]
for s in SLIDES:
    corpo.append(bloco(s))
corpo += [r"\newpage\section*{\color{grafite}Perguntas: quem responde o quê}", tabela_perguntas(), dicas()]
compila("roteiro-completo", "\n".join(corpo))

# ---------- um por integrante ----------
for k, arq in (("J", "roteiro-jarlisson"), ("B", "roteiro-brunno"), ("C", "roteiro-caio")):
    nome = P[k][0]
    meus = [s for s in SLIDES if s[0] == k]
    total = {"J": "3 min 20 s", "B": "3 min 10 s", "C": "3 min 30 s"}[k]
    corpo = [cabecalho("Roteiro do " + nome.split()[0], "Sua parte: slides %s \\textbullet{} cerca de %s"
                       % (", ".join(str(s[1]) for s in meus), total), "c" + k),
             r"\section*{\color{grafite}Onde você entra}", tabela_divisao(k), r"\bigskip"]
    if k == "B":
        corpo.append(r"\nota{Você entra depois que o Jarlisson diz: ``Agora o Brunno vai mostrar como o banco foi montado.''}\par\medskip")
    if k == "C":
        corpo.append(r"\nota{Você entra depois que o Brunno diz: ``Agora o Caio mostra as provas de que tudo isso funciona.''}\par\medskip")
    if k == "J":
        corpo.append(r"\nota{Você abre (slides 1 a 3) e volta no final (slides 10 e 11), depois que o Caio diz: ``Volto com o Jarlisson.''}\par\medskip")
    for s in meus:
        corpo.append(bloco(s))
    corpo += [r"\section*{\color{grafite}Perguntas que você responde}", tabela_perguntas(k), dicas()]
    compila(arq, "\n".join(corpo))

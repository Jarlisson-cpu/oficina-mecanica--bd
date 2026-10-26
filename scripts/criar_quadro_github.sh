#!/usr/bin/env bash
# Cria no GitHub: labels, 5 sprints (milestones), o backlog (issues) e o quadro Kanban (Projects).
# Pré-requisitos: GitHub CLI autenticado ->  gh auth login  &&  gh auth refresh -s project
# Uso (na pasta do repositório já publicado):  ./scripts/criar_quadro_github.sh
set -euo pipefail
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
DONO=${REPO%%/*}
echo "Repositório: $REPO"

# ---------- labels ----------
lbl() { gh label create "$1" --color "$2" --description "$3" --force >/dev/null; }
lbl historia   1d76db "História de usuário"
lbl tarefa     c5def5 "Tarefa técnica"
lbl modelagem  5319e7 "Modelo conceitual/lógico"
lbl sql        0e8a16 "DDL, triggers, consultas"
lbl teste      fbca04 "Teste e evidência"
lbl indice     d93f0b "Índices e desempenho"
lbl artigo     b60205 "Artigo SBC"
lbl apresentacao 006b75 "Slides e ensaio"

# ---------- sprints (milestones) ----------
ms() { gh api "repos/$REPO/milestones" -f title="$1" -f due_on="$2T23:59:00Z" -f description="$3" >/dev/null 2>&1 || true; }
ms "Sprint 1 - Problema e modelagem"   2026-11-01 "Escolha do tema, levantamento do problema, DER"
ms "Sprint 2 - Implementação"          2026-11-08 "DDL, domínios, triggers, carga de dados"
ms "Sprint 3 - Testes e índices"       2026-11-15 "34 testes, EXPLAIN ANALYZE antes/depois"
ms "Sprint 4 - Artigo"                 2026-11-22 "Artigo SBC com evidências"
ms "Sprint 5 - Revisão e apresentação" 2026-11-30 "Slides, ensaio de 10 min, apresentação 30/11"

# ---------- quadro Kanban (GitHub Projects) ----------
NUM=$(gh project create --owner "$DONO" --title "Oficina Mecânica - BD" --format json -q .number)
gh project link "$NUM" --owner "$DONO" --repo "$REPO" >/dev/null || true
URL=$(gh project view "$NUM" --owner "$DONO" --format json -q .url)
echo "Quadro: $URL  (a coluna Status já vem com Todo / In Progress / Done)"

# ---------- backlog ----------
iss() { # titulo | labels | sprint | corpo
  u=$(gh issue create --title "$1" --label "$2" --milestone "$3" --body "$(printf '%b' "$4")")
  gh project item-add "$NUM" --owner "$DONO" --url "$u" >/dev/null
  echo "  + $1"
}
S1="Sprint 1 - Problema e modelagem"; S2="Sprint 2 - Implementação"; S3="Sprint 3 - Testes e índices"
S4="Sprint 4 - Artigo"; S5="Sprint 5 - Revisão e apresentação"

iss "Descrever o problema real da oficina" "tarefa,modelagem" "$S1" "Problemas do controle em papel/planilha: placa duplicada, peça usada sem baixa, OS sem responsável, histórico lento. Saída: seção 1 do artigo."
iss "DER: CLIENTE, VEICULO, MECANICO, ORDEM_SERVICO, PECA, OS_PECA" "tarefa,modelagem" "$S1" "Saída: docs/diagramas/der.mmd + der.png"
iss "Definir tipos e domínios (placa, CPF/CNPJ, dinheiro, telefone, status)" "tarefa,modelagem" "$S1" "Justificar NUMERIC x FLOAT, ENUM x tabela, CHAR(7) para placa."
iss "Como recepção, quero cadastrar cliente e veículo sem duplicar placa/CPF" "historia,sql" "$S2" "- [ ] UNIQUE placa, chassi, CPF/CNPJ\n- [ ] domínios de formato\n- [ ] testes T01-T05, T10, T11, R02, R03"
iss "Como recepção, quero abrir OS sempre com mecânico responsável e km coerente" "historia,sql" "$S2" "- [ ] FK + NOT NULL id_mecanico\n- [ ] trigger mecânico ativo e hodômetro\n- [ ] testes G05, G06"
iss "Como mecânico, quero lançar peças e o estoque baixar sozinho" "historia,sql" "$S2" "- [ ] trigger baixa/estorno\n- [ ] CHECK estoque >= 0\n- [ ] preço congelado\n- [ ] testes G01-G03, G08"
iss "Como gerência, quero que OS concluída não seja alterada" "historia,sql" "$S2" "- [ ] CHECKs de data/status/desconto\n- [ ] trigger ciclo de vida\n- [ ] testes R07-R09, G04, G07"
iss "Script de carga com 300 mil OS (dados sintéticos reproduzíveis)" "tarefa,sql" "$S2" "sql/03_carga_dados.sql com setseed"
iss "Automatizar 34 testes com captura de tela" "tarefa,teste" "$S3" "scripts/executar_testes.py -> evidencias/"
iss "Medir índices com EXPLAIN ANALYZE antes/depois" "tarefa,indice" "$S3" "scripts/medir_indices.py -> indices_antes_depois.csv"
iss "Comparar view GROUP BY x LATERAL" "tarefa,indice" "$S3" "scripts/comparar_views.py"
iss "Consultas de negócio C01-C08 (relatórios)" "tarefa,sql" "$S3" "faturamento, ranking, estoque, retrabalho"
iss "GitHub Actions rodando tudo a cada push" "tarefa,teste" "$S3" ".github/workflows/testes.yml"
iss "Artigo: Introdução e Trabalhos Relacionados" "tarefa,artigo" "$S4" ""
iss "Artigo: Metodologia, Resultados (tabelas e figuras) e Conclusão" "tarefa,artigo" "$S4" ""
iss "Revisão cruzada do artigo e conferência dos números com evidencias/" "tarefa,artigo" "$S5" ""
iss "Slides (10 min) e ensaio cronometrado" "tarefa,apresentacao" "$S5" "Roteiro: problema 1 min, arquitetura 2, testes ao vivo 3, índices 3, conclusão 1"
echo "Concluído. Abra o quadro e arraste as issues entre Todo / In Progress / Done ao longo das sprints."

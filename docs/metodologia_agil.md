# Metodologia ágil do projeto

Adotamos um **Scrum simplificado com quadro Kanban**, tudo dentro do GitHub, para que o professor acompanhe o andamento sem precisar de outra ferramenta.

## Onde o professor acompanha

| O quê | Onde no GitHub |
|---|---|
| Backlog (histórias e tarefas) | **Issues** (rótulos `historia`, `tarefa`, `sql`, `teste`, `indice`, `artigo`) |
| Sprints e prazos | **Milestones**: Sprint 1 a 5, com data de entrega |
| Quadro Kanban | **Projects** → "Oficina Mecânica - BD" (Todo / In Progress / Done) |
| Quem fez o quê | Histórico de **commits** e **Pull Requests** (cada PR fecha uma issue) |
| Prova de que funciona | **Actions**: a cada push o banco é recriado e os 34 testes rodam; as evidências ficam como artefato da execução |

## Sprints (semanais, até a apresentação de 30/11/2026)

| Sprint | Período | Meta | Entregas |
|---|---|---|---|
| 1 | 26/10 – 01/11 | Problema e modelagem | descrição do problema, DER, tipos e domínios |
| 2 | 02/11 – 08/11 | Implementação | `sql/01` a `sql/03`: tabelas, restrições, triggers, carga |
| 3 | 09/11 – 15/11 | Testes e índices | 34 testes, `sql/04_indices.sql`, medições antes/depois, consultas C01–C08 |
| 4 | 16/11 – 22/11 | Artigo | artigo SBC com tabelas e capturas |
| 5 | 23/11 – 30/11 | Revisão e apresentação | revisão cruzada, slides, ensaio de 10 min, **apresentação 30/11 (15h10–18h30)** |

## Ritos (adaptados para um grupo de faculdade)

- **Planejamento** (início de cada sprint, 20 min): o grupo puxa as issues da sprint para a coluna *Todo* e cada uma ganha um responsável (*Assignee*).
- **Daily assíncrona**: comentário curto na issue em andamento — *fiz / vou fazer / impedimento*.
- **Revisão** (fim da sprint): demonstração do que está em *Done*; o GitHub Actions precisa estar verde.
- **Retrospectiva**: 3 linhas na descrição da milestone — *manter / melhorar / experimentar*.

## Definição de Pronto (DoD)

Uma issue só vai para **Done** quando:

1. o SQL ou script está no repositório, via Pull Request revisado por outro integrante;
2. existe um teste automatizado que comprova a regra (`scripts/executar_testes.py` ou `scripts/medir_indices.py`);
3. a evidência (captura PNG ou CSV) está em `evidencias/`;
4. o GitHub Actions passou.

> Regra do professor aplicada como DoD: **"opinião sem teste não conta ponto"** — nenhuma afirmação entra no artigo sem um arquivo em `evidencias/` que a sustente.

## Como criar o quadro

Com o repositório publicado e o GitHub CLI autenticado (`gh auth login` e `gh auth refresh -s project`):

```bash
./scripts/criar_quadro_github.sh
```

O script cria os rótulos, as 5 milestones, 17 issues já distribuídas nas sprints e o quadro do GitHub Projects ligado ao repositório.

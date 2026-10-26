#!/usr/bin/env bash
# Recria o banco do zero e gera TODAS as evidências.
# Pré-requisitos: PostgreSQL 16 (psql no PATH), Python 3 + Pillow.
# Conexão via variáveis padrão do libpq: PGHOST, PGUSER, PGPASSWORD, PGDATABASE (padrão: oficina)
set -euo pipefail
cd "$(dirname "$0")/.."
export PGDATABASE="${PGDATABASE:-oficina}"
echo "== 1/6 Estrutura (DDL)";          psql -X -q -v ON_ERROR_STOP=1 -f sql/01_ddl.sql 2>/dev/null
echo "== 2/6 Regras e triggers";        psql -X -q -v ON_ERROR_STOP=1 -f sql/02_regras_triggers.sql
echo "== 3/6 Carga de dados";           psql -X -q -v ON_ERROR_STOP=1 -f sql/03_carga_dados.sql > /dev/null
echo "== 4/6 Testes de tipos/restrições/regras"; python3 scripts/executar_testes.py
echo "== 5/6 Índices antes x depois";   python3 scripts/medir_indices.py
python3 scripts/comparar_views.py
echo "== 6/6 Consultas de negócio";     python3 scripts/executar_consultas.py > /dev/null
echo "Pronto. Veja evidencias/resultados e evidencias/capturas."

@echo off
REM ======================================================================
REM  Oficina Mecanica - roda TUDO no Windows (banco, carga, testes, indices)
REM  Requisitos: PostgreSQL 16 (ou mais novo) e Python 3 com Pillow
REM     pip install pillow
REM  Uso: de dois cliques neste arquivo (ou rode no Prompt de Comando).
REM ======================================================================
chcp 65001 >nul
setlocal
set PYTHONUTF8=1
set PGCLIENTENCODING=UTF8
if "%PGUSER%"=="" set PGUSER=postgres
if "%PGHOST%"=="" set PGHOST=localhost
set PGDATABASE=oficina

REM --- encontra o psql se ele nao estiver no PATH ---
where psql >nul 2>nul
if errorlevel 1 (
  for %%V in (18 17 16 15) do (
    if exist "C:\Program Files\PostgreSQL\%%V\bin\psql.exe" (
      set "PATH=C:\Program Files\PostgreSQL\%%V\bin;%PATH%"
      goto achou
    )
  )
  echo [ERRO] psql nao encontrado. Instale o PostgreSQL: https://www.postgresql.org/download/windows/
  goto erro
)
:achou

where python >nul 2>nul
if errorlevel 1 (
  echo [ERRO] Python nao encontrado. Instale em https://www.python.org/downloads/ e marque "Add to PATH".
  goto erro
)

if "%PGPASSWORD%"=="" set /p PGPASSWORD=Senha do usuario postgres (a que voce criou na instalacao):

cd /d "%~dp0\.."

echo.
echo == 0/6 Criando o banco "oficina" (se ainda nao existir)
psql -X -q -d postgres -c "CREATE DATABASE oficina" 2>nul

echo == 1/6 Estrutura (DDL)
psql -X -q -v ON_ERROR_STOP=1 -f sql/01_ddl.sql 2>nul || goto erro
echo == 2/6 Regras e triggers
psql -X -q -v ON_ERROR_STOP=1 -f sql/02_regras_triggers.sql || goto erro
echo == 3/6 Carga de dados (300 mil OS - leva de 30 s a 2 min)
psql -X -q -v ON_ERROR_STOP=1 -f sql/03_carga_dados.sql >nul || goto erro
echo == 4/6 Testes de tipos, restricoes e regras
python scripts\executar_testes.py || goto erro
echo == 5/6 Indices antes x depois
python scripts\medir_indices.py || goto erro
python scripts\comparar_views.py || goto erro
echo == 6/6 Consultas de negocio
python scripts\executar_consultas.py >nul || goto erro

echo.
echo ================================================================
echo  PRONTO! Resultados em evidencias\resultados e evidencias\capturas
echo ================================================================
pause
exit /b 0

:erro
echo.
echo [ERRO] A execucao parou. Leia a mensagem acima.
pause
exit /b 1

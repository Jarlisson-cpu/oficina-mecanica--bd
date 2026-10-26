| ID | Categoria | Teste | Esperado | Obtido | Resultado |
|---|---|---|---|---|---|
| T01 | Tipo | Placa com 8 caracteres não cabe em CHAR(7) | ERRO 22001 | ERRO 22001 | ✅ PASSOU |
| T02 | Tipo | Placa fora do padrão (domínio dm_placa) | ERRO 23514 | ERRO 23514 | ✅ PASSOU |
| T03 | Tipo | Placa Mercosul válida é aceita | OK | OK | ✅ PASSOU |
| T04 | Tipo | Texto em coluna SMALLINT (ano) | ERRO 22P02 | ERRO 22P02 | ✅ PASSOU |
| T05 | Tipo | Ano 40000 estoura o limite de SMALLINT | ERRO 22003 | ERRO 22003 | ✅ PASSOU |
| T06 | Tipo | Valor acima de NUMERIC(10,2) é rejeitado | ERRO 22003 | ERRO 22003 | ✅ PASSOU |
| T07 | Tipo | NUMERIC(10,2) arredonda 10,555 para 10,56 (sem erro de ponto flutuante) | OK | OK | ✅ PASSOU |
| T08 | Tipo | Status fora do ENUM status_os | ERRO 22P02 | ERRO 22P02 | ✅ PASSOU |
| T09 | Tipo | Data inexistente (30/02) em TIMESTAMP | ERRO 22008 | ERRO 22008 | ✅ PASSOU |
| T10 | Tipo | CPF com pontuação viola o domínio dm_doc | ERRO 23514 | ERRO 23514 | ✅ PASSOU |
| T11 | Tipo | Telefone com letras viola o domínio dm_telefone | ERRO 23514 | ERRO 23514 | ✅ PASSOU |
| R01 | Restrição | NOT NULL: cliente sem nome | ERRO 23502 | ERRO 23502 | ✅ PASSOU |
| R02 | Restrição | UNIQUE: CPF/CNPJ repetido | ERRO 23505 | ERRO 23505 | ✅ PASSOU |
| R03 | Restrição | UNIQUE: placa repetida | ERRO 23505 | ERRO 23505 | ✅ PASSOU |
| R04 | Restrição | FOREIGN KEY: veículo de cliente inexistente | ERRO 23503 | ERRO 23503 | ✅ PASSOU |
| R05 | Restrição | ON DELETE RESTRICT: excluir cliente que tem veículos | ERRO 23503 | ERRO 23503 | ✅ PASSOU |
| R06 | Restrição | CHECK: km do veículo negativo | ERRO 23514 | ERRO 23514 | ✅ PASSOU |
| R07 | Restrição | CHECK: conclusão antes da abertura | ERRO 23514 | ERRO 23514 | ✅ PASSOU |
| R08 | Restrição | CHECK: OS CONCLUIDA sem data de conclusão | ERRO 23514 | ERRO 23514 | ✅ PASSOU |
| R09 | Restrição | CHECK: desconto maior que a mão de obra | ERRO 23514 | ERRO 23514 | ✅ PASSOU |
| R10 | Restrição | PRIMARY KEY composta: mesma peça duas vezes na OS | ERRO 23505 | ERRO 23505 | ✅ PASSOU |
| R11 | Restrição | CHECK: quantidade zero de peça | ERRO 23514 | ERRO 23514 | ✅ PASSOU |
| R12 | Restrição | CHECK: e-mail sem @ | ERRO 23514 | ERRO 23514 | ✅ PASSOU |
| R13 | Restrição | ON DELETE CASCADE: excluir OS aberta remove seus itens | OK | OK | ✅ PASSOU |
| G01 | Regra | Lançar peça na OS baixa o estoque automaticamente | OK | OK | ✅ PASSOU |
| G02 | Regra | Estoque insuficiente bloqueia o lançamento | ERRO 23514 | ERRO 23514 | ✅ PASSOU |
| G03 | Regra | Preço da peça é copiado do catálogo quando omitido | OK | OK | ✅ PASSOU |
| G04 | Regra | OS CONCLUIDA não aceita novas peças | ERRO P0001 | ERRO P0001 | ✅ PASSOU |
| G05 | Regra | Mecânico inativo não pode assumir OS | ERRO P0001 | ERRO P0001 | ✅ PASSOU |
| G06 | Regra | Hodômetro não pode voltar (km_entrada < km_atual) | ERRO P0001 | ERRO P0001 | ✅ PASSOU |
| G07 | Regra | OS CONCLUIDA não pode ser reaberta | ERRO P0001 | ERRO P0001 | ✅ PASSOU |
| G08 | Regra | Cancelar a OS devolve as peças ao estoque | OK | OK | ✅ PASSOU |
| G09 | Regra | Mão de obra = horas trabalhadas x valor/hora do mecânico | OK | OK | ✅ PASSOU |
| G10 | Regra | Fluxo completo: abrir, lançar peças, concluir e faturar | OK | OK | ✅ PASSOU |

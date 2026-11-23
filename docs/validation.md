# Verificação da implementação — 23/11/2026

## Cinco sugestões em quatro commits

| Commit | Sugestões atendidas | Evidência de conclusão |
|---|---|---|
| 1 — Contrato de dados reproduzível | 26/10: conectar preparação e exploração | Notebook 01 gera os nomes/colunas consumidos pelo 02; caminhos funcionam da raiz e de `notebook/`; testes de cobertura, integração e reconciliação |
| 2 — População alinhada a 2021 | 09/11: recalcular per capita e mostrar sensibilidade | Arquivo oficial fixado; população reconciliada com UFs; seis posições alteradas; numerador invariável; gráfico de pontos e CSV comparativo |
| 3 — Análises setoriais | 03/11: decompor 2003/2009; 16/11: cruzar UF/setor | Duas cascatas reconciliadas; tabela UF/setor com cobertura explícita; composição dos dez maiores emissores e três comparações calculadas no notebook |
| 4 — Brutas/líquidas e documentação | 23/11: definir e comparar os indicadores | Sinais validados; NCI/bunkers excluídos; ponte bruto→líquido; fontes e hashes; README com achados, imagens, instruções e limites |

## Verificações executadas

- Os dois notebooks executados em kernels novos na ordem 01→02, sem erro de célula, a partir da raiz e de `notebook/`. O executor salva as saídas e valida o formato dos notebooks.
- Onze testes aprovados com `python -m unittest discover -s tests -v`. Incluem comparação dos CSVs exportados com a fonte, reconciliação de deltas, controles de população e testes negativos para sinais e integração.
- Figuras novas de sensibilidade, decomposição, composição estadual, série histórica e bruto/líquido inspecionadas como PNGs. Gráficos legados exportados com títulos e fontes explícitos.
- Prévia HTML dos notebooks gerada. A abertura no navegador local ficou indisponível por restrições do ambiente; a inspeção visual foi feita nos PNGs, sem alegar revisão interativa do HTML.

## Limites preservados

- Edição histórica SEEG 10, sem atualização para novas coleções.
- Ausências de Processos Industriais em AC, AP e RR permanecem ausentes, com sinalização de cobertura.
- Parcela sem alocação estadual permanece nos totais nacionais, separada dos rankings das UFs.
- Antes de 1990, o total tem cobertura setorial parcial. Decomposição não demonstra causalidade.
- População de 2022 preservada como comparação metodológica; o indicador principal usa julho de 2021.

# Definições e limites da análise

## Fontes fixadas

- SEEG 10: arquivo original `data/raw/1-SEEG10_GERAL-BR_UF_2022.10.27-FINAL-SITE.xlsx`, aba `GEE Estados`, série 1970–2021. A edição histórica é preservada; não se mistura com coleções posteriores.
- [Relatório analítico da coleção 10](https://energiaeambiente.org.br/wp-content/uploads/2023/04/SEEG-10-anos-v5.pdf), seção 1 e capítulo de mudanças de uso da terra. Define o saldo líquido descontando remoções em áreas protegidas, vegetação secundária e mudanças de uso da terra. Reporta aproximadamente 2,4 GtCO₂e brutas e 1,76 GtCO₂e líquidas em 2021, GWP-AR5. NCI é discutido separadamente.
- [IBGE, estimativas originais de julho de 2021](https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2021/estimativa_dou_2021.xls). [Tratamento da população](population.md).
- Referências consultadas em 23/11/2026. `sources.json` registra nomes, URLs e SHA-256 dos arquivos brutos.

## Regras contábeis

| Indicador | Seleção | Fórmula |
|---|---|---|
| Brutas | Categoria `Emissão` | Soma de `CO2e (t) GWP-AR5` |
| Remoções assinadas | Categoria `Remoção` | Soma dos valores negativos da fonte |
| Líquidas | As duas categorias anteriores | Brutas + remoções assinadas |
| Per capita | Brutas estaduais / população da mesma UF | tCO₂e por habitante; ambos de 2021 |

`Emissão NCI`, `Remoção NCI` e `Bunker` são excluídos dos indicadores principais e do balanço líquido. Não se somam gases físicos com equivalências CO₂e ou métricas GWP/GTP distintas. O código valida a convenção negativa das remoções. Pequenos valores negativos presentes na categoria `Emissão` são mantidos conforme a classificação original; não são reclassificados silenciosamente.

## Nacional versus estadual

O bruto filtrado não possui uma linha agregada `BR`. O nacional é a soma de todos os registros elegíveis, incluindo os sem UF. Somente os registros atribuídos às 27 UFs entram em rankings e composição estadual. A reconciliação correta é **nacional = soma das UFs + sem alocação**. A existência de um agregado `BR` nas categorias incluídas faz a execução falhar para revisão; ele nunca é somado automaticamente.

## Comparabilidade e interpretação

Mudança de Uso da Terra e Floresta possui cobertura a partir de 1990. Os valores anteriores não equivalem a um total de mesma cobertura: zeros de MUT nesse período não representam ausência de emissões. As taxas nacionais comparáveis começam em 1991.

As decomposições 2002→2003 e 2008→2009 são contábeis. As contribuições em pontos percentuais dividem cada delta setorial pelo total nacional do ano inicial; sua soma é a taxa nacional. Elas não estabelecem causalidade de políticas, crises ou desmatamento. A composição UF/setor usa o total bruto de cada UF como denominador. Per capita mede uma razão territorial, não uma pegada pessoal de consumo.

## Validação

`python -m unittest discover -s tests -v` verifica reconciliação com a fonte, 27 UFs, municípios únicos, população oficial, invariância do numerador, componentes setoriais, rejeição da quebra 1989→1990 e sinais das remoções. Valores reconciliados usam tolerância relativa de 1e-12 e absoluta até 1e-6 tCO₂e. Exportações já equivalentes são preservadas para evitar alterações de serialização sem mudança analítica.

# Decomposições setoriais

Os CSVs `decomposicao_setorial_historica.csv` e `emissao_uf_setor_2021.csv` são gerados pelo notebook 01 a partir do mesmo recorte bruto GWP-AR5.

Na decomposição histórica, os deltas de cada setor somam a variação nacional. `Contribuicao_pp` divide o delta pelo total nacional inicial, em pontos percentuais. Essa leitura é contábil, sem atribuição causal. O nacional inclui emissões sem alocação estadual.

Na composição estadual, `Participacao_pct` divide as emissões do setor pelo total registrado da própria UF. O CSV contém 135 combinações (27 UFs × 5 setores). Três delas — Processos Industriais em AC, AP e RR — não possuem registros no recorte da fonte. Nessas linhas, emissão e participação permanecem vazias e `Cobertura` informa a ausência; não se presume emissão zero. Os totais estaduais são a soma dos registros disponíveis.

Os dez maiores emissores apresentados nas barras empilhadas têm registros para todos os cinco setores. A função de visualização rejeita ausências nesse subconjunto para evitar que uma barra esconda dados faltantes. Os valores absolutos ao lado das UFs impedem interpretar participações iguais como volumes iguais.

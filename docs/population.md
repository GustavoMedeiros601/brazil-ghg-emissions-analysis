# População e comparabilidade

O indicador principal combina emissões de 2021 com estimativas de população em 1º de julho de 2021, publicadas em agosto de 2021. Arquivo oficial: https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2021/estimativa_dou_2021.xls (consultado em 23/11/2026). A versão original foi fixada para reproduzir a comparação; o diretório do IBGE também contém revisões posteriores.

Os municípios são agregados por UF e reconciliados com a aba `BRASIL E UFs` do mesmo arquivo. População nacional: 213.317.639 habitantes. O parser remove apenas referências de notas entre parênteses e rejeita números inválidos, municípios duplicados ou UFs ausentes.

A fonte legada `POP2022_Municipios.xls` é preservada. O CSV de sensibilidade mantém o numerador de emissões de 2021 constante e compara valores e posições com os dois denominadores. Isso não mede queda de emissões nem crescimento populacional puro: as bases diferem também em metodologia/levantamento. Per capita é uma razão territorial, não uma pegada de consumo pessoal.

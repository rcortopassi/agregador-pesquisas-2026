# Reconstrução do 1º turno de 2010, 2014, 2018 e 2022

Base da aba **Previsão** do painel. Gerado em 21/08/2026.

## O que tem aqui

- `pesquisas_1t_2010_2022.json` — as 390 pesquisas, uma a uma: dia, mês, instituto,
  percentual bruto de cada lado, denominador e os valores já em votos válidos.
- `serie_mensal_1t.json` — a série mensal consolidada (margem, soma dos dois primeiros,
  denominador, nº de institutos e de pesquisas), mais o resultado de urna de cada ciclo.
- `wiki.py`, `extrai.py`, `base.py` — o extrator. Roda `carrega()` do `base.py` para refazer tudo.

## De onde vêm os dados

Tabelas de pesquisas da Wikipédia em português, um artigo por ciclo. 2014 mora em predefinição
transcluída (`Predefinição:Pesquisas de opinião da Eleição presidencial no Brasil em 2014
(1º turno)`), e é por isso que ele parecia não existir. **Não há página de pesquisas de 1998,
2002 nem 2006 em nenhuma das duas Wikipédias**, conferido título por título: quatro ciclos é o
teto desta fonte. O TSE não serve, registra a pesquisa mas nunca o percentual.

## Decisões que não são óbvias

- **Denominador = só colunas de candidato.** É o que "votos válidos" quer dizer, e é a única
  base em que pesquisa e urna se comparam, porque a urna não tem indeciso. Somar a coluna
  "Outros/Nenhum/Não sabe" inflava tudo; em 2010 eu ainda somava a coluna "Vantagem" por engano
  e o denominador dava 122, o que só apareceu quando fui testar se o viés era artefato.
- **Régua igual à do painel:** uma rodada por instituto por mês, a mais recente. Medido: usar
  todas as pesquisas em vez de uma por instituto muda a mediana em 0,7 ponto em agosto, 0,5 em
  setembro e 0,0 em outubro. Pequeno, mas agora é medido e não suposto.
- **2018 exige o cenário com Haddad.** A tabela agrupa cenários por `rowspan` e mistura "com
  Lula" e "sem Lula" na mesma coluna do PT. Sem esse filtro, e sem tratar o `rowspan` e as
  células escritas inline com `||`, o extrator perdia 220 das 300 linhas de 2018.
- **Agosto de 2018 não é análogo de nada.** O candidato do PT era o Lula até 11/09, então o
  Haddad de agosto é um nome quase desconhecido: os dois projetados somam mais de 100. O peso
  por semelhança já o zera sozinho, e a tabela do painel troca o número por um traço.

## Conferência

O extrator reproduz números que os próprios institutos publicaram em válidos:
Datafolha final de 2022 (Lula 50 x Bolsonaro 36) sai 50,5 x 35,8; Ibope final de 2014
(Dilma 46 x Aécio 27) sai 45,5 x 27,3.

## 2026 incluído (05/10/2026)

Urna final do TSE (100% das seções, 05/10 02h59): Flávio 47,03 x Lula 45,16 em válidos.
`inclui_2026.py` acrescenta a chave `2026` às duas bases, pela mesma régua, tirando as pesquisas
do próprio `DI` do painel (já é uma rodada por instituto por mês; por isso `npesq` = `ninst`).
Denominador = 100 menos Br/N/Ind. Ficam fora linhas sem Br/N/Ind, sem Flávio, com valor
estimado (`*`) ou de outro cenário (`†`): jan Paraná, Meio/Ideia, Quaest e mai AtlasIntel.
No painel: `VH1DET` ganhou 2026 (finais com campo a partir de 25/9), `HIST1T['2026']` (fora de
`CICLOS1T`), terceiro elemento em `HERR`/`HERRN`, `HERRINST2026` e `PRES2026`. `CICLO_ATUAL=2026`
impede o ciclo em curso de entrar no próprio ajuste. Em 2030: trocar `CICLO_ATUAL` para 2030,
pôr '2026' em `CICLOS1T` e refazer `HERRINST` a partir desta base.

# Agregador de Pesquisas Presidenciais 2026 — Metodologia

Painel próprio, inspirado no RealClearPolitics (visual) e no FiveThirtyEight (estatística), para consolidar as pesquisas de intenção de voto para presidente em 2026.

Arquivo do painel: `electoralpolls.html` (abre no navegador, dados embutidos no JS; seletor por mês; abre SEMPRE no mês mais recente).

## ATENÇÃO — estado atual do painel (NÃO REVERTER)

- LOTE DATAFOLHA DE 21/08/2026, E O ESCOPO QUE O RADAR ERRA (21/08/2026). O Datafolha (CNPJ 07630546000175, que no CSV do TSE vem com `NM_EMPRESA_FANTASIA` = `#NULO#`) divulgou em 21/08 a primeira leva das 130 pesquisas que Globo e Folha anunciaram até 3 de outubro: uma nacional (BR-04496/2026, N=2058, campo 18 a 20/8) e as estaduais de SP, MG, RJ, PE, DF e PI. Entraram no painel a nacional e o governo/senado de SP, MG, RJ, PE e DF. Duas coisas para o próximo agente:

  1. O ESCOPO `ESTADUAL[UF]` DO RADAR NÃO É CONFIÁVEL QUANDO VÁRIOS REGISTROS COMPARTILHAM CNPJ, DATAS E N. O `radar_tse.py` casa o gêmeo por (CNPJ, início, fim, N). Neste lote, MG, RJ e PE têm os três exatamente iguais (1.204 entrevistas, 18 a 21/8, mesmo CNPJ), então o desempate cai no primeiro gêmeo encontrado e os três presidenciais saíram rotulados como `ESTADUAL[MG]` numa rodada e `ESTADUAL[RJ]` na fila da anterior. O rótulo estava errado nas duas. Quem manda é a coluna `DS_DADO_MUNICIPIO` do CSV, que diz em texto de qual estado é a amostra: BR-04396 é MINAS GERAIS, BR-08448 é RIO DE JANEIRO e BR-00109 é PERNAMBUCO. Confira sempre essa coluna antes de escrever UF no `PRES26`.

  2. AS DATAS DA MATÉRIA DIVERGEM DAS DO REGISTRO, E VALE O REGISTRO. Para a mesma pesquisa de SP o Poder360 e o g1 escrevem "18 a 19 de agosto", para MG e PE escrevem "18 a 20", e o TSE registra 18 a 21/8 nos três. Foi usado o TSE (`18-21 ago`), que é a regra do `AGENTS.md`. Só a nacional é mesmo 18 a 20/8, e aí matéria e registro coincidem.

- REGISTRO COM DIVULGAÇÃO VENCIDA NO MESMO DIA NÃO É "NÃO PUBLICOU" (21/08/2026). Os seis presidenciais por estado desse lote (BR-07185 SP, BR-04396 MG, BR-08448 RJ, BR-00109 PE, BR-02094 DF, BR-05672 PI) estavam registrados com divulgação 21/08 e às 21h50 daquele dia NENHUM tinha número publicado: Globo e Folha soltaram governo, senado e avaliação primeiro, e seguraram o presidencial por estado. NÃO resolver esses itens como descartados no dia da divulgação, porque o número costuma sair na manhã seguinte e a fila é o único lugar que lembra deles. O mesmo vale para a nacional da Veritá BR-04006/2026 (N=3840, campo 16 a 20/8): em 21/08 a home `eleicoes26.institutoverita.com.br` respondia "Nenhuma pesquisa publicada ainda".

- PESQUISA MUNICIPAL DISFARÇADA DE ESTADUAL (21/08/2026). O radar do TSE traz escopo `PI`, `MT`, `BA` e afins quando os CARGOS pesquisados são estaduais e federais, e isso NÃO diz nada sobre a área da amostra. Existe um caso frequente de registro cujo escopo lê como estadual mas cuja amostra é de UM município só, e ele não pode entrar em `DG`, `DS`, `DGM`, `DSM` nem `PRES26`: seria um vilarejo passando por estado inteiro no mapa. O caso que descobriu o padrão é o Instituto Estimativa, registros PI-04138/2026 (governador e senador) e BR-09479/2026 (presidente), N=301, divulgados em 21/08/2026 pelo Portal R10: são 301 eleitores da cidade de JAICÓS, e o Portal R10 diz isso no título ("Rafael Fonteles lidera corrida para o Governo do Estado em Jaicós com 48,84%", "Lula lidera com 73,09% ... em Jaicós"). Nenhum dos dois foi inserido.

  O TESTE BARATO, que dispensa abrir a matéria, é a coluna `DS_DADO_MUNICIPIO` do CSV `pesquisa_eleitoral_2026_*.csv`. Quando o registro é mesmo estadual ou nacional, ela traz texto de metodologia (RDD telefônico, domicílio eleitoral, "municípios das cinco grandes regiões") ou vem `#NULO#`. Quando é municipal, ela lista BAIRROS. No caso do Estimativa vem "ZONA URBANA JOSÉ ARMINIO 32, COHAB 10, NOVA OLINDA 20, ALTO DO ADÃO 10, MATADOURO 8, CENTRO 30, SERRANÓPOLES 45. ZONA RURAL: BOA VISTA 8, CROZAL 18...". Bairro na coluna de município é o sinal. N pequeno (aqui 301) reforça, mas não basta sozinho: há pesquisa estadual pequena e há municipal grande.

  Isto é o análogo ESTADUAL do falso positivo de nacional que o `AGENTS.md` já registra (Futura/Apex BR-08054/2026, que é de 291 municípios mineiros). Um outro registro na mesma família, ainda em aberto em 21/08/2026, é o MT-02422/2026 da Meta Publicidade (senador, N=500, contratante Barra Produções), cuja coluna de município diz só "EM ANEXO" e cujo número não foi achado publicado: não resolver como estadual sem antes ver a abrangência.

- BLOCO DE DEBATES (21/08/2026, pedido do usuário). Objeto `DEBATES` e faixa `#debates`, logo abaixo da faixa do calendário eleitoral. Traz os quatro debates presidenciais de 1º turno com data, hora, canal de TV, onde assistir na internet, quem vai e quem falta, e o vídeo AO VIVO embutido na própria página, no modelo da live do Kilauea. NÃO apagar por "não ser dado de pesquisa": foi pedido explicitamente. Três coisas que o próximo agente precisa saber:
  1. O embed usa `youtube-nocookie.com/embed/live_stream?channel=ID`, que toca o que estiver ao vivo NAQUELE canal. É de propósito: id de vídeo de uma transmissão só passa a existir quando ela começa, então fixar id deixaria o quadro quebrado até o dia do debate. Canais usados: Band Jornalismo `UCoa-D_VfMkFrCYodrOC9-mA` e CNN Brasil `UCvdwhh_fDyWccR42-rReZLw`. Record e Globo NÃO anunciaram YouTube, e por isso levam link para R7/RecordPlay e g1, que é o que existe. Não inventar canal para elas.
  2. A lista de quem vai é a parte que apodrece. Cada debate tem o campo `sit` com a data da última conferência, e o painel escreve essa data ao lado da lista. Ao mexer, ATUALIZAR o `sit`. Sem fonte, o nome entra em `conv` (convidado), nunca em `vao` (confirmado).
  3. Cores: o painel já usa vermelho para Lula e azul para Flávio, então o bloco de debates NÃO pode usar esses dois tokens para outra coisa. Ausência é `P.warn`, títulos são `P.ink`, secundário é `P.mut`.

  Situação em 21/08/2026: Band 23/8 às 20h (Renan Santos, Caiado, Cury e Zema confirmados; Lula e Flávio não vão, e a Band mantém o púlpito vazio); A Hora da Decisão 14/9 às 22h, consórcio de 11 veículos, com Lula e Flávio esperados; Record 27/9 às 21h; Globo 1/10 depois do Jornal Nacional. A Record prevê um segundo debate em 18/10 se houver 2º turno.

- TÍTULO DO PAINEL: "Agregador de pesquisas · Eleições 2026", em UMA linha só na faixa dourada do topo e no `<title>`. O painel NÃO tem nome de marca. Histórico curto para não se repetir: em 20/07/2026 o usuário pediu um nome próprio, escolheu "50+1" (limiar de 50% mais um dos votos válidos) e ele foi aplicado com wordmark grande no topo; em 21/07/2026 ele mandou remover de tudo, dizendo que o título "não está bom". NÃO reintroduzir "50+1" nem voltar para "Agregador Brasil". O `apple-mobile-web-app-title` é "Agregador 2026". O favicon (medidor) continua igual, porque é gráfico e não tem texto.
- UMA RODADA POR INSTITUTO POR MÊS (regra reafirmada pelo usuário em 21/07/2026, quando perguntou se "todas as pesquisas" estavam no painel). O `DI` guarda a rodada MAIS RECENTE de cada instituto em cada mês, não todas as rodadas publicadas. NÃO é descuido, é proteção estatística: se todas as rodadas entrassem como linhas separadas, um instituto que publica toda semana entraria com 5 ou 6 linhas no mês enquanto o Datafolha entraria com 1, e a MEDIANA passaria a refletir quem pesquisa mais, não o consenso do campo (PoderData e AtlasIntel, os mais frequentes, dominariam). Foi apresentada ao usuário a alternativa de agregação em DOIS ESTÁGIOS (mediana das rodadas dentro de cada instituto, depois mediana entre institutos), que permitiria incluir tudo sem dar peso extra a ninguém; ele optou por MANTER uma rodada por instituto. Se um dia quiser mudar, é esse o caminho correto, e nunca empilhar linhas.
- COBERTURA NACIONAL CONFERIDA (21/07/2026): 17 institutos distintos e 57 rodadas no `DI` (Alfa, American, Apex/Futura, AtlasIntel, CNT/MDA, Datafolha, Gerp, Indexa, Meio/Ideia, Nexus/BTG, Paraná, PoderData, Quaest, RTBD, Veritá, Vetor/Arrow, Vox Brasil). Isso bate um a um com a lista consolidada de pesquisas presidenciais nacionais de 2026; não há instituto nacional conhecido de fora. `OUTLIERS={}`, então Veritá e Vetor/Arrow contam normalmente. A lacuna real de cobertura é ESTADUAL, não nacional.
- INCERTEZA POR DISTÂNCIA DA ELEIÇÃO (21/07/2026). Objeto `HERR`, linha dourada no banner.
  ORIGEM: o usuário levantou que os institutos ficariam enviesados durante a campanha e
  "consertariam" na pesquisa final, e que medir o house effect só na final captura a fase em
  que eles são mais honestos. Fomos medir. Reconstruímos a série mensal de 2º turno de 2010,
  2018 e 2022 (2014 não tem série: o adversário provável da Dilma era a Marina até setembro;
  2018 idem, o candidato do PT era o Lula até 11/09).
  ACHADO 1, que CONFIRMA a intuição: em 2022 a mediana do campo superestimou o Lula nos DEZ
  meses, sem exceção, indo de +25,3 em janeiro a +2,6 em outubro; e TODOS os 11 institutos com
  série comparável corrigiram na direção do Bolsonaro na rodada final (Quaest −16,1,
  Datafolha −15,7, Ipespe −15,2, CNT/MDA −11,9, Ipec −11,4).
  ACHADO 2, que REFUTA a versão forte: o SINAL NÃO É ESTÁVEL entre ciclos. Em 2010 o campo
  SUBESTIMOU a Dilma quase o ano inteiro (−22,9 em abril, −11,0 em julho) e só passou a
  superestimar em agosto. A correção mediana de última hora foi +2,1 em 2010, +2,8 em 2014,
  +7,6 em 2018 e ~+12 em 2022. Logo, NÃO EXISTE correção direcional defensável, e 2022 é o
  ciclo atípico, não a regra.
  DECISÃO: NÃO alterar o cálculo. Foi apresentada ao usuário a alternativa estilo FiveThirtyEight
  (alargar a faixa de empate técnico em função da distância, o que levaria a faixa de 4,0 para
  ~13 pontos em julho e trocaria "empate técnico" por "corrida indefinida"); ele optou pela
  FORMA CONSERVADORA: manter a conta e ACRESCENTAR CONTEXTO. Motivo: calibrar a curva do 538
  exigiria dezenas de eleições e nós temos duas séries completas, que por acaso erraram em
  direções opostas.
  IMPLEMENTAÇÃO: `HERR` guarda, por mês do ciclo, o erro medido da mediana do campo vs urna em
  2010 e 2022 (votos válidos, margem esquerda menos direita). O banner mostra uma terceira
  linha, em `P.goldtxt`, que acompanha o seletor de mês. NÃO transformar isso em coeficiente
  nem embutir na classificação sem antes ter mais ciclos medidos.
  TENTATIVA DESCARTADA (22/07/2026): cheguei a desenhar a incerteza no GRÁFICO como uma zona
  dourada vertical no mês mais recente (±13, com setas de transbordo), e o usuário viu e
  mandou TIRAR ("ficou ruim"). Removida por completo. A representação da incerteza histórica
  fica SÓ na linha de texto do banner. `HERRN`/`herrAmp` ficaram no código sem uso (dados
  numéricos corretos, podem servir no futuro), mas NÃO reintroduzir a zona no gráfico sem o
  usuário pedir.
  RESSALVA REGISTRADA: os erros históricos foram medidos em VOTOS VÁLIDOS com 15-20% de
  indeciso no campo; a margem do painel está em AMOSTRA TOTAL. Não são a mesma régua, e por
  isso o número entra como CONTEXTO, não como correção.
  PROBLEMA CORRELATO AINDA ABERTO: em jul/2026 o Br/N/Ind varia de 1,2% (AtlasIntel, online)
  a 19% (Quaest, telefone). As margens de 2º turno que entram na mediana NÃO são comparáveis
  entre si pelo mesmo mecanismo. Padronizar a base antes de medianizar resolveria, e é
  defensável sozinho, mas ainda não foi feito.
- PADRONIZAÇÃO EM VOTOS VÁLIDOS (22/07/2026, a pedido do usuário). Objetos `T2R` e função
  `t2valid`. PROBLEMA: cada instituto publica a margem do 2º turno numa base diferente,
  conforme o quanto de indeciso deixa na conta (AtlasIntel online tem 1,2% de Br/N/Ind e
  entrega quase em válidos; Quaest telefone tem 19% e entrega em amostra total, com a margem
  comprimida). Jogar essas margens juntas na mediana mistura réguas. SOLUÇÃO: `T2R` guarda os
  dois números do 2º turno (Lula, Flávio) por instituto; `t2valid` renormaliza sobre os dois
  candidatos, `(L-F)/(L+F)*100`, e aplica o house effect (que foi medido em válidos, então
  casa). O banner mostra os DOIS lados: "Lula +3,0 amostra total · Lula +3,3 votos válidos".
  SUPOSIÇÃO embutida nos válidos: o indeciso se dividiria na mesma proporção dos declarados
  (em 2022 o indeciso final pendeu para o Bolsonaro, então não é neutra) — por isso os dois
  lados ficam visíveis, com a suposição no title/tooltip da palavra "válidos".
  IMPACTO REAL: pequeno. Em julho a mediana foi de +3,0 (total) para +3,3 (válidos). Eu havia
  estimado "+4 ou +5" e ERREI: a conversão infla mais quem tem muito indeciso (Quaest, Indexa),
  mas esses já estão ACIMA da mediana; quem fica no MEIO da fila (RTBD, Nexus) tem indeciso
  moderado e quase não muda. Como a mediana é o valor do meio, ela mal se move.
  ESCOPO: só há pares (`T2R`) para JULHO. Meses anteriores seguem só com a margem bruta até
  se coletar os pares. Esta padronização arruma a comparabilidade ENTRE institutos (eixo 1),
  NÃO o viés do campo inteiro vs urna (eixo 2) — esse continua só endereçado pela linha de
  incerteza histórica (HERR).
- STRESS TEST DO INDECISO e RÓTULO CONDICIONAL (22/07/2026, após revisão comparativa
  internacional). `t2stress` + `STRESS_DIR=0.736`. Os votos válidos assumem rateio proporcional
  do indeciso; em 2022 isso foi falso e caro (Opinião Pública 2024: entre a pesquisa de sábado e
  a urna de domingo do 1º turno, Bolsonaro +7,8 e Lula +2,8, ou seja ~74% do movimento tardio foi
  para a direita). O painel agora mostra os TRÊS números de julho: **+3,0 amostra total, +3,3
  votos válidos, e Flávio +2,2 no cenário de estresse**. O terceiro é o maior modo de falha
  histórico virado número visível. NÃO é previsão; é sensibilidade.
  O rótulo do 2º turno virou "2º turno · cenário", porque antes do 1º turno (4/out) toda
  simulação de 2º turno é condicional: um estudo de 423 eleições em dois turnos achou ~30% de
  viradas do 2º colocado, e o resultado do 1º turno realinha o jogo.
- MARCOS DA CORRIDA SEM DIREÇÃO (06/08/2026, a pedido do usuário). O objeto `PEVENTS` tinha um campo
  `p` ('+'/'-') que virava um selo "favorece Flávio" / "prejudica Lula" na legenda do gráfico e
  distinguia o marcador (círculo vazado para favorece, cheio para prejudica). O usuário mandou TIRAR:
  "isso não é tão fácil de avaliar assim". Dizer que um fato ajudou ou atrapalhou alguém é inferência
  causal sobre uma série que tem ruído amostral maior que o efeito, e o painel não tem como sustentar.
  O QUE FICOU: o selo nomeia apenas de quem é o fato (Lula ou Flávio), que é factual, e a cor `c`
  segue sendo só isso. Todos os marcadores são cheios. NÃO reintroduzir o campo `p`, o selo
  "favorece/prejudica" nem o círculo vazado sem o usuário pedir.
- PLACAR DO 2º TURNO NO BANNER (11/08/2026, a pedido do usuário). Ele perguntou se dava para
  apresentar o cenário de 2º turno do mesmo jeito que o de 1º turno. Dava, e agora o banner traz
  "2º TURNO · CENÁRIO Lula 47,4 · Flávio 43,9", com as duas margens (amostra total e votos
  válidos) descendo para uma linha própria logo abaixo. Função `t2placar`.
  A ARMADILHA, que é o motivo de este parágrafo existir: o caminho óbvio seria tirar a mediana de
  cada lado em separado, como faz o `adjMonth` do 1º turno. NÃO SERVE aqui. A margem que o painel
  publica é o `adj2Month`, que é a MEDIANA DAS MARGENS, e mediana das margens não é igual à
  diferença das medianas de cada lado. Medido: em jul/2026, com 12 institutos, dá 3,9 contra 4,1,
  diferença tolerável; em ago/2026, com 4 institutos, dá 3,5 contra 2,6. Um placar de 46,5 x 43,9
  ao lado de um "+3,5" na mesma tela é o painel se contradizendo, que é exatamente o tipo de erro
  que esta seção existe para evitar.
  SOLUÇÃO ADOTADA: o placar DECOMPÕE a margem oficial em torno de um centro medido. Centro =
  mediana de (Lula+Flávio)/2 entre os institutos do mês, ou seja, quanto da amostra os dois
  ocupam juntos; Lula = centro + margem/2, Flávio = centro − margem/2. A soma é medida de
  verdade, a diferença bate com a margem publicada por construção, e em julho as duas contas
  quase coincidem (46,5/42,5 contra 46,7/42,5), que foi o teste de sanidade.
  ESCOPO: depende do `T2R`, que só tem pares de julho em diante. Nos meses anteriores `t2placar`
  devolve null e o banner volta sozinho ao formato antigo, com a margem em linha. Conferido em
  jun (cai no fallback), jul e ago, no desktop e em 375px.
  NÃO transformar isso em novo agregado: o número que manda continua sendo o `adj2Month`, e o
  placar é apresentação dele. Se um dia se quiser trocar o estimador, o lugar é o `adj2Month`,
  e aí muda banner, gráfico e síntese juntos, que é decisão do usuário, não de apresentação.
  MESMA COISA NO CENÁRIO DE ESTRESSE (11/08/2026, no mesmo dia, a pedido do usuário). A linha do
  estresse era a última que ainda falava só em margem ("ago vira Flávio +2,5") e agora traz o
  placar também, `t2placarStress`. Aqui o centro NÃO precisa ser estimado: o estresse distribui
  TODO o indeciso entre os dois, então o cenário já sai em votos válidos e o centro é exatamente
  50. Ou seja, os dois placares do banner estão em bases diferentes de propósito, o de cima em
  amostra total e o do estresse em válidos, e isso está dito na caixa "entenda estes números".
  ARREDONDAMENTO, que virou função (`par1`): com uma casa decimal, abrir a margem em torno do
  centro e arredondar cada lado por si pode fazer a subtração do placar não bater com a margem
  exibida ao lado. Caso real: margem de 2,512 vira "+2,5" no rótulo e 2,6 na subtração de
  51,3 menos 48,7. `par1` arredonda a margem primeiro e deriva o segundo número do primeiro,
  então a diferença EXIBIDA é sempre a margem EXIBIDA. O preço é que a soma do par pode mostrar
  100,1 em vez de 100 no estresse; foi escolhido assim porque a margem está impressa na tela ao
  lado e a soma não. Não voltar a arredondar os dois lados separadamente.
  TAMBÉM DE 11/08: mapa `MESEXT`/`mesExt` para escrever o mês por extenso em frase corrida
  ("o 2º turno de agosto vira..."), que a abreviação deixava truncada. É constante da língua, não
  série de dados; a lista de meses do painel continua saindo do `months` e do `DI`, e o que
  faltar no mapa cai na própria abreviação.
- RECORTE REGIONAL REGISTRADO COMO SE FOSSE ESTADUAL (18/08/2026). ARMADILHA NOVA, irmã do
  desempate do gêmeo. O TSE registrou SP-05511/2026 (Vox Brasil, campo 11-14/08, N=2000, cargos
  Governador/Deputado Federal/Deputado Estadual) com o gêmeo BR-02244/2026 para Presidente. Pelo
  método do gêmeo isso qualificaria como pesquisa ESTADUAL de São Paulo, insumo de DG/DGM e do
  PRES26. É FALSO: a íntegra publicada pelo ABC Repórter
  (abcreporter.com.br/wp-content/uploads/2026/08/PESQUISA-VOX-BRASIL-CENARIO-ABC-16-de-Agosto.pdf)
  traz na ficha técnica "MUNICÍPIO/UF: ELEIÇÕES GERAIS 2026 - REGIÃO ABC PAULISTA". Os 2.000
  entrevistados são só do ABC, e as perguntas de governador de SP e de presidente são respondidas
  por esse eleitorado regional (Tarcísio 44,6 x Haddad 29,5; Lula 43,5 x Flávio 30,2), números que
  não representam o estado. DESCARTADA, nas duas frentes.
  O QUE ISSO ENSINA: o campo do TSE que separa estadual de municipal não separa estadual de
  REGIONAL. A amostra pode ser de uma região metropolitana, de um grupo de municípios ou de uma
  única cidade e ainda assim vir marcada com a UF. O gêmeo não protege contra isso, porque o par
  BR- + UF existe do mesmo jeito. O que protege é ABRIR A ÍNTEGRA e ler "MUNICÍPIO/UF" na ficha
  técnica antes de inserir. Sinal barato de suspeita, quando não se tem a íntegra à mão: quem
  divulga é veículo de uma região específica (aqui, o ABC Repórter, o SBT RP e a TV Metropolitana
  de Piracicaba), e não a imprensa estadual.
  CUIDADO PARA NÃO CONFUNDIR: a Vox Brasil TEM uma rodada estadual de SP no mesmo período,
  SP-04670/2026, campo 11-13/08, N=1480, e é essa que está no painel (Tarcísio 53,7 x Haddad 34,0).
  Duas rodadas do mesmo instituto, quase as mesmas datas, uma estadual e uma regional. O que
  distingue é a íntegra, não a data nem o N.
- BACKEND DO VERITÁ SUMIU DO DNS (18/08/2026). O `rotina_6h.py` vem escrevendo "Não consegui ler a
  lista do Veritá nesta rodada" e a causa NÃO é nossa: o `radar_verita()` acha a home, acha o bundle
  JS e acha a chave anon corretamente, mas o host do projeto Supabase que o próprio site do Veritá
  chama, `lgjdbpskgjfbmlffbntx.supabase.co`, responde NXDOMAIN. Conferido em dois resolvedores
  independentes (DoH do Google e da Cloudflare, Status 3 nos dois), enquanto
  `eleicoes26.institutoverita.com.br` resolve normalmente para 185.158.133.1. O bundle atual
  (`/assets/index-ZXY8sPJe.js`) continua apontando para esse mesmo host e não tem nenhum outro
  endpoint, ou seja, o painel de pesquisas DELES está quebrado para todo mundo, não só para nós.
  CONSEQUÊNCIA PRÁTICA: enquanto isso durar, pesquisa do Veritá só se acha pela imprensa ou pelo
  registro do TSE, e a seção "Últimas publicações do Veritá" do `PENDENCIAS.md` fica vazia sem que
  isso seja falha da rodada. NÃO reescrever o `radar_verita()` tentando consertar: se um dia eles
  republicarem, o caminho volta a funcionar sozinho; se mudarem de projeto, o que muda é a URL no
  bundle, e é lá que se olha primeiro.
  NOTA DE AMBIENTE, de quebra: o `urllib` da tarefa local não resolve nome nenhum neste sandbox
  (`URLError ... nodename nor servname`), então rodar `radar_verita()` à mão pelo `python3 -c`
  engana e parece queda do Veritá. O `curl_cffi` com `impersonate="chrome"` resolve e é o que
  serve para apurar; o NXDOMAIN acima foi medido por ele, não pelo urllib.
  MESMO PROBLEMA NO `radar_tse.py` (19/08/2026). Rodar o radar à mão na máquina local morre com
  **HTTP 403** no `cdn.tse.jus.br`, e não é bloqueio do TSE contra nós: é o `urlopen` do script,
  que o CDN recusa. O `curl` de linha de comando com User-Agent de navegador também toma 403.
  O que passa é o `curl_cffi` com `impersonate="chrome"`. O radar reaproveita o que já está no
  cache do dia, então o contorno é baixar os dois ZIPs por fora e descompactar onde ele procura:

      D=$(python3 -c "import tempfile,os;print(os.path.join(tempfile.gettempdir(),'radar_tse_2026'))")
      # curl_cffi baixa pesquisa_eleitoral_2026.zip e pesquisa_contratante_2026.zip para $D
      # e extrai em $D/pe_AAAAMMDD e $D/pc_AAAAMMDD

  Depois disso `python3 radar_tse.py AAAA-MM-DD` roda normalmente. NÃO alterar o `radar_tse.py`
  para usar curl_cffi: ele roda no Actions, onde o urllib funciona, e a dependência não está lá.
- DATA DE DIVULGAÇÃO PODE SER ANTERIOR AO FIM DO CAMPO (18/08/2026). Terceira armadilha da mesma
  família das duas acima, e a mais barata de cair. A Badra registrou PE-00080/2026 (e o gêmeo
  BR-00523/2026) com divulgação em 17/08 e campo de 12/08 a 18/08: o radar listou como "divulgação
  vencida" e o item entrou na fila, mas o campo só fecha depois, então o número NÃO PODE existir
  ainda. Antes de sair procurando íntegra que não existe, e principalmente antes de descartar o
  item como "registra e não publica", compare `DT_DIVULGACAO` com `DT_FIM_PESQUISA`: se a
  divulgação vem antes, o item é só PREMATURO, e o lugar dele é continuar na fila.
  DESFECHO DESTE CASO, 19/08/2026: a Badra não era só prematura. O TRE-PE deferiu
  liminar em 16/08 (processo 0601502-34.2026.6.17.0000) proibindo divulgar qualquer
  resultado da PE-00080/2026, com multa de R$ 30 mil por ato, e um dos fundamentos foi
  exatamente a divulgação marcada para antes do fim da coleta. Ou seja, o descompasso
  entre DT_DIVULGACAO e DT_FIM_PESQUISA não é só sinal de que o número ainda não
  existe: é também sinal de irregularidade que a Justiça Eleitoral pune. Os dois
  registros (PE-00080 e o gêmeo BR-00523) saíram da fila como DESCARTE, e o detalhe
  está no ALERTA_PESQUISAS_SUSPENSAS_JUDICIALMENTE_20260721.md. Antes de descartar por
  "prematuro que nunca saiu", procure a liminar: ela costuma ser a explicação.
  REGRA GERAL QUE VALE PARA A FILA INTEIRA: item cuja divulgação é de HOJE quase nunca está
  publicado quando a rodada local acorda, porque o TSE libera a divulgação e o veículo publica ao
  longo do dia. Descartar no primeiro dia é o erro; o custo de deixar na fila é zero, ela sai
  sozinha em 21 dias e a saída é anunciada. Só marque descarte quando houver motivo POSITIVO
  (recorte regional, veículo publicou outra coisa, instituto com histórico de não divulgar).
  CADÊNCIA POR PARCELAS, mesmo assunto: o GP1 divulgou a rodada de 11-13/08 em capítulos, governador
  em 17/08, senador e deputados em 18/08, e o presidencial (BR-09803/2026) ainda não saiu. Um mesmo
  registro pode estar metade publicado, então "o gêmeo estadual já entrou" não implica que o
  presidencial exista.
- PENDÊNCIAS DATADAS (registrar agora, executar depois):
  (a) SETEMBRO: implementar detector de herding (ADPA do Silver Bulletin). Se na última quinzena
  a dispersão entre institutos ficar ABAIXO do mínimo teórico dado o erro amostral, é manada e a
  banda de incerteza deve ALARGAR, nunca estreitar. Foi o que Nate Silver documentou nos EUA 2024.
  (b) OUTUBRO, após o 1º turno: REANCORAR a série do 2º turno nas pesquisas novas, sem dar
  continuidade à série hipotética anterior. A literatura mostra que o 1º turno realinha o
  eleitorado; a série condicional velha deixa de valer.
- REVISÃO COMPARATIVA INTERNACIONAL (22/07/2026). O que o espelho de França, Argentina, Chile,
  Colômbia, Peru, Equador, Turquia, Uruguai e Portugal ensinou: (i) MEDIANA sem pesos é adequada
  ao campo brasileiro — o Pindograma mediu que a vantagem dos institutos tradicionais sobre o
  resto caiu de 1,35 p.p. (2014) para 0,19 (2022), então não há padrão-ouro que justifique
  ponderação forte; e agregadores bateram institutos individuais em 2022 (Ipec só superou o
  agregador em 3 de 22 estados). (ii) O risco dominante em sistemas de dois turnos NÃO é
  dispersão entre institutos, é o CAMPO INTEIRO ERRAR JUNTO (Argentina 2019 e 2023, Turquia 2023,
  Equador 2025, Brasil 2022-1º turno). (iii) NÃO existe viés universal por país (Jennings &
  Wlezien, 30 mil pesquisas, 45 países); há viés por país e por ciclo. Na onda 2018-2025 o erro
  correu contra a direita populista nas Américas e na Turquia, mas na França a extrema-direita é
  SUPERestimada nos runoffs. (iv) A fama da AtlasIntel de "mais precisa" é marketing sobre
  amostra seletiva: a final dela no 2º turno brasileiro de 2022 (53x47) ficou FORA da margem,
  atrás de Datafolha, Quaest, MDA e Paraná.
- DESEMPATE NACIONAL x ESTADUAL PELO GÊMEO (23/07/2026). **A técnica mais útil descoberta neste
  projeto.** PROBLEMA: o TSE marca `NM_UE = "BRASIL"` em TODA pesquisa com pergunta presidencial,
  mesmo quando a amostra é de uma única UF. Isso já quase nos fez inserir a Paraná Pesquisas do
  RIO DE JANEIRO como se fosse nacional, e me fez afirmar erradamente que faltavam cinco rodadas
  nacionais do Veritá em julho.
  SOLUÇÃO: cruzar o registro BR- contra TODOS os registros estaduais casando por
  **CNPJ + data de início + data de fim + tamanho da amostra**. Se existe um gêmeo estadual, a
  pesquisa é daquela UF. Roda local, em segundos, sem busca web, e é definitivo.
  RESULTADO NA PRÁTICA: das 6 pesquisas "nacionais" do Veritá em julho, **todas as 6 eram
  estaduais** (PA×2, SP, RS, GO, PR). E a rodada do RTBD de 20-21/07 que parecia mais nova que a
  nossa era a do ESPÍRITO SANTO. Nenhuma lacuna existia.
  LIMITE CONHECIDO: o gêmeo pode ter sido RETIRADO do PesqEle (foi o caso do PR-03335, gêmeo do
  BR-00558), e aí a nacional aparece como falso positivo. Também há o caso de o instituto
  simplesmente não registrar a versão estadual. Portanto: "sem gêmeo" significa CANDIDATA a
  nacional, não nacional confirmada.
- RADAR DE PESQUISAS REGISTRADAS E NÃO INCORPORADAS (23/07/2026). Ideia importada do Polling Data,
  que mantém no ar por 7 dias as pesquisas registradas e não divulgadas — é um detector de viés
  de publicação. DECISÃO DE DESENHO: NÃO embutir a lista no painel. Uma lista congelada fica
  obsoleta em dias e passaria a mentir. O radar é PASSO DE PROCESSO, não widget: roda a cada
  atualização, sobre o CSV do TSE, com o desempate do gêmeo acima. Está na SKILL da tarefa
  semanal. Rodando em 23/07/2026: 15 presidenciais nacionais com divulgação nos 25 dias
  anteriores, das quais 5 de institutos que não acompanhamos (DMP, Boas Ideias, 100 Cidades,
  IGAPE, Instituto Mais). ARMADILHA do filtro: "Boas Ideias" casa com a palavra "IDEIA" da lista
  de institutos conhecidos e passa batido; conferir por nome inteiro, não por substring.
- CORREÇÃO DA ARMADILHA "BOAS IDEIAS" (11/08/2026). A regra do parágrafo acima continua valendo
  para substring, mas a CONCLUSÃO que se tirou dela em 23/07 estava errada: a "Boas Ideias" foi
  listada entre os 5 institutos "que não acompanhamos", e ela é justamente o instituto que o
  painel chama de **Meio/Ideia**. Conferido POR CNPJ, que é o método certo: CNPJ
  13.475.743/0001-60, razão social BOAS IDEIAS INTELIGENCIA EM PESQUISA E ESTRATEGIA DIGITAL
  LTDA, fantasia "BOAS IDEIAS, ESTRATEGIA E INTELIGENCIA DIGITAL.". As 12 nacionais dela em 2026
  batem uma a uma com a cadência mensal do Meio/Ideia no `DI`, incluindo BR-05628/2026
  (campo 3-6 jul, a rodada de julho do painel) e BR-04579/2026 (campo 31/7-3/8, a de agosto).
  A CEO é a Cila Schulman, e o Poder360 e a Gazeta do Povo escrevem ora "Meio/Ideia" ora só
  "Ideia", conforme quem contratou a rodada. LIÇÃO: nome fantasia do TSE e nome de mercado do
  instituto são coisas diferentes; o desempate é sempre o CNPJ, do mesmo jeito que na auditoria
  de house effect. Não voltar a tratar "Boas Ideias" como instituto desconhecido.
- QUEM PODE TER HOUSE EFFECT: AUDITORIA POR CNPJ (31/07/2026). PERGUNTA que originou: o usuário
  reparou que a Alfa e a Vox Brasil, acrescentadas ao `DI` de julho, entravam sem ajuste, e mandou
  verificar se isso era corrigível. MÉTODO, que vale para qualquer instituto novo: baixar os ZIPs
  `pesquisa_eleitoral_AAAA` do TSE de 2018, 2020, 2022, 2024 e 2026 e cruzar **por CNPJ**, nunca
  por nome. Buscar "Vox" no texto traz Datavox, Vox Pesquisas (SE), Vox Opinião Pública (SP) e
  Invox Brasil, que são quatro empresas diferentes; é a mesma armadilha de substring do radar
  ("Boas Ideias" x "IDEIA"). Complementar com a data de abertura do CNPJ na Receita, que sozinha
  já mata alguns casos.
  RESULTADO. **Vox Brasil** (CNPJ 45.613.076/0001-20, Barretos/SP): CNPJ aberto em 11/03/2022;
  zero registros no PesqEle em 2018, 2020 e 2022; 462 em 2024, todas MUNICIPAIS (cargo Prefeito,
  SP e MG); a primeira presidencial é de 25/04/2026. Existiu sete meses do calendário de 2022 e
  não registrou nada. **Alfa Inteligência** (CNPJ 22.400.349/0001-53, São Paulo): CNPJ aberto em
  07/05/2015, ou seja a empresa EXISTIA em 2018 e 2022, mas tem zero registros em 2018, 2020,
  2022 e também 2024; os únicos são 3, todos de 2026, todos BRASIL/Presidente, o primeiro em
  11/03/2026. O site dela explica: é consultoria de campanha ("desde 2008", placar de 1 campanha
  presidencial, 10 de Senado, 260 de prefeitura), e pesquisa interna contratada por campanha não
  vai ao PesqEle porque não é divulgada.
  CONCLUSÃO: as duas ficam FORA do `VH2DET` por impossibilidade, não por descuido. Não há rodada
  final para comparar com a urna. O motivo é diferente em cada caso e está escrito no campo `nt`
  do `IM` de cada uma, para o painel explicar sozinho. NÃO reabrir a checagem: só vale refazer se
  alguma das duas publicar rodada final em eleição futura.
  CUIDADO AO ESCREVER ESSE TEXTO (achado ao conferir a gaveta): "sem house effect" NÃO pode ser
  dito solto, porque a gaveta lateral mostra, no campo "viés histórico (vs urnas)", um número
  COM ASTERISCO mesmo para quem não tem histórico. São dois objetos distintos e fáceis de
  confundir: o `VH2DET`/`VHIST2` é de 2º TURNO, sem default, e é o que alimenta banner, aba House
  effect e gráfico; o `VH1DET`/`VHIST`/`VLULA` é o legado de 1º TURNO, vive SÓ na gaveta e TEM
  default desde 23/07/2026 (`VHDEF`/`VLDEF`, mediana do campo com histórico, encolhida como uma
  eleição, marcada com asterisco). Sem essa distinção, o `nt` e o campo logo acima dele se
  contradizem na mesma tela. Os textos da Alfa e da Vox já dizem qual é qual.
  LIÇÃO GERAL: "instituto novo no painel" e "instituto sem histórico" não são a mesma coisa, e o
  inverso também vale. A Apex/Futura, o Gerp, a PoderData, o RTBD e o Veritá já eram "novos" e
  ganharam house effect quando se foi atrás da rodada final de 2018/2022 deles. Antes de declarar
  que alguém não tem histórico, rodar esta auditoria por CNPJ.
- O PUSH PUBLICA, DE NOVO: SEGREDOS CADASTRADOS (02/08/2026, 12h). As duas primeiras execuções
  do repositório (runs 30751237086 e 30751486814) falharam em "Sobe para o PythonAnywhere" com
  `falta o segredo PA_TOKEN no repositorio`, e por umas horas quem publicou foi só o
  `deploy_agregador.py` rodado à mão. RESOLVIDO: o usuário mandou cadastrar os segredos, e
  `PA_TOKEN` (o valor de `painel/.env`) e `PA_USER` (`rafaelcortopassi`) foram gravados com
  `gh secret set` a partir da máquina dele, com o `gh` já autenticado como `rcortopassi` e escopo
  `repo`. O token saiu do `.env` para o cofre do GitHub sem passar por nenhum arquivo do
  repositório nem pelo log. Conferido de ponta a ponta no run 30753444692 (`workflow_dispatch`):
  valida JS, sobe `electoralpolls.html` e `index.html`, dá reload, verde. Confirmar sempre no ar
  com `curl -s https://rafaelcortopassi.pythonanywhere.com/electoralpolls/ | grep "Última atualização"`.
  O `deploy_agregador.py` à mão continua funcionando e é idempotente: serve para publicar na
  hora, sem esperar o Actions.
  NOTA DE DESENHO que permanece: o passo do workflow trata o segredo como OPCIONAL e sai com 0
  quando ele não existe, para push não ficar vermelho à toa. Isso quer dizer que **workflow verde
  não prova que publicou**; se precisar de prova, é o log do passo ou o `curl` acima.
  ARMADILHA CORRELATA, JÁ MORTA: `deploy_agregador.py` procurava o token em
  `<pasta do script>/painel/.env`, e o clone novo em `~/agregador-pesquisas-2026` não tem essa
  pasta (é gitignorada; o arquivo real mora no Google Drive). Uma rodada improvisou um symlink
  `painel` dentro do repo, que acabou versionado por engano. O certo, e o que está no código
  agora, é o caminho ABSOLUTO para o `.env` do Drive. Não recriar o symlink.
- GAVETA DA METODOLOGIA NO RODAPÉ (31/07/2026, a pedido do usuário). O rodapé citava este arquivo
  como texto morto; agora o nome do arquivo é CLICÁVEL e abre `openMetodologia()`, que reusa a
  gaveta `#dr` com a classe `.wide` (560px, `max-width:85vw` segura o celular em ~319px).
  DECISÃO DE DESENHO: NÃO publicar este .md junto do painel. Ele é documento INTERNO, cheio de
  decisão datada, cicatriz ("ficou ruim", "o usuário mandou remover") e instrução para o próximo
  agente. A gaveta é a versão PÚBLICA, escrita para quem chega sem contexto, em oito seções: o que
  o painel é, mediana sem exclusão, uma rodada por instituto por mês, house effect, os três números
  do 2º turno, o que a margem de erro não cobre, mapa e estaduais com contratante, fontes por
  prioridade, e "o que o painel não faz".
  REGRA AO MEXER: todo número da gaveta é DERIVADO ao vivo (`DI`, `T2R`, `VH2DET`, `PRES26`, `DG`,
  `CONTR`, `months`, `avgMonth`, `adj2Month`, `t2valid`, `t2stress`, `moeMonth`). NÃO escrever
  contagem nem lista à mão: instituto novo no `DI` já se reflete sozinho no texto. `closeInst()`
  tira `.wide`, senão a ficha de instituto abriria larga depois.
  ERRO QUE EU COMETI E QUE VALE REGISTRAR: escrevi na primeira versão que quem não tem histórico
  "nunca recebe viés emprestado do campo". É FALSO para o 1º turno, pela distinção do bloco acima:
  `adjMonth` usa `avies`/`avlula`, que aplicam o default `VHDEF`/`VLDEF`. Só o 2º turno é que não
  tem default. O texto já foi corrigido para explicar os dois casos. É a SEGUNDA vez que essa
  confusão morde no mesmo dia.
- NOME DO CANDIDATO TEM QUE SER IDÊNTICO DENTRO DO MESMO MÊS (02/08/2026). SINTOMA: o painel do
  Paraná anunciava "Disputa aberta (Moro à frente por 0,9 p.p., dentro da margem)" numa corrida em
  que o Moro abre 20 pontos. CAUSA: `stateBanner` agrega por NOME (`sums[c[0]]`), e o `DGM` do PR
  guardava o MESMO candidato como 'Moro' (Paraná Pesquisas) e 'Sergio Moro' (Neokemp, Quaest, IRG).
  Vira duas pessoas: a média de 'Moro' (39,9) contra a de 'Sergio Moro' (39,0), diferença 0,9, e o
  banner conclui empate. NÃO é bug de código: o `stateBanner` está certo, o dado é que estava
  inconsistente. CORRIGIDO em julho nos seis estados afetados (ES Hartung/Paulo Hartung e
  Salomão/Helder Salomão, PR Moro/Sergio Moro e Greca/Rafael Greca, BA Jerônimo/Jerônimo Rodrigues,
  RN Cadu/Cadu Xavier e Álvaro/Álvaro Dias, DF Cappelli/Ricardo Cappelli e Grass/Leandro Grass,
  PI Fonteles/Rafael Fonteles), padronizando sempre no nome COMPLETO.
  TO jun FECHADO em 04/08/2026, junto com a entrada da VÓPE de agosto: o `DGM` do TO foi
  padronizado em 'Dorinha Rezende', 'Vicentinho Júnior' e 'Laurez Moreira' (15 trocas) e o `DSM`
  em 'Irajá Abreu' (1 troca). Valia a pena porque a série do TO acabara de ganhar jul e ago, e o
  `stateChart` escolhe os dois candidatos pelo TOTAL somado dos meses: com o nome partido, metade
  da série da Dorinha ficava fora da conta.
  AINDA ABERTO nos meses anteriores (não afetam o banner, que só lê o último mês com rodada, mas
  sujam o gráfico do estado). A lista antiga só olhava o `DGM`; a varredura de 04/08/2026 nos DOIS
  objetos dá: `DGM` BA abr (Mansur), PE fev (Moura), MA mar (Braide, Brandão, Bonfim), PI mar
  (Toni), AC jun (Bocalom), DF jun (Arruda, Grass); `DSM` ES abr (Hartung), RN mai (Rafael Motta),
  MS abr e MS mai (Azambuja, Capitão Contar). Ao varrer, rodar o detector sobre `DGM` E `DSM`.
  REGRA AO INSERIR RODADA ESTADUAL: antes de acrescentar, conferir como o candidato JÁ está escrito
  naquele UF/mês e repetir exatamente. Detector, que roda em segundos sobre o próprio HTML: para
  cada UF e mês, listar os nomes e apontar par em que um é substring do outro. CUIDADO com falso
  positivo de sobrenome comum: 'Joel Rodrigues' x 'Toni Rodrigues' no PI são duas pessoas.
  O CASO INVERSO, que o detector de substring NÃO pega (15/08/2026): no RN o painel escreve
  'Rodrigo Bolsonaro' e a íntegra do Item/Difusora escreve 'Rodrigo Vieira (AGIR)'. É a MESMA
  pessoa, Karlo Rodrigo Lúcio Vieira, lançado pelo Agir em 3/8 e que pediu para usar 'Rodrigo
  Bolsonaro' na urna (o MP Eleitoral se opôs ao nome de urna, o que não muda quem é o candidato).
  Nenhum nome é substring do outro, então só a conferência humana pega. Quando o jornal trocar o
  nome de urna pelo nome civil, casar pelo partido antes de criar candidato novo.
- FEED DE PUBLICAÇÃO DO VERITÁ, QUE RESOLVE "REGISTRADA MAS NÃO DIVULGADA" (02/08/2026, 21h).
  PROBLEMA RECORRENTE: o Veritá é, de longe, o instituto que mais aparece no radar do TSE, e
  registra vários estados na MESMA leva (mesmo CNPJ, mesmas datas de campo). Só que ele divulga
  um estado por vez, dias depois, e o radar não distingue o que já saiu do que ainda vai sair.
  Sem essa distinção o agente ou fica caçando número que não existe ou dá a leva por completa
  quando só metade publicou. Exemplo do dia: a leva de campo 28/07-01/08 tem PR, MA, AP, AM e PA;
  às 21h de 02/08 só PR e MA estavam publicados.
  SOLUÇÃO: o site do site institucional NÃO serve (institutoverita.com.br está tomado por spam de
  cassino e farmácia, com "hello world" no meio; nada eleitoral desde 2025). O que serve é o site
  DEDICADO `eleicoes26.institutoverita.com.br`, um SPA feito no Lovable cujo backend é Supabase.
  Dá para listar tudo o que ele publicou, com data e hora, em uma chamada:
  `GET https://lgjdbpskgjfbmlffbntx.supabase.co/rest/v1/pesquisas?select=id,titulo,descricao,pdf_url,created_at&order=created_at.desc&limit=30`
  com a chave anônima nos cabeçalhos `apikey` e `Authorization: Bearer`. A chave é pública, está
  embutida no bundle `/assets/index-*.js` do próprio site (extrair de lá se ela rodar), e devolve
  exatamente o que a página mostra a qualquer visitante. Cada linha tem `titulo` (com o estado),
  `created_at` e `pdf_url`, que é a ÍNTEGRA, ou seja a fonte de prioridade 1 do Passo 3.
  ATENÇÃO: `created_at` vem em UTC. 15:48Z é 12:48 em Brasília; não confundir com a hora do TSE.
  USO NO PROCESSO: quando o radar apontar Veritá, consultar este feed ANTES de sair procurando em
  jornal regional. Se o estado não está no feed, a rodada existe mas não foi divulgada, e a
  conduta certa é não inserir e registrar como pendente.
- MIGRACAO PARA O GIT E A NUVEM QUE NAO DEU (02/08/2026). O usuario pediu que a atualizacao
  rodasse "direto pelo site", sem o app aberto no Mac, e mandou passar tudo para o git deixando o
  Google Drive como copia morta. A migracao foi feita: fonte de verdade agora e o repositorio
  privado rcortopassi/agregador-pesquisas-2026, clonado em ~/agregador-pesquisas-2026, com o
  AGENTS.md carregando as instrucoes da tarefa e scripts novos (radar_tse.py e mercados.py).
  A PARTE DA NUVEM NAO FUNCIONA, e foi medida, nao suposta. Depois de instalar o app do Claude no
  GitHub e liberar o repositorio, a rotina rodou e o resultado esta em DIAGNOSTICO_NUVEM.md: o
  sandbox tem proxy de saida obrigatorio que responde 403 Forbidden ao CONNECT para TODO dominio
  externo. Caiu tudo: ZIPs do TSE, Poder360, static.poder360, Gazeta, Polymarket, Kalshi e a API
  do PythonAnywhere. So git e relogio funcionam. Como a tarefa e quase toda apuracao, ela CONTINUA
  na tarefa agendada local. NAO refazer essa tentativa sem antes reexecutar o diagnostico.
  GANHO QUE FICOU, mesmo com a nuvem fora: versionamento, e o mercados.py, que resolveu de forma
  robusta o acesso a Polymarket e Kalshi NO MAC. A receita antiga (nslookup 8.8.8.8 + curl
  --resolve) depende de UDP/53; a nova tenta HTTPS direto, depois DNS-over-HTTPS no dns.google e
  no cloudflare-dns.com, e so entao o nslookup. No Mac o direto falha (DNS do provedor) e o DoH
  salva. Se todos falharem o script sai com codigo 2 e quem chama NAO inventa numero.
- "BOAS IDEIAS, ESTRATEGIA E INTELIGENCIA" NO TSE É A MEIO/IDEIA (05/08/2026). Mesmo caso do
  "100 CIDADES" logo abaixo, e mais antigo: desde 23/07/2026 o radar listava "Boas Ideias" como
  instituto desconhecido e não acompanhado, com a anotação de que o nome casava por substring com
  a palavra "IDEIA" da lista de conhecidos. A conclusão da época estava invertida: não é falso
  positivo de substring, é a MESMA CASA. O registro BR-04579/2026 sai no PesqEle com o nome
  fantasia BOAS IDEIAS, ESTRATEGIA E INTELIGENCIA e contratante CANAL MEIO S.A., e a matéria da
  Gazeta do Povo de 05/08/2026 sobre a rodada nacional do "instituto Ideia, em parceria com o
  Canal Meio" fecha citando exatamente "Registro no TSE nº BR-04579/2026", campo 31/07 a 03/08,
  N=1.500, margem de ±2,5. Ou seja: quando o radar apontar BOAS IDEIAS, leia Meio/Ideia, que JÁ
  está no painel desde janeiro, e aplique a regra de uma rodada por instituto por mês. Fica a
  regra geral, agora com dois casos: nome fantasia no PesqEle não é o nome que a imprensa usa, e
  o que amarra os dois é o par CONTRATANTE + NÚMERO DE REGISTRO, não o nome.
- "100 CIDADES" NO TSE É A FUTURA/APEX (03/08/2026). O radar vinha listando "100 CIDADES" como
  instituto desconhecido e não acompanhado desde 23/07/2026. É a mesma casa: o registro sai com o
  nome fantasia "100 CIDADES" (a marca 100% Cidades) e contratante FUTURA CONSULTORIA E ASSESSORIA
  LTDA, e o Poder360 publica exatamente esses registros como "Futura/Apex". Confirmado nos pares
  BR-01327/2026 + BA-07924/2026 (Bahia, campo 24-25 jul) e BR-05425/2026 (Rio de Janeiro, campo
  27-28 jul), os dois com R$ 80.000 pagos pela Futura. Ou seja: quando o radar apontar 100 CIDADES,
  leia Futura/Apex, que JÁ está no painel, e aplique a regra de uma rodada por instituto por mês.
- FALSO POSITIVO DE NACIONAL SEM GÊMEO: BR-05425/2026 (03/08/2026). O registro apareceu como
  NACIONAL? por não ter gêmeo estadual, e é a pesquisa do RIO DE JANEIRO da Futura/Apex: a íntegra
  e as três matérias do Poder360 dizem "1.000 pessoas no Estado do Rio de Janeiro" e citam SÓ o
  BR-05425/2026, sem par RJ-. É o LIMITE CONHECIDO do desempate pelo gêmeo virando caso concreto:
  a Futura simplesmente não registrou a versão estadual. Regra prática que fica: N=1.000 e custo de
  R$ 80 mil são a assinatura das ESTADUAIS da Futura; as nacionais dela têm amostra maior. Antes de
  tratar "sem gêmeo" como nacional, confira o N e abra a matéria.
- DATATRENDS EM ALAGOAS ESTÁ SOB RESTRIÇÃO DO TRE-AL (30/07/2026, anotado em 03/08/2026). O
  instituto registra rodadas de Alagoas (AL-08883/2026, campo 31/7-2/8, e o gêmeo presidencial
  BR-06278/2026) mas há decisão do TRE mantendo restrição à divulgação, e nenhum número da rodada
  apareceu publicado. Não inserir AL da DataTrends sem antes checar a situação judicial, conforme a
  regra de checagem de suspensão que já vale para o ciclo.
- SUMÁRIO DA ÍNTEGRA PROMETE SEÇÃO QUE O PDF NÃO TEM (13/08/2026). A íntegra da AtlasIntel/Focus do
  Ceará (CE-02777/2026, campo 6-11/8, publicada pelo Poder360 em
  `static.poder360.com.br/uploads/2026/08/pesquisa-atlasintel-governo-ce-12ago2026.pdf`) traz no
  sumário oito seções, entre elas "3 Eleição para Presidente no Ceará", mas o arquivo tem 23 páginas
  e termina na do Senado: as seções 3 a 7 não foram divulgadas. Governo e Senado entraram no painel;
  o gêmeo presidencial BR-08314/2026, que alimentaria o `PRES26` do CE, FICOU SEM NÚMERO e segue na
  fila do `PENDENCIAS.md` à espera de o instituto liberar o resto. Regra que fica: o sumário de um
  deck NÃO é prova de que o número existe publicado, e nesses casos vale conferir a última página
  antes de contar com a seção. Não preencher `PRES26` por dedução do resultado estadual.
- O SUPABASE DO VERITÁ SAIU DO AR (14/08/2026). O `radar_verita()` do `rotina_6h.py` vinha falhando
  em silêncio ("Não consegui ler a lista do Veritá nesta rodada") e a causa NÃO é bloqueio nem
  mudança de bundle: o projeto `lgjdbpskgjfbmlffbntx.supabase.co` responde **NXDOMAIN** no DNS do
  sistema, no 8.8.8.8, no DoH do Google e no da Cloudflare, enquanto o apex `supabase.co` resolve
  normalmente. A home `eleicoes26.institutoverita.com.br` continua no ar e o bundle JS ainda traz a
  MESMA chave anon e o MESMO ref (conferido, `iss:supabase, ref:lgjdbpskgjfbmlffbntx`), ou seja o
  site do instituto está apontando para um projeto que não existe mais. CONSEQUÊNCIA QUE IMPORTA
  PARA O PAINEL: os PDFs do Veritá hospedados nesse Supabase viraram link morto, e um deles era o
  campo `u` do `PRES26` do Paraná (`1785685708802_Relatorio_Parana_Agosto_2026.pdf`), trocado nesta
  rodada junto com o dado. Antes de citar Veritá como fonte, teste o link; e se a lista voltar, é
  porque eles recriaram o projeto, o que muda o ref e exige atualizar `VERITA_REST`.
- PESQUISA MUNICIPAL REGISTRADA COM CÓDIGO ESTADUAL: SETA/POLÊMICA NA PARAÍBA (14/08/2026). A fila
  vinha acumulando registros do INSTITUTO SETA na PB com N pequeno (450, 550, 800) e gêmeo
  presidencial BR-, o que parecia rodada estadual nova toda semana. Não é: são as rodadas
  MUNICIPAIS da série Polêmica Paraíba/Seta. Confirmado no caso PB-00866/2026 (N=550, campo 5-6/8,
  gêmeo BR-09441/2026), que o próprio Polêmica publica como "a disputa para o Governo **na cidade
  de Santa Rita**", com margem de 4 pontos. Ou seja, a amostra é de um município e a pergunta de
  governador é sobre o voto daquele município, o que NÃO alimenta `DGM`/`DSM` (série estadual) nem
  `PRES26` (mapa por UF). REGRA QUE FICA: na Paraíba, Seta com N abaixo de ~1.000 é municipal até
  prova em contrário; abra a matéria do Polêmica antes de inserir, porque o cargo no registro do
  TSE diz "Governador" mesmo quando o universo é uma cidade. É o primo do desempate pelo gêmeo: lá
  o gêmeo estadual denuncia a falsa nacional, aqui o N pequeno denuncia a falsa estadual.
- A REGRA DO N PEQUENO SE CONFIRMOU FORA DA PARAÍBA (15/08/2026). O caso irmão do parágrafo acima
  apareceu no PIAUÍ: PI-00017/2026, INSTITUTO CREDIBILIDADE, cargo "Governador, Senador, Deputado
  Federal" no registro do TSE, N=426, campo 5-6/8. A matéria do 180graus mostra que o universo é o
  MUNICÍPIO DE CORRENTE, no sul do estado, e o número que sai é "Fonteles 76,65% dos votos válidos
  em Corrente". Descartada, não entrou em `DGM`/`DSM`. Na mesma rodada, GO-04894, GO-02118 (IGAPE,
  N=500 e 800) e GO-04491, GO-05836 (Direct Pesquisas, N=400 e 500) tinham divulgação vencida em
  13/8 e NENHUM número publicado dois dias depois, enquanto as rodadas ESTADUAIS desses dois
  institutos em Goiás saem sempre com N de 1.150 a 1.500 e viram matéria no mesmo dia. REGRA QUE
  FICA, agora geral e não só da PB: registro estadual com N abaixo de ~1.000 é candidato a
  municipal ou regional; confira o universo na matéria antes de inserir, e quando não houver
  matéria nenhuma, o mais provável é que a rodada seja de recorte local que ninguém publica.
- "VÉRITAS PLANEJAMENTO" NÃO É O "INSTITUTO VERITÁ" (15/08/2026). Armadilha de nome com potencial de
  estrago, porque o Veritá é o instituto com histórico sistêmico de suspensão (onze estados) e
  aparece na base estadual do painel. São empresas diferentes: a VERITAS PLANEJAMENTO assinou
  MA-01632/2026 (campo 8-11/8, N=1000, contratante Farol Pesquisa e Comunicação) e o TRE-MA
  REJEITOU o pedido de suspensão apresentado pela coligação do Felipe Camarão, decisão do juiz
  auxiliar Rubem Lima de Paula Filho, ou seja a divulgação está liberada. No painel ela entra como
  `Véritas Planejamento`, com acento e sobrenome, exatamente para não colar no `Veritá` que já
  existe em MA/mar e MA/jul. Não unificar os dois nomes.
- O MARANHÃO VIROU DE CABEÇA PARA BAIXO EM QUATRO DIAS (15/08/2026, registrado porque parece erro e
  não é). O `DG['MA']` passou de "Eduardo Braide 44 x Orleans Brandão 25,9" (IPPI/Café Quente,
  campo 6-10/8) para "Orleans Brandão 47,5 x Eduardo Braide 39,1" (Véritas Planejamento, campo
  8-11/8). Não é troca de sinal por engano de digitação nem inversão de colunas: são dois
  institutos diferentes, com campos quase sobrepostos, divergindo em mais de 30 pontos de margem.
  As duas rodadas estão no `DGM['MA'].ago`, lado a lado, que é o lugar onde a divergência fica
  visível; o `DG` mostra a mais recente porque essa é a regra do mapa. Se alguém for mexer, mexa no
  critério do `DG`, não apague uma das duas.
- NÚMERO PUBLICADO SEM NENHUMA METODOLOGIA NÃO ENTRA (15/08/2026). O Mega Portal RN publicou em
  15/8 "Pesquisa Data Census / Mega Portal RN: 1º Voto para o Senado", com treze nomes e
  percentuais (Styvenson 22,1 · Zenaide 20,0 · Samanda 7,2 · Rafael Motta 7,2 · Cel. Hélio 6,7).
  A matéria não traz campo, nem N, nem margem, nem registro no TSE, e nenhum outro veículo
  republicou com metodologia. O único registro compatível na janela é RN-09307/2026 (contratante
  Mega Assessoria / Mega Portal RN, campo 10-13/8, N=2000), mas isso é inferência, não confirmação.
  Somado a que o Data Census já teve a RN-05562/2026 SUSPENSA no RN, a decisão foi NÃO inserir e
  deixar o item na fila. Vale como regra: casar número com registro é condição de entrada, e
  "só um portal publicou, sem ficha técnica" é motivo suficiente para segurar, ainda mais quando o
  instituto tem suspensão no mesmo estado. Ver [[feedback_checagem_judicial_pesquisas]].
- PRES26 NÃO É SÓ "A MAIS RECENTE" QUANDO A MAIS RECENTE É MAIS POBRE (14/08/2026). O Ranking Brasil
  Inteligência publicou presidencial em MS (BR-03493/2026, campo 7-12/8, N=2.000): Flávio 40, Lula
  33, sem cenário de 2º turno. Era 7 dias mais nova que a do Real Time Big Data (1-5/8) que estava
  no `PRES26`, e mesmo assim NÃO entrou. Motivo: a do RTBD traz 2º turno (Lula 38 x Flávio 50), e é
  do 2º turno que o `pmargin` tira a intensidade da cor do mapa; trocar por uma sem 2º turno faria o
  mapa perder informação para ganhar seis dias, com as duas apontando o mesmo `lead` ('F'). A regra
  geral continua sendo a mais recente por UF; a exceção é quando a mais recente não publica 2º turno
  e a anterior publica, e a diferença de data é de poucos dias. Registrar no resumo quando acontecer,
  senão a próxima rodada acha que o radar deixou passar.
- DUAS SUSPENSÕES JUDICIAIS NO MESMO DIA, E O QUE ELAS ENSINAM (14/08/2026). Duas pesquisas que
  estavam na fila do `PENDENCIAS.md` com divulgação vencida NÃO existem como dado publicável, porque
  a Justiça Eleitoral barrou as duas ANTES da data de divulgação, e o radar do TSE não tem como saber
  disso: ele lê o registro, não a liminar. **PE-08982/2026** (Opinião Pesquisas Sociais, campo 6-9/08,
  R$ 45 mil, contratada pelo Blog do Magno Martins) foi suspensa em 11/08 pelo desembargador Paulo
  Augusto de Freitas Oliveira, a pedido da coligação de Raquel Lyra, por "aparente incoerência" no
  universo amostral, mistura de métodos de amostragem e falta de clareza sobre a origem dos recursos;
  a liminar proíbe até recortes e tabelas, com multa de R$ 30 mil por descumprimento. **SE-04226/2026**
  (Instituto França, campo 10-12/08, divulgação prevista para 13/08) foi suspensa pelo TRE-SE por
  inconsistências metodológicas e vícios de amostragem, com multa diária de R$ 10 mil, e junto dela caiu
  a SE-07506/2026 do mesmo instituto. Descartados também os gêmeos presidenciais BR-03921/2026 e
  BR-05808/2026, que são a mesma coleta. REGRA QUE FICA: antes de inserir pesquisa de instituto local
  pouco conhecido, procurar "TRE-UF suspende pesquisa" no período entre o registro e a divulgação. O
  sinal de alerta é o mesmo nos dois casos: contratante que é parte interessada (blog que faz campanha
  aberta por um dos candidatos) ou instituto sem histórico. O painel já tem a convenção certa para isso
  no `DGM`/`DSM`, o terceiro elemento do par com o texto da suspensão (ver AL, AM, MS, RO, TO); use-a
  quando a pesquisa já estiver no painel e a suspensão vier depois, e simplesmente não insira quando a
  suspensão for anterior.
- PRES26 RN: A DIVERGÊNCIA QUE FICOU REGISTRADA (14/08/2026). O Instituto Consult/Tribuna do Norte
  (BR-09418/2026, campo 8-10/08, N=1.700) deu Lula 42,41 x Flávio 31,76 no RN, 10,65 pontos. A Metadata/
  Grupo Dial (BR-05736/2026, campo 6-8/08), que está no `PRES26`, dá Lula 54,6 x Flávio 23,4, mais de 31
  pontos, com 2º turno 60,2 x 30,7. Duas coletas separadas por DOIS dias e uma diferença de margem de 3
  para 1. Mantive a Metadata pela regra do dia anterior (a mais recente não tem 2º turno, e é dele que o
  `pmargin` tira a cor), e as duas dão o mesmo `lead` ('L'), então o mapa não muda de cor, só de
  intensidade. Mas fica o registro: essa é a maior discordância entre dois institutos na mesma janela
  que apareceu até aqui no mapa estadual, e quando a Datavero (RN-06313/2026) ou a do Mega Portal
  (RN-09307/2026) publicarem, elas servem de desempate. Conferido que a Metadata é ESTADUAL apesar do
  "Natal" no nome: são 1.536 entrevistas em 63 municípios do RN, e "Grupo Dial Natal" é o nome do grupo
  de comunicação, não o recorte da amostra. Não repetir a suspeita a cada rodada.
- A QUAEST TROCOU DE CONTRATANTE, E ISSO MUDA O QUE ESPERAR DELA (14/08/2026). A rodada de 10-13/8
  (BR-06773/2026, N=2.004, divulgada em 14/8 às 18h) é a PRIMEIRA encomendada pela GLOBO em parceria
  com o jornal O Globo. Até a rodada de 31/7 a 3/8 quem pagava era o Banco Genial, e o painel a
  chamava de Genial/Quaest, com `ctt:'financeiro'`. Agora é `ct:'Globo e O Globo'` e `ctt:'mídia'`.
  O nome da CHAVE no `DI`, `T2R`, `IM` e `VH2DET` continua 'Quaest' e NÃO deve ser renomeado, senão o
  house effect para de casar. O que importa para as próximas rodadas: a Globo anunciou 130 pesquisas
  até 3 de outubro, de presidente, Senado e governos de todos os estados e do DF, divididas entre
  Quaest e Datafolha. Ou seja, a lacuna estadual do painel deve fechar sozinha nas próximas semanas,
  e o radar do TSE vai passar a acusar muita coisa com contratante GLOBO COMUNICACAO E PARTICIPACOES.
- POR QUE A MEDIANA DO 1º TURNO NÃO SE MEXEU COM A QUAEST NOVA (14/08/2026). A rodada nova trocou
  Lula 39 x Flávio 30 por 38 x 31, e a mediana de agosto ficou parada em Lula 40,5 x Flávio 35. Não é
  erro de conta: com oito institutos a mediana é a média dos dois valores centrais, e a Quaest está
  ABAIXO da mediana nos dois lados, tanto antes quanto depois, então ela nunca entra no meio da fila.
  O 2º turno, sim, andou, porque ali a conta é a mediana das MARGENS: caiu de Lula +3,4 para +2,5 em
  amostra total e de +3,6 para +2,9 em votos válidos, e o placar do banner foi de 47,1 x 43,7 para
  46,6 x 44,1. Já o cenário de estresse ficou idêntico em Flávio +2,5, porque ele parte da mediana
  BRUTA das margens, que continua 2,75. Guardar este exemplo: rodada nova de um instituto de cauda
  mexe no 2º turno e não mexe no 1º, e isso é propriedade da mediana, não defeito.
- SENADO, VAGAS E NEGRITO (21/07/2026). Em 2026 TODOS os 27 estados elegem DOIS senadores: o Senado tem 81 cadeiras, 3 por unidade da federação, renovadas alternadamente em 1/3 (1 vaga) e 2/3 (2 vagas), e 2026 é ano de 2/3 (2014 e 2022 foram 1; 2018 e 2026 são 2). O painel destaca em negrito tantos nomes quantas forem as vagas: 2 no Senado, 1 no Governador. Implementado em `SENVAGAS_PADRAO=2` + `SENVAGAS_UF={}` (override por estado, hoje vazio, para vaga extra por cassação/renúncia/morte) + `senVagas(uf)` + `nDestaque(office,uf)`, consumidos por `stateSinglePoll(d,nb)` e `stateInstTable(monthsObj,nb)`. Não fixar o 2 no código nem voltar a destacar só o primeiro colocado.

O painel foi muito reformulado em jun-jul/2026. Ao regenerar/atualizar, siga o estado ATUAL abaixo, nunca versões antigas desta metodologia:
- O HOUSE EFFECT é de 2º TURNO (Lula x Flávio). Fonte de verdade: objeto `VH2DET` (por instituto: anos das eleições cobertas + erro por eleição = margem da última pesquisa de 2º turno menos a margem da urna TSE); `VHIST2` é DERIVADO como a média desses erros. Valores atuais: Datafolha +0,8 (2010-2022), AtlasIntel +5,0 (2022), Quaest +2,2 (2022), Paraná −6,3 (2018-2022), Meio/Ideia +2,2 (2018-2022). Urna TSE (válidos): 2010 Dilma +12,10 · 2014 Dilma +3,28 · 2018 Haddad −10,26 · 2022 Lula +1,80. NÃO usar house effect de 1º turno (VHIST/VLULA/adjMonth) na aba nem no gráfico. NÃO voltar ao "erro só de 2022".
- A aba GRÁFICO tem UM ÚNICO gráfico (mudança 09/07/2026, a pedido do usuário): `chartSVG` = "1º turno ajustado pelo house effect". Mesmo estilo de sempre (linhas Lula vermelha / Flávio azul, faixa de erro hachurada, eventos `PEVENTS`, mês recente <3 institutos tracejado/ponto vazado), mas as LINHAS agora plotam os valores AJUSTADOS (`adjMonth`, que aplica VHIST/VLULA por instituto), NÃO os brutos (`avgMonth`). Eixo Y reescalado para 30-44 (`yv(v)=57.5+(44-v)*16.0714`) para caber o ajustado. A legenda diz "Lula (ajustado)"/"Flávio (ajustado)". O `marginChart` (margem do 2º turno) foi REMOVIDO da aba — a função ainda existe no código mas NÃO é mais chamada; não reintroduzir. O house effect do 2º turno continua só na ABA "House effect". NÃO voltar o gráfico para valores brutos (`avgMonth`).
- As COLUNAS de candidatos na aba Institutos se reordenam pela média do mês (maior à esquerda), objeto `CAND`.
- Existe 4ª aba MAPA (presidencial por estado) com SELETOR DE ANO (`cur.mapyear`, `window.setMapYear`): 2018/2022 = resultado real do 2º turno por estado (objetos `PRES2018`/`PRES2022`, urna/TSE); 2026 = pesquisas estaduais (`PRES26`, só ~9 estados coloridos). Padrão 2026. 2018/2022 é comparação que o usuário ESCOLHE (não é o padrão nem "a corrida atual"). Estados clicáveis (`window.openPresState`, mostra o ano selecionado). Helper `ufOf` conserta o id quebrado de AC/RO no topojson. Não remover.
- BARRA DO VOTO POPULAR na aba Mapa (17/07/2026, pedida pelo usuário). Só nos anos 2018 e 2022 (em 2026 não há resultado, `natBar` devolve ''). Barra única horizontal dividida em vermelho (esquerda) e azul (direita), com marcador vertical nos 50% e leitura "X venceu por N pontos". Objeto `PRESNAT` = resultado NACIONAL do 2º turno em votos válidos (TSE): 2018 Haddad 44,87 x Bolsonaro 55,13; 2022 Lula 50,90 x Bolsonaro 49,10. Confere com o anchor do VH2DET (2018 −10,26 · 2022 +1,80) e soma 100 nos dois anos. Serve de contraponto ao mapa: em 2022 a linha dos 50% quase encosta na divisa (Lula +1,8) enquanto a direita venceu em mais estados — é o ponto que o rodapé do mapa já fazia. Não remover nem trocar por média dos estados (seria errado: exige ponderar pelo eleitorado).
- FAIXA DE FASES DO CALENDÁRIO (20/07/2026). Objeto `CAL` + `CALNOTA` + `calFase()`/`calStrip()`, renderizada na div `#calstrip` (abaixo do banner). Mostra pré-campanha → convenções (20/7-5/8) → registro (até 15/8) → campanha (16/8-3/10) → 1º turno (4/10) → 2º turno (25/10), destacando a fase ATUAL e dizendo quantos dias faltam para a próxima. A fase é calculada ao vivo com `new Date()` (como a contagem regressiva; só o CARIMBO é manual). Aparece nas 3 dimensões e some dentro do painel de um estado. Datas OFICIAIS do TSE (calendário aprovado em 2/3/2026, infográfico JOTA de 4/3/2026) — não alterar sem fonte. Serve de contexto estrutural: até o registro (15/8) o campo de candidatos NÃO está fechado, o que é o que dá sentido às pesquisas que testam substitutos do Flávio; e a partir de 16/8 (rádio e TV) há quebra estrutural, pesquisas de antes e depois não são diretamente comparáveis.
- RELÓGIO DO AMBIENTE PODE ESTAR ERRADO (descoberto 20/07/2026): o `date` do sandbox estava 3 dias atrasado (dizia 17/07) e eu carimbei o painel com data errada. Para o carimbo e para qualquer conferência de data, pegar a hora pelo NAVEGADOR (`new Date().toLocaleString('pt-BR',{timeZone:'America/Sao_Paulo'})`), não pelo shell. Sintoma que denunciou: matéria da Gazeta com data "futura".
- REGRA DE FONTE (vale para tudo): prioridade TSE (base primária: resultados + PesqEle) > imprensa/instituto > Wikipédia (só em último caso). O campo `u` (link) aponta para a fonte de maior prioridade obtida.
- TEMA CLARO/ESCURO (10/07/2026). O painel tem um BOTÃO ÚNICO e discreto (ícone + rótulo, sem preenchimento) na faixa dourada do topo, ACIMA do título e centralizado, div `#themetog`. Cada clique CICLA Sistema → Claro → Escuro → Sistema (ordem em `TORDER`, ícones em `TICO`, rótulos em `TLBL`); `paintToggle()` mostra o modo atual e o onclick vai para o próximo. Preferência em `localStorage['ep-theme']`. NÃO escrever cor literal em lugar nenhum: a paleta vive em custom properties do CSS (`:root`, `:root[data-theme="dark"]` e a media query `prefers-color-scheme` para o modo Sistema). O JS lê a paleta em `P` via `readPal()` (getComputedStyle) e TODO desenho (HTML e SVG) usa `P.surf`, `P.txt`, `P.red`, `P.blue`, `P.ink`, `P.purple`, `P.mut`, etc. O modo escuro usa a paleta "Grafite neutro" (cinza-grafite puro, escolhida pelo usuário em 10/07/2026 entre 4 opções: bg #121212, surf #1c1c1c, band #1f1f1f com título dourado #e0c877, aba ativa roxa #3d3168, sem dominância de cor; o marrom-oliva anterior foi rejeitado). NÃO voltar ao band marrom nem mudar essa paleta sem o usuário pedir. Trocar de tema chama `applyTheme()` → `readPal()` + `render()`, então os SVGs são regerados com as cores novas (por isso não se usa `var()` dentro de atributo de SVG). Exceções propositais que continuam literais: `#fff` como texto branco SOBRE cor forte, e as cores dos candidatos do mapa (Caiado `#2e8b57`, Renan `#7a3fb0`, Zema `#e8730c`, empate `#c9a227`, outros `#9a9a9a`). `PEVENTS[].c` guarda TOKEN ('red'/'blue'), resolvido em `evc()` no render — nunca hex, senão congela no tema do carregamento. `mixw()` mistura a cor do candidato com `P.surf` (não com branco fixo), senão a intensidade do mapa fica errada no escuro.
- ÍCONES no padrão iOS (20/07/2026). Gerados por `_gera_icones_agregador.py` (mesma receita do `tabelinha/_gera_icones.py` do Self Creighton: squircle superelipse n=5, peça elevada com gradiente próprio, fio de luz na aresta, especular banda+radial para ler como vidro, base escurecida, sombra montada no canvas INTEIRO senão vira halo). Variante escolhida pelo usuário: **medidor** (arco vermelho à esquerda, azul à direita, ponteiro dourado quase de pé com leve inclinação à direita, pivô creme, placa roxa). O script gera PNG (32/64/180/512) e SVG das MESMAS constantes, para não divergirem; `python3 _gera_icones_agregador.py medidor` regera tudo em `icones_agregador/medidor/`. Os arquivos ficam ao lado do HTML em `/home/rafaelcortopassi/electoralpolls/` e o `<head>` os referencia por caminho relativo (favicon.svg, favicon-32/64.png, apple-touch-icon.png de 180px + `apple-mobile-web-app-title`). Isso DEIXOU DE SER data URI: o HTML não é mais 100% autossuficiente para o ícone, mas ganha ícone de tela de início no iOS. Se mudar de variante, rodar o script e subir os 5 arquivos pela API antes de publicar o HTML. Outras variantes prontas no script: barras, anel, curvas.
- REVISÃO DE RIGOR CIENTÍFICO (10/07/2026, o usuário pediu "todas as alterações sugeridas"). Seis mudanças, todas no sentido de mostrar MENOS certeza do que os dados sustentam:
  (1) BANNER não mostra mais "X% de chance de vitória" (era `Φ(margem/6)`, com sigma arbitrário e falsa precisão sobre um empate). Agora mostra faixa qualitativa: se |margem| < 2×moeMonth = "Empate técnico" (com a margem entre parênteses, "dentro da margem"); senão "leve vantagem" (< 4×moe) ou "vantagem clara". Segunda linha em cinza: "Foto do [ctx] em [mês], não é previsão para outubro · faltam N dias para o 1º turno (4/out)". N vem de `new Date()` (contagem regressiva é legitimamente ao vivo; só o CARIMBO é manual). Hoje mai/jun/jul dão todos "empate técnico". O `stateBanner` (governador/senador) ganhou a mesma lógica com marMoe fixo=5 ("Disputa aberta"/"leve vantagem"/"vantagem clara"). `ncdf` virou código morto.
  (2) HOUSE EFFECT REGULARIZADO: o viés medido é ENCOLHIDO na direção de zero por `shrink(b,n)=b*n/(n+1)` (n=nº de eleições, `hn()`), porque 1 eleição não é tendência. Aplicado via `avies2/avies/avlula` (usados por adjMonth, adj2Month, aba House effect e banner); `vies2/vies/vlula` seguem crus (usados na gaveta e na coluna "medido"). ATUALIZADO 20/07/2026: o `VH2DET` passou de 5 para 9 institutos (acrescentados CNT/MDA 2014-2022 e Apex/Futura, PoderData, Gerp só 2022; Apex/Futura herda a linhagem Modalmais/Futura). Aplicado (medido→aplicado): Datafolha +0,8→+0,6 (4 el.), CNT/MDA −2,3→−1,7 (3 el.), Paraná −6,3→−4,2 (2 el.), Meio/Ideia +2,2→+1,5 (2 el.), AtlasIntel +5,0→+2,5, Quaest +2,2→+1,1, PoderData +4,2→+2,1, Apex/Futura −2,4→−1,2, Gerp −5,8→−2,9 (1 el. cada). NOTA: o Nexus/BTG chegou a entrar (só 2018, pesquisa NÃO-final, aplicado −4,9) mas foi REMOVIDO no mesmo dia, a pedido do usuário, por ser frágil demais — não reintroduzir sem pesquisa final vs urna. Cabeçalho da aba virou "Ajustada (viés regularizado)".
  (3) AGREGADO = MEDIANA, SEM EXCLUSÃO (mudança 20/07/2026, a pedido do usuário). Antes: média simples com `OUTLIERS={Veritá, Vetor/Arrow}` excluídos. Agora: `OUTLIERS={}` VAZIO e todo o agregado usa a função `med()` (mediana) no lugar da média — avgMonth, adjMonth, adj2Month, moeMonth, cavg/cavgFor. Motivo: a mediana é naturalmente robusta a outlier, então ninguém precisa ser excluído (o problema clássico do RCP é a média deixar um outlier distorcer o consenso; a mediana resolve sem julgar quem é "outlier"). `isOut()` continua existindo mas sempre retorna false com o objeto vazio. Rodapés das abas Institutos e Gráfico dizem "MEDIANA de TODOS os institutos (não a média)". NÃO reintroduzir exclusão nem voltar para média.
  (4) TENDÊNCIA: setinha ▲/▼ + delta no cabeçalho de cada coluna da tabela de Institutos (`trendArrow`/`cavgFor`, agregado do mês vs mês anterior).
  (5) FAIXA DE ERRO do gráfico rotulada como "margem de erro TÍPICA de uma pesquisa (não do agregado)".
  (6) RESSALVAS nos rodapés: indecisos (Br/N/Ind) não são realocados no 2º turno; mercados Polymarket/Kalshi são cotação de 1/7/2026 que não atualiza sozinha.
- BASE DO 2º TURNO na aba House effect (17/07/2026). A aba mostra uma faixa com quantos institutos publicaram cenário de 2º turno em CADA mês (helper `t2cov(m)` → [publicaram, total do mês], já sem outliers). Cores: 0 = cinza, 1-2 = dourado (base fina), 3+ = normal. Quando o mês tem menos de 3, aparece o aviso "Base fina: o ajuste de X se apoia em N institutos só". Motivo: o ajuste de mar/abr/mai se apoia em só 2 institutos cada (mai = AtlasIntel e Gerp, que puxam para lados opostos), contra 6 em jun/jul. Não escrever o mês de comparação à mão: usa `months[months.length-1]`.
- JUDICIALIZAÇÃO DO 2º TURNO (risco a monitorar, NÃO é ressalva do painel). Matéria da Gazeta de 03/07/2026 (Gustavo Ribeiro): institutos pararam de perguntar 2º turno por medo de impugnação; partidos exigem que os cenários incluam todos os pré-candidatos e vêm ganhando nos TREs; sem jurisprudência uniforme porque quase nada chega ao TSE. IMPORTANTE: cheguei a propor uma ressalva no painel dizendo que "a amostra de 2º turno está encolhendo", e os DADOS DERRUBARAM isso — a cobertura nacional está CRESCENDO (jan 0, fev 0, mar 2, abr 2, mai 2, jun 6/11, jul 6/6). A matéria fala de pesquisas DE GOVERNADOR em estados específicos, não do presidencial nacional. NÃO adicionar essa ressalva ao painel sem antes rodar `t2cov` e checar se a cobertura realmente caiu. Cicatriz real e já sinalizada: o 1º turno do Flávio na AtlasIntel de maio foi vetado por liminar (Kassio) e o 34* é reconstruído.
- VERITÁ: FONTE PRÓPRIA E QUAL COLUNA LER (02/08/2026). O Instituto Veritá publica as íntegras em
  PDF, de graça e sem cadastro, em `https://eleicoes26.institutoverita.com.br/` (a home lista todas
  as rodadas com data de divulgação, e cada página tem o link direto do PDF, hospedado no Supabase).
  É a fonte mais rápida e completa para ele, melhor que esperar a imprensa local. QUAL NÚMERO ENTRA:
  os relatórios dele trazem TRÊS colunas por pergunta (Frequência, Porcentual, Porcentagem válida), e
  o painel usa a coluna **Porcentual** (amostra total) para governador e presidente, que é o que
  mantém a comparabilidade com Paraná Pesquisas, Quaest, Neokemp e afins. Conferido contra o PDF do
  Paraná de junho: o 52,7 do Moro que está no `DGM` é o Porcentual, não os 57,9 dos válidos. Para
  SENADOR, onde o eleitor tem dois votos, entra a **Porcentagem de casos** do bloco "CONSOLIDAÇÃO DAS
  PERGUNTAS X E Y", também conferido contra junho (Deltan 35,6). Ler a coluna errada infla o
  instituto em 6 a 10 pontos e faz parecer house effect o que é só base diferente.
  RITMO DE PUBLICAÇÃO (visto em 02/08/2026): a data de divulgação do registro no TSE chega ANTES
  da íntegra aparecer na home do instituto. Naquele dia o TSE já listava as rodadas de PR, AP, AM
  e PA com divulgação em 2 e 3/8, e a home só tinha PR e MA. Não vale insistir nem procurar em
  portal local: sem PDF, o número não existe ainda, e a rodada seguinte da tarefa pega.
- MÊS DE UMA RODADA QUE ATRAVESSA A VIRADA (02/08/2026). Rodada com campo em dois meses entra no mês
  em que o campo TERMINA, que é também como o próprio instituto batiza o relatório. Precedente que
  fixou a regra: a nota do `DI` de agosto já tratava a Nexus de campo 31/7 a 2/8 como a primeira
  rodada de AGOSTO, e a Veritá do Paraná (campo 28/7 a 1/8) veio com o PDF chamado
  "Relatorio_Parana_Agosto_2026", enquanto a do Maranhão (25 a 29/7) veio como "Julho". Por isso o
  Paraná abriu o mês 'ago' no `DGM`/`DSM` e o Maranhão entrou em 'jul'.
- A CNN BRASIL É A FONTE MAIS RÁPIDA DAS RODADAS ESTADUAIS DA RTBD (04/08/2026). A rodada do Pará
  (BR-09650/2026 e PA-08492/2026, campo 30/07 a 03/08) estava completa na CNN às 7h da manhã do dia
  da divulgação, em três matérias separadas (presidente no estado, governador, Senado), com 1º e 2º
  turno, enquanto o Poder360 e a Gazeta do Povo ainda não tinham nada daquele dia. Índice:
  `cnnbrasil.com.br/tudo-sobre/pesquisas-eleitorais/`. Vale para o horário desta tarefa, que acorda
  cedo: quando o radar apontar RTBD, olhar a CNN ANTES do Poder360.
  RESSALVA QUE JÁ QUASE ENGANOU: a CNN declara que gera esses textos por IA a partir do relatório
  do instituto, e o bloco "Metodologia" das duas matérias do PARÁ dizia "ouvidas 1.600 pessoas no
  estado de PERNAMBUCO". O corpo da matéria e o protocolo TSE (PA-08492/2026) estavam certos. Ou
  seja: conferir sempre o estado pelo PROTOCOLO, nunca pela frase da metodologia.
- Ao atualizar dados, AVANÇAR o carimbo "Última atualização: DD/MM/AAAA HH:MM" (é manual).

Estrutura do painel: QUATRO abas no topo (acima dos meses):
- Aba "Institutos": dados BRUTOS por instituto; colunas de candidatos ordenadas pela média do mês (objeto `CAND`); Br/N/Ind; 2º turno. Headline = caixas Polymarket + Kalshi.
- Aba "House effect": 2º TURNO Lula x Flávio. Por instituto: margem bruta do 2º turno → ajustada pelo viés histórico dele = média do erro em TODAS as eleições que cobriu (`VH2DET`→`VHIST2`: Datafolha +0,8 [2010-2022], AtlasIntel +5,0 [2022], Quaest +2,2 [2022], Paraná −6,3 [2018-2022], Meio/Ideia +2,2 [2018-2022]; só esses 5 têm histórico, resto "sem histórico"). Cada linha mostra os anos usados; o cabeçalho é "Ajustada (viés histórico vs urna)". Funções `adj2Month`/`t2margin`/`vies2`/`vies2anos`/`vies2n`/`has2`/`m2str`.
- Aba "Gráfico": linha do tempo do 1º turno AJUSTADO pelo house effect, `chartSVG()` (plota `adjMonth`, não `avgMonth`). Vermelho = Lula, azul = Flávio, faixa hachurada = margem de erro em torno da linha ajustada, linhas pontilhadas verticais numeradas = eventos (`PEVENTS`). Mês recente com <3 institutos = tracejado/ponto vazado (provisório). Um único gráfico (o marginChart do 2º turno foi removido daqui em 09/07/2026).
- Aba "Mapa": mapa do Brasil com seletor de ano 2018/2022/2026 (botões chamam `setMapYear`). Vermelho = esquerda/PT (Haddad 2018, Lula 2022/2026), azul = direita (Bolsonaro 2018/2022, Flávio 2026). 2018/2022 colorem todos os estados (resultado de urna); 2026 só os ~9 com pesquisa, resto bege. Estados clicáveis abrem gaveta com o dado do ano + fonte (TSE p/ urna, instituto p/ pesquisa). Funções `presLead` (lê `cur.mapyear`)/`drawPresMap`/`openPresState`; helper `ufOf`.
- VERITÁ ESTÁ BARRADO EM SE E RN (constatado em 15/08/2026). O TRE-SE proibiu em 07/08/2026 a divulgação de pesquisa do instituto por super-representar eleitor com ensino superior (declarou 31,1% quando o dado oficial é 12,82%), e o TRE-RN fez o mesmo em 12/08/2026 para governo e Senado (34% de superior contra 13,73% reais), em reincidência que já rendera multa de mais de R$ 58 mil. O registro SE-05262/2026, campo 08 a 12/08 e divulgação em 13/08, é justamente o novo levantamento feito com os mesmos critérios tidos como irregulares, e por isso NÃO foi inserido. Antes de inserir qualquer Veritá estadual, conferir se aquele estado tem proibição vigente. Isso vale só para o estadual: `OUTLIERS={}` continua vazio e o Veritá nacional segue contando no `DI`.
- ESCALA DO SENADO VARIA ENTRE INSTITUTOS, e misturar corrompe o `stateBanner`. Em 2026 cada eleitor escolhe DOIS senadores, então uns publicam o "1º voto" (soma perto de 100), outros o "consolidado" dos dois votos (soma perto de 200). Constatado em 15/08/2026 no RN: o Seta publica consolidado (Styvenson 45,5 e Zenaide 40 em agosto) enquanto Metadata, Consult e DataVero publicam escala de voto único (Styvenson entre 19,8 e 27,5). Alguém já resolveu isso em julho DIVIDINDO o Seta por 2 (47,7 virou 23,85, 41,6 virou 20,8), o que não é conversão válida e não estava documentado. Por isso o Seta de agosto entrou só em governador, onde a escala é inequívoca, e ficou de fora do `DSM`. Regra: conferir a soma da linha antes de inserir Senado e, se passar de 100, ou achar a tabela de 1º voto ou não inserir.
- FALSO POSITIVO DE NACIONAL: A DMP É DO AMAZONAS (17/08/2026). O radar apontou BR-08020/2026 (DMP
  PESQUISA E EVENTOS, campo 11-14/08, N=2.000, contratante REDE DE RADIO E TELEVISAO TIRADENTES)
  como NACIONAL?, por não ter gêmeo estadual registrado. Não é nacional. O campo
  `DS_PLANO_AMOSTRAL` do próprio CSV do TSE resolve sem sair do terminal: "o universo da pesquisa é
  composto por eleitores que residem e votam na capital (Manaus) e nos 61 municípios do estado do
  Amazonas". A rodada anterior do mesmo instituto, BR-05620/2026 (campo 1-3/07, N=1.200), diz a
  mesma coisa com 19 municípios. As duas alimentam o `PRES26` do AM, nunca o `DI`. REGRA QUE FICA,
  e que é mais barata que abrir matéria: quando o registro aparecer como NACIONAL? sem gêmeo, LEIA
  `DS_PLANO_AMOSTRAL` e `DS_DADO_MUNICIPIO` antes de qualquer outra coisa. O texto do plano amostral
  quase sempre declara o universo com todas as letras, e vale mais do que o N ou o custo.
- A SUSPENSÃO ATRIBUÍDA AO INSTITUTO FRANÇA EM SE NÃO SE CONFIRMOU (17/08/2026). A nota de
  14/08/2026 acima diz que SE-04226/2026 e os gêmeos presidenciais BR-03921/2026 e BR-05808/2026
  (Instituto França, campo 10-12/08) foram suspensos pelo TRE-SE. Fui conferir antes de inserir e
  não achei nenhuma decisão contra o França. As suspensões de pesquisa em Sergipe neste ciclo que
  se confirmam nas fontes são de OUTROS institutos: a ECM (Edição, Comunicação & Marketing Eireli),
  barrada em 04/08/2026 a pedido do Republicanos por não comprovar a origem dos recursos, com multa
  diária de R$ 5 mil; o Instituto CTAS (SE-05326/2026 e SE-06052/2026, junho); e uma do Real Time
  Big Data. A confusão provável é com a ECM, que também põe Mitidieri na frente. Contra a suspensão
  pesa ainda o fato de a rodada ter sido publicada em 15/08 por veículos de Sergipe e em 16/08 pelo
  Poder360, que hospedou a ÍNTEGRA em `static.poder360.com.br` e citou o BR-05808/2026 no texto,
  o que não aconteceria sob liminar com multa diária. Por isso ela ENTROU no painel em 17/08, nas
  três frentes (governo e Senado no `DGM`/`DSM` e no `DG`/`DS`, presidencial no `PRES26` do SE).
  ATENÇÃO PARA A PRÓXIMA RODADA: a ECM tem registro novo na fila, SE-02682/2026 (campo 9-12/08,
  divulgação 15/08). Dado o histórico, não inserir ECM em Sergipe sem antes conferir se a decisão
  de 04/08 alcança também essa rodada.
- O PLANO AMOSTRAL RESOLVE A FILA MAIS BARATO DO QUE QUALQUER BUSCA (17/08/2026, à noite). A regra de
  17/08 sobre a DMP do Amazonas ("leia `DS_PLANO_AMOSTRAL` antes de qualquer outra coisa") vale muito
  além do desempate nacional x estadual: aplicada aos 16 itens da fila, ela matou dois de uma vez, sem
  abrir uma página. **RJ-06580/2026** (D'Art, N=474, contratante RJInterior Comunicação) diz com todas
  as letras "distribuídas entre as localidades do município de Macaé (RJ)": é municipal, não alimenta
  `DGM`/`DSM`. **PI-00748/2026 e o gêmeo BR-00662/2026** (Instituto Amostragem, N=1.700) dizem "o
  conjunto do eleitorado do município ... referente ao município TERESINA-PI": também municipal,
  apesar do N grande e do cargo "Governador, Senador" no registro. Ou seja, o N pequeno é um INDÍCIO
  de recorte local (regra de 14 e 15/08), mas o plano amostral é a PROVA, e ele pega o caso que o N
  deixa passar: 1.700 entrevistas só em Teresina parecem estaduais até você ler o campo. Ler o plano
  amostral dos itens da fila deve ser o PRIMEIRO passo da rodada humana, antes de qualquer busca.
- O INSTITUTO AMOSTRAGEM TEVE O GOVERNADOR SUSPENSO NO PIAUÍ POR EFEITO DE ANCORAGEM (17/08/2026).
  Além de ser municipal (parágrafo acima), a PI-00748/2026 foi suspensa em 14/08 pela desembargadora
  Lucicleide Pereira Belo, do TRE-PI, a pedido da federação União Progressista. O fundamento é novo
  no ciclo e vale guardar: não é amostra nem dinheiro, é a ORDEM DAS PERGUNTAS. O questionário punha
  uma sequência longa de avaliação do governador (Piauí Saúde Digital, Escola de Tempo Integral, Mais
  Asfalto e outros) e a pergunta "qual a maior obra do gestor" ANTES da espontânea de intenção de
  voto, o que a decisão chamou de efeito de ancoragem "manifesto e auto evidente". A suspensão é
  PARCIAL: senador, deputado federal e estadual seguem liberados, só governador está barrado. Fonte:
  GP1, 15/08/2026. Regra que fica: suspensão pode alcançar um cargo só, então antes de descartar a
  rodada inteira confira o alcance da decisão, e antes de inserir governador de instituto local
  procure também por "pergunta tendenciosa" e "ancoragem", não só por "origem dos recursos".
- FONTE QUE SOME EM 24 HORAS: A DOXA NO PARÁ (17/08/2026). A rodada PA-01857/2026 + BR-06005/2026
  (Doxa, campo 10-15/08, N=2.000, margem 3,1, contratante a própria Doxa) foi divulgada em 16/08 e no
  dia seguinte TRÊS das quatro fontes já estavam mortas: o post do próprio instituto
  (`pesquisasdoxa.com/post/...`) e as duas matérias da Gazeta Carajás (governo, Senado e presidente)
  devolvem 404, embora os trechos sigam no índice do buscador. Não há decisão judicial contra a Doxa
  que explique isso (a suspensão do TRE-PA em julho foi do Veritá, PA-09674/2026). O que sobreviveu
  foi o Portal O Fato, e é dele que saiu o governador que entrou no `DGM`: Hana Ghassan 35,1 e
  Dr. Daniel 30,2, só os dois nomes, porque a matéria viva só publicou a estimulada da dupla. O
  Senado (Helder 25,32) e o presidencial (Lula 38,5 x Flávio 32,6, sem 2º turno conhecido) ficaram de
  FORA por não terem fonte viva que se possa citar no campo `u`. Por isso o `PRES26['PA']` continua
  com o Real Time Big Data de 30/07-03/08, que tem 2º turno (45 x 36) e link que abre, e o `DG['PA']`
  também continua no RTBD, que é a linha completa com cinco nomes e 2º turno. É desvio consciente do
  "DG mostra a mais recente": trocar cinco nomes mais 2º turno por dois nomes sem 2º turno degradaria
  o cartão do mapa por onze dias de recência. REGRA QUE FICA: quando a fonte de prioridade 1 e 2 cair,
  não se insere pelo snippet do buscador; e vale COPIAR o número e o link vivo na mesma sessão em que
  se acha, porque em pesquisa regional a janela pode ser de horas.
- `pmargin` LIA MARGEM COM DECIMAL PELA METADE (18/08/2026). Nos estados sem 2º turno divulgado, a
  intensidade de cor do mapa sai do texto do campo `t2`, e a expressão era `/(\d+)\s*pontos/`: em
  "Lula abre 9,4 pontos" ela casava com "4 pontos" e o estado era pintado como se a diferença fosse
  de 4, não de 9,4. Era o caso do AM. A expressão passou a aceitar o decimal e a trocar vírgula por
  ponto antes do `parseFloat`. Ao escrever `t2` em texto, o número pode agora ter vírgula, mas
  confira que ele é o PRIMEIRO "N pontos" da frase, porque `match` sem `/g` pega só a primeira
  ocorrência.

Objeto de dados a manter: `DI` (brutos por instituto, jan-jul). Ao atualizar números, acrescentar rodadas ao `DI`; house effect (2º turno), gráfico e mapa derivam dele. O objeto `VHIST`/`VLULA` (1º turno) ainda existe só para a gaveta lateral, NÃO para o gráfico.

## Duas falhas MUDAS da rodada mecânica, achadas e corrigidas em 19/08/2026

As duas faziam o `PENDENCIAS.md` sair com a fila e a tabela do TSE vazias, o que uma rodada
local lê como "não há pesquisa nova" e encerra em duas linhas. O workflow ficava VERDE nas
duas, porque as exceções eram engolidas e viravam lista vazia. É o modo de falha mais caro
que este projeto tem: o painel para de andar sem que ninguém tenha decidido isso.

**1. O CDN do TSE passou a devolver 403.** `cdn.tse.jus.br` ficou atrás de Cloudflare e
recusa User-Agent de robô. As quatro rodadas de 19/08 falharam assim, e o relatório das 19h35
saiu dizendo zero divulgações quando havia 52 registradas em quatro dias. Não é DNS nem
proxy: com o conjunto de cabeçalhos de navegador COMPLETO (User-Agent do Chrome mais Accept,
Accept-Language, Accept-Encoding, Connection, Upgrade-Insecure-Requests e os quatro
Sec-Fetch) o download volta a passar em stdlib puro, 4 tentativas em 4. Só trocar o
User-Agent NÃO basta, foi testado e continuou 403. Os cabeçalhos estão em
`radar_tse.CABECALHOS`, com três tentativas e espera crescente. Não enxugue essa lista.

**2. O gêmeo estadual era casado pelo nome do ARQUIVO, e não pela coluna `SG_UF`.** O CSV
`pesquisa_eleitoral_2026_BRASIL.csv` guarda também os registros ESTADUAIS de quem perguntou
presidente: 1.014 deles em 19/08/2026, contra 626 de fato nacionais. Como o filtro era
`_UF != "BRASIL"`, esses 1.014 ficavam de fora do índice de gêmeos e a pesquisa estadual
correspondente era anunciada como `NACIONAL?`. Pego na Real Time Big Data do DF, em que
`BR054232026` e `DF078492026` têm o mesmo CNPJ, o mesmo campo (14 a 18/08) e o mesmo N
(1.600): é a rodada do Distrito Federal, e entrar no `DI` nacional teria sido erro grosso.
O escopo agora sai de `SG_UF` (campo `_SGUF`); o nome do arquivo continua servindo só para
não listar a mesma pesquisa duas vezes.

**3. Falha do radar agora é anunciada no topo do relatório.** `escreve_pendencias` recebe
`erro_tse` e escreve, em negrito, que nada foi varrido e que ausência não quer dizer ausência
de pesquisa. Rodada local que ler isso deve rodar `python3 radar_tse.py` à mão antes de
encerrar.

**O site do Veritá está fora do ar desde algum ponto antes de 19/08/2026.** O Supabase deles,
`lgjdbpskgjfbmlffbntx.supabase.co`, responde NXDOMAIN, e o próprio
`eleicoes26.institutoverita.com.br` mostra "Nenhuma pesquisa publicada ainda". Não é bug do
`radar_verita`: o bundle JS da home ainda aponta para esse mesmo projeto, que deixou de
existir. Enquanto durar, o `PENDENCIAS.md` vai dizer que não conseguiu ler a lista, e isso é
verdade, não falha nossa. O Veritá continua REGISTRANDO no TSE (nacional `BR040062026`, campo
16 a 20/08, e as estaduais de MG, MS e GO de 19 a 23/08), então o radar do TSE continua
pegando as rodadas deles; o que se perdeu foi o atalho para o PDF da íntegra.

## O `PENDENCIAS.md` só mostra o DELTA, e por isso uma pesquisa pode sumir

Registrado em 07/08/2026. O `rotina_6h.py` marca cada registro do TSE em `estado_rotina.json`
assim que o vê e, da rodada seguinte em diante, ele deixa de ser "novo". Se a rodada humana que
recebeu o aviso não inseriu o dado, seja porque o número ainda não estava publicado, seja porque
a sessão fez outra coisa, NINGUÉM avisa de novo: as rodadas seguintes dizem "nada novo" e a
pesquisa fica de fora para sempre.

Foi exatamente o que houve com a Real Time Big Data de Mato Grosso do Sul (campo 1 a 5/8,
divulgação 6/8, registros MS-07706/2026 e BR-01784/2026). Ela foi sinalizada, não entrou, e na
rodada de 07/08 02:48 o relatório já dizia "nada novo". Só apareceu porque, ao investigar a
pendência de Santa Catarina, a capa da Gazeta do Povo mostrava a matéria de MS como a mais
recente e o painel não tinha agosto naquele estado.

REMÉDIO ENQUANTO NÃO HOUVER CONFERÊNCIA AUTOMÁTICA: quando o `PENDENCIAS.md` apontar qualquer
novidade, antes de encerrar compare a capa da Gazeta do Povo e a tag `pesquisa-eleitoral` do
Poder360 com o que o painel tem no MÊS CORRENTE. É barato e pega o que escorreu. Cuidado para
não confundir com a regra de não fazer varredura pesada quando NÃO há novidade: aí a rodada
acaba em duas linhas mesmo.

## Registro com divulgação liberada ANTES do fim do campo (e o atalho do Poder360)

Registrado em 07/08/2026, a partir da pendência de Santa Catarina. O TSE pode ter DT_DIVULGACAO
anterior ao fim do campo: a Visão Pesquisas registrou SC-03192/2026 (governador, senador e
deputados) e o gêmeo presidencial BR-09228/2026, N=880, campo de 03/08 a 08/08, com divulgação
liberada em 07/08. Ou seja, o `PENDENCIAS.md` sinaliza a pesquisa como nova enquanto as
entrevistas ainda estão sendo feitas, e não existe número para procurar. Não é instituto que
registra e não publica: é pesquisa que ainda não terminou. Nesse caso não se insere nada e a
busca só faz sentido DEPOIS da data de fim do campo.

ATALHO QUE RESOLVE ISSO EM UMA PÁGINA: o Poder360 publica todo dia, por volta das 7h, a matéria
"Saiba quais pesquisas eleitorais podem sair nesta 6ª feira" (o dia da semana muda), na tag
`pesquisa-eleitoral`. Ela lista os levantamentos liberados para divulgação naquele dia com
instituto, contratante e as datas de entrevista. É a maneira mais barata de separar "vai sair
hoje" de "ainda está em campo", e de confirmar o contratante sem abrir o CSV do TSE. A de
07/08/2026 trazia exatamente a Visão Pesquisas de SC, financiamento próprio, entrevistas de 3 a
8 de agosto.

PENDENTE PARA A PRÓXIMA RODADA (senão o delta engole, como engoliu o MS): procurar o resultado da
Visão Pesquisas em SC a partir de 09/08/2026, presidencial, governador e senador. O painel hoje
tem SC com Neokemp de 22-24 jul no `DG`/`DS` e IPC/ACJ de 9-13 jul no `PRES26`, nenhum de agosto.
A busca do dia 07/08 no Poder360, na Gazeta do Povo e na web aberta não achou nada da Visão em
2026, só as rodadas dela de 2022, o que é coerente com o campo em andamento.

## Fontes dos dados

- Agregador Wikipédia: "Pesquisas de opinião para a eleição presidencial no Brasil em 2026" (base principal, por instituto e mês).
- Agregador Gazeta do Povo (eleicoes/2026/pesquisa-eleitoral-2026).
- Fontes primárias dos institutos e cobertura (CNN, Poder360, Exame, InfoMoney).

ONDE ACHAR O GÊMEO PRESIDENCIAL DE UMA ESTADUAL (aprendido em 07/08/2026, custou meia dúzia de
tentativas). A matéria do presidencial por estado NÃO aparece na capa da tag `pesquisa-eleitoral`
do Poder360, que lista sobretudo o governador e o senado. Ela está na TAG DO INSTITUTO, por
exemplo `poder360.com.br/tag/real-time-big-data/`, com título no formato "Flávio tem X% e Lula,
Y%, no 2º turno no UF". Vá pela tag do instituto sempre que o TSE mostrar um registro BR com
escopo ESTADUAL[UF] e a capa não trouxer nada.

E NÃO ADIANTA ADIVINHAR O NOME DO PDF: o do estadual e o do presidencial seguem padrões
diferentes, mesmo instituto e mesmo dia. Em 06/08/2026 o de MS saiu como
`Mato-Grosso-do-Sul-MS-07706_2026-AGO26-1.pdf` (registro no nome) e o presidencial como
`presidente-mato-grosso-do-sul-real-time-big-data-6ago.pdf` (sem registro nenhum). Abra a matéria
e leia o href; sondar URL por tentativa só gasta rodada.

## Três métricas no painel

1. Média simples (estilo RCP): média aritmética não ponderada das pesquisas do mês, uma rodada (a mais recente) por instituto.
2. Média ajustada por house effect (estilo 538): cada pesquisa é corrigida pelo viés do instituto antes de agregar.
3. Odds (probabilidade estimada de vitória): derivada da margem do 2º turno.

## Notas dos institutos (calibragem)

Calibradas pelo desempenho histórico: 2022 (1º turno real Lula 48,4% x Bolsonaro 43,2%; a maioria subestimou a direita; AtlasIntel foi a mais próxima) e 2024 municipais (AtlasIntel melhor desempenho geral, mais precisa em 13 disputas).

| Nota | Peso | Institutos |
|---|---|---|
| A+ | 1,00 | AtlasIntel |
| A | 0,90 | Quaest |
| A- | 0,80 | Datafolha, Ipespe |
| B | 0,55-0,60 | CNT/MDA, Nexus/BTG, PoderData, Paraná Pesquisas |
| B- | 0,50 | Real Time Big Data |
| C | 0,35 | Gerp, Apex/Futura, Veritá, Vetor/Arrow, Meio/Ideia, Indexa, Alfa, American Analytics |

Padrão de viés conhecido: AtlasIntel, Veritá, Vetor/Arrow e Gerp medem a direita mais forte; Quaest, Datafolha, CNT/MDA medem a direita mais fraca.

## House effect 1º turno (VIÉS HISTÓRICO vs urnas) — SUPERADO, só registro histórico

NOTA (jul/2026): esta seção descreve o house effect ANTIGO, de 1º turno (VHIST/VLULA/adjMonth). Foi SUBSTITUÍDO pelo house effect de 2º turno (objeto `VHIST2`, ver bloco "NÃO REVERTER" no topo). NÃO aplicar ao painel atual nem ao gráfico. Mantido abaixo apenas como registro.

Base mudada em 29/06/2026: de "desvio vs consenso 2026" para VIÉS HISTÓRICO frente ao RESULTADO REAL das urnas, desde 2010 ou desde quando o instituto tem dados.

Backtest 1º turno (pesquisa final de véspera vs urna): nas 4 últimas eleições a direita foi SUBESTIMADA (2014 Aécio +7,6; 2018 Bolsonaro +10; 2022 Bolsonaro +6 a +7), enquanto a esquerda foi medida com razoável precisão (Lula 2022 superestimado só ~2). Logo a correção incide quase toda no candidato da DIREITA (Flávio).

Viés histórico aplicado (pontos somados ao Flávio bruto), objeto JS `VHIST`:
- Datafolha +7 (2014, 2018, 2022)
- Quaest +3 (2022)
- Paraná Pesquisas +3 (2022)
- AtlasIntel +2 (2022; a mais acurada)
- Demais institutos: SEM ajuste (não mediram presidencial anterior; marcados "sem histórico"). Default removido em 30/06/2026.

Ajuste dos DOIS lados, ANCORADO NO ERRO MÉDIO REAL DE CADA INSTITUTO vs urnas (científico, não número redondo). Base: 2022 (votos válidos, urna Lula 48,4 / Bolsonaro 43,2), e Datafolha multi-eleição (2010-2022).

Erro de cada candidato por instituto, objetos JS `VHIST` (direita) e `VLULA` (esquerda):
- Direita subestimada (soma ao Flávio): Datafolha +7,2 · Quaest +3,2 · Paraná +3,2 · AtlasIntel +2,1.
- Esquerda superestimada (subtrai do Lula): Datafolha +1,6 · AtlasIntel +1,9 · Quaest +1,6 · Paraná −1,3 (a Paraná SUBESTIMAVA o Lula, então some).

ATUALIZAÇÃO 30/06/2026 (a pedido do usuário): REMOVIDO o default da "média do conjunto" para institutos sem histórico. `vies()` e `vlula()` retornam 0 quando o instituto não tem valor próprio. SÓ os 4 institutos com histórico real vs urnas (Datafolha, Quaest, Paraná, AtlasIntel) são ajustados; os demais entram no agregado SEM ajuste e aparecem marcados "sem histórico" (cor #b08900) na coluna Viés. Motivo: a maioria dos institutos novos (Nexus, Indexa, Apex, Vox, Gerp, etc.) não mediu a presidencial de 2022, então um default era chute, não ciência. **[CORREÇÃO 31/07/2026: a LISTA desta frase envelheceu, embora a DECISÃO de não usar default siga valendo e por esse mesmo motivo. Apex/Futura e Gerp foram atrás e TÊM house effect desde 20/07/2026 (Apex −2,4, Gerp −5,8, ambos de 2022); PoderData, RTBD e Veritá também entraram depois. Quem de fato não pode ter, auditado por CNPJ, é Alfa e Vox Brasil, e o Nexus/BTG foi removido de propósito por fragilidade. Ver o bloco "QUEM PODE TER HOUSE EFFECT: AUDITORIA POR CNPJ" no topo; a fonte de verdade é sempre o `VH2DET` do código, não esta lista.]** Achado científico mantido: o erro da direita (+2 a +7) é muito maior que o da esquerda (~+1,6), e a Paraná inverte o sinal na esquerda. Lula_aj = Lula − VLULA; Flávio_aj = Flávio + VHIST. Aba House effect calcula ao vivo do `DI`.

Efeito (sem default) por mês — bruto => ajustado: fev 39,7/34,4 => 39,4/35,6 · mar 39,2/36,0 => 38,4/37,7 · abr 40,4/35,4 => 39,6/37,4 · mai 40,3/34,1 => 39,9/35,1 · jun 40,1/32,0 => 39,8/32,9. Lula fica à frente no ajustado em TODOS os meses (março é o mais apertado, +0,7). O Flávio não cruza mais o Lula no 1º turno. Gráfico (chartSVG) agora é DINÂMICO: calcula brutos via avgMonth e ajustados via adjMonth, sem pontos chumbados. Texto "House Effect: desvio padrão histórico e sistemático..." adicionado na aba (div #heexpl, acima da legenda).

Central de notificações (gaveta lateral): ao clicar no nome do instituto mostra método, amostra (N), margem, ÚLTIMA PUBLICAÇÃO (data de campo) e LINK da fonte (objeto `IM`, campos `d` e `u`; Gazeta do Povo para alguns, Wikipédia para o resto).

Indicador "quem está à frente" (banner discreto acima das abas): mostra líder + % de chance de vitória do mês selecionado. Calculado do AGREGADO AJUSTADO (house effect): margem = Lula_aj − Flávio_aj; P = Φ(|margem|/6) via função `ncdf` (aprox. Abramowitz-Stegun); helper `adjMonth`. Desde a remoção do default (30/06/2026), o banner mostra Lula à frente em todos os meses (margem ajustada mínima +0,7 em março). Atualiza ao trocar o mês.

Base de institutos: campo brasileiro 2026 ativo tem ~17 institutos (todos no painel). "Times Brasil" = pesquisa da American Analytics (mesmo dado). Ipsos-Ipec só publicou dez/2025 (fora do recorte). Ipespe faz o Índice CNN (agregador), não horse-race próprio. A base já é praticamente o campo completo; o diferencial é frescor (monitorar) e metodologia.

Limitações: o "erro final vs urna" combina house effect + movimento de reta final (indecisos decidindo) + comparecimento, não é house effect puro; aplicar o viés de pesquisa FINAL a uma pesquisa de junho (4 meses antes) é heurística, não previsão; a amostra histórica é curta (no máximo 4 eleições, 2010-2022, e a maioria dos institutos só tem 1 ou 2); só 5 institutos têm histórico próprio (Datafolha 4, Paraná e Meio/Ideia 2, Quaest e AtlasIntel 1 cada), o resto entra sem ajuste. Institutos com 1 só eleição (Quaest, AtlasIntel) têm viés pouco robusto — é 1 ponto, não uma média.

## Odds (probabilidade de vitória)

Não há mercado de apostas brasileiro (o RCP usa Polymarket). Estimativa estatística própria:

    P(Lula vencer) = Φ(margem_2º_turno / s),  com s = 6 pontos

- Φ = função de distribuição acumulada da normal padrão.
- margem_2º_turno = % Lula − % Flávio no 2º turno (positivo = Lula na frente).
- s = 6 representa a incerteza a meses da eleição (out/2026). Parâmetro ajustável: s menor deixa odds mais extremas; s maior aproxima de 50%.

Odds por instituto só existe quando o instituto publicou 2º turno; senão fica em branco ("—"), como o "Latest Polls" do RCP.

## Convenção de cores

- Vermelho (#c01f2e) = Lula na frente.
- Azul (#1f3fd0) = Flávio na frente.
- Coluna "2º turno": mostra o líder e a margem (ex.: "Lula +4" vermelho; "Flávio +2" azul).
- Coluna "Odds Lula": vermelho se >= 50%, azul se < 50%.

## Margem de erro

Mostrada ao lado do nome do instituto, em cinza, no formato "±2,0" (pontos percentuais). Vem da mesma fonte. É quase constante por instituto (AtlasIntel ±1,0; Vetor/Arrow ±1,0; maioria ±2,0 a ±2,2; Meio/Ideia ±2,5; Alfa ±2,6). No painel usa-se um valor representativo por instituto (objeto JS `MOE`); algumas rodadas variam por décimos (ex.: Gerp ±2,19 a ±2,24).

## Coluna Br/N/Ind (brancos, nulos e indecisos)

A fonte (agregador Wikipédia) NÃO separa brancos/nulos de indecisos — vêm num único número "brancos, nulos e indecisos/não sabe". A coluna usa esse valor reportado, não é estimativa, exceto a indecisão da Atlas em março (interpolada a partir dos outros meses dela, que ficam entre 1,9% e 5,3%). Para um split puro de brancos/nulos seria preciso o crosstab de cada pesquisa, que os institutos raramente publicam.

## Notas de dados

- AtlasIntel maio: 1º turno do Flávio (34*) é reconstruído. O número foi vetado pelo TSE (liminar de Kassio Nunes Marques, 8/6/2026). Reconstruído a partir do 2º turno divulgado (Lula 48,9 x Flávio 41,8) e da diferença histórica ~8 pts entre 1º e 2º turno da Atlas.
- AtlasIntel: rodou jan, fev, mar, abr, mai. Não publicou em junho.
- Janeiro: campo fragmentado (Tarcísio e Haddad ainda candidatos); só Atlas e Apex mediam Flávio de forma comparável.
- Em meses com várias rodadas do mesmo instituto, usar a mais recente do mês.
- REGISTRADAS E AINDA SEM NÚMERO PUBLICADO (situação em 02/08/2026, 16h). O radar do TSE mostra rodadas estaduais com divulgação marcada para 02/08 que a imprensa ainda não publicou: Veritá no AMAPÁ (AP-04661/2026, campo 28/07 a 01/08, N=1030) e no AMAZONAS (AM-00886/2026, mesmo campo, N=1220), do mesmo lote cujas rodadas de PR e PA já entraram, e Perfil no ESPÍRITO SANTO (ES-05181/2026, campo 29 a 31/07, N=600, que é um terço da amostra da rodada de 13-16 jul que está no painel). Conferidos nesta ordem e sem resultado: Gazeta do Povo (a lista para na Datafolha de PE, divulgada em 31/07), Poder360 e CNN Eleições (a matéria de pesquisa mais recente do dia é a Vox de SP, que já está no painel). Não inserir por dedução; a próxima rodada horária deve procurar de novo. RECONFERIDO ÀS 20h do mesmo dia, tudo igual: a página de pesquisas do próprio Veritá (https://eleicoes26.institutoverita.com.br/) lista MARANHÃO e PARANÁ como as duas publicações de 02/08, e as rodadas mais recentes de AMAZONAS e AMAPÁ que aparecem lá continuam sendo as de 01 a 05 de julho; a lista da Gazeta ainda para na Datafolha de PE e a tag de pesquisa eleitoral do Poder360 ainda para em 1º/08. Atalho para as próximas rodadas: o Veritá publica o lote inteiro nessa página por estado, então dá para conferir AM, AP e PA de uma vez só ali, sem abrir jornal. RECONFERIDO ÀS 22h, ainda igual.
- ATALHO BARATO PARA CONFERIR O VERITÁ (achado em 02/08/2026, 22h). A home `https://eleicoes26.institutoverita.com.br/` é um app JS, então `curl` na página devolve só a palavra "Veritá" e não serve. O conteúdo vem do Supabase e dá para ler direto, em um comando, sem navegador e sem baixar PDF:

  ```bash
  KEY=$(curl -sL https://eleicoes26.institutoverita.com.br/assets/index-ZXY8sPJe.js | grep -o 'eyJhbGciOiJIUzI1NiI[A-Za-z0-9._-]*' | head -1)
  curl -s "https://lgjdbpskgjfbmlffbntx.supabase.co/rest/v1/pesquisas?select=titulo,descricao,pdf_url,created_at&order=created_at.desc&limit=10" -H "apikey: $KEY" -H "Authorization: Bearer $KEY"
  ```

  A resposta traz título, período de campo na descrição, URL do PDF e o `created_at` da publicação, que é o carimbo real de quando o número passou a existir. O nome do arquivo do bundle (`index-ZXY8sPJe.js`) muda a cada deploy do site deles; se der 404, pegue o novo com `curl -sL https://eleicoes26.institutoverita.com.br/ | grep -o 'src="/assets/[^"]*"'`. A chave é a anon pública que o próprio site expõe no JS.
- O PDF do MARANHÃO do Veritá (25 a 29/07, `1785685809495_Relatorio_Maranhao_Julho_2026.pdf`) NÃO tem seção presidencial, apesar do título do post dizer "Presidente, Governador e Senador". Conferido pergunta a pergunta: o relatório começa na PERGUNTA 04 (governador espontânea) e termina na 13 (rejeição a senador); as três primeiras são só perfil demográfico. Por isso o `PRES26.MA` continua com o Real Time Big Data de 6-7 jul, que é mais antigo mas é o dado que existe. Não reabrir esse PDF procurando Lula x Flávio.
- O `radar_tse.py` guarda o ZIP baixado por DIA, e o ZIP do TSE também é regerado uma vez por dia (o cabeçalho do radar diz "ZIP gerado em"). Numa tarefa de hora em hora isso significa que apagar o cache no meio do dia normalmente NÃO traz registro novo: dá o mesmo arquivo. Vale apagar uma vez por dia, na primeira rodada depois da virada, não a cada hora.
- QUEM É O `#NULO#` DE SERGIPE, E ONDE ELE PUBLICA (19/08/2026). No CSV do TSE o campo
  `NM_EMPRESA_FANTASIA` volta `#NULO#` em vários registros, e o radar mostra só o
  contratante. Em Sergipe, `#NULO#` + contratante **MARTINS, PRODUÇÕES E PUBLICIDADE
  LTDA** + N=1070 + margem 3,0 é o **INOR** (Instituto de Pesquisa do Nordeste). A
  conferência: a SE-00281/2026 (campo 27 a 29/07, N=1070, mesmo contratante) saiu
  assinada pelo INOR no NE Notícias em 05 e 06/08. Ou seja, a **SE-04930/2026** (campo
  13 a 16/08, divulgação 18/08), que está na fila, é rodada do INOR e o lugar de
  procurar o número é `nenoticias.com.br` e a Nova Brasil FM, não o site de instituto.
- LACUNAS ESTADUAIS CONFERIDAS EM 19/08/2026 E NÃO INSERIDAS. Ao investigar a fila
  apareceram rodadas estaduais publicadas que o painel não tem. Ficam anotadas para
  serem inseridas com fonte primária, porque a fonte onde as encontrei foi a Wikipédia,
  que é último recurso pela regra do `AGENTS.md`:
  - SERGIPE, julho: o `DGM.SE.jul` traz o INOR de 6 a 8/07 (Mitidieri 32,90, Valmir
    38,69, Ricardo Marques 8,97), mas existe rodada MAIS RECENTE do mesmo instituto no
    mesmo mês, a de 27 a 29/07 (Mitidieri 37,94, Valmir 46,07, Ricardo Marques 7,01,
    SE-00281/2026, N=1070), e essa tem fonte primária boa (NE Notícias, com dados
    técnicos completos). Pela regra de uma rodada por instituto por mês, valendo a mais
    recente, a entrada de julho deveria ser essa. Faltam também W1 de 14 a 18/07 e CTAS
    de 21 a 24/07.
  - GOIÁS, julho: faltam Directa de 28 a 31/07 (N=2000, Daniel Vilela 45,8, Marconi
    24,5, Wilder 13,1) e Veritá de 12 a 16/07.
  - PARAÍBA, julho: falta Índice de 10 a 12/07 (N=2000, Cícero Lucena 33,4, Lucas
    Ribeiro 28,3, Efraim Filho 16,5).
  AGOSTO, por outro lado, está em dia nos três estados: GO tem Paraná Pesquisas e Goiás
  Pesquisas/Mais Goiás, SE tem Real Time Big Data, Instituto França e ECM, e a Paraíba
  não teve nenhuma rodada publicada no mês até 19/08.
- API DE POSTS DOS PORTAIS SERGIPANOS: O CAMINHO BARATO (19/08/2026, rodada das 13h30).
  Procurar número estadual abrindo jornal no navegador é caro e falha quando a busca do
  site é renderizada em JS (o `?s=pesquisa` do NE Notícias devolve página vazia). O que
  funciona, em um comando e sem navegador, é a API REST do WordPress:

  ```bash
  curl -s "https://www.nenoticias.com.br/wp-json/wp/v2/posts?search=INOR&per_page=10&orderby=date&order=desc"
  ```

  Devolve título, data, link e o CONTEÚDO INTEIRO da matéria em JSON, com as tabelas de
  percentual. Conferido funcionando em `nenoticias.com.br`, `faxaju.com.br`,
  `roacontece.com.br` e `infonet.com.br`. NÃO tem API: `a8se.com` (portal da TV Atalaia),
  `jornaldacidade.net`, `horanews.com.br`, `cinform.com.br`, `f5news.com.br`. Trocar
  `search=` pelo nome do instituto é mais eficaz do que procurar por "pesquisa", porque
  pega a matéria mesmo quando o título não traz a palavra.

- JULHO DE SERGIPE FECHADO COM FONTE PRIMÁRIA (19/08/2026, rodada das 13h30). A lacuna
  anotada de manhã foi resolvida. O `DGM.SE.jul` trazia o INOR da rodada de 06 a 08/07
  (SE-05317/2026: Valmir 38,69, Mitidieri 32,90, Ricardo Marques 8,97). Pela regra de uma
  rodada por instituto por mês, valendo a MAIS RECENTE, o certo é a de 27 a 29/07
  (**SE-00281/2026**, N=1070, contratante Martins Produções, divulgada pela Nova Brasil e
  publicada pelo NE Notícias em 05 e 06/08). Números inseridos, da estimulada:
  **Valmir 46,07, Mitidieri 37,94, Ricardo Marques 7,01, Emanuel Cacho 0,28,
  Helton Monteiro 0,19**. Fonte primária:
  `https://www.nenoticias.com.br/inor-valmir-mitidieri-pesquisa-governo-sergipe/`.
  O `DSM.SE.jul` NÃO mudou: o registro no TSE cobre Governador e Senador, mas a matéria
  publicou só governador e rejeição, então o Senado de julho segue com a rodada de 06 a
  08/07. Não é descuido; é o que existe publicado.

- 'IFP' ERA O INSTITUTO FRANÇA (19/08/2026). O `DGM.SE.jul` e o `DSM.SE.jul` traziam um
  instituto chamado `IFP`, que não aparecia em nenhum outro mês. É o **Instituto França**:
  os números (Mitidieri 40,67, Valmir 29,22, Ricardo Marques 4,89) batem exatamente com a
  rodada de 30/06 a 02/07, N=1116, publicada pelo NE Notícias em 09/07. Renomeado para
  'Instituto França' nos dois objetos, que é como março e agosto já escrevem. O gráfico do
  estado não usa nome de instituto (o `stateChart` faz média por CANDIDATO), então a
  troca é de rótulo, mas evita que uma rodada futura ache que falta o Instituto França em
  julho e insira uma segunda linha do mesmo instituto no mesmo mês.

- SENADO DO ECM EM AGOSTO: LACUNA QUE NÃO DÁ PARA FECHAR AINDA (19/08/2026). O
  `DGM.SE.ago` tem a rodada do ECM (SE-02682/2026, campo 09 a 12/08, N=1500), mas o
  `DSM.SE.ago` NÃO tem, e o ECM mediu Senado. O número existe publicado, só que apenas em
  release de campanha: roacontece e faxaju, em 18/08, com texto idêntico assinado
  "assessoria", dão SÓ o André Moura (15,07% no primeiro voto, a 2,86 pontos do primeiro
  colocado, 24,07% somando primeiro e segundo voto, 9% na segunda opção). Não dizem quem
  lidera nem com quanto. Pela regra de não inventar número, NÃO foi inserido: daria para
  deduzir que o líder tem ~17,93%, mas não quem é. O que fecha isso é a tabela completa,
  provavelmente no Cinform (que publicou o recorte de deputado estadual da mesma rodada) ou
  na íntegra registrada no TSE.

- REGISTRO QUE MUDA DEPOIS DE ENTRAR NA FILA (19/08/2026). A PB-07815/2026 (Índice
  Inteligência, N=2000) entrou na fila em 18/08 com campo de 13 a 15/08. No ZIP do dia
  19/08 o mesmo registro aparece com campo de **18 a 20/08** e divulgação em 18/08, que
  é incoerente por si só e indica retificação do registro. Enquanto o campo não fecha
  não existe número para procurar. Antes de dar um item por "não publicado", reler a
  linha no radar do dia: ela pode ter mudado desde que entrou na fila.

- ITEM RESOLVIDO COMO "NAO PUBLICADO" PODE PUBLICAR DEPOIS, E A FILA NAO O REABRE
  (20/08/2026). Os tres itens de 18/08 foram fechados sem insercao em 19/08 e reconferidos
  na madrugada de 20/08, com o mesmo resultado: nenhum numero publicado. Fica o alerta de
  cadencia, porque "nao publicou ate a data de divulgacao" nao quer dizer "nunca vai
  publicar":
  - **SE-04930/2026 (INOR, campo 13 a 16/08)**: o INOR publica com cerca de UMA SEMANA de
    atraso sobre o fim de campo. A rodada anterior do mesmo instituto e do mesmo
    contratante (SE-00281/2026, campo 27 a 29/07) so saiu no NE Noticias em 05 e 06/08.
    Pela mesma regua, esta deve aparecer entre 22 e 24/08, quando a fila ja nao vai
    lembrar dela. Vale procurar `search=INOR` no `nenoticias.com.br` nas rodadas desses
    dias e, se sair, entra no `DGM.SE.ago` e no `DSM.SE.ago` como rodada mais recente do
    instituto no mes.
  - **SE-08978/2026 (Verita, contratante TV Atalaia)**: em 20/08, tres dias depois do fim
    de campo, nada no portal do proprio contratante (`a8se.com`, que nao tem API REST e
    precisa de navegador), nada nas APIs do `nenoticias`, `faxaju` e `roacontece`, e o
    backend do instituto continua fora do ar. Com o TRE-SE tendo proibido a divulgacao do
    Verita para governo e Senado em 12/08, o desfecho provavel e que este numero nunca
    apareca. Nao insistir a cada rodada.

## Rodada de 21/08/2026 (segunda passagem): Rio Grande do Sul de agosto

- **O RS DE AGOSTO ENTROU COM A PARANA PESQUISAS DE 18 A 20/08** (RS-03898/2026, N=1504, 67
  municipios, margem 2,6, paga pelo PL por R$ 135.200). Governador: Zucco 34,4, Brizola 31,4,
  Gabriel Souza 11,3, Maranata 4,1, com Cesar Pontes 2,3, Rejane de Oliveira 1,3 e Priscila
  Voigt 1,1 no `DG`. Senado: d'Avila 33,6, van Hattem 26,9, Rigotto 24,3, Pimenta 22,5 e
  Sanderson 16,0. Entrou nos quatro objetos (`DGM`, `DSM`, `DG`, `DS`) e as duas chaves de
  contratante foram marcadas no `CONTR` como partido.
- **UM ITEM PODE NASCER PUBLICADO ENTRE DUAS RODADAS LOCAIS.** A RS-03898 foi anunciada como
  NOVA pela rodada do Actions de 01h49 e a materia do Poder360 so saiu as 7h00, ou seja, depois
  que a rodada local anterior ja estava rodando. Quem pegar a fila logo apos o Actions vai
  achar item sem numero que ganha numero uma hora depois. Nao dar por "nao publicado" item cuja
  divulgacao e do proprio dia: o certo e deixar na fila e olhar de novo na rodada seguinte.
- **A PARANA PESQUISAS PUBLICA O SENADO NA SOMA DA 1a COM A 2a OPCAO**, igual a DataTrends da
  Bahia, e a propria arte diz isso na observacao 2. Por isso a coluna do `DSM.RS.ago` passa de
  100 e o aviso ficou no `t2` do `DS.RS`. O `DSM.RS.jul` da mesma empresa ja seguia essa regua,
  entao a serie e comparavel dentro do instituto.
- **SEM 2o TURNO NO RS.** A rodada nao publicou simulacao de 2o turno para o governo, so 1o
  turno e rejeicao, entao o `t2` do `DG.RS` ficou vazio e o placar "Brizola 35 x Zucco 31" da
  Genial/Quaest de 24 a 28/07 saiu do mapa por ser rodada mais velha. Nao e perda de dado: o
  numero da Quaest continua no `DGM.RS.jul`.
- **PUSH DA RODADA LOCAL EM CIMA DA RODADA DO ACTIONS DERRUBA O WORKFLOW.** Em 21/08/2026 o
  `rotina.yml` comecou as 10h40m20s UTC e o push desta rodada entrou as 10h40m23s. O workflow
  commitou, tentou `pull --rebase`, bateu CONFLITO no `electoralpolls.html` (os dois lados
  mexem na linha do carimbo) e morreu com exit 1: nao publicou, nao gravou mercado nenhum e
  perdeu o `PENDENCIAS.md` que tinha acabado de gerar. O horario do cron do GitHub anda,
  entao nao da para "evitar a janela". A regra pratica e outra: DEPOIS de dar push numa rodada
  local, rodar `gh run list --workflow=rotina.yml --limit 2`; se a rodada mecanica estiver
  vermelha por conflito, refazer a mao com `python3 rotina_6h.py`, publicar e commitar. Foi o
  que se fez aqui, e o painel ficou com carimbo de 07h41 e os mercados do dia.
- **NEXUS NO TOCANTINS CONTINUA SEM NUMERO.** TO-09573/2026 e o gemeo BR-01901/2026 tinham
  divulgacao em 19/08 e ate a manha de 21/08 nao ha materia, nem no Poder360, nem em busca por
  protocolo, nem nos portais do estado. Contratante e a federacao das radios comunitarias do
  Tocantins, entao a divulgacao, se vier, sai em radio local. Fica na fila.

## Rodada de 21/08/2026 (7h30): CE, BA e MA de agosto

- **INSTITUTO QUE SOLTA A MESMA RODADA EM PARCELAS, UM CARGO POR DIA.** A DataTrends
  registrou BA-03367/2026 e o gemeo BR-07947/2026 numa unica pesquisa de campo (15 a 17/08,
  N=1200) e publicou GOVERNADOR em 19 e 20/08, SENADO so em 21/08 e a parte PRESIDENCIAL ainda
  nao publicou. A rodada de 20/08 fechou o governador e nao tinha como ver o resto. Licao para
  quem for dar um item por "nao publicado": conferir a data de cada CARGO, nao a da pesquisa.
  Enquanto um cargo do mesmo registro ainda esta saindo, o registro nao esta morto. Por isso a
  BR-07947/2026 ficou DELIBERADAMENTE na fila nesta rodada, e nao foi resolvida.
  O Senado da BA entrou agora no `DSM.BA.ago` e no `DS.BA`, com fonte primaria no Blog do
  Waldiney Passos (21/08).
- **SENADO DA BAHIA MISTURA DUAS REGUAS, E ISSO NAO E ERRO DE DIGITACAO.** O `DSM.BA.ago` tem
  Real Time Big Data com Rui Costa em 25 e DataTrends com Rui Costa em 51. O RTBD publica o
  PRIMEIRO voto (a soma da coluna fecha em 100); Parana Pesquisas e DataTrends publicam a SOMA
  do primeiro com o segundo voto, e a coluna passa de 100 porque cada eleitor escolhe dois
  nomes. Nao "corrigir" o 51 para 25: o numero esta certo e a fonte diz isso com todas as
  letras. O `DS.BA` traz o aviso no campo `t2`.
- **O RELEASE DO IPSOS-IPEC E MELHOR QUE A MATERIA, E DA OS DOIS REGISTROS DE UMA VEZ.** A
  CE-00195/2026 (estadual) e a BR-06231/2026 (presidencial no CE) sao a MESMA coleta, e o
  release do Ipsos traz governador, Senado e presidente no mesmo texto, com a ficha tecnica no
  fim. O Poder360 hospeda o PDF em `static.poder360.com.br`, e `pdftotext -layout` le tudo sem
  precisar renderizar imagem. Caminho para achar: buscar no Google pelo protocolo, que os
  portais regionais sempre citam.
  ARMADILHA DE DATA, ja conhecida e confirmada aqui: o registro no TSE diz campo de 13 a 19/08,
  o release do proprio instituto diz 14 a 17/08. Vale a regra do `AGENTS.md`, que manda usar o
  REGISTRO, mas a diferenca importa na hora de decidir qual rodada e a mais recente do estado.
- **PRES26.CE NAO MUDOU, E FOI DECISAO, NAO ESQUECIMENTO.** O Ipsos-Ipec publicou presidencial
  no Ceara (Lula 57, Flavio 24; 2o turno Lula 61 x Flavio 29), mas o `PRES26.CE` ja tinha o Real
  Time Big Data de 15 a 19/08, cujo campo e mais recente pelos dois criterios (registro e
  release). Ficou o RTBD. O mesmo raciocinio vale para o `DG.CE` e o `DS.CE`.
- **VERITA NA BAHIA E NO TOCANTINS: NAO INSISTIR.** BA-02806/2026 e TO-07896/2026 tinham
  divulgacao em 20/08 e nada apareceu. O instituto acumula suspensoes em 13 estados e no DF, e
  no proprio Tocantins ja houve decisao apontando "vicio substancial" na fonte da amostra.
  Cuidado com um falso positivo que aparece na busca: ha post do Instituto Verita de 30/07 com
  a Bahia em ACM Neto 39 x Jeronimo 38, que e rodada ANTERIOR e nao tem registro de campo em
  agosto no ZIP do TSE (os registros baianos do Verita sao mar, abr, mai e ago).
- **REGISTRO QUE TROCA DE PROTOCOLO, NAO SO DE DATA.** A RN-06093/2026 (Data Capital, N=2100,
  campo 15 a 18/08, divulgacao 20/08) simplesmente NAO EXISTE MAIS no ZIP do dia 20/08. No lugar
  dela ha a RN-02513/2026, do mesmo instituto, mesmo campo, mesmo N, com divulgacao empurrada
  para 25/08. E o irmao do caso PB-07815 de 19/08: la o registro mudou de data, aqui mudou de
  numero. Antes de sair procurando numero de um item da fila, conferir se o protocolo ainda
  esta no ZIP; se nao estiver, foi retificado e nao ha o que procurar.
- **AGREGADOR DO PODER360 NAO SERVE COMO FONTE.** Em 20/08 o Poder360 abriu o acesso ao
  agregador dele (`drive.poder360.com.br/agregador-de-pesquisas`), com mais de 620 levantamentos
  de 2026. Foi testado: o dado nao vem por API publica nem esta no bundle JS, e o recorte
  estadual cai em paywall ("assine / entrar"). Nao vale gastar rodada tentando raspar de la.
- **DATAFOLHA NACIONAL COM PABLO MARCAL SAI EM 21/08.** A Gazeta do Povo anunciou em 20/08 que
  o Datafolha publicaria na sexta a primeira nacional depois do registro das candidaturas, com
  DOIS cenarios, um com e outro sem Pablo Marcal (que voltou ao PRTB por liminar e esta
  inelegivel ate 2032, com o TSE tendo ate 14/09 para decidir). Quando entrar no `DI`, escolher
  UM cenario e dizer qual na nota do mes: empilhar os dois viraria duas linhas do mesmo
  instituto no mesmo mes, que e exatamente o que a regra de uma rodada por instituto proibe.

## Nomes de urna e cenarios que nao entram (rodada de 20/08/2026)

- **RN: "Cadu de Lula" E "Cadu Xavier"**, a mesma pessoa. O candidato do PT ao governo do RN
  foi lancado como Cadu Xavier e registrou na Justica Eleitoral o nome de urna Cadu de Lula, e
  a imprensa potiguar passou a usar as duas formas trocando de uma materia para outra. O painel
  ja tinha SEIS rodadas de agosto escritas como `Cadu Xavier`, entao a rodada Perfil/Blog do BG
  entrou tambem como `Cadu Xavier`. Se algum dia entrar como `Cadu de Lula`, o `stateBanner`
  vai anunciar dois terceiros colocados numa corrida de um so.

- **CE: `Vera Lucia` no Ceara nao e a `Vera Lucia` de Sao Paulo.** No Ceara e a candidata do
  Novo ao governo, e em Sao Paulo e a do PSTU. Como o `stateBanner` agrega por UF e mes, nao ha
  colisao, mas nao vale "consertar" o nome achando que e a mesma pessoa. Duas fontes
  independentes (Gazeta do Povo e GCMais) escrevem assim a rodada do Real Time Big Data de
  15 a 19/08.

- **PI: o cenario de Senado do Instituto Amostragem NAO ENTRA.** Sao tres motivos somados, e
  o terceiro sozinho ja bastaria. Primeiro, os percentuais saem em VOTOS VALIDOS, e o `DSM`
  guarda amostra total. Segundo, os candidatos sao apresentados ACOMPANHADOS DO APOIO POLITICO
  ("Marcelo Castro, com o apoio do presidente Lula"), o que nao e a mesma pergunta que os
  outros institutos fazem. Terceiro, em 18/08/2026 a desembargadora Lucicleide Pereira Belo
  suspendeu liminarmente a divulgacao da rodada anterior do mesmo instituto para senador
  (PI-00748/2026). Da rodada PI-02188/2026 (campo 8 a 12/08) entrou SO o governador, e so os
  dois numeros publicados em amostra total: Rafael Fonteles 58,84 e Joel Rodrigues 15,3.

## Como atualizar

1. Coletar as novas rodadas (Wikipédia/Gazeta/institutos).
2. Acrescentar ao objeto `D` no JS do HTML (uma linha por instituto: nome, Lula, Flávio, Caiado, Zema, Renan, 2º turno, Odds, flagAtlas).
3. Recalcular o consenso do mês, os house effects e as odds (Φ(margem/6)).
4. Atualizar as caixas "Odds mês" (agregado do mês).

Snapshot atual: até 29/06/2026. Agregado de junho (simples): Lula 40,1 x Flávio 32,0. Ajustado: Lula 40,4 x Flávio 32,7. Odds mês Lula 67%.

# Agregador de pesquisas · Eleições 2026

Fonte de verdade do painel publicado em https://rafaelcortopassi.pythonanywhere.com/electoralpolls/

**ARQUIVO DO PAINEL: `electoralpolls.html`.** Sempre este, nunca crie outro nome.

Leia `METODOLOGIA_AGREGADOR_PESQUISAS_2026.md`, o bloco "ATENÇÃO — estado atual do painel
(NÃO REVERTER)" no topo, antes de mexer em qualquer coisa. Ele registra decisões datadas que
já foram revertidas por engano mais de uma vez.

O PAINEL É DINÂMICO. Gráfico, aba House effect, banner, mapa, ordem das colunas e o texto acima
do mapa derivam sozinhos dos objetos de dados. Sua tarefa é ACRESCENTAR dados e atualizar poucos
campos. NÃO reescreva `chartSVG`, não recalcule pontos do gráfico à mão, não escreva lista de
meses nem lista de estados à mão no código (já congelou duas vezes).

## Quem faz o quê: Actions de 6 em 6 horas, Claude local de 6 em 6 horas

Desde 02/08/2026 a rotina é DIVIDIDA, e deixou de ser de hora em hora. A pergunta a fazer antes
de trabalhar é: isto é mecânico ou exige julgamento?

**MECÂNICO, e já está feito quando você acorda.** O workflow `.github/workflows/rotina.yml` roda
`rotina_6h.py` às 01h05, 07h05, 13h05 e 19h05 de Brasília, com o Mac desligado, e cuida de:
cotações do Polymarket e do Kalshi, carimbo de "Última atualização", detecção do que é NOVO no
TSE e no Veritá, validação do JS, commit e publicação no PythonAnywhere. Ou seja, o Passo 6
(mercados) e o Passo 7 (carimbo) NÃO são mais seus, salvo se o workflow tiver falhado.

**JULGAMENTO, e é só isto que sobra para você.** Abrir a íntegra em PDF, ler número que só
existe em gráfico, confirmar se a rodada é nacional ou estadual, escolher o mês, casar nome de
candidato e inserir nos objetos de dados. Nada disso o Actions faz, e é de propósito: exigiria
um modelo lendo PDF no CI, com `ANTHROPIC_API_KEY` no repositório, que não existe e não deve ser
criada sem o Rafael pedir.

**COMECE PELO `PENDENCIAS.md`.** Ele é gerado a cada rodada do Actions e diz, na primeira seção,
o que está NA FILA esperando olho humano. Se a fila estiver vazia, sua rodada acaba em duas
linhas: NÃO refaça o radar, NÃO rode mercados, NÃO mexa no carimbo, NÃO dê commit vazio.
O arquivo é reescrito inteiro toda vez, então não o edite à mão. O estado mora em
`estado_rotina.json`, que também é do script, não seu.

**CONFIRA A FILA NO `estado_rotina.json` ANTES DE INVESTIGAR (20/08/2026).** O `PENDENCIAS.md`
só é reescrito pelo Actions, de 6 em 6 horas, e o `--resolver` NÃO o reescreve: mexe apenas na
chave `pendentes` do `estado_rotina.json`. Então, quando uma rodada local resolve itens DEPOIS
da última rodada do Actions, o `PENDENCIAS.md` continua anunciando fila cheia até o próximo
carimbo mecânico, e a rodada seguinte reabre trabalho já feito. Foi o que aconteceu na madrugada
de 20/08: os três itens de 18/08 (PB-07815, SE-08978 e SE-04930) já tinham sido resolvidos às
20h11 de 19/08, mas o `PENDENCIAS.md` de 19h35 ainda os listava, e eles foram reapurados do zero.

O teste é de uma linha, e vale mais do que o texto do relatório:

```bash
python3 -c "import json;print(json.load(open('estado_rotina.json'))['pendentes'])"
```

Lista vazia quer dizer fila vazia, mesmo que o `PENDENCIAS.md` diga o contrário: sua rodada acaba
ali. Se as duas discordarem, quem manda é o `estado_rotina.json`, e o motivo da divergência
costuma estar na mensagem do último commit local.

**A FILA NÃO SE ESVAZIA SOZINHA, e isso é de propósito (10/08/2026).** Até esta data a primeira
seção era o diff de UMA rodada, e o protocolo era marcado como visto na mesma hora em que era
anunciado. Como o ZIP do TSE é regerado uma vez por dia, de madrugada, toda novidade caía na
primeira rodada do dia (~02h40) e era apagada pela seguinte (~08h17), enquanto a rodada local lê
07h30/13h30/19h30. Em 10/08 as três nacionais do dia (Nexus/BTG, Palver e GERP) foram
sinalizadas às 02h40 e o arquivo já dizia "nada novo" às 08h17: o painel passou de 07/08 a 10/08
sem dado novo sem que ninguém tivesse decidido isso.

Agora cada item fica na fila, rodada após rodada, marcado `[NOVO]` ou `[aguardando desde DATA]`,
até você fechá-lo:

```bash
python3 rotina_6h.py --resolver BR084282026            # um ou vários, separados por vírgula
python3 rotina_6h.py --resolver tudo                   # limpa a fila inteira
```

**Resolver quer dizer as duas coisas:** inserido no painel, OU verificado que o instituto
registrou e não publicou número. Marque também o que você descartou, senão volta amanhã e a fila
vira ruído. Item não resolvido sai sozinho depois de 21 dias, e a saída é anunciada no próprio
`PENDENCIAS.md`, nunca silenciosa. `--resolver` só mexe na fila: não carimba, não lê mercado e
não toca no painel, então pode ser usado à vontade sem gerar rodada mecânica.

Se o `PENDENCIAS.md` estiver velho (data de mais de 7 horas atrás), o Actions falhou: confira com
`gh run list --workflow=rotina.yml --limit 3` e, aí sim, rode `python3 rotina_6h.py` à mão.

A tarefa agendada local roda 25 minutos depois do Actions, também de 6 em 6 horas, no clone em
`~/agregador-pesquisas-2026`. Não tente movê-la para uma rotina de nuvem do claude.ai.

Foi tentado em 02/08/2026 e MEDIDO, com o relatório em `DIAGNOSTICO_NUVEM.md`. O sandbox da
nuvem tem um proxy de saída obrigatório em `127.0.0.1` que responde **403 Forbidden ao CONNECT**
para todo domínio externo. Falharam, todos pelo mesmo motivo: os ZIPs do TSE, Poder360,
static.poder360, Gazeta do Povo, Polymarket, Kalshi e a API do PythonAnywhere. Não é DNS, não é
o `mercados.py`, e não adianta trocar de caminho de rede: os quatro caminhos dele (direto, DoH
Google, DoH Cloudflare, nslookup) morreram no mesmo 403, e o `nslookup` nem existe lá. O que
funciona na nuvem é git (por outro proxy local) e o relógio, que está certo.

Ou seja, um agente de nuvem consegue editar arquivo e dar push, mas não consegue APURAR nada.
Como esta tarefa é 90 por cento apuração, ela não tem como rodar lá. Se algum dia o proxy passar
a liberar esses domínios, o teste é rodar de novo o que está em `DIAGNOSTICO_NUVEM.md`.

## Escopo desde 26/09/2026: só Presidente

A pedido do Rafael, o agregador PAROU de acompanhar Governador e Senador. `rotina_6h.py` já
filtra o radar do TSE para só trazer registros de Presidente; `DG`/`DS`/`DGM`/`DSM` (os objetos
de Governador/Senador) ficam CONGELADOS com o que já tinha — não apague, não mexa, só não
acrescente rodada nova. Se aparecer pesquisa de Governador ou Senador em qualquer fonte
(Veritá, Gazeta, Wikipédia), ignore: fora de escopo agora, não é esquecimento seu.

Restam duas frentes. Investigue as duas.

1. **Presidencial nacional** → objeto `DI` (uma rodada por instituto por mês, a mais recente)
   + `T2R` (par de 2º turno) + `IM` (metadados do instituto).
2. **Presidencial por estado** → `PRES26` (aba Mapa). Hoje tem 26 dos 27 estados (falta RR).

## Ferramentas do repositório

```bash
python3 rotina_6h.py              # a rodada mecânica inteira (é o que o Actions executa)
python3 rotina_6h.py --dry-run    # mostra o que faria, sem gravar
python3 radar_tse.py              # o que o TSE registrou nos últimos 7 dias
python3 radar_tse.py 2026-07-28   # a partir de uma data
python3 mercados.py               # cotações do Polymarket e do Kalshi
python3 mercados.py --debug       # mostra qual caminho de rede funcionou
```

`rotina_6h.py` é do Actions. Só rode à mão quando o workflow tiver falhado, porque ele carimba e
mexe nos mercados, e rodar por cima de uma rodada boa só gera commit à toa.

`radar_tse.py` já baixa os ZIPs, faz o desempate nacional x estadual pelo gêmeo e cruza o
contratante. `mercados.py` já tenta HTTPS direto, depois DNS-over-HTTPS, depois o
`nslookup 8.8.8.8` antigo; se todos falharem sai com código 2 e você NÃO inventa número.

## Passo 1 — Leia o `PENDENCIAS.md` (é ele que decide se você tem trabalho)

O Actions já rodou o radar por você. Abra o `PENDENCIAS.md` e leia a seção "Precisa de olho
humano nesta rodada". **Na maioria das rodadas não haverá pesquisa nova, e isso é o esperado,
não é falha.** Nesse caso responda em duas linhas e PARE: sem carimbo, sem mercados, sem commit.
NÃO refaça a varredura pesada (baixar íntegra em PDF, renderizar página, abrir jornal) quando o
relatório não apontou nada novo: ele é o filtro barato que decide se vale abrir o resto.

Se apontou novidade, o resto do arquivo dá o contexto: as últimas publicações do Veritá e a
tabela de tudo que o TSE registrou com divulgação vencida nos últimos 10 dias. Só aí vale rodar
`radar_tse.py` para ver a linha inteira.

Cuidado com a distinção que já enganou agente antes: estar na tabela significa que a DATA DE
DIVULGAÇÃO venceu, não que o número exista publicado. Instituto que registra e não publica é
caso conhecido, e aí não se insere nada.

Colunas úteis do CSV: `NR_PROTOCOLO_REGISTRO`, `NM_EMPRESA_FANTASIA`, `NR_CNPJ_EMPRESA`,
`DS_CARGO`, `DT_INICIO_PESQUISA`, `DT_FIM_PESQUISA`, `DT_DIVULGACAO`, `QT_ENTREVISTADO`,
`VR_PESQUISA`.

Falsos positivos de "nacional" já pegos: Futura/Apex BR-08054/2026 (é de MINAS GERAIS, 291
municípios mineiros), Veritá de julho (6 registros, todos estaduais) e Factum BR-08523/2026
(é MUNICIPAL: o campo `DS_DADO_MUNICIPIO` do registro diz "os bairros e distritos do município
de CABO FRIO/RJ", com 700 entrevistas e R$ 20 mil).

**O DESEMPATE ESTÁ NO `DS_DADO_MUNICIPIO` (04/09/2026).** Antes de abrir jornal atrás de um
`NACIONAL?`, leia esse campo do próprio registro: ele diz em uma linha se a abrangência é
nacional, de um estado ou de um município, e resolve a maioria dos casos sem sair do CSV. Foi
assim que a Factum caiu, e é assim que se acha o estado do gêmeo quando o `NM_EMPRESA_FANTASIA`
vem `#NULO#` (BR-05635/2026 diz "o estado de Ceará" e a `NM_EMPRESA` revela o Datafolha).

## Passo 2 — O gêmeo estadual É a fonte do PRES26

Durante meses o cruzamento do gêmeo foi usado só como FILTRO de exclusão, e o material era
jogado fora. Está errado: pesquisa presidencial com amostra de um estado é exatamente o insumo
do mapa presidencial por estado. Há ~490 delas registradas em 2026, cobrindo 26 UFs.

## Passo 3 — Onde achar os NÚMEROS (registro não é divulgação)

O TSE dá existência, instituto, datas, N, custo e contratante, mas NÃO os percentuais.
Ordem de prioridade:

1. **Íntegra da pesquisa em PDF**, a melhor fonte. O Poder360 publica junto das matérias, em
   `static.poder360.com.br`. `pdftotext -layout` resolve muitos; quando o número está em
   gráfico, renderize a página com PyMuPDF (`fitz`, matrix 3x) e LEIA a imagem. Nos decks da
   Quaest (100+ páginas) procure as páginas cujo título é exatamente "Intenção de voto
   estimulada para presidente (1º turno)" e "... (2º turno) - Cenários", sem "| Sexo",
   "| Faixa etária" etc. (essas são recortes).
2. Poder360 (`poder360.com.br/tag/pesquisa-eleitoral` e `/tag/poderdata`) e Gazeta do Povo
   (`gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/`). A Gazeta NÃO publica
   presidencial por estado; o Poder360 publica.
3. Site do próprio instituto.
4. Wikipédia só em último caso.

O campo `u` aponta para a fonte de maior prioridade obtida. Se um instituto registra mas nunca
publica percentual, NÃO invente e NÃO insira. Caso conhecido: JOTA Jornalismo (BR-09823/2026 e
BR-03796/2026) registra presidencial nacional e não divulga número no site aberto.

## Passo 4 — Inserir

**DI (nacional):** linha = `[nome, Lula, Flávio, Caiado, Zema, Renan, "Br/N/Ind", "2º turno",
odds, flagAtlas]`. A coluna odds é LEGADO, use `"—"`. Se o instituto já tem rodada no mês,
SUBSTITUA pela mais recente (uma por instituto por mês, é proteção estatística, não descuido) e
diga isso na nota do mês e no campo `nt` do `IM`. Atualize também `T2R[mes][instituto] = [lula,
flavio]` e, no `IM`, os campos `n`, `d` (data + div + registro TSE) e `u`.

**PRES26:** classifique `lead` pelo 2º turno quando publicado e pelo 1º turno quando não houver;
empate técnico (`'E'`) quando a diferença cabe na margem. Preencha `dt` com o ISO do FIM de
campo, conferido no REGISTRO DO TSE, não no que a matéria diz (cinco rótulos já estavam
errados). Onde não há 2º turno, escreva o `t2` em texto contendo "N pontos" (ex.: "Sem 2º turno
divulgado; no 1º turno Lula abre 18 pontos"), porque `pmargin` lê esse número para dar
intensidade de cor ao mapa.

**DGM/DSM + DG/DS: CONGELADOS desde 26/09/2026, não inserir mais nada aqui** (ver "Escopo desde
26/09/2026" no topo deste arquivo). O texto abaixo descreve o formato só para referência
histórica, caso um dia o escopo volte a incluir Governador/Senador.

**FORMATO DA LINHA DE `DGM`/`DSM`, e o 4º elemento importa (08/09/2026).** A linha é
`[instituto, [[nome, valor], ...], nota, suspensa]`. O 3º elemento é NOTA de texto livre e sai
esmaecida embaixo dos nomes. O 4º elemento só existe quando a Justiça Eleitoral barrou a
divulgação: aí vale `1`, a nota passa a ser lida como motivo, a rodada ganha o sinal de alerta e
os números aparecem RISCADOS, para não serem lidos como dado válido. Até 08/09/2026 a suspensão
era o próprio 3º elemento, então TODA rodada com nota comum aparecia riscada, e 106 rodadas
legítimas estavam assim. Nunca ponha `1` no 4º elemento por causa de reputação do instituto ou
de cargo que não é o daquele objeto: risco é para decisão judicial contra AQUELA rodada.

**NOME DO CANDIDATO IDÊNTICO DENTRO DO MESMO MÊS.** `stateBanner` agrega por nome. Se o mesmo
candidato entra como 'Moro' numa pesquisa e 'Sergio Moro' noutra, viram duas pessoas e o banner
anuncia empate numa corrida de 20 pontos (aconteceu no PR até 02/08/2026). Antes de inserir,
confira como o candidato JÁ está escrito naquele UF/mês e repita exatamente. Cuidado com falso
positivo de sobrenome comum: 'Joel Rodrigues' e 'Toni Rodrigues' no PI são duas pessoas.

**CONTRATANTE:** o objeto `CONTR` marca linhas ESTADUAIS pagas por PARTIDO ou por
BANCO/financeiro. Chave = `uf|cargo|mes|instituto` (cargo é `'gov'` ou `'sen'`; instituto
exatamente como escrito em DGM/DSM). Mídia, entidade e própria NÃO marcam. O contratante das
nacionais fica no `IM` (`ct`/`ctt`).

## Passo 5 — Não mexer

Não altere `chartSVG`, a aba House effect, o `VH2DET`/`VHIST2`, o mapa nem as colunas: tudo
deriva do `DI`. `OUTLIERS={}` está VAZIO de propósito, não reintroduza exclusão de instituto nem
volte de mediana para média. O agregado é a MEDIANA de todos os institutos (função `med()`). Não
reintroduza house effect de 1º turno no gráfico nem "% de chance de vitória" no banner.

## Passo 6 — Mercados: NÃO É MAIS SEU

O `rotina_6h.py` no Actions lê o Polymarket e o Kalshi e escreve `PM`, `KAL` e a data
"cotação de D/M/AAAA" do rodapé (`#foot`) quatro vezes por dia, nas janelas de 1h, 7h, 13h e 19h.
Não rode `mercados.py` para atualizar o painel: você duplicaria a cotação com o mesmo número e
geraria commit à toa.

Só assuma este passo se o `PENDENCIAS.md` disser que os mercados falharam ou se o workflow estiver
vermelho. A regra antiga continua valendo quando isso acontecer: formato `['NN,N%','NN,N%']`, e se
o script sair com erro, deixe como está e AVISE no resumo. Nunca chute.

## Passo 7 — Carimbo: também NÃO É MAIS SEU

O Actions carimba "Última atualização" a cada rodada de 6 horas, com o relógio de São Paulo.
Você só mexe no carimbo quando ALTEROU dado nesta rodada, e aí é obrigatório: confira a hora com
`TZ=America/Sao_Paulo date "+%d/%m/%Y %H:%M"` e substitua o texto após "Última atualização: ".
Rodada sem dado novo não leva carimbo, porque o do Actions já é recente.

## Passo 8 — Validar e publicar

```bash
node -e "const s=require('fs').readFileSync('electoralpolls.html','utf8'); const m=s.match(/<script>([\s\S]*)<\/script>/)[1]; try{ new Function(m); console.log('JS OK'); }catch(e){ console.log('JS ERRO:', e.message); }"
```

Corrija até dar "JS OK". Depois faça commit e push na `main`, **só se você mudou dado**. Rodada
sem novidade não commita: quem mantém o repositório vivo agora é a rodada do Actions.

```bash
git add -A && git commit -m "atualiza painel" && git push
```

**O push publica** (desde 02/08/2026, 12h). Os segredos `PA_TOKEN` e `PA_USER` foram cadastrados
no repositório, então o workflow `.github/workflows/deploy.yml` revalida o JS e chama o
`deploy_agregador.py` sozinho a cada push que toque no `electoralpolls.html`. Execução de
referência, verde de ponta a ponta: run 30753444692. Se o JS estiver quebrado, o workflow ABORTA
antes do upload e nada vai ao ar.

Rodar `python3 deploy_agregador.py` à mão continua valendo e não faz mal, porque o upload é
idempotente: use quando quiser o painel no ar na mesma hora sem esperar o Actions, ou quando
`gh run list --limit 3` mostrar o workflow vermelho. No Mac o script lê o token do `painel/.env`;
no Actions, dos segredos do repositório.

**São DOIS workflows, com papéis diferentes.** O `deploy.yml` reage a push que toque no painel e
só publica. O `rotina.yml` é a rodada de 6 em 6 horas descrita no topo deste arquivo, e publica
sozinho no fim. Detalhe do GitHub que importa: push feito pelo `GITHUB_TOKEN` NÃO dispara outro
workflow, então o `deploy.yml` não roda atrás do `rotina.yml`, e por isso o `rotina.yml` chama o
`deploy_agregador.py` ele mesmo. Execução de referência do `rotina.yml`, verde de ponta a ponta:
run 30776807373.

## Regras obrigatórias

- Edite apenas `electoralpolls.html` (e a metodologia, quando aprender algo que o próximo agente
  precise saber). `PENDENCIAS.md` e `estado_rotina.json` são gerados pelo `rotina_6h.py`: leia,
  nunca edite, porque a rodada seguinte sobrescreve.
- Título: "Agregador de pesquisas · Eleições 2026", uma linha só, no `<title>` e na faixa
  dourada. O painel NÃO tem nome de marca. Não reintroduza "50+1" nem "Agregador Brasil".
- SENADO: em 2026 todos os 27 estados elegem DOIS senadores (`SENVAGAS_PADRAO=2`). O painel
  destaca 2 nomes no Senado e 1 no Governador.
- TEMA CLARO/ESCURO: NUNCA escreva cor literal (#hex) no JS. Use os tokens do objeto `P`
  (P.surf, P.txt, P.txt2, P.mut, P.ink, P.purple, P.red, P.blue, P.bord, P.bsoft, P.gold,
  P.goldtxt, P.rowhl, P.link, P.warn). Cor nova exige token no `:root`, no
  `:root[data-theme="dark"]`, na media query e em `PKEYS`.
- Cor: vermelho = Lula à frente, azul = Flávio à frente.
- Não invente número de pesquisa. Sem dado consolidado, não insira.
- Textos sem emojis e sem travessões.

## Passo 9 — Resumo

O que entrou em cada uma das duas frentes, como o agregado do mês mudou (1º turno e margem do 2º
turno) e o que ficou pendente. Se nada novo surgiu, diga isso em duas linhas e pare: o carimbo já
é do Actions e não precisa ser tocado.


## APURAÇÃO AO VIVO NO DIA DA ELEIÇÃO (4/10 e 25/10/2026)

A aba Mapa, ano 2026, vira apuração oficial do TSE sozinha a partir das 8h de 4/10 (e de 25/10), lendo
os JSONs de resultados.tse.jus.br direto do navegador, a cada 60 segundos, enquanto a aba estiver
aberta. Código no painel: bloco "APURAÇÃO AO VIVO DO TSE", funções `res*`, objeto `RES26`.

- O CÓDIGO DA ELEIÇÃO é descoberto no dia em `comum/config/ele-c.json` (eleições com a data do turno,
  testando qual tem LULA no cargo 1). Se falhar, o bloco mostra "procurando a eleição..." por mais de
  um minuto: aí descubra o código à mão (2022 foi 544 no 1º turno e 545 no 2º) e preencha `RES26_COD`.
- TESTE SEM ESPERAR O DIA: abrir o painel com `?simula=2022` carrega a apuração real de 2022 no lugar.
  Em 10/09/2026 esse teste deu 27 UFs, Lula 14 x Bolsonaro 13 e barra 48,4 x 43,2, igual à urna.
- O cache do código é por turno (`localStorage res26cod_<data>`), então o 2º turno não reusa o do 1º.
- Fonte única é o TSE; o painel não recebe número de imprensa nesse modo. Depois de 100% das seções,
  copiar o resultado para um objeto fixo (como PRES2022) e desligar o modo ao vivo é tarefa manual.

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

## Onde esta rotina roda, e por que NÃO roda na nuvem do claude.ai

Esta tarefa roda na **máquina do Rafael** (tarefa agendada local, de hora em hora, sobre o clone
em `~/agregador-pesquisas-2026`). Não tente movê-la para uma rotina de nuvem do claude.ai.

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

## São três frentes. Investigue as três.

1. **Presidencial nacional** → objeto `DI` (uma rodada por instituto por mês, a mais recente)
   + `T2R` (par de 2º turno) + `IM` (metadados do instituto).
2. **Governador / senador por estado** → `DGM`/`DSM` (série mensal, alimenta o painel do estado)
   **e** `DG`/`DS` (resumo do mapa). Mexa SEMPRE nos dois: só DG/DS deixa o painel do estado
   velho, e só DGM/DSM deixa o mapa velho. Confira: se `DG[uf].d` diz "jul" mas `DGM[uf].jul`
   não existe, faltou.
3. **Presidencial por estado** → `PRES26` (aba Mapa). Hoje tem 26 dos 27 estados (falta RR).

## Ferramentas do repositório

```bash
python3 radar_tse.py              # o que o TSE registrou nos últimos 7 dias
python3 radar_tse.py 2026-07-28   # a partir de uma data
python3 mercados.py               # cotações do Polymarket e do Kalshi
python3 mercados.py --debug       # mostra qual caminho de rede funcionou
```

`radar_tse.py` já baixa os ZIPs, faz o desempate nacional x estadual pelo gêmeo e cruza o
contratante. `mercados.py` já tenta HTTPS direto, depois DNS-over-HTTPS, depois o
`nslookup 8.8.8.8` antigo; se todos falharem sai com código 2 e você NÃO inventa número.

## Passo 1 — Radar do TSE (faça SEMPRE antes de sair pesquisando)

Rode `radar_tse.py` e compare com o que já está no painel. **Na maioria das rodadas não haverá
pesquisa nova, e isso é o esperado, não é falha.** Se nada divulgado for novo, pule direto para
o carimbo e o commit, e escreva um resumo de duas linhas. NÃO refaça a varredura pesada (baixar
íntegra em PDF, renderizar página, abrir jornal) quando o radar não apontou nada novo: ele é o
filtro barato que decide se vale abrir o resto.

Colunas úteis do CSV: `NR_PROTOCOLO_REGISTRO`, `NM_EMPRESA_FANTASIA`, `NR_CNPJ_EMPRESA`,
`DS_CARGO`, `DT_INICIO_PESQUISA`, `DT_FIM_PESQUISA`, `DT_DIVULGACAO`, `QT_ENTREVISTADO`,
`VR_PESQUISA`.

Falsos positivos de "nacional" já pegos: Futura/Apex BR-08054/2026 (é de MINAS GERAIS, 291
municípios mineiros) e Veritá de julho (6 registros, todos estaduais).

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

**DGM/DSM + DG/DS:** os dois objetos, sempre.

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

## Passo 6 — Mercados

Rode `python3 mercados.py` e atualize `PM`, `KAL` e a data "cotação de D/M/AAAA" no rodapé
(`#foot`). Formato `['NN,N%','NN,N%']`. **No máximo uma vez a cada 6 horas:** se a data do rodapé
já for de hoje e o horário não for por volta de 7h, 13h ou 19h, pule este passo. Se o script sair
com erro, deixe como está e AVISE no resumo. Nunca chute.

## Passo 7 — Carimbo

Confira a data com `TZ=America/Sao_Paulo date "+%d/%m/%Y %H:%M"`. Substitua o texto após
"Última atualização: ". Faça SEMPRE, mesmo sem rodada nova.

## Passo 8 — Validar e publicar

```bash
node -e "const s=require('fs').readFileSync('electoralpolls.html','utf8'); const m=s.match(/<script>([\s\S]*)<\/script>/)[1]; try{ new Function(m); console.log('JS OK'); }catch(e){ console.log('JS ERRO:', e.message); }"
```

Corrija até dar "JS OK". Depois faça commit e push na `main`:

```bash
git add -A && git commit -m "atualiza painel" && git push
```

**O push publica.** O workflow `.github/workflows/deploy.yml` revalida o JS e sobe para o
PythonAnywhere pela API; se o JS estiver quebrado, ABORTA sozinho e nada vai ao ar. Não rode
`deploy_agregador.py` à mão a menos que o workflow tenha falhado.

## Regras obrigatórias

- Edite apenas `electoralpolls.html` (e a metodologia, quando aprender algo que o próximo agente
  precise saber).
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

O que entrou em cada uma das três frentes, como o agregado do mês mudou (1º turno e margem do 2º
turno) e o que ficou pendente. Se nada novo surgiu, diga isso claramente, mas lembre de atualizar
o carimbo mesmo assim.

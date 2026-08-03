# RETOMAR AQUI — agregador de pesquisas, 21/07/2026

Documento de passagem. O Rafael saiu da internet e pediu para terminar depois.
Se você é uma sessão nova, LEIA ESTE ARQUIVO PRIMEIRO, depois a METODOLOGIA.

PASTA: "/Users/rafael/Library/CloudStorage/GoogleDrive-rafael@dfcarvalho.com.br/Meu Drive/Brasília - Freire Carvalho/Claude"
PAINEL: electoralpolls.html · DEPLOY: `python3 deploy_agregador.py`
NO AR: https://rafaelcortopassi.pythonanywhere.com/electoralpolls/

## 1. A DECISÃO QUE ESTÁ TRAVANDO TUDO (pergunte ao Rafael assim que voltar)

Há pesquisas com divulgação SUSPENSA pela Justiça Eleitoral publicadas no painel AGORA.
Detalhamento completo em `ALERTA_PESQUISAS_SUSPENSAS_JUDICIALMENTE_20260721.md`.

Eu me comprometi a NÃO remover nada sem autorização dele, e ele ainda não respondeu.
O "depois vc termina isso" NÃO é autorização para remover: é instrução genérica de
continuidade. Retirar dado do ar é decisão dele. PERGUNTE.

Minha recomendação registrada: MARCAR como "divulgação suspensa pela Justiça Eleitoral"
e tirar do cálculo, em vez de apagar. Apagar esconde do leitor que a pesquisa existiu e
foi barrada, o que é informação jornalística relevante. Isso exige criar um campo de
flag no modelo dos estaduais (DG/DS/DGM/DSM) e tratá-lo no render.

Ordem de gravidade das entradas hoje publicadas:
1. **SC jun Futura Inteligência** (SC-01761/2026). NÃO é liminar: mérito julgado
   PROCEDENTE por unanimidade em 13/07/2026, pesquisa declarada juridicamente NÃO
   REGISTRADA, proibição DEFINITIVA e multa de R$ 53.205,00 para CADA representada.
   É a de maior risco do painel inteiro.
2. **SC mai Veritá** (SC-02747/2026). Plano amostral listava municípios do MARANHÃO
   como coleta em SC; metadados alterados 7 dias após o campo.
3. **TO jun Paraná Pesquisas** (TO-04463/2026). Suspensão mantida, multa de R$ 15 mil/dia,
   quebra de sigilo de perfis que divulgaram, autos ao MP Eleitoral para apuração CRIMINAL.
4. **TO jan Exata GO**, **TO jan e abr Lucro Ativo** (uma delas declarada não registrada
   + multa de R$ 53.205,00).
5. **DF mai Veritá** (DF-01208/2026), **GO abr Veritá**, **MS mar Veritá**
   (MS-03077/2026), **AL jun Vox Brasil** (AL-05861/2026).
6. **PE abr Veritá** (PE-02184/2026) e **PE mai Instituto Múltipla** (PE-07611/2026):
   períodos batem, registro NÃO confirmado. Confirmar antes de agir.

CONFIRMADO LIMPO: o presidencial nacional. A AtlasIntel suspensa pelo TSE é a
BR-06939/2026; a que está no `DI` é a BR-04582/2026 (campo 25-30/jun). Registros
diferentes. O "Lula +3,0" do topo NÃO está contaminado.

## 2. O QUE JÁ FOI FEITO E PUBLICADO EM 20-21/07 (não refazer)

- Agregado virou MEDIANA; `OUTLIERS={}` vazio; ninguém é excluído.
- `VH2DET` foi de 5 para 9 institutos. Nexus/BTG entrou e foi REMOVIDO no mesmo dia
  (1 pesquisa não-final de 2018, frágil demais).
- Título: "Agregador de pesquisas · Eleições 2026", uma linha. O nome "50+1" foi
  adotado e depois REMOVIDO de tudo a pedido dele. Não reintroduzir.
- Senado destaca em negrito 2 nomes (2026 elege 2 senadores em todos os 27 estados);
  Governador destaca 1. `SENVAGAS_PADRAO=2`, `SENVAGAS_UF={}`, `nDestaque(office,uf)`.
- 32 rodadas estaduais novas publicadas: SC e PE (IPC/ACJ e Conecta), RS, MG, RJ, SP,
  PA, TO, GO, MS, DF.
- Carimbo em 21/07/2026 09:34.

## 3. DADOS JÁ PESQUISADOS E AINDA NÃO INSERIDOS

Estão nos relatórios da conversa; se ela se perdeu, será preciso repesquisar.

- **PE**: Instituto Múltipla (13-16/jun, PE-02553/2026) e Numen Data (20-24/jun,
  PE-00918/2026, ALERTA de outlier: Raquel +9,4 contra o inverso nas demais).
- **CE**: Senado por Paraná Pesquisas em jan (CE-05139/2026) e fev (CE-08478/2026).
  Bloqueio: as pesquisas de Senado de PE e CE usam VOTO MÚLTIPLO, somam mais de 100%
  e não são comparáveis ao formato atual. Precisa decisão de modelagem.
- **RR**: contexto anômalo (governador cassado, eleição suplementar em 21/06 vencida
  por Arthur Henrique com 60,87%, diplomação suspensa no TSE aguardando o STF). NÃO há
  pesquisa de mai/jun/jul. O vazio é real.
- **MG**: NÃO existe pesquisa estadual de julho. A única candidata é do MDA, sem margem
  de erro, sem registro TSE, sem contratante, sem datas de campo, N=600, publicada só
  por um jornal de Juiz de Fora, possivelmente regional. NÃO publicar.
- **GO**: rodada Veritá de 12-16/jul (GO-02507/2026) NÃO inserida de propósito: o
  relatório traz perguntas de PRESIDENTE dentro de pesquisa registrada para governador
  e senador, que é o vício que já derrubou a rodada de abril no próprio TRE-GO.

## 4. FALSO ALARME QUE NÃO DEVE SER "CORRIGIDO"

Um pesquisador afirmou que a Wikipédia corrompeu os números de RORAIMA e que o painel
deveria ter Arthur Henrique 60% no lugar de 42,6%. ELE ESTAVA ERRADO. A conta fecha:
42,6 / 70,9 = 60,1%; 22,5 / 70,9 = 31,7%; 4,2 / 70,9 = 5,9%. São a MESMA pesquisa em
bases diferentes (o painel guarda amostra total; ele leu votos válidos). NÃO alterar RR.
No Senado de RR há divergência real de medida (o painel soma 119,1, indicando menção
múltipla; ele traz 100,1, de voto único). Essa sim fica pendente de verificação.

## 5. ERROS RECORRENTES DA WIKIPÉDIA (confirmados várias vezes hoje)

Usar a Wikipédia SÓ como índice do que existe, nunca como fonte de número:
- troca votos válidos por amostra total (RS/Veritá, PA/Veritá, SC/Veritá);
- atribui percentual ao candidato errado (RS/Brasmarket, RR/Jucá, DF/França);
- SOMA 1º e 2º voto do Senado por conta própria quando o instituto não somou, e chega a
  errar a soma (MS/Ranking: publica 36,6 onde a soma dá 38,6);
- duplica linha de um instituto atribuindo a outro (MS/IPR recebeu números do Novo Ibrape).

## 6. LIÇÃO DE PROCESSO PARA O PRÓXIMO LOTE

Dar 6 ou 7 estados por pesquisador FALHOU: dois deles subdividiram em subagentes
próprios e encerraram sem compilar, devolvendo "vou esperar os agentes" e queimando
~185 mil tokens sem entregar linha aproveitável. Foi preciso cobrar com ordem explícita
de não delegar. Com 3 a 4 estados por pesquisador funcionou bem.
Instrua sempre: "não delegue; entregue relatório parcial imediato se faltar algo".

## 6-B. DESCOBERTA MAIS IMPORTANTE DO DIA: O TSE PUBLICA TUDO EM DADOS ABERTOS

Pare de usar a Wikipédia como índice. O PesqEle web (`pesqele.tse.jus.br`) está fora do
ar e o de divulgação exige sessão, MAS o portal de DADOS ABERTOS funciona e é melhor:

    https://dadosabertos.tse.jus.br/dataset/pesquisas-eleitorais-2026
    arquivos: pesquisa_eleitoral_2026.zip e pesquisa_contratante_2026.zip

Baixei e PRESERVEI na pasta do projeto: **`tse_pesqele_2026/`** (8,4 MB, 27 CSVs por UF
mais o BRASIL.csv e o leiame.pdf). Geração 21/07/2026 08:47. Encoding **latin-1**,
separador **ponto e vírgula**.

Colunas úteis: SG_UF, NR_PROTOCOLO_REGISTRO, DT_REGISTRO, ST_PESQUISA_PROPRIA,
NM_EMPRESA, NM_EMPRESA_FANTASIA, DS_CARGO, DT_INICIO_PESQUISA, DT_FIM_PESQUISA,
DT_DIVULGACAO, QT_ENTREVISTADO, VR_PESQUISA, NM_ESTATISTICO_RESP, DS_METODOLOGIA_PESQUISA,
DS_PLANO_AMOSTRAL. O ZIP de contratante dá QUEM PAGOU cada pesquisa.

ARMADILHA: `DS_CARGO` traz cargos COMBINADOS ("Governador, Senador, Deputado Federal").
Filtrar por igualdade exata subconta gravemente. Use substring ('overnador'/'enador').

### O UNIVERSO REAL, MEDIDO (não estimado), em 21/07/2026

- **1.258** registros de pesquisa em 2026 no Brasil todo.
- **475** deles são de **Presidente**.
- **773** registros distintos incluem **Governador e/ou Senador**, de **135 empresas**.

Por UF (registros gov/sen): PI 105 · GO 74 · RN 52 · PB 49 · SE 40 · SP 35 · PE 31 ·
RJ 30 · AM 27 · PA 27 · MA 25 · PR 24 · CE 23 · TO 23 · DF 22 · MS 21 · MG 19 ·
ES 18 · RO 18 · RS 18 · AL 16 · MT 16 · AC 15 · AP 14 · BA 13 · SC 13 · RR 5.

Isso mostra que o Piauí, Goiás, RN, PB e Sergipe são os estados com mais pesquisas
registradas, e não os grandes colégios eleitorais. E confirma RR como o mais vazio (5).

### RESSALVA CRÍTICA ANTES DE SE ANIMAR

**Registro não é divulgação.** Boa parte dessas 773 nunca teve percentual publicado.
No DF, por exemplo, das 22 registradas, a maioria (Narreal, CEPPHOR, Badra, 4 ondas da
Exata OP, 3 ondas do Veritá) NÃO divulgou número nenhum. O CSV diz o que EXISTE e quem
pagou; os percentuais continuam vindo da imprensa ou do site do instituto.

Uso correto: o CSV vira a LISTA DE VERIFICAÇÃO do que procurar, substituindo a Wikipédia
como índice, e vira a fonte autoritativa de registro, N, datas de campo, custo e
contratante. Isso mata de uma vez os erros de transcrição da Wikipédia.

## 7. O QUE FALTA

- Estados sem varredura concluída: AC, AL, AM, AP, ES, MA, MT, PB, PI, RN, RO, SE.
  (O pesquisador do Nordeste — PB, RN, SE, MA — disse ter os dados verificados em fonte
  primária mas encerrou sem entregar; foi cobrado no fim da sessão e pode não ter dado
  tempo.)
- Checagem judicial fica como PASSO FIXO do processo, já anotada na SKILL semanal.
- Confirmar no PesqEle os registros de PE (Veritá abr, Múltipla mai).

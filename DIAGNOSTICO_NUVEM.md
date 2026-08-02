# Diagnostico do ambiente de nuvem

Data e hora da execucao (horario de Brasilia): 02/08/2026 11:21
Data e hora da execucao (UTC): 02/08/2026 14:21

## 1. Versoes e binarios disponiveis

Status: OK (com uma ausencia)

```
python3 --version
Python 3.11.15

node --version
v22.22.2

which curl
/usr/bin/curl

which pdftotext
(nada retornado, exit code 1, binario nao encontrado)

which git
/usr/bin/git
```

Resultado: python3, node, curl e git estao disponiveis. O pdftotext NAO esta instalado neste ambiente.

## 2. mercados.py --debug (Polymarket e Kalshi)

Status: FALHOU

```
[debug] direto falhou para gamma-api.polymarket.com: <urlopen error Tunnel connection failed: 403 Forbidden>
[debug] DoH google falhou para gamma-api.polymarket.com: <urlopen error Tunnel connection failed: 403 Forbidden>
[debug] DoH cloudflare falhou para gamma-api.polymarket.com: <urlopen error Tunnel connection failed: 403 Forbidden>
[debug] nslookup 8.8.8.8 falhou para gamma-api.polymarket.com: [Errno 2] No such file or directory: 'nslookup'
[debug] direto falhou para api.elections.kalshi.com: <urlopen error Tunnel connection failed: 403 Forbidden>
[debug] DoH google falhou para api.elections.kalshi.com: <urlopen error Tunnel connection failed: 403 Forbidden>
[debug] DoH cloudflare falhou para api.elections.kalshi.com: <urlopen error Tunnel connection failed: 403 Forbidden>
[debug] nslookup 8.8.8.8 falhou para api.elections.kalshi.com: [Errno 2] No such file or directory: 'nslookup'
{
 "erros": {
  "PM": "nao consegui falar com gamma-api.polymarket.com por nenhum caminho de rede",
  "KAL": "nao consegui falar com api.elections.kalshi.com por nenhum caminho de rede"
 }
}
```

PM_via: nenhum caminho funcionou (direto, DoH google, DoH cloudflare e nslookup falharam todos)
KAL_via: nenhum caminho funcionou (direto, DoH google, DoH cloudflare e nslookup falharam todos)

Observacao adicional: o binario nslookup tambem nao esta instalado neste ambiente (Errno 2, No such file or directory), entao esse caminho de fallback nunca chega a ser testado de fato, ele falha por ausencia do programa.

Todas as tentativas diretas e via DoH falharam com o mesmo erro de tunel HTTP: "Tunnel connection failed: 403 Forbidden". Isso indica que existe um proxy de saida obrigatorio neste ambiente que esta bloqueando (403) as conexoes para esses dominios especificos.

## 3. radar_tse.py 2026-07-28 (download dos ZIPs do TSE)

Status: FALHOU

```
Traceback (most recent call last):
  File "/usr/lib/python3.11/urllib/request.py", line 1348, in do_open
    h.request(req.get_method(), req.selector, req.data, headers,
  File "/usr/lib/python3.11/http/client.py", line 1323, in request
    self._send_request(method, url, body, headers, encode_chunked)
  File "/usr/lib/python3.11/http/client.py", line 1369, in _send_request
    self.endheaders(body, encode_chunked=encode_chunked)
  File "/usr/lib/python3.11/http/client.py", line 1318, in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
  File "/usr/lib/python3.11/http/client.py", line 1078, in _send_output
    self.send(msg)
  File "/usr/lib/python3.11/http/client.py", line 1016, in send
    self.connect()
  File "/usr/lib/python3.11/http/client.py", line 1488, in connect
    super().connect()
  File "/usr/lib/python3.11/http/client.py", line 992, in connect
    self._tunnel()
  File "/usr/lib/python3.11/http/client.py", line 963, in _tunnel
    raise OSError(f"Tunnel connection failed: {code} {message.strip()}")
OSError: Tunnel connection failed: 403 Forbidden

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/user/agregador-pesquisas-2026/radar_tse.py", line 132, in <module>
    main()
  File "/home/user/agregador-pesquisas-2026/radar_tse.py", line 83, in main
    pe = carregar("pe")
         ^^^^^^^^^^^^^^
  File "/home/user/agregador-pesquisas-2026/radar_tse.py", line 54, in carregar
```

Mesmo erro de tunel 403 Forbidden ao tentar baixar os arquivos do TSE.

## 4. curl https://www.poder360.com.br/tag/pesquisa-eleitoral/

Status: FALHOU

Codigo HTTP retornado: 000 (sem resposta do servidor de destino)

Execucao verbosa para diagnostico:

```
* Trying 127.0.0.1:32995...
* Connected to 127.0.0.1 (127.0.0.1) port 32995
* CONNECT tunnel: HTTP/1.1 negotiated
* allocate connect buffer
* Establish HTTP proxy tunnel to www.poder360.com.br:443
> CONNECT www.poder360.com.br:443 HTTP/1.1
> Host: www.poder360.com.br:443
> User-Agent: curl/8.5.0
> Proxy-Connection: Keep-Alive
>
< HTTP/1.1 403 Forbidden
< Content-Length: 36
<
* CONNECT tunnel failed, response 403
* Closing connection
curl: (56) CONNECT tunnel failed, response 403
```

O proxy de saida local (127.0.0.1) recusa com 403 Forbidden a abertura do tunel HTTPS para este dominio.

## 5. curl https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/

Status: FALHOU

Codigo HTTP retornado: 000 (mesmo padrao do item 4, tunel do proxy recusado com 403 Forbidden)

## 6. curl https://static.poder360.com.br/

Status: FALHOU

Codigo HTTP retornado: 000 (mesmo padrao do item 4, tunel do proxy recusado com 403 Forbidden)

## 7. curl https://www.pythonanywhere.com/api/v0/

Status: FALHOU

Codigo HTTP retornado: 000 (mesmo padrao do item 4, tunel do proxy recusado com 403 Forbidden)

## 8. Relogio (TZ=America/Sao_Paulo)

Status: OK

```
TZ=America/Sao_Paulo date '+%d/%m/%Y %H:%M'
02/08/2026 11:21

date -u '+%d/%m/%Y %H:%M'
02/08/2026 14:21
```

A diferenca entre o horario UTC e o horario de Brasilia e de exatamente 3 horas, o que corresponde ao fuso correto (UTC-3, sem horario de verao). A data 02/08/2026 confere com a data atual esperada. O relogio esta certo.

## 9. Estado do git

Status: OK

```
git remote -v
origin	http://local_proxy@127.0.0.1:41729/git/rcortopassi/agregador-pesquisas-2026 (fetch)
origin	http://local_proxy@127.0.0.1:41729/git/rcortopassi/agregador-pesquisas-2026 (push)

git status
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean

git log --oneline -1
2f82565 nao versionar o symlink painel (aponta para pasta local com o .env)
```

O remote origin nao aponta diretamente para o GitHub, e sim para um proxy local (127.0.0.1:41729) que intermedeia o acesso ao repositorio remoto. O repositorio esta limpo e atualizado com o origin/main antes deste diagnostico.

## Conclusao

(a) O sandbox NAO consegue ler Polymarket nem Kalshi. Nenhum dos caminhos de rede testados por mercados.py funcionou (nem conexao direta, nem DNS-over-HTTPS via Google, nem DNS-over-HTTPS via Cloudflare, nem o fallback de nslookup, que nem sequer esta instalado). Todas as tentativas de rede saem por um proxy HTTP local obrigatorio, e esse proxy responde 403 Forbidden ao tentar abrir o tunel HTTPS para gamma-api.polymarket.com e para api.elections.kalshi.com.

(b) O sandbox NAO consegue baixar os ZIPs do TSE (mesmo erro de tunel 403 Forbidden do proxy local) e tambem NAO consegue abrir Poder360, static.poder360.com.br nem Gazeta do Povo (todos retornaram codigo HTTP 000, com o proxy recusando o CONNECT com 403 Forbidden). O teste do endpoint do PythonAnywhere (https://www.pythonanywhere.com/api/v0/) tambem falhou pelo mesmo motivo.

(c) Push para o origin: ver secao de tentativa de push abaixo, executada apos a escrita deste arquivo.

(d) O relogio esta certo. TZ=America/Sao_Paulo bateu com o horario de Brasilia (UTC-3) e com a data atual esperada (02/08/2026).

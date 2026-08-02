#!/usr/bin/env python3
"""
Le as cotacoes de Polymarket e Kalshi para a eleicao presidencial brasileira de 2026.

POR QUE ESTE ARQUIVO EXISTE. Na maquina do usuario os dois dominios nao resolvem pelo DNS
do provedor, e a receita que funcionava era `nslookup ... 8.8.8.8` + `curl --resolve`. Essa
receita depende de UDP porta 53 para 8.8.8.8, que e exatamente o tipo de trafego que um
sandbox de nuvem costuma bloquear. Entao aqui a resolucao de nome e feita por DNS-over-HTTPS,
que e HTTPS comum na porta 443 e funciona em qualquer lugar onde HTTPS funcione.

ORDEM DE TENTATIVA, da mais simples para a mais teimosa:
  1. HTTPS direto (funciona onde o DNS nao esta envenenado; provavel na nuvem)
  2. DoH no dns.google, depois curl --resolve no IP obtido
  3. DoH no cloudflare-dns.com, mesma coisa
  4. nslookup 8.8.8.8 (a receita local antiga, para nao perder o que ja funcionava)

Se as quatro falharem, sai com codigo 2 e NAO inventa numero. Quem chama deve deixar os
valores como estao no painel e avisar no resumo. Essa regra e da metodologia e nao muda.

Uso:
  python3 mercados.py            # imprime JSON com as cotacoes
  python3 mercados.py --debug    # mostra qual caminho de rede funcionou
Somente stdlib.
"""
import json
import re
import ssl
import subprocess
import sys
import urllib.request

TIMEOUT = 25
UA = "Mozilla/5.0 (compativel; agregador-pesquisas-2026)"

PM_HOST = "gamma-api.polymarket.com"
PM_URL = f"https://{PM_HOST}/events?slug=brazil-presidential-election"
KAL_HOST = "api.elections.kalshi.com"
KAL_URL = (f"https://{KAL_HOST}/trade-api/v2/markets"
           "?series_ticker=KXBRPRES&status=open&limit=200")

DEBUG = "--debug" in sys.argv
def log(*a):
    if DEBUG:
        print("[debug]", *a, file=sys.stderr)


def _get_direct(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read().decode("utf-8", "replace")


def _doh(host, resolver):
    """Resolve um nome por DNS-over-HTTPS. Devolve o primeiro A, ou None."""
    if resolver == "google":
        url = f"https://dns.google/resolve?name={host}&type=A"
        headers = {"User-Agent": UA}
    else:
        url = f"https://cloudflare-dns.com/dns-query?name={host}&type=A"
        headers = {"User-Agent": UA, "Accept": "application/dns-json"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
        for ans in data.get("Answer", []):
            if ans.get("type") == 1 and re.match(r"^\d+\.\d+\.\d+\.\d+$", ans.get("data", "")):
                return ans["data"]
    except Exception as e:
        log(f"DoH {resolver} falhou para {host}: {e}")
    return None


def _nslookup_8888(host):
    try:
        out = subprocess.run(["nslookup", host, "8.8.8.8"],
                             capture_output=True, text=True, timeout=TIMEOUT).stdout
        ips = re.findall(r"^Address: (\d+\.\d+\.\d+\.\d+)", out, re.M)
        return ips[0] if ips else None
    except Exception as e:
        log(f"nslookup 8.8.8.8 falhou para {host}: {e}")
    return None


def _get_via_ip(url, host, ip):
    """Conecta no IP mas com SNI/Host do dominio real. Tenta curl; se nao houver, http.client."""
    try:
        p = subprocess.run(
            ["curl", "-s", "--max-time", str(TIMEOUT), "-A", UA,
             "--resolve", f"{host}:443:{ip}", url],
            capture_output=True, text=True, timeout=TIMEOUT + 10)
        if p.returncode == 0 and p.stdout.strip():
            return p.stdout
        log(f"curl --resolve devolveu rc={p.returncode}")
    except FileNotFoundError:
        log("curl nao encontrado, caindo para http.client")
    except Exception as e:
        log(f"curl --resolve falhou: {e}")
    import http.client
    path = url.split(host, 1)[1]
    ctx = ssl.create_default_context()
    conn = http.client.HTTPSConnection(ip, 443, timeout=TIMEOUT, context=ctx)
    conn.sock = None
    # server_hostname correto e o que faz o certificado validar
    conn._context.check_hostname = True
    conn.host = host
    conn.request("GET", path, headers={"Host": host, "User-Agent": UA})
    return conn.getresponse().read().decode("utf-8", "replace")


def buscar(url, host):
    """Devolve (texto, como_conseguiu). Levanta RuntimeError se todos os caminhos falharem."""
    try:
        txt = _get_direct(url)
        if txt.strip():
            return txt, "direto"
    except Exception as e:
        log(f"direto falhou para {host}: {e}")
    for nome, resolvedor in (("doh-google", "google"),
                             ("doh-cloudflare", "cloudflare"),
                             ("nslookup-8.8.8.8", None)):
        ip = _nslookup_8888(host) if resolvedor is None else _doh(host, resolvedor)
        if not ip:
            continue
        log(f"{host} resolveu para {ip} via {nome}")
        try:
            txt = _get_via_ip(url, host, ip)
            if txt.strip():
                return txt, f"{nome} + IP {ip}"
        except Exception as e:
            log(f"conexao ao IP {ip} falhou: {e}")
    raise RuntimeError(f"nao consegui falar com {host} por nenhum caminho de rede")


def pct(x):
    """0.665 -> '66,5%' (uma casa, virgula decimal, como o painel escreve)."""
    return f"{x * 100:.1f}".replace(".", ",") + "%"


def polymarket():
    txt, via = buscar(PM_URL, PM_HOST)
    eventos = json.loads(txt)
    precos = {}
    for ev in eventos:
        for m in ev.get("markets", []):
            nome = (m.get("groupItemTitle") or "").strip()
            try:
                p = float(json.loads(m["outcomePrices"])[0])
            except Exception:
                continue
            if nome:
                precos[nome] = p
    lula = precos.get("Luiz Inácio Lula da Silva")
    flavio = precos.get("Flávio Bolsonaro")
    if lula is None or flavio is None:
        raise RuntimeError(f"Polymarket sem Lula/Flavio no payload (achei {sorted(precos)[:6]})")
    return [pct(lula), pct(flavio)], via


def kalshi():
    txt, via = buscar(KAL_URL, KAL_HOST)
    dados = json.loads(txt)
    precos = {}
    for m in dados.get("markets", []):
        nome = (m.get("yes_sub_title") or "").strip()
        p = m.get("last_price_dollars")
        if p is None and m.get("last_price") is not None:
            p = m["last_price"] / 100.0
        if nome and p is not None:
            precos[nome] = float(p)
    lula = precos.get("Luiz Inácio Lula da Silva")
    flavio = precos.get("Flávio Bolsonaro")
    if lula is None or flavio is None:
        raise RuntimeError(f"Kalshi sem Lula/Flavio no payload (achei {sorted(precos)[:6]})")
    return [pct(lula), pct(flavio)], via


def main():
    saida, erros = {}, {}
    for nome, fn in (("PM", polymarket), ("KAL", kalshi)):
        try:
            valores, via = fn()
            saida[nome] = valores
            saida[nome + "_via"] = via
        except Exception as e:
            erros[nome] = str(e)
    if erros:
        saida["erros"] = erros
    print(json.dumps(saida, ensure_ascii=False, indent=1))
    return 2 if len(erros) == 2 else (1 if erros else 0)


if __name__ == "__main__":
    sys.exit(main())

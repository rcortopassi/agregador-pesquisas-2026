#!/usr/bin/env python3
"""
RADAR DO TSE. Diz o que EXISTE de pesquisa registrada, antes de sair procurando numero.

E o filtro barato da rotina: se nada foi divulgado depois do que ja esta no painel, nao vale
abrir integra em PDF nem navegador. Baixa os dois ZIPs de dados abertos (pesquisa e
contratante), casa um com o outro pelo protocolo e imprime dois blocos: presidenciais (cada
uma marcada NACIONAL? ou ESTADUAL[UF]) e governador/senador por estado, com quem pagou.

DESEMPATE NACIONAL x ESTADUAL PELO GEMEO. O TSE marca NM_UE="BRASIL" em TODA pesquisa com
pergunta presidencial, mesmo com amostra de um unico estado. O jeito de separar e cruzar o
registro BR- contra TODOS os registros estaduais casando por CNPJ + data inicio + data fim +
tamanho da amostra. Se existe gemeo estadual, e daquele estado e NAO entra no DI nacional.
LIMITE: "sem gemeo" significa CANDIDATA a nacional, nao confirmada (o gemeo pode nao ter sido
registrado, ou ter sido retirado). Confirme sempre pela materia antes de inserir.

ARMADILHA: DS_CARGO traz cargos combinados ("Governador, Senador, Deputado Federal").
Filtre por SUBSTRING, nunca por igualdade.

Uso:
  python3 radar_tse.py                 # divulgacao dos ultimos 7 dias
  python3 radar_tse.py 2026-07-28      # divulgacao a partir da data
Somente stdlib. Baixa para um diretorio temporario e reaproveita se ja baixou hoje.
"""
import csv
import io
import os
import sys
import tempfile
import zipfile
from datetime import datetime, timedelta
from urllib.request import Request, urlopen

BASE_URL = "https://cdn.tse.jus.br/estatistica/sead/odsele/pesquisa_eleitoral"
ZIPS = {"pe": "pesquisa_eleitoral_2026.zip", "pc": "pesquisa_contratante_2026.zip"}
CACHE = os.path.join(tempfile.gettempdir(), "radar_tse_2026")
UA = "Mozilla/5.0 (compativel; agregador-pesquisas-2026)"


def baixar(qual):
    os.makedirs(CACHE, exist_ok=True)
    destino = os.path.join(CACHE, qual + "_" + datetime.now().strftime("%Y%m%d"))
    if os.path.isdir(destino) and os.listdir(destino):
        return destino
    req = Request(f"{BASE_URL}/{ZIPS[qual]}", headers={"User-Agent": UA})
    with urlopen(req, timeout=180) as r:
        dados = r.read()
    with zipfile.ZipFile(io.BytesIO(dados)) as z:
        z.extractall(destino)
    return destino


def carregar(qual):
    d = baixar(qual)
    linhas = []
    for nome in sorted(os.listdir(d)):
        if not nome.endswith(".csv"):
            continue
        uf = nome.replace(".csv", "").split("_")[-1]
        with open(os.path.join(d, nome), encoding="latin-1") as fh:
            for r in csv.DictReader(fh, delimiter=";"):
                r["_UF"] = uf
                linhas.append(r)
    return linhas


def dt(s):
    s = (s or "").strip()
    for f in ("%Y-%m-%d %H:%M:%S", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, f)
        except ValueError:
            pass
    return None


def ds(s):
    x = dt(s)
    return x.strftime("%d/%m") if x else "??"


def main():
    pe = carregar("pe")
    pc = carregar("pc")
    print(f"registros: {len(pe)} pesquisa, {len(pc)} contratante | ZIP gerado em {pe[0]['DT_GERACAO']}")

    contr = {}
    for r in pc:
        contr.setdefault(r["NR_PROTOCOLO_REGISTRO"], []).append(
            (r["NM_CONTRATANTE"], r.get("DS_ORIGEM_RECURSO", "")))

    def quem_pagou(proto):
        return "; ".join(f"{a} [{b}]" for a, b in contr.get(proto, []))

    corte = dt(sys.argv[1]) if len(sys.argv) > 1 else datetime.now() - timedelta(days=7)
    print(f"corte de divulgacao: {corte:%d/%m/%Y}\n")

    nao_br = [r for r in pe if r["_UF"] != "BRASIL"]
    gemeos = {}
    for r in nao_br:
        k = (r["NR_CNPJ_EMPRESA"], r["DT_INICIO_PESQUISA"], r["DT_FIM_PESQUISA"], r["QT_ENTREVISTADO"])
        gemeos.setdefault(k, []).append(r)

    def recente(r):
        d = dt(r["DT_DIVULGACAO"])
        return d is not None and d >= corte

    pres = [r for r in pe if "PRESIDENTE" in r["DS_CARGO"].upper() and recente(r)]
    print("=== PRESIDENCIAIS ===")
    for r in sorted(pres, key=lambda x: dt(x["DT_DIVULGACAO"])):
        k = (r["NR_CNPJ_EMPRESA"], r["DT_INICIO_PESQUISA"], r["DT_FIM_PESQUISA"], r["QT_ENTREVISTADO"])
        g = gemeos.get(k)
        tag = f"ESTADUAL[{g[0]['_UF']}]" if g else "NACIONAL?"
        print("%-14s %-16s %-26s campo %s-%s | div %s | N=%s | %s" % (
            tag, r["NR_PROTOCOLO_REGISTRO"], r["NM_EMPRESA_FANTASIA"][:26],
            ds(r["DT_INICIO_PESQUISA"]), ds(r["DT_FIM_PESQUISA"]), ds(r["DT_DIVULGACAO"]),
            r["QT_ENTREVISTADO"], quem_pagou(r["NR_PROTOCOLO_REGISTRO"])[:60]))

    print("\n=== GOVERNADOR / SENADOR (estaduais) ===")
    gs = [r for r in nao_br
          if ("GOVERNADOR" in r["DS_CARGO"].upper() or "SENADOR" in r["DS_CARGO"].upper())
          and recente(r)]
    for r in sorted(gs, key=lambda x: (x["_UF"], dt(x["DT_DIVULGACAO"]))):
        print("%-4s %-16s %-24s [%-30s] campo %s-%s | div %s | N=%s | %s" % (
            r["_UF"], r["NR_PROTOCOLO_REGISTRO"], r["NM_EMPRESA_FANTASIA"][:24],
            r["DS_CARGO"][:30], ds(r["DT_INICIO_PESQUISA"]), ds(r["DT_FIM_PESQUISA"]),
            ds(r["DT_DIVULGACAO"]), r["QT_ENTREVISTADO"],
            quem_pagou(r["NR_PROTOCOLO_REGISTRO"])[:55]))


if __name__ == "__main__":
    main()

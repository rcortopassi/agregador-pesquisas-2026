#!/usr/bin/env python3
"""
ROTINA MECANICA DE 6 EM 6 HORAS. E o que o GitHub Actions consegue fazer sozinho.

DIVISAO DE TRABALHO (decidida em 02/08/2026, quando a rotina saiu de hora em hora):
  - AQUI, no Actions, fica tudo que e deterministico: cotacoes de mercado, carimbo de
    "Ultima atualizacao", deteccao do que E NOVO no TSE e no Verita, validacao do JS,
    commit e publicacao no PythonAnywhere.
  - NA RODADA LOCAL do Claude, tambem de 6 em 6 horas, fica o que exige julgamento:
    abrir a integra em PDF, ler numero que so existe em grafico, decidir se a rodada e
    nacional ou estadual, escolher o mes, casar nome de candidato e inserir nos objetos.

Este script NUNCA insere pesquisa no painel. Ele so avisa, no PENDENCIAS.md, que existe
algo novo para a rodada local olhar. Nao inventar numero continua valendo aqui tambem.

Uso:
  python3 rotina_6h.py                # rodada completa
  python3 rotina_6h.py --sem-mercados # pula Polymarket/Kalshi
  python3 rotina_6h.py --semear       # so marca o estado atual como visto, nao escreve painel
  python3 rotina_6h.py --dry-run      # mostra o que faria, sem gravar nada

Saida: mexe em electoralpolls.html, PENDENCIAS.md e estado_rotina.json. Codigo 0 sempre que
a rodada faz sentido; codigo 1 so quando o painel ficaria quebrado (ai nada e gravado).
Somente stdlib.
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from urllib.request import Request, urlopen

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("America/Sao_Paulo")
except Exception:  # pragma: no cover - so cai aqui em ambiente sem tzdata
    TZ = None

RAIZ = os.path.dirname(os.path.abspath(__file__))
PAINEL = os.path.join(RAIZ, "electoralpolls.html")
ESTADO = os.path.join(RAIZ, "estado_rotina.json")
PENDENCIAS = os.path.join(RAIZ, "PENDENCIAS.md")

UA = "Mozilla/5.0 (compativel; agregador-pesquisas-2026)"
VERITA_HOME = "https://eleicoes26.institutoverita.com.br/"
VERITA_REST = ("https://lgjdbpskgjfbmlffbntx.supabase.co/rest/v1/pesquisas"
               "?select=id,titulo,descricao,pdf_url,created_at&order=created_at.desc&limit=12")
DIAS_JANELA = 10  # quanto tempo para tras o relatorio lista divulgacoes


def agora():
    return datetime.now(TZ) if TZ else datetime.now()


def ler_estado():
    if os.path.exists(ESTADO):
        with open(ESTADO, encoding="utf-8") as fh:
            return json.load(fh)
    return {"tse_vistos": [], "verita_vistos": [], "ultima_rodada": None}


# ---------------------------------------------------------------- TSE

def radar_tse():
    """Registros com divulgacao ja vencida, dos ultimos DIAS_JANELA dias.

    Reaproveita o radar_tse.py em vez de reimplementar o desempate nacional x estadual:
    se a regra do gemeo mudar la, muda aqui junto e nao ficam duas versoes brigando.
    """
    sys.path.insert(0, RAIZ)
    import radar_tse

    pe = radar_tse.carregar("pe")
    hoje = agora().date()
    corte = hoje - timedelta(days=DIAS_JANELA)

    nao_br = [r for r in pe if r["_UF"] != "BRASIL"]
    gemeos = {}
    for r in nao_br:
        k = (r["NR_CNPJ_EMPRESA"], r["DT_INICIO_PESQUISA"],
             r["DT_FIM_PESQUISA"], r["QT_ENTREVISTADO"])
        gemeos.setdefault(k, []).append(r)

    itens = []
    vistos = set()
    for r in pe:
        cargo = r["DS_CARGO"].upper()
        if not any(c in cargo for c in ("PRESIDENTE", "GOVERNADOR", "SENADOR")):
            continue
        # Uma pesquisa estadual aparece DUAS vezes: no CSV do estado e no de BRASIL. Sem
        # este filtro cada linha estadual sai repetida no relatorio (73 repetidas em 195).
        if "PRESIDENTE" not in cargo and r["_UF"] == "BRASIL":
            continue
        if r["NR_PROTOCOLO_REGISTRO"] in vistos:
            continue
        vistos.add(r["NR_PROTOCOLO_REGISTRO"])
        d = radar_tse.dt(r["DT_DIVULGACAO"])
        if d is None:
            continue
        div = d.date()
        # so interessa o que JA podia estar publicado: divulgacao no passado ou hoje
        if div > hoje or div < corte:
            continue
        if "PRESIDENTE" in cargo:
            k = (r["NR_CNPJ_EMPRESA"], r["DT_INICIO_PESQUISA"],
                 r["DT_FIM_PESQUISA"], r["QT_ENTREVISTADO"])
            g = gemeos.get(k)
            escopo = f"ESTADUAL[{g[0]['_UF']}]" if g else "NACIONAL?"
        else:
            escopo = r["_UF"]
        itens.append({
            "proto": r["NR_PROTOCOLO_REGISTRO"],
            "escopo": escopo,
            "inst": (r["NM_EMPRESA_FANTASIA"] or "#NULO#")[:28],
            "cargo": r["DS_CARGO"][:34],
            "campo": "%s-%s" % (radar_tse.ds(r["DT_INICIO_PESQUISA"]),
                                radar_tse.ds(r["DT_FIM_PESQUISA"])),
            "div": div.isoformat(),
            "n": r["QT_ENTREVISTADO"],
        })
    itens.sort(key=lambda x: (x["div"], x["escopo"]))
    return itens


# ---------------------------------------------------------------- Verita

def radar_verita():
    """Le a lista de publicacoes do Verita direto do Supabase.

    A home deles e um app JS: curl na pagina devolve so a palavra "Verita". O conteudo vem
    da tabela `pesquisas`, com a chave anonima que o proprio bundle expoe. O nome do bundle
    muda a cada deploy do site, entao ele e descoberto na hora.
    """
    req = Request(VERITA_HOME, headers={"User-Agent": UA})
    with urlopen(req, timeout=45) as r:
        home = r.read().decode("utf-8", "replace")
    m = re.search(r'src="(/assets/index-[A-Za-z0-9_-]+\.js)"', home)
    if not m:
        raise RuntimeError("nao achei o bundle JS na home do Verita")
    req = Request(VERITA_HOME.rstrip("/") + m.group(1), headers={"User-Agent": UA})
    with urlopen(req, timeout=60) as r:
        bundle = r.read().decode("utf-8", "replace")
    k = re.search(r"eyJhbGciOiJIUzI1NiI[A-Za-z0-9._-]+", bundle)
    if not k:
        raise RuntimeError("nao achei a chave anon no bundle do Verita")
    chave = k.group(0)
    req = Request(VERITA_REST, headers={"User-Agent": UA, "apikey": chave,
                                        "Authorization": "Bearer " + chave})
    with urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode("utf-8"))


# ---------------------------------------------------------------- mercados

def mercados():
    out = subprocess.run([sys.executable, os.path.join(RAIZ, "mercados.py")],
                         capture_output=True, text=True, timeout=300)
    if out.returncode != 0:
        raise RuntimeError((out.stderr or out.stdout or "").strip()[:300])
    return json.loads(out.stdout)


# ---------------------------------------------------------------- painel

def patch_painel(html, pm, kal, carimbo, data_cotacao):
    """Troca so os quatro campos mecanicos. Qualquer um que nao case e erro, nao silencio."""
    trocas = []

    def sub1(padrao, novo, rotulo, texto):
        novo_texto, n = re.subn(padrao, novo, texto, count=1)
        if n != 1:
            raise RuntimeError(f"nao consegui localizar {rotulo} no painel")
        trocas.append(rotulo)
        return novo_texto

    html = sub1(r"Última atualização: \d{2}/\d{2}/\d{4} \d{2}:\d{2}",
                "Última atualização: " + carimbo, "carimbo", html)
    if pm and kal:
        html = sub1(r"var PM=\['[^']*','[^']*'\];",
                    "var PM=['%s','%s'];" % (pm[0], pm[1]), "PM", html)
        html = sub1(r"var KAL=\['[^']*','[^']*'\];",
                    "var KAL=['%s','%s'];" % (kal[0], kal[1]), "KAL", html)
        html = sub1(r"cotação de \d{1,2}/\d{1,2}/\d{4}",
                    "cotação de " + data_cotacao, "data da cotação", html)
    return html, trocas


def valida_js(caminho):
    """Mesma checagem do deploy e do workflow: painel com JS quebrado nao vai ao ar."""
    js = ("const s=require('fs').readFileSync(process.argv[1],'utf8');"
          "const m=s.match(/<script>([\\s\\S]*)<\\/script>/);"
          "if(!m){console.error('sem <script> inline');process.exit(1);}"
          "try{new Function(m[1]);}catch(e){console.error(e.message);process.exit(1);}")
    out = subprocess.run(["node", "-e", js, caminho], capture_output=True, text=True)
    return out.returncode == 0, (out.stderr or "").strip()


# ---------------------------------------------------------------- relatorio

def escreve_pendencias(itens, novos_tse, verita, novos_verita, nota_mercados, carimbo):
    L = []
    L.append("# Pendências do agregador")
    L.append("")
    L.append("Gerado pela rotina de 6 em 6 horas (`rotina_6h.py`, GitHub Actions). "
             "Não editar à mão: cada rodada reescreve o arquivo inteiro.")
    L.append("")
    L.append(f"Rodada de {carimbo}. Mercados: {nota_mercados}.")
    L.append("")

    L.append("## Precisa de olho humano nesta rodada")
    L.append("")
    if not novos_tse and not novos_verita:
        L.append("Nada novo. O TSE não registrou divulgação que a rotina ainda não tivesse "
                 "visto, e o Veritá não publicou relatório novo.")
    else:
        for it in novos_tse:
            L.append("- NOVO no TSE: %s, %s (%s), campo %s, divulgação %s, N=%s, registro %s"
                     % (it["escopo"], it["inst"], it["cargo"], it["campo"],
                        it["div"], it["n"], it["proto"]))
        for v in novos_verita:
            L.append("- NOVO no Veritá: %s. %s PDF: %s"
                     % (v.get("titulo", "?"), (v.get("descricao") or "").strip(),
                        v.get("pdf_url", "?")))
    L.append("")

    L.append("## Últimas publicações do Veritá")
    L.append("")
    if verita is None:
        L.append("Não consegui ler a lista do Veritá nesta rodada.")
    else:
        for v in verita[:8]:
            quando = (v.get("created_at") or "")[:10]
            L.append("- %s | %s" % (quando, v.get("titulo", "?")))
    L.append("")

    L.append(f"## Divulgações registradas no TSE nos últimos {DIAS_JANELA} dias")
    L.append("")
    L.append("Estar aqui significa que a data de divulgação já venceu, não que o número "
             "exista publicado. Instituto que registra e não publica é caso conhecido.")
    L.append("")
    L.append("| divulgação | escopo | instituto | cargo | campo | N | registro |")
    L.append("| --- | --- | --- | --- | --- | --- | --- |")
    for it in itens:
        L.append("| %s | %s | %s | %s | %s | %s | %s |"
                 % (it["div"], it["escopo"], it["inst"], it["cargo"],
                    it["campo"], it["n"], it["proto"]))
    L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------- main

def main():
    args = set(sys.argv[1:])
    dry = "--dry-run" in args
    semear = "--semear" in args
    sem_mercados = "--sem-mercados" in args or semear

    estado = ler_estado()
    vistos_tse = set(estado.get("tse_vistos", []))
    vistos_ver = set(estado.get("verita_vistos", []))
    resumo = []

    # 1. TSE
    try:
        itens = radar_tse()
    except Exception as e:
        print("radar do TSE falhou:", e)
        itens = []
    novos_tse = [] if semear else [i for i in itens if i["proto"] not in vistos_tse]
    if vistos_tse or semear:
        resumo.append(f"TSE: {len(itens)} divulgações na janela, {len(novos_tse)} novas")
    else:
        # primeira rodada de verdade sem estado: tudo pareceria novo, o que e ruido
        novos_tse = []
        resumo.append(f"TSE: {len(itens)} divulgações na janela (primeira rodada, nada marcado como novo)")

    # 2. Verita
    try:
        verita = radar_verita()
    except Exception as e:
        print("radar do Veritá falhou:", e)
        verita = None
    novos_ver = []
    if verita is not None and not semear and vistos_ver:
        novos_ver = [v for v in verita if v.get("id") not in vistos_ver]
    if verita is not None:
        resumo.append(f"Veritá: {len(verita)} publicações lidas, {len(novos_ver)} novas")

    # 3. mercados
    pm = kal = None
    nota_mercados = "pulados nesta rodada"
    if not sem_mercados:
        try:
            m = mercados()
            pm, kal = m["PM"], m["KAL"]
            nota_mercados = "Polymarket %s/%s, Kalshi %s/%s" % (pm[0], pm[1], kal[0], kal[1])
        except Exception as e:
            nota_mercados = "falharam, valores antigos mantidos (%s)" % str(e)[:120]
        resumo.append("Mercados: " + nota_mercados)

    # 4. painel
    ts = agora()
    carimbo = ts.strftime("%d/%m/%Y %H:%M")
    data_cot = "%d/%d/%d" % (ts.day, ts.month, ts.year)
    if not semear:
        with open(PAINEL, encoding="utf-8") as fh:
            html = fh.read()
        try:
            novo, trocas = patch_painel(html, pm, kal, carimbo, data_cot)
        except RuntimeError as e:
            print("ERRO ao editar o painel:", e)
            return 1
        if dry:
            print("dry-run, trocaria:", ", ".join(trocas))
        else:
            with open(PAINEL, "w", encoding="utf-8") as fh:
                fh.write(novo)
            ok, err = valida_js(PAINEL)
            if not ok:
                with open(PAINEL, "w", encoding="utf-8") as fh:
                    fh.write(html)  # desfaz: painel quebrado nao fica no disco
                print("ERRO: JS quebrou depois da edição, revertido.", err)
                return 1
            resumo.append("Painel: " + ", ".join(trocas))

        texto = escreve_pendencias(itens, novos_tse, verita, novos_ver, nota_mercados, carimbo)
        if not dry:
            with open(PENDENCIAS, "w", encoding="utf-8") as fh:
                fh.write(texto + "\n")

    # 5. estado
    if not dry:
        estado["tse_vistos"] = sorted({i["proto"] for i in itens} | vistos_tse)
        if verita is not None:
            estado["verita_vistos"] = sorted({v["id"] for v in verita} | vistos_ver)
        estado["ultima_rodada"] = ts.isoformat()
        with open(ESTADO, "w", encoding="utf-8") as fh:
            json.dump(estado, fh, ensure_ascii=False, indent=1)

    for linha in resumo:
        print(linha)
    tem_novidade = bool(novos_tse or novos_ver)
    print("NOVIDADE: sim" if tem_novidade else "NOVIDADE: nao")

    # Deixa o veredito no resumo do Actions, para dar para ver sem abrir o log.
    sumario = os.environ.get("GITHUB_STEP_SUMMARY")
    if sumario:
        with open(sumario, "a", encoding="utf-8") as fh:
            fh.write("## Rotina de 6h, %s\n\n" % carimbo)
            for linha in resumo:
                fh.write("- %s\n" % linha)
            fh.write("\n**%s**\n\n" % ("Tem coisa nova para a rodada local olhar"
                                       if tem_novidade else "Nada novo"))
            for it in novos_tse:
                fh.write("- TSE %s %s %s (div %s)\n" % (it["escopo"], it["inst"],
                                                        it["campo"], it["div"]))
            for v in novos_ver:
                fh.write("- Veritá %s\n" % v.get("titulo", "?"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

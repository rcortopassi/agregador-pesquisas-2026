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
# Quanto tempo um item fica na fila sem ser resolvido antes de sair sozinho. Existe por causa
# do instituto que registra e nunca publica (caso JOTA): sem isso a fila so cresce. A saida e
# ANUNCIADA no PENDENCIAS, nunca silenciosa.
DIAS_EXPIRA = 21


def agora():
    return datetime.now(TZ) if TZ else datetime.now()


def ler_estado():
    vazio = {"tse_vistos": [], "verita_vistos": [], "pendentes": [],
             "verita_pendentes": [], "ultima_rodada": None}
    if os.path.exists(ESTADO):
        with open(ESTADO, encoding="utf-8") as fh:
            estado = json.load(fh)
        for k, v in vazio.items():
            estado.setdefault(k, v)
        return estado
    return vazio


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

def escreve_pendencias(itens, pendentes, novos_agora, verita, ver_pendentes, ver_novos,
                       expirados, nota_mercados, carimbo):
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
    if not pendentes and not ver_pendentes:
        L.append("Nada pendente. Tudo que o TSE registrou e o Veritá publicou já foi "
                 "olhado por uma rodada local e baixado da fila.")
    else:
        L.append("A fila abaixo NÃO se esvazia sozinha. Cada item fica aqui, rodada após "
                 "rodada, até uma rodada local resolvê-lo com "
                 "`python3 rotina_6h.py --resolver PROTOCOLO`. Resolver quer dizer as duas "
                 "coisas: inserido no painel, ou verificado que o instituto não publicou "
                 "número. Marque também o que descartar, senão volta amanhã.")
        L.append("")
        for it in pendentes:
            marca = "NOVO" if it["proto"] in novos_agora else "aguardando desde %s" % it["visto"]
            L.append("- [%s] TSE %s, %s (%s), campo %s, divulgação %s, N=%s, registro %s"
                     % (marca, it["escopo"], it["inst"], it["cargo"], it["campo"],
                        it["div"], it["n"], it["proto"]))
        for v in ver_pendentes:
            marca = "NOVO" if v.get("id") in ver_novos else "aguardando desde %s" % v.get("visto", "?")
            L.append("- [%s] Veritá: %s. %s PDF: %s"
                     % (marca, v.get("titulo", "?"), (v.get("descricao") or "").strip(),
                        v.get("pdf_url", "?")))
    if expirados:
        L.append("")
        L.append("Saíram da fila por idade nesta rodada (mais de %d dias sem serem "
                 "resolvidos, provavelmente instituto que registrou e nunca publicou): %s."
                 % (DIAS_EXPIRA, ", ".join(expirados)))
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

def resolver(estado, alvos):
    """Tira da fila o que uma rodada local ja tratou. Nao mexe em `tse_vistos`.

    Aceita protocolo do TSE, id do Verita ou `--resolver tudo`. Quem chama e a rodada local,
    depois de inserir no painel OU de confirmar que o instituto nao publicou numero.
    """
    fila = estado.get("pendentes", [])
    vfila = estado.get("verita_pendentes", [])
    if "tudo" in alvos:
        estado["pendentes"], estado["verita_pendentes"] = [], []
        return [i["proto"] for i in fila] + [str(v.get("id")) for v in vfila]
    baixados = [i["proto"] for i in fila if i["proto"] in alvos]
    baixados += [str(v.get("id")) for v in vfila if str(v.get("id")) in alvos]
    estado["pendentes"] = [i for i in fila if i["proto"] not in alvos]
    estado["verita_pendentes"] = [v for v in vfila if str(v.get("id")) not in alvos]
    return baixados


def main():
    argv = sys.argv[1:]
    args = set(argv)
    dry = "--dry-run" in args
    semear = "--semear" in args
    sem_mercados = "--sem-mercados" in args or semear

    estado = ler_estado()

    # --resolver: so mexe na fila e sai. Nao carimba, nao le mercado, nao toca no painel,
    # para a rodada local poder fechar item sem gerar uma rodada mecanica por tabela.
    if "--resolver" in argv:
        i = argv.index("--resolver")
        alvos = set()
        for a in argv[i + 1:]:
            if a.startswith("--"):
                break
            alvos.update(x.strip() for x in a.split(",") if x.strip())
        if not alvos:
            print("uso: rotina_6h.py --resolver BR012342026[,BR056782026 | tudo]")
            return 1
        baixados = resolver(estado, alvos)
        nao_achei = alvos - set(baixados) - {"tudo"}
        if not dry:
            with open(ESTADO, "w", encoding="utf-8") as fh:
                json.dump(estado, fh, ensure_ascii=False, indent=1)
        print("resolvidos (%d): %s" % (len(baixados), ", ".join(baixados) or "nenhum"))
        if nao_achei:
            print("não estavam na fila: %s" % ", ".join(sorted(nao_achei)))
        print("restam na fila: %d TSE, %d Veritá"
              % (len(estado["pendentes"]), len(estado["verita_pendentes"])))
        return 0

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

    # 2b. FILA. O que e novo entra; o que ja estava CONTINUA, ate `--resolver` tirar.
    #
    # Por que isto existe (10/08/2026): antes, `novos_tse` era o diff de UMA rodada e o
    # estado era marcado como visto na mesma hora. Como o ZIP do TSE e regerado uma vez por
    # dia, de madrugada, toda novidade caia na primeira rodada do dia (~02h40) e era apagada
    # pela seguinte (~08h17), enquanto a rodada local le 07h30/13h30/19h30. Resultado medido:
    # em 10/08 as tres nacionais do dia (Nexus/BTG, Palver e GERP) foram sinalizadas as 02h40
    # e o arquivo ja dizia "nada novo" as 08h17. O painel ficou tres dias sem dado novo sem
    # que ninguem tivesse decidido isso.
    hoje = agora().date()
    fila = list(estado.get("pendentes", []))
    ja_na_fila = {i["proto"] for i in fila}
    novos_agora = {i["proto"] for i in novos_tse}
    for it in novos_tse:
        if it["proto"] not in ja_na_fila:
            fila.append(dict(it, visto=hoje.isoformat()))

    def velho(it):
        try:
            d = datetime.strptime(it.get("visto", ""), "%Y-%m-%d").date()
        except ValueError:
            return False
        return (hoje - d).days > DIAS_EXPIRA

    expirados = [i["proto"] for i in fila if velho(i)]
    fila = [i for i in fila if not velho(i)]
    fila.sort(key=lambda x: (x["div"], x["escopo"]))

    vfila = list(estado.get("verita_pendentes", []))
    ja_ver = {v.get("id") for v in vfila}
    ver_novos = {v.get("id") for v in novos_ver}
    for v in novos_ver:
        if v.get("id") not in ja_ver:
            vfila.append(dict(v, visto=hoje.isoformat()))

    resumo.append("Fila: %d pendentes no TSE (%d entraram agora), %d no Veritá"
                  % (len(fila), len(novos_agora - ja_na_fila), len(vfila)))
    if expirados:
        resumo.append("Saíram por idade (>%d dias): %s" % (DIAS_EXPIRA, ", ".join(expirados)))

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

        texto = escreve_pendencias(itens, fila, novos_agora, verita, vfila, ver_novos,
                                   expirados, nota_mercados, carimbo)
        if not dry:
            with open(PENDENCIAS, "w", encoding="utf-8") as fh:
                fh.write(texto + "\n")

    # 5. estado
    if not dry:
        # `tse_vistos` responde "ja passei os olhos nisto" e evita reanunciar como NOVO.
        # `pendentes` responde "ainda falta alguem tratar", e SO sai com --resolver. Sao
        # perguntas diferentes: era confundir as duas que fazia o aviso evaporar.
        estado["tse_vistos"] = sorted({i["proto"] for i in itens} | vistos_tse)
        if verita is not None:
            estado["verita_vistos"] = sorted({v["id"] for v in verita} | vistos_ver)
        estado["pendentes"] = fila
        estado["verita_pendentes"] = vfila
        estado["ultima_rodada"] = ts.isoformat()
        with open(ESTADO, "w", encoding="utf-8") as fh:
            json.dump(estado, fh, ensure_ascii=False, indent=1)

    for linha in resumo:
        print(linha)
    # O veredito e a FILA, nao o diff desta rodada. Uma rodada que nao descobriu nada mas
    # tem item esperando ha dois dias continua tendo trabalho para a rodada local.
    tem_novidade = bool(fila or vfila)
    print("NOVIDADE: sim" if tem_novidade else "NOVIDADE: nao")

    # Deixa o veredito no resumo do Actions, para dar para ver sem abrir o log.
    sumario = os.environ.get("GITHUB_STEP_SUMMARY")
    if sumario:
        with open(sumario, "a", encoding="utf-8") as fh:
            fh.write("## Rotina de 6h, %s\n\n" % carimbo)
            for linha in resumo:
                fh.write("- %s\n" % linha)
            fh.write("\n**%s**\n\n" % ("Tem coisa na fila para a rodada local olhar"
                                       if tem_novidade else "Fila vazia"))
            for it in fila:
                fh.write("- TSE %s %s %s (div %s)%s\n"
                         % (it["escopo"], it["inst"], it["campo"], it["div"],
                            "" if it["proto"] in novos_agora else " [aguardando]"))
            for v in vfila:
                fh.write("- Veritá %s\n" % v.get("titulo", "?"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

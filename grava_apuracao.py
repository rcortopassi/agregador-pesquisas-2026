"""Grava a apuração nacional do TSE minuto a minuto e publica a série no PythonAnywhere.

Uso: nohup python3 grava_apuracao.py > grava_apuracao.log 2>&1 &
Para sozinho quando o TSE chega a 100% das seções. Sem Claude no meio: não gasta token.
"""
import base64, json, os, sys, time, urllib.request
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deploy_agregador as dep

COD = sys.argv[1] if len(sys.argv) > 1 else "6257"
URL = f"https://resultados.tse.jus.br/oficial/ele2026/{COD}/dados/br/br-c0001-e{int(COD):06d}-u.jws"
NOME = f"apuracao_serie_{COD}.json"
OUT = Path(__file__).resolve().parent / NOME
ENVIO_S = 300

cfg = dep.ler_env()
TOKEN = cfg.get("PA_TOKEN")
USER = cfg.get("PA_USER") or cfg.get("PAINEL_URL", "").split("//")[-1].split("/")[0].split(".")[0]


def num(s):
    return float(str(s).replace(".", "").replace(",", "."))


def le():
    t = urllib.request.urlopen(URL + "?nocache=%d" % time.time(), timeout=30).read().decode()
    p = t.split(".")[1]
    j = json.loads(base64.urlsafe_b64decode(p + "=" * (-len(p) % 4)))
    c = {}
    for cg in j["carg"]:
        if str(cg.get("cd")) != "1":
            continue
        for a in cg.get("agr", []):
            for pa in a.get("par", []):
                for k in pa.get("cand", []):
                    c[(k.get("nmu") or k["nm"]).upper()] = num(k["pvap"])
    lula = next((v for n, v in c.items() if "LULA" in n), None)
    flav = next((v for n, v in c.items() if "FLAVIO" in n or "FLÁVIO" in n), None)
    return {"hg": j["hg"], "dg": j["dg"], "pst": num(j["s"]["pst"]), "lula": lula, "flavio": flav}


def envia():
    try:
        code, dest = dep.upload(USER, TOKEN, OUT, NOME)
        print("enviado", code, dest, flush=True)
    except Exception as e:
        print("erro envio", e, flush=True)


serie = json.loads(OUT.read_text()) if OUT.exists() else []
ultimo_envio = 0
while True:
    fim = False
    try:
        pt = le()
        if pt["lula"] is not None and (not serie or serie[-1]["hg"] != pt["hg"]):
            serie.append(pt)
            OUT.write_text(json.dumps(serie, ensure_ascii=False))
            print(pt, flush=True)
        fim = pt["pst"] >= 100
    except Exception as e:
        print("erro leitura", e, flush=True)
    if fim or time.time() - ultimo_envio >= ENVIO_S:
        envia()
        ultimo_envio = time.time()
    if fim:
        print("100% das seções: fim", flush=True)
        break
    time.sleep(60)

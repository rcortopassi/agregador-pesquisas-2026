"""Inclui o 1º turno de 2026 na base histórica de erro das pesquisas (rodado em 05/10/2026).

Entradas: ../resultado_2026/DI_2026.json (o DI do painel, uma rodada por instituto por mês)
          ../resultado_2026/presidente_1t_6257.json (urna final do TSE, 100% das seções)
Saídas:   pesquisas_1t_2010_2022.json e serie_mensal_1t.json ganham a chave '2026'
          ../resultado_2026/historico_2026.json com os blocos prontos para o painel.

Mesma régua da reconstrução de 2010-2022 (LEIAME.md): votos válidos com denominador só de
candidatos, que no DI é 100 menos Br/N/Ind; mediana por mês; margem = esquerda menos direita.
Linhas sem Br/N/Ind, sem Flávio, ou com valor estimado (*) ou de outro cenário (†) ficam fora.
"""
import json, statistics as st
from pathlib import Path

AQUI = Path(__file__).resolve().parent
R26 = AQUI.parent / "resultado_2026"
MESES = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out']
# Finais: última rodada com campo encerrado a partir de 25/9 (10 dias antes da urna).
FINAIS_SET = {'Apex/Futura', 'Nexus/BTG', 'Meio/Ideia', 'Indexa', 'RTBD'}

tse = json.load(open(R26 / "presidente_1t_6257.json"))["br"]["cand"]
U_E = next(c["pvap"] for c in tse if c["nm"] == "LULA")
U_D = next(c["pvap"] for c in tse if "FLAVIO" in c["nm"])
URNA_M, URNA_T = round(U_E - U_D, 2), round(U_E + U_D, 2)


def num(x):
    x = str(x)
    if x in ("—", "") or "*" in x or "†" in x:
        return None
    return float(x.replace(",", "."))


DI = json.load(open(R26 / "DI_2026.json"))
recs, fora = [], []
for mi, m in enumerate(MESES, 1):
    for r in DI.get(m, {}).get("rows", []):
        e, d, bni = num(r[1]), num(r[2]), num(r[6])
        if e is None or d is None or bni is None:
            fora.append(f"{m} {r[0]}")
            continue
        den = round(100 - bni, 1)
        recs.append({"dia": 0, "mes": mi, "inst": r[0], "e_bruto": e, "d_bruto": d, "den": den,
                     "e_val": round(e / den * 100, 2), "d_val": round(d / den * 100, 2),
                     "marg_val": round((e - d) / den * 100, 2), "marg_bruta": round(e - d, 2)})

base = json.load(open(AQUI / "pesquisas_1t_2010_2022.json"))
base["2026"] = recs
json.dump(base, open(AQUI / "pesquisas_1t_2010_2022.json", "w"), ensure_ascii=False)

meses = {}
for mi in range(1, 11):
    g = [r for r in recs if r["mes"] == mi]
    if not g:
        continue
    meses[str(mi)] = {"marg": round(st.median(r["marg_val"] for r in g), 2),
                      "top2": round(st.median(r["e_val"] + r["d_val"] for r in g), 2),
                      "den": round(st.median(r["den"] for r in g), 1),
                      "ninst": len(g), "npesq": len(g)}
serie = json.load(open(AQUI / "serie_mensal_1t.json"))
serie["2026"] = {"urna_m": URNA_M, "urna_top2": URNA_T, "meses": meses}
json.dump(serie, open(AQUI / "serie_mensal_1t.json", "w"), ensure_ascii=False, indent=1)

# Erro final por instituto (VH1DET): dir = urna - pesquisa no candidato de direita
# (positivo = subestimou a direita); esq = pesquisa - urna no candidato do PT.
finais = {}
for r in recs:
    if r["mes"] == 10 or (r["mes"] == 9 and r["inst"] in FINAIS_SET):
        if r["inst"] not in finais or r["mes"] > finais[r["inst"]]["mes"]:
            finais[r["inst"]] = r
vh1 = {k: {"dir": round(U_D - r["d_val"], 2), "esq": round(r["e_val"] - U_E, 2), "mes": r["mes"]}
       for k, r in sorted(finais.items())}

# Erro da margem por instituto e mês (camada 2026 do HERRINST); erro da mediana do campo (HERRN).
herrinst = {}
for r in recs:
    herrinst.setdefault(r["inst"], {})[r["mes"]] = round(r["marg_val"] - URNA_M, 1)
herrn = {MESES[int(k) - 1]: round(v["marg"] - URNA_M, 1) for k, v in meses.items()}

json.dump({"urna": {"e": U_E, "d": U_D, "m": URNA_M, "t": URNA_T}, "fora": fora, "vh1": vh1,
           "herrinst": herrinst, "herrn": herrn, "hist1t": meses},
          open(R26 / "historico_2026.json", "w"), ensure_ascii=False, indent=1)
print("urna", U_E, U_D, URNA_M, URNA_T, "| pesquisas", len(recs), "| fora", fora)
print("finais", json.dumps(vh1, ensure_ascii=False))
print("herrn", herrn)
print("hist1t", {k: (v["marg"], v["top2"], v["ninst"]) for k, v in meses.items()})

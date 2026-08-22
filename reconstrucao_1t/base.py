import sys,re,json,statistics as st
sys.path.insert(0,'/tmp/recon')
from extrai import (linhas,completa,cabec,dia_mes,ano,n2,inst,norm)
import wiki

URNA={  # 1o turno, votos validos, TSE
 '2010':{'e':46.91,'d':32.61,'par':'Dilma x Serra','pres_esq':'Dilma'},
 '2014':{'e':41.59,'d':33.55,'par':'Dilma x Aécio','pres_esq':'Dilma'},
 '2018':{'e':29.28,'d':46.03,'par':'Haddad x Bolsonaro','pres_esq':'Haddad'},
 '2022':{'e':48.43,'d':43.20,'par':'Lula x Bolsonaro','pres_esq':'Lula'},
}

def colher(titulo,corte,ano_alvo,rot_e,rot_d,off,ncols,i_data,i_inst,den,exige=None,fatia=None):
    wt=wiki.wikitext(titulo)
    if fatia:
        a=wt.find(fatia[0]); b=wt.find(fatia[1])
        wt=wt[a:b if b>a else len(wt)]
    else:
        i=wt.find(corte); wt=wt[:i] if i>0 else wt
    recs=[]
    for tb in re.findall(r'\{\|.*?\n\|\}', wt, re.S):
        rs=completa(linhas(tb),ncols,off)
        if len(rs)<5: continue
        h=cabec(tb); ie=id_=None
        for k,x in enumerate(h):
            if ie is None and any(r.lower()==x.lower() or r.lower() in x.lower() for r in rot_e): ie=k
            if id_ is None and any(r.lower()==x.lower() or r.lower() in x.lower() for r in rot_d): id_=k
        if ie is None or id_ is None: continue
        b=min(ie,id_); ce=off+(ie-b); cd=off+(id_-b)
        for r in rs:
            if len(r)<ncols or ce>=len(r) or cd>=len(r): continue
            t=wiki.limpa(r[i_data]); a=ano(t)
            if a is not None and a!=ano_alvo: continue
            dm=dia_mes(t)
            if not dm: continue
            if exige and exige.lower() not in r[ce].lower(): continue
            e=n2(r[ce]); d=n2(r[cd])
            if e is None or d is None: continue
            lo,hi=den
            soma=sum(v for v in (n2(r[k]) for k in range(lo,min(hi,len(r)))) if v is not None and v<=100)
            if soma<40 or soma>135: continue
            recs.append({'dia':dm[0],'mes':dm[1],'inst':norm(inst(r[i_inst])),
                         'e_bruto':e,'d_bruto':d,'den':round(soma,1),
                         'e_val':round(e/soma*100,2),'d_val':round(d/soma*100,2),
                         'marg_val':round((e-d)/soma*100,2),'marg_bruta':round(e-d,2)})
    return recs

CFG={
 '2010':dict(titulo='Pesquisas de opinião para a eleição presidencial no Brasil em 2010',
             corte='== Ligações',ano_alvo=2010,rot_e=['Dilma'],rot_d=['Serra'],off=2,ncols=8,i_data=0,i_inst=1,den=(2,7)),
 '2014':dict(titulo='Predefinição:Pesquisas de opinião da Eleição presidencial no Brasil em 2014 (1º turno)',
             corte='ZZZ',ano_alvo=2014,rot_e=['Dilma'],rot_d=['Aécio'],off=3,ncols=14,i_data=0,i_inst=1,den=(3,14)),
 '2018':dict(titulo='Pesquisas de opinião para a eleição presidencial no Brasil em 2018',
             corte='== Segundo turno',ano_alvo=2018,rot_e=['Partido dos Trabalhadores','PT'],
             rot_d=['Partido Social Liberal','PSL'],off=4,ncols=15,i_data=0,i_inst=1,den=(4,14),exige='Haddad'),
 '2022':dict(titulo='Pesquisas de opinião para a eleição presidencial no Brasil em 2022',
             corte='== Segundo turno',ano_alvo=2022,rot_e=['Lula'],rot_d=['Bolsonaro'],
             off=4,ncols=18,i_data=1,i_inst=0,den=(4,17),fatia=('=== 2022 ===','=== 2021 ===')),
}

def carrega():
    pool={}
    for k,cfg in CFG.items():
        rs=colher(**cfg)
        rs=[r for r in rs if not re.fullmatch(r'\d{4}',r['inst'])]
        pool[k]=rs
    return pool

def por_inst_mes(rs):
    """regra do painel: 1 rodada por instituto por mes, a mais recente"""
    out={}
    for r in rs:
        k=(r['mes'],r['inst'])
        if k not in out or r['dia']>out[k]['dia']: out[k]=r
    d={}
    for (m,_),r in out.items(): d.setdefault(m,[]).append(r)
    return d

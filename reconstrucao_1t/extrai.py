import sys,re,json,statistics as st
sys.path.insert(0,'/tmp/recon')
import wiki

MES={'jan':1,'fev':2,'mar':3,'abr':4,'mai':5,'jun':6,'jul':7,'ago':8,'set':9,'out':10,'nov':11,'dez':12}
def dia_mes(txt):
    t=txt.replace('&nbsp;',' ').replace('–','-').replace('—','-')
    par=None
    for d,nome in re.findall(r'(\d{1,2})\s*(?:de\s+|a\s+)?([A-Za-zçÇéê]{3,})',t):
        k=nome[:3].lower().replace('ç','c')
        if k in MES: par=(int(d),MES[k])
    return par

def ano(t):
    m=re.findall(r'\b(19|20)(\d{2})\b',t)
    return int(m[-1][0]+m[-1][1]) if m else None

def n2(c): return wiki.num(c.split('|')[-1])

def inst(cell):
    c=re.sub(r'<ref[^>]*>.*?</ref>','',cell,flags=re.S)
    c=re.sub(r'<ref[^>]*/>','',c)
    c=re.sub(r'\[https?://\S+\s*([^\]]*)\]',r'\1',c)
    c=re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]',r'\2',c)
    c=re.sub(r'\[\[([^\]]+)\]\]',r'\1',c)
    c=re.sub(r'\{\{[^}]*\}\}','',c)
    c=re.sub(r'<[^>]+>',' ',c)
    c=re.sub(r'rowspan=\S+','',c)
    c=re.sub(r'BR[-–]?\d{5}/\d{4}','',c)
    c=re.sub(r'\s+',' ',c).strip(' ,;|')
    if '/' in c: c=c.split('/')[-1]
    return c.strip()[:28]

NORM=[('datafolha','Datafolha'),('ipec','Ipec'),('ibope','Ibope'),('vox populi','Vox Populi'),
 ('sensus','Sensus'),('ipespe','Ipespe'),('paran','Paraná'),('quaest','Quaest'),
 ('atlas','AtlasIntel'),('mda','CNT/MDA'),('poder360','DataPoder360'),('poderdata','PoderData'),
 ('futura','Futura'),('ideia','Meio/Ideia'),('real time','RTBD'),('big data','RTBD'),
 ('gerp','Gerp'),('verit','Veritá'),('modalmais','Modalmais'),('fsb','FSB'),
 ('genial','Quaest'),('xp','XP/Ipespe'),('nexus','Nexus'),('opini','Opinião'),
 ('brasmarket','Brasmarket'),('brasilis','Brasilis'),('exame','Exame/Ideia')]
def norm(x):
    l=x.lower()
    for k,v in NORM:
        if k in l: return v
    return x

def linhas(tb):
    rows,cur,cell=[],None,None
    def fecha(cur,cell):
        if cell is not None: cur.append(cell)
        saida=[]
        for c in cur: saida.extend(c.split('||'))
        return saida
    for l in tb.split('\n'):
        if l.startswith('|-'):
            if cur is not None:
                r=fecha(cur,cell)
                if len(r)>3: rows.append(r)
            cur,cell=[],None; continue
        if cur is None or l.startswith('|}'): continue
        if l.startswith('!'): continue
        if l.startswith('|'):
            if cell is not None: cur.append(cell)
            cell=l[1:]
        elif cell is not None: cell+='\n'+l
    if cur is not None:
        r=fecha(cur,cell)
        if len(r)>3: rows.append(r)
    return rows

def completa(rows,ncols,nlead):
    saida,ult=[],None
    for r in rows:
        if len(r)>=ncols:
            ult=r; saida.append(r)
        elif ult is not None and len(r)+nlead>=ncols:
            saida.append(ult[:nlead]+r)
        else:
            saida.append(r)
    return saida

def cabec(tb):
    out=[]
    for l in tb.split('\n'):
        if not l.startswith('!'): continue
        for p in re.split(r'!!', l.lstrip('!')):
            m=re.search(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]',p)
            if m: out.append((m.group(2) or m.group(1)).strip())
            else:
                t=wiki.limpa(re.sub(r'^[^|]*\|','',p))
                if t and len(t)<40: out.append(t)
    return out

def extrai(titulo,corte,ano_alvo,rot_e,rot_d,off,ncols,i_data,i_inst,exige=None):
    wt=wiki.wikitext(titulo)
    i=wt.find(corte); i=i if i>0 else len(wt)
    recs=[]; desc=0
    for tb in re.findall(r'\{\|.*?\n\|\}', wt[:i], re.S):
        rs=completa(linhas(tb),ncols,off)
        if len(rs)<5: continue
        h=cabec(tb); ie=id_=None
        for k,x in enumerate(h):
            if ie is None and any(r.lower() in x.lower() for r in rot_e): ie=k
            if id_ is None and any(r.lower() in x.lower() for r in rot_d): id_=k
        if ie is None or id_ is None: continue
        b=min(ie,id_); ce=off+(ie-b); cd=off+(id_-b)
        for r in rs:
            if len(r)<ncols: desc+=1; continue
            t=wiki.limpa(r[i_data]); a=ano(t)
            if a is not None and a!=ano_alvo: continue
            dm=dia_mes(t)
            if not dm or ce>=len(r) or cd>=len(r): desc+=1; continue
            if exige and exige.lower() not in r[ce].lower(): continue
            e=n2(r[ce]); d=n2(r[cd])
            if e is None or d is None: desc+=1; continue
            tot=sum(v for v in (n2(r[k]) for k in range(off,len(r))) if v is not None and v<=100)
            if tot<40 or tot>135: desc+=1; continue
            recs.append({'dia':dm[0],'mes':dm[1],'inst':norm(inst(r[i_inst])),
                         'marg':round((e-d)/tot*100,2)})
    return recs,desc

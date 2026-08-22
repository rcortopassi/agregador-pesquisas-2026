import json,re,urllib.request,urllib.parse,os
UA={"User-Agent":"agregador-pesquisas/1.0 (rafael@dfcarvalho.com.br)"}
def wikitext(title):
    f='/tmp/recon/'+re.sub(r'\W+','_',title)[:80]+'.wt'
    if os.path.exists(f): return open(f,encoding='utf-8').read()
    q=urllib.parse.urlencode({'action':'query','prop':'revisions','rvprop':'content',
        'rvslots':'main','format':'json','titles':title})
    r=urllib.request.Request('https://pt.wikipedia.org/w/api.php?'+q,headers=UA)
    d=json.load(urllib.request.urlopen(r,timeout=90))
    pg=list(d['query']['pages'].values())[0]
    if 'revisions' not in pg: return ''
    t=pg['revisions'][0]['slots']['main']['*']
    open(f,'w',encoding='utf-8').write(t)
    return t

MES={'jan':1,'fev':2,'mar':3,'abr':4,'mai':5,'jun':6,'jul':7,'ago':8,'set':9,'out':10,'nov':11,'dez':12}
def mes_fim(txt):
    """Mes do FIM do campo. 'ual30 Set-01 Out' -> 10."""
    t=txt.replace('&nbsp;',' ').replace('–','-').replace('—','-')
    achados=re.findall(r'(\d{1,2})\s*(?:de\s+)?([A-Za-zçÇ]{3,})',t)
    m=None
    for _dia,nome in achados:
        k=nome[:3].lower().replace('ç','c')
        k={'set':'set','out':'out','ago':'ago','jul':'jul','jun':'jun','mai':'mai',
           'abr':'abr','mar':'mar','fev':'fev','jan':'jan','nov':'nov','dez':'dez'}.get(k)
        if k: m=MES[k]
    return m

def limpa(c):
    c=re.sub(r'<ref[^>]*>.*?</ref>','',c,flags=re.S)
    c=re.sub(r'<ref[^>]*/>','',c)
    c=re.sub(r'\{\{small\|(.*?)\}\}',r'\1',c,flags=re.S)
    c=re.sub(r'<[^>]+>',' ',c)
    return c.strip()

def num(c):
    c=limpa(c)
    if 'n/a' in c.lower() or c in ('','-','—'): return None
    m=re.search(r'(\d{1,3}(?:[.,]\d+)?)\s*%?',c.replace("'",''))
    return float(m.group(1).replace(',','.')) if m else None

def tabelas(wt):
    """Devolve lista de (cabecalhos_candidatos, linhas_de_celulas)."""
    out=[]
    for tb in re.findall(r'\{\|.*?\n\|\}', wt, re.S):
        linhas=tb.split('\n')
        cands=[]
        for l in linhas:
            m=re.match(r'^!\s*\[\[([^\]|]+)(?:\|([^\]]+))?\]\]', l)
            if m and 'Imagem' not in l and 'Ficheiro' not in l:
                cands.append((m.group(2) or m.group(1)).strip())
        rows,cur,cell=[],None,None
        for l in linhas:
            if l.startswith('|-'):
                if cur is not None:
                    if cell is not None: cur.append(cell)
                    if len(cur)>4: rows.append(cur)
                cur,cell=[],None; continue
            if cur is None: continue
            if l.startswith('|}'): break
            if l.startswith('!'): continue
            if l.startswith('|'):
                if cell is not None: cur.append(cell)
                cell=l[1:]
            elif cell is not None:
                cell+='\n'+l
        if cur is not None:
            if cell is not None: cur.append(cell)
            if len(cur)>4: rows.append(cur)
        if cands and rows: out.append((cands,rows))
    return out

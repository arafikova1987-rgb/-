#!/usr/bin/env python3
"""Разбирает размеченный markdown проекта в JSON-дерево блоков для сборки docx."""
import re, sys, json, io

class P:
    def __init__(self, lines): self.l=lines; self.i=0
    def peek(self): return self.l[self.i] if self.i < len(self.l) else None
    def next(self): v=self.peek(); self.i+=1; return v
    def eof(self): return self.i >= len(self.l)

def parse_table(p):
    rows=[]
    while not p.eof() and p.peek().startswith('|'):
        rows.append([c.strip() for c in p.next().strip().strip('|').split('|')])
    if len(rows)>=2 and set(rows[1][0])<=set('-: '):
        head, body = rows[0], rows[2:]
    else:
        head, body = None, rows
    clean=[]
    for r in body:
        clean.append([ (c[1:] if c[:1] in '+!' else c) for c in r ])
    return {'t':'table','head':head,'rows':clean}

def parse_list(p):
    ordered=bool(re.match(r'\d+\.\s', p.peek()))
    items=[]
    while not p.eof() and re.match(r'(\d+\.|-)\s', p.peek() or ''):
        line=re.sub(r'^(\d+\.|-)\s+','',p.next())
        while not p.eof() and p.peek().startswith('  ') and p.peek().strip():
            line+=' '+p.next().strip()
        items.append(line)
    return {'t':'ol' if ordered else 'ul','items':items}

def parse_blocks(p, stop_at_fence=False):
    out=[]
    while not p.eof():
        line=p.peek()
        if stop_at_fence and line.strip()==':::': break
        if not line.strip(): p.next(); continue
        if line.startswith('|'): out.append(parse_table(p)); continue
        if re.match(r'(\d+\.|-)\s', line): out.append(parse_list(p)); continue
        if line.startswith('> '):
            buf=[]
            while not p.eof() and (p.peek() or '').startswith('> '): buf.append(p.next()[2:])
            out.append({'t':'quote','text':' '.join(buf)}); continue
        if line.startswith('#### '): p.next(); out.append({'t':'h4','text':line[5:]}); continue
        if line.startswith('### '): p.next(); out.append({'t':'h3','text':line[4:]}); continue
        if line.startswith(':::'): out.append(parse_fence(p)); continue
        if line.startswith('## '): break
        buf=[]
        while not p.eof() and (p.peek() or '').strip() and not re.match(r'^(\||#|>|-\s|\d+\.\s|:::)', p.peek()):
            buf.append(p.next().strip())
        text=' '.join(buf); lede=False
        if text.startswith('^'): lede=True; text=text[1:].strip()
        out.append({'t':'p','text':text,'lede':lede})
    return out

FOOT=('Метрика','Уточнить')
def scenario_fields(p):
    fields=[]; foot=[]
    while not p.eof() and p.peek().strip()!=':::':
        line=p.next()
        if not line.strip(): continue
        m=re.match(r'\*\*(.+?):\*\*\s*(.*)', line)
        if not m: fields.append({'label':'','kind':'text','value':line.strip()}); continue
        label, rest = m.group(1), m.group(2).strip()
        items=[]
        while not p.eof() and (p.peek() or '').startswith('- '): items.append(p.next()[2:].strip())
        key=label.split(',')[0].strip()
        if key in FOOT: foot.append({'label':label,'value':rest}); continue
        if key=='Раскадровка':
            shots=[]
            for it in items:
                parts=[x.strip() for x in it.split('|')]
                shots.append([parts[0], parts[1] if len(parts)>2 else '', parts[-1] if len(parts)>1 else ''])
            fields.append({'label':label,'kind':'shots','shots':shots}); continue
        if key=='Текст на экран':
            fields.append({'label':label,'kind':'text','value':' · '.join(c.strip() for c in rest.split(' / '))}); continue
        if items:
            fields.append({'label':label,'kind':'list','items':items}); continue
        fields.append({'label':label,'kind':'caption' if key=='Подпись' else ('hook' if key.startswith('Хук') else 'text'),'value':rest})
    return fields, foot

def parse_fence(p):
    head=p.next()[3:].strip()
    kind,_,arg=head.partition(' ')
    parts=[a.strip() for a in arg.split('|')]
    if kind=='scenario':
        num,name,meta,cover=(parts+['','','',''])[:4]
        fields,foot=scenario_fields(p); p.next()
        return {'t':'scenario','num':num,'name':name,'meta':meta,'cover':cover,'fields':fields,'foot':foot}
    if kind=='take':
        num,tm,plan,mode=(parts+['','','',''])[:4]
        rows=[]
        while not p.eof() and p.peek().strip()!=':::':
            line=p.next().strip()
            if not line: continue
            m=re.match(r'\*\*(.+?):\*\*\s*(.*)', line)
            rows.append([m.group(1),m.group(2)] if m else ['',line])
        p.next()
        return {'t':'take','num':num,'tm':tm,'plan':plan,'mode':mode,'rows':rows}
    if kind=='spec':
        items=[]
        while not p.eof() and p.peek().strip()!=':::':
            line=p.next().strip()
            if not line: continue
            a,_,b=line.partition('|'); items.append([a.strip(),b.strip()])
        p.next(); return {'t':'spec','items':items}
    if kind=='stats':
        items=[]
        while not p.eof() and p.peek().strip()!=':::':
            line=p.next().strip()
            if not line: continue
            b=[x.strip() for x in line.split('|')]; items.append((b+['',''])[:3])
        p.next(); return {'t':'stats','items':items}
    if kind=='note':
        inner=parse_blocks(p,True); p.next(); return {'t':'note','title':arg,'blocks':inner}
    if kind=='phase':
        cls,name,days=(parts+['','',''])[:3]
        inner=parse_blocks(p,True); p.next(); return {'t':'phase','name':name,'days':days,'blocks':inner}
    inner=parse_blocks(p,True); p.next(); return {'t':'group','blocks':inner}

def convert(md):
    p=P(md.split('\n'))
    doc={'title':'','eyebrow':'','stand':'','sections':[]}
    intro=[]
    while not p.eof():
        line=p.peek()
        if not line.strip(): p.next(); continue
        if line.startswith('# '): doc['title']=p.next()[2:].strip(); continue
        if line.startswith('^^ '): doc['stand']=p.next()[3:].strip(); continue
        if line.startswith('~~ '): doc['eyebrow']=p.next()[3:].strip(); continue
        if line.startswith('## '):
            head=p.next()[3:].strip(); eyebrow,_,h2=head.partition('|')
            doc['sections'].append({'label':eyebrow.strip(),'title':h2.strip(),'blocks':parse_blocks(p)})
            continue
        intro+=parse_blocks(p)
    doc['intro']=intro
    return doc

if __name__=='__main__':
    md=io.open(sys.argv[1],encoding='utf-8').read()
    io.open(sys.argv[2],'w',encoding='utf-8').write(json.dumps(convert(md),ensure_ascii=False,indent=1))
    print('json written', sys.argv[2])

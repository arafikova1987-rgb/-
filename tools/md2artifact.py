#!/usr/bin/env python3
"""Собирает HTML-страницу артефакта из размеченного markdown.

Разметка сверх обычного markdown:
  ## NN · Ярлык | Заголовок раздела
  :::note Заголовок / ... / :::         выноска
  :::stats / значение | подпись | pos|neg / :::
  :::phase p1 | Название | дни 1-30 / ... / :::
  :::scenario 01 | Название | мета | Обложка / ... / :::
Внутри сценария поля вида **Хук, 0-3 сек:** текст, а также
**Раскадровка:** со строками "- 0-3 | что в кадре".
"""
import re, sys, html, io

def esc(t):
    return html.escape(t, quote=False)

def inline(t):
    t = esc(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'`(.+?)`', r'<code>\1</code>', t)
    return t

class P:
    def __init__(self, lines):
        self.l = lines
        self.i = 0
    def peek(self):
        return self.l[self.i] if self.i < len(self.l) else None
    def next(self):
        v = self.peek(); self.i += 1; return v
    def eof(self):
        return self.i >= len(self.l)

def parse_table(p):
    rows = []
    while not p.eof() and p.peek().startswith('|'):
        rows.append([c.strip() for c in p.next().strip().strip('|').split('|')])
    if len(rows) >= 2 and set(rows[1][0]) <= set('-: '):
        head, body = rows[0], rows[2:]
    else:
        head, body = None, rows
    out = ['<div class="tw"><table>']
    if head:
        out.append('<thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in head) + '</tr></thead>')
    out.append('<tbody>')
    for r in body:
        cells = []
        for c in r:
            cls = ''
            if c.startswith('+'):
                cls, c = ' class="yes"', c[1:]
            elif c.startswith('!'):
                cls, c = ' class="no"', c[1:]
            elif re.fullmatch(r'[\d\s.,%-]+', c or 'x'):
                cls = ' class="num"'
            cells.append(f'<td{cls}>{inline(c)}</td>')
        out.append('<tr>' + ''.join(cells) + '</tr>')
    out.append('</tbody></table></div>')
    return '\n'.join(out)

def parse_list(p):
    ordered = bool(re.match(r'\d+\.\s', p.peek()))
    items = []
    while not p.eof() and re.match(r'(\d+\.|-)\s', p.peek() or ''):
        line = re.sub(r'^(\d+\.|-)\s+', '', p.next())
        while not p.eof() and p.peek().startswith('  ') and p.peek().strip():
            line += ' ' + p.next().strip()
        items.append(f'<li>{inline(line)}</li>')
    tag = 'ol' if ordered else 'ul'
    return f'<{tag}>' + ''.join(items) + f'</{tag}>'

def parse_blocks(p, stop_at_fence=False):
    out = []
    while not p.eof():
        line = p.peek()
        if line is None:
            break
        if stop_at_fence and line.strip() == ':::':
            break
        if not line.strip():
            p.next(); continue
        if line.startswith('|'):
            out.append(parse_table(p)); continue
        if re.match(r'(\d+\.|-)\s', line):
            out.append(parse_list(p)); continue
        if line.startswith('> '):
            buf = []
            while not p.eof() and (p.peek() or '').startswith('> '):
                buf.append(p.next()[2:])
            out.append('<blockquote><p>' + inline(' '.join(buf)) + '</p></blockquote>')
            continue
        if line.startswith('#### '):
            p.next(); out.append(f'<h4>{inline(line[5:])}</h4>'); continue
        if line.startswith('### '):
            p.next(); out.append(f'<h3>{inline(line[4:])}</h3>'); continue
        if line.startswith(':::'):
            out.append(parse_fence(p)); continue
        if line.startswith('## '):
            break
        buf = []
        while not p.eof() and (p.peek() or '').strip() and not re.match(r'^(\||#|>|-\s|\d+\.\s|:::)', p.peek()):
            buf.append(p.next().strip())
        cls = ''
        text = ' '.join(buf)
        if text.startswith('^'):
            cls, text = ' class="lede"', text[1:].strip()
        out.append(f'<p{cls}>{inline(text)}</p>')
    return '\n'.join(out)

SC_FOOT = ('Метрика', 'Уточнить')

def scenario_fields(p):
    fields, foot = [], []
    while not p.eof() and p.peek().strip() != ':::':
        line = p.next()
        if not line.strip():
            continue
        m = re.match(r'\*\*(.+?):\*\*\s*(.*)', line)
        if not m:
            fields.append(('_raw', line.strip()))
            continue
        label, rest = m.group(1), m.group(2).strip()
        items = []
        while not p.eof() and (p.peek() or '').startswith('- '):
            items.append(p.next()[2:].strip())
        key = label.split(',')[0].strip()
        if key.startswith('Хук'):
            fields.append(('hook', label, rest)); continue
        if key in SC_FOOT:
            foot.append((label, rest)); continue
        if key == 'Раскадровка':
            shots = []
            for it in items:
                parts = [x.strip() for x in it.split('|')]
                t = parts[0]
                mode = parts[1] if len(parts) > 2 else ''
                txt = parts[-1] if len(parts) > 1 else ''
                cls = {'синхрон': 'sync', 'закадр': 'vo', 'без слов': 'mute', 'титр': 'card'}.get(mode.lower(), 'mute')
                m = f'<span class="mode {cls}">{esc(mode)}</span>' if mode else ''
                shots.append(f'<li><span class="t">{esc(t)}</span>{m}<span class="what">{inline(txt)}</span></li>')
            fields.append(('shots', label, '<ol class="shots">' + ''.join(shots) + '</ol>')); continue
        if key == 'Текст на экран':
            chips = ''.join(f'<span class="chip">{esc(c.strip())}</span>' for c in rest.split(' / '))
            fields.append(('html', label, f'<div class="chips">{chips}</div>')); continue
        if key == 'Подпись':
            fields.append(('html', label, f'<div class="caption-box"><p>{inline(rest)}</p></div>')); continue
        if items:
            lis = ''.join(f'<li>{inline(i)}</li>' for i in items)
            fields.append(('html', label, f'<ul class="tight">{lis}</ul>')); continue
        fields.append(('text', label, rest))
    body = []
    for f in fields:
        if f[0] == '_raw':
            body.append(f'<p>{inline(f[1])}</p>')
        elif f[0] == 'hook':
            body.append(f'<div class="hook"><span class="lbl">{esc(f[1])}</span><p>{inline(f[2])}</p></div>')
        elif f[0] in ('shots', 'html'):
            body.append(f'<div class="field"><span class="lbl">{esc(f[1])}</span>{f[2]}</div>')
        else:
            body.append(f'<div class="field"><span class="lbl">{esc(f[1])}</span><p>{inline(f[2])}</p></div>')
    if foot:
        cells = []
        for label, rest in foot:
            cls = ' class="ask"' if label.startswith('Уточнить') else ''
            cells.append(f'<div{cls}><span class="lbl">{esc(label)}</span><p>{inline(rest)}</p></div>')
        body.append('<div class="sc-foot">' + ''.join(cells) + '</div>')
    return '\n'.join(body)

def parse_fence(p):
    head = p.next()[3:].strip()
    kind, _, arg = head.partition(' ')
    parts = [a.strip() for a in arg.split('|')]
    if kind == 'scenario':
        num, name, meta, cover = (parts + ['', '', '', ''])[:4]
        inner = scenario_fields(p)
        p.next()  # closing :::
        return (f'<article class="sc"><div class="sc-head"><span class="sc-num">{esc(num)}</span>'
                f'<div><h3>{inline(name)}</h3><p class="sc-meta">{esc(meta)}</p></div>'
                f'<span class="cover"><i>Обложка</i>{esc(cover)}</span></div>'
                f'<div class="sc-body">{inner}</div></article>')
    if kind == 'take':
        num, tm, plan, mode = (parts + ['', '', '', ''])[:4]
        rows = []
        while not p.eof() and p.peek().strip() != ':::':
            line = p.next().strip()
            if not line:
                continue
            m = re.match(r'\*\*(.+?):\*\*\s*(.*)', line)
            if not m:
                rows.append(('', line)); continue
            rows.append((m.group(1), m.group(2)))
        p.next()
        cls = {'синхрон': 'sync', 'закадр': 'vo', 'без слов': 'mute', 'титр': 'card'}.get(mode.lower(), 'mute')
        head = (f'<div class="take-h"><span class="take-n">Кадр {esc(num)}</span>'
                f'<span class="take-t">{esc(tm)}</span><span class="take-p">{esc(plan)}</span>'
                + (f'<span class="mode {cls}">{esc(mode)}</span>' if mode else '') + '</div>')
        body = []
        for label, val in rows:
            speech = label.startswith(('Говорит', 'Закадр', 'Реплика', 'Отвечает', 'Читает'))
            rc = 'take-r speech' if speech else 'take-r'
            body.append(f'<div class="{rc}"><span class="take-l">{esc(label)}</span>'
                        f'<span class="take-v">{inline(val)}</span></div>')
        return f'<div class="take">{head}{"".join(body)}</div>'
    if kind == 'spec':
        cells = []
        while not p.eof() and p.peek().strip() != ':::':
            line = p.next().strip()
            if not line:
                continue
            a, _, b = line.partition('|')
            cells.append(f'<div class="spec-i"><span class="spec-l">{esc(a.strip())}</span>'
                         f'<span class="spec-v">{inline(b.strip())}</span></div>')
        p.next()
        return '<div class="spec">' + ''.join(cells) + '</div>'
    if kind == 'stats':
        cards = []
        while not p.eof() and p.peek().strip() != ':::':
            line = p.next().strip()
            if not line:
                continue
            bits = [b.strip() for b in line.split('|')]
            val, lab = bits[0], bits[1]
            tone = bits[2] if len(bits) > 2 else ''
            cards.append(f'<div class="stat"><b class="{tone}">{esc(val)}</b><span>{esc(lab)}</span></div>')
        p.next()
        return '<div class="stats">' + ''.join(cards) + '</div>'
    if kind == 'note':
        inner = parse_blocks(p, True); p.next()
        return f'<div class="callout"><span class="lbl">{esc(arg)}</span>{inner}</div>'
    if kind == 'phase':
        cls, name, days = (parts + ['', '', ''])[:3]
        inner = parse_blocks(p, True); p.next()
        return (f'<div class="phase {esc(cls)}"><div class="phase-h"><h3>{inline(name)}</h3>'
                f'<span class="days">{esc(days)}</span></div>{inner}</div>')
    inner = parse_blocks(p, True); p.next()
    return inner

def convert(md, head_html):
    lines = md.split('\n')
    p = P(lines)
    sections, nav = [], []
    intro = ''
    title = subtitle = stand = ''
    while not p.eof():
        line = p.peek()
        if not line.strip():
            p.next(); continue
        if line.startswith('# '):
            title = p.next()[2:].strip(); continue
        if line.startswith('^^ '):
            stand = p.next()[3:].strip(); continue
        if line.startswith('~~ '):
            subtitle = p.next()[3:].strip(); continue
        if line.startswith('## '):
            head = p.next()[3:].strip()
            eyebrow, _, h2 = head.partition('|')
            sid = 's%d' % (len(sections) + 1)
            body = parse_blocks(p)
            sections.append(f'<section id="{sid}"><span class="sec-no">{esc(eyebrow.strip())}</span>'
                            f'<h2>{inline(h2.strip())}</h2>{body}</section>')
            nav.append(f'<li><a href="#{sid}">{esc(eyebrow.strip())}</a></li>')
            continue
        intro += parse_blocks(p)
    return (head_html
            + '<div class="wrap"><header class="top">'
            + f'<p class="eyebrow">{esc(subtitle)}</p>'
            + f'<h1>{inline(title)}</h1>'
            + f'<p class="stand">{inline(stand)}</p></header>'
            + '<div class="layout"><nav class="toc" aria-label="Разделы"><ol>'
            + ''.join(nav) + '</ol></nav><main>' + intro + ''.join(sections)
            + '</main></div></div>')

if __name__ == '__main__':
    md = io.open(sys.argv[1], encoding='utf-8').read()
    head = io.open(sys.argv[2], encoding='utf-8').read()
    io.open(sys.argv[3], 'w', encoding='utf-8').write(convert(md, head))
    print('written', sys.argv[3])

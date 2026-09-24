// Собирает .docx из JSON-дерева, которое даёт tools/md2json.py
const fs = require('fs');
const path = require('path');
const D = require(process.argv[4] ? path.resolve(process.argv[4], 'node_modules/docx') : 'docx');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType,
  AlignmentType, HeadingLevel, BorderStyle, LevelFormat, PageBreak, TableLayoutType
} = D;

const src = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const out = process.argv[3];

const INK = '15191C', INK2 = '454D53', INK3 = '79838A', MARK = 'B93A2E', CHALK = '275B78', GOOD = '2C6B4E';
const CARD = 'F3F5F6', CHALK_SOFT = 'E4EDF2', MARK_SOFT = 'F7E6E3', RULE = 'D2D8DB';
const PAGE_W = 11906, MARG = 1134, CONTENT_W = PAGE_W - 2 * MARG; // A4, поля 2 см

const border = { style: BorderStyle.SINGLE, size: 4, color: RULE };
const borders = { top: border, bottom: border, left: border, right: border };
const noBorder = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

function runs(text, opts = {}) {
  // **жирный** и `код`
  const parts = String(text).split(/(\*\*[^*]+\*\*|`[^`]+`)/g).filter(Boolean);
  return parts.map(p => {
    if (p.startsWith('**') && p.endsWith('**')) return new TextRun({ text: p.slice(2, -2), bold: true, ...opts });
    if (p.startsWith('`') && p.endsWith('`')) return new TextRun({ text: p.slice(1, -1), font: 'Consolas', ...opts });
    return new TextRun({ text: p, ...opts });
  });
}
const para = (text, o = {}) => new Paragraph({ children: runs(text, o.run || {}), spacing: { after: o.after ?? 120, before: o.before ?? 0 }, alignment: o.align, ...(o.p || {}) });
const label = (text) => new Paragraph({ children: [new TextRun({ text: text.toUpperCase(), size: 15, color: INK3, characterSpacing: 20 })], spacing: { before: 120, after: 40 } });

function cell(children, w, opts = {}) {
  return new TableCell({
    children, width: { size: w, type: WidthType.DXA },
    shading: opts.fill ? { type: ShadingType.CLEAR, fill: opts.fill, color: 'auto' } : undefined,
    borders: opts.borders || borders,
    margins: { top: 80, bottom: 80, left: 110, right: 110 },
    verticalAlign: 'top',
  });
}
function table(colWidths, rowsCells, opts = {}) {
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: colWidths, layout: TableLayoutType.FIXED,
    rows: rowsCells.map(r => new TableRow({ children: r, cantSplit: opts.cantSplit })),
  });
}
function splitWidths(n, weights) {
  const total = weights.reduce((a, b) => a + b, 0);
  const w = weights.map(x => Math.floor(CONTENT_W * x / total));
  w[w.length - 1] += CONTENT_W - w.reduce((a, b) => a + b, 0);
  return w;
}
function box(children, fill) {
  return table([CONTENT_W], [[cell(children, CONTENT_W, { fill })]]);
}
const spacer = (after = 120) => new Paragraph({ children: [], spacing: { after } });

function mdTable(b) {
  const ncol = (b.head || b.rows[0]).length;
  let weights;
  if (ncol === 2) weights = [1, 2];
  else if (ncol === 3) weights = [1.2, 2, 1.4];
  else if (ncol === 4) weights = [1.2, 2, 1.2, 1.2];
  else weights = Array(ncol).fill(1);
  const cw = splitWidths(ncol, weights);
  const rows = [];
  if (b.head) rows.push(b.head.map((h, i) => cell([new Paragraph({ children: [new TextRun({ text: h.toUpperCase(), size: 15, bold: true, color: INK3 })], spacing: { after: 0 } })], cw[i], { fill: CARD })));
  for (const r of b.rows) rows.push(r.map((c, i) => cell([new Paragraph({ children: runs(c, { size: 19, bold: i === 0 && !!b.head, color: i === 0 ? INK : INK2 }), spacing: { after: 0 } })], cw[i])));
  return [table(cw, rows), spacer()];
}

function list(b) {
  return b.items.map(it => new Paragraph({ children: runs(it), numbering: { reference: b.t === 'ol' ? 'nums' : 'bullets', level: 0 }, spacing: { after: 80 } }));
}

function scenario(b) {
  const els = [];
  els.push(new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun({ text: `${b.num}. ${b.name}` })], spacing: { before: 360, after: 60 }, keepNext: true }));
  els.push(new Paragraph({ children: [new TextRun({ text: b.meta, size: 17, color: INK3 }), new TextRun({ text: b.cover ? `   ·   Обложка: ${b.cover}` : '', size: 17, color: INK })], spacing: { after: 160 } }));
  for (const f of b.fields) {
    if (f.kind === 'hook') {
      els.push(box([label(f.label), new Paragraph({ children: runs(f.value, { size: 22, bold: true }), spacing: { after: 0 } })], CHALK_SOFT)); els.push(spacer(100));
    } else if (f.kind === 'shots') {
      els.push(label(f.label));
      const cw = splitWidths(3, [0.7, 0.9, 5]);
      const rows = f.shots.map(s => [
        cell([new Paragraph({ children: [new TextRun({ text: s[0], size: 17, color: MARK, font: 'Consolas' })], spacing: { after: 0 } })], cw[0]),
        cell([new Paragraph({ children: [new TextRun({ text: s[1].toUpperCase(), size: 15, color: s[1] === 'синхрон' ? MARK : s[1] === 'закадр' ? CHALK : INK3 })], spacing: { after: 0 } })], cw[1]),
        cell([new Paragraph({ children: runs(s[2], { size: 19, color: INK2 }), spacing: { after: 0 } })], cw[2]),
      ]);
      els.push(table(cw, rows)); els.push(spacer(100));
    } else if (f.kind === 'list') {
      els.push(label(f.label));
      f.items.forEach(it => els.push(new Paragraph({ children: runs(it, { size: 19 }), numbering: { reference: 'bullets', level: 0 }, spacing: { after: 40 } })));
    } else if (f.kind === 'caption') {
      els.push(label(f.label));
      els.push(box([new Paragraph({ children: runs(f.value, { size: 19 }), spacing: { after: 0 } })], CARD)); els.push(spacer(100));
    } else {
      if (f.label) els.push(label(f.label));
      els.push(para(f.value, { after: 80, run: { size: 20 } }));
    }
  }
  if (b.foot.length) {
    const cw = splitWidths(b.foot.length, b.foot.map(() => 1));
    els.push(table(cw, [b.foot.map((f, i) => cell([label(f.label), new Paragraph({ children: runs(f.value, { size: 18, color: f.label.startsWith('Уточнить') ? MARK : INK2 }), spacing: { after: 0 } })], cw[i], { fill: CARD }))]));
  }
  els.push(spacer(200));
  return els;
}

function take(b) {
  const isSlide = b.tm && b.tm.startsWith('Слайд');
  const head = isSlide ? b.tm : `Кадр ${b.num}`;
  const modeColor = b.mode === 'синхрон' ? MARK : b.mode === 'закадр' ? CHALK : b.mode === 'титр' ? GOOD : INK3;
  const cw = splitWidths(2, [1, 4.2]);
  const rows = [];
  rows.push([new TableCell({
    children: [new Paragraph({ children: [
      new TextRun({ text: head, bold: true, size: 20 }),
      new TextRun({ text: isSlide ? '' : `   ${b.tm}`, size: 17, color: MARK, font: 'Consolas' }),
      new TextRun({ text: `   ${b.plan.toUpperCase()}`, size: 15, color: INK3 }),
      new TextRun({ text: b.mode ? `   ${b.mode.toUpperCase()}` : '', size: 15, bold: true, color: modeColor }),
    ], spacing: { after: 0 } })],
    columnSpan: 2, width: { size: CONTENT_W, type: WidthType.DXA }, borders,
    shading: { type: ShadingType.CLEAR, fill: CARD, color: 'auto' }, margins: { top: 80, bottom: 80, left: 110, right: 110 },
  })]);
  for (const [l, v] of b.rows) {
    const speech = /^(Говорит|Закадр|Реплика|Отвечает|Читает|Смысл)/.test(l);
    const fill = speech ? CHALK_SOFT : undefined;
    rows.push([
      cell([new Paragraph({ children: [new TextRun({ text: l.toUpperCase(), size: 14, color: speech ? CHALK : INK3, characterSpacing: 15 })], spacing: { after: 0 } })], cw[0], { fill }),
      cell([new Paragraph({ children: runs(v, { size: speech ? 21 : 19, bold: speech, color: speech ? INK : INK2 }), spacing: { after: 0 } })], cw[1], { fill }),
    ]);
  }
  return [table(cw, rows, { cantSplit: true }), spacer(120)];
}

function spec(b) {
  const cw = splitWidths(2, [1, 3.2]);
  const rows = b.items.map(([k, v]) => [
    cell([new Paragraph({ children: [new TextRun({ text: k.toUpperCase(), size: 14, color: INK3, characterSpacing: 15 })], spacing: { after: 0 } })], cw[0], { fill: CARD }),
    cell([new Paragraph({ children: runs(v, { size: 19 }), spacing: { after: 0 } })], cw[1], { fill: CARD }),
  ]);
  return [table(cw, rows), spacer(160)];
}

function stats(b) {
  const cw = splitWidths(b.items.length, b.items.map(() => 1));
  return [table(cw, [b.items.map(([v, l, tone], i) => cell([
    new Paragraph({ children: [new TextRun({ text: v, bold: true, size: 34, color: tone === 'neg' ? MARK : tone === 'pos' ? GOOD : INK })], spacing: { after: 40 } }),
    new Paragraph({ children: [new TextRun({ text: l.toUpperCase(), size: 14, color: INK3 })], spacing: { after: 0 } }),
  ], cw[i], { fill: CARD }))]), spacer()];
}

function blocks(bs) {
  const els = [];
  for (const b of bs) {
    switch (b.t) {
      case 'p': els.push(para(b.text, { run: b.lede ? { size: 23, color: INK2 } : {}, after: b.lede ? 200 : 120 })); break;
      case 'h3': els.push(new Paragraph({ heading: HeadingLevel.HEADING_3, children: runs(b.text), spacing: { before: 320, after: 100 }, keepNext: true })); break;
      case 'h4': els.push(new Paragraph({ heading: HeadingLevel.HEADING_4, children: runs(b.text), spacing: { before: 200, after: 80 }, keepNext: true })); break;
      case 'ul': case 'ol': els.push(...list(b)); break;
      case 'table': els.push(...mdTable(b)); break;
      case 'quote': els.push(box([new Paragraph({ children: runs(b.text, { size: 22, bold: true }), spacing: { after: 0 } })], CARD)); els.push(spacer()); break;
      case 'note': {
        const inner = [new Paragraph({ children: [new TextRun({ text: b.title.toUpperCase(), size: 15, bold: true, color: MARK, characterSpacing: 20 })], spacing: { after: 80 } }), ...blocks(b.blocks)];
        els.push(box(inner, MARK_SOFT)); els.push(spacer()); break;
      }
      case 'stats': els.push(...stats(b)); break;
      case 'phase':
        els.push(new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun({ text: b.name }), new TextRun({ text: `   ${b.days}`, size: 17, color: INK3, bold: false })], spacing: { before: 320, after: 100 }, keepNext: true }));
        els.push(...blocks(b.blocks)); break;
      case 'scenario': els.push(...scenario(b)); break;
      case 'take': els.push(...take(b)); break;
      case 'spec': els.push(...spec(b)); break;
      case 'group': els.push(...blocks(b.blocks)); break;
    }
  }
  return els;
}

const children = [];
// титульная часть
children.push(new Paragraph({ children: [new TextRun({ text: src.eyebrow.toUpperCase(), size: 16, color: INK3, characterSpacing: 25 })], spacing: { before: 2400, after: 300 } }));
children.push(new Paragraph({ children: runs(src.title, { size: 60, bold: true }), spacing: { after: 300 } }));
children.push(new Paragraph({ children: runs(src.stand, { size: 24, color: INK2 }), spacing: { after: 400 } }));
// оглавление вручную
children.push(new Paragraph({ children: [new TextRun({ text: 'РАЗДЕЛЫ', size: 15, color: INK3, characterSpacing: 20 })], spacing: { before: 200, after: 120 } }));
for (const s of src.sections) children.push(new Paragraph({ children: [new TextRun({ text: `${s.label}   ` , size: 19, color: MARK, font: 'Consolas' }), new TextRun({ text: s.title, size: 20 })], spacing: { after: 60 } }));
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(...blocks(src.intro || []));
src.sections.forEach((s, i) => {
  if (i > 0) children.push(new Paragraph({ children: [new PageBreak()] }));
  children.push(new Paragraph({ children: [new TextRun({ text: s.label.toUpperCase(), size: 16, color: MARK, characterSpacing: 25 })], spacing: { after: 80 } }));
  children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: runs(s.title), spacing: { after: 240 } }));
  children.push(...blocks(s.blocks));
});

const doc = new Document({
  creator: 'Infinity Story',
  styles: {
    default: { document: { run: { font: 'Calibri', size: 21, color: INK }, paragraph: { spacing: { line: 300 } } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { size: 40, bold: true, color: INK, font: 'Calibri' }, paragraph: { spacing: { before: 0, after: 240 }, outlineLevel: 0 } },
      { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { size: 27, bold: true, color: INK, font: 'Calibri' }, paragraph: { spacing: { before: 320, after: 100 }, outlineLevel: 2 } },
      { id: 'Heading4', name: 'Heading 4', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { size: 22, bold: true, color: INK2, font: 'Calibri' }, paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 3 } },
    ],
  },
  numbering: { config: [
    { reference: 'bullets', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 300 } } } }] },
    { reference: 'nums', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 300 } } } }] },
  ] },
  sections: [{ properties: { page: { size: { width: PAGE_W, height: 16838 }, margin: { top: MARG, bottom: MARG, left: MARG, right: MARG } } }, children }],
});

Packer.toBuffer(doc).then(buf => { fs.writeFileSync(out, buf); console.log('docx written', out, buf.length); });

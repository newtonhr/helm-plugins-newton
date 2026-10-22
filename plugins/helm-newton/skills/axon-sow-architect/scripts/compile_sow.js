#!/usr/bin/env node
/*
 * compile_sow.js — convert a filled sow_draft.md into an AXON SOW .docx
 *
 * Usage (from the skill directory or anywhere, with an absolute path):
 *   node scripts/compile_sow.js <path-to-sow_draft.md> <output.docx>
 *
 * Or with just a milestone slug relative to a workspace:
 *   node scripts/compile_sow.js --workspace <workspace-dir> --slug <milestone-slug>
 *   → reads  <workspace-dir>/<slug>/drafts/sow_draft.md
 *   → writes <workspace-dir>/<slug>/<slug>_SOW.docx
 *
 * Design assumptions about the input markdown:
 *   - H1 "#"     → document title (one per doc)
 *   - H2 "##"    → numbered top-level sections (1. Milestone Scope, 2. ...)
 *   - H3 "###"   → subsection
 *   - Tables in GitHub-flavored markdown
 *   - Bulleted lists with "-" or "*"
 *   - Paragraphs separated by blank lines
 *   - Inline **bold** and *italic*
 *   - Fenced code blocks rendered as monospace
 *
 * Intentionally NOT a full markdown engine — the sow_draft.md written by
 * the drafter subagent is a disciplined subset. Anything the parser
 * doesn't understand is emitted as plain paragraph text so nothing is
 * silently dropped.
 */

const fs = require('fs');
const path = require('path');

const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, HeadingLevel, WidthType, BorderStyle, LevelFormat,
  Header, Footer, PageNumber, ShadingType, TableLayoutType
} = require('docx');

// ───────── page geometry (DXA = 1/20 of a point) ─────────
// A4: 11906 × 16838 DXA. With 1440 DXA (1") margins on left and right,
// the content width is 11906 − 2×1440 = 9026 DXA. All tables span the
// full content width; all cells are sized in DXA and sum to 9026 exactly.
const PAGE_WIDTH_DXA = 11906;
const PAGE_MARGIN_DXA = 1440;
const CONTENT_WIDTH_DXA = PAGE_WIDTH_DXA - 2 * PAGE_MARGIN_DXA; // 9026

// ───────── args ─────────
function parseArgs() {
  const args = process.argv.slice(2);
  if (args[0] === '--workspace') {
    const workspace = args[1];
    if (args[2] !== '--slug') die('expected --slug after workspace');
    const slug = args[3];
    const draft = path.join(workspace, slug, 'drafts', 'sow_draft.md');
    const out = path.join(workspace, slug, `${slug}_SOW.docx`);
    return { draft, out };
  }
  if (args.length !== 2) die('usage: compile_sow.js <draft.md> <output.docx>  OR  --workspace <dir> --slug <slug>');
  return { draft: args[0], out: args[1] };
}

function die(msg) { console.error('ERROR:', msg); process.exit(2); }

// ───────── markdown lexer (narrow subset) ─────────
function tokenize(md) {
  const lines = md.split(/\r?\n/);
  const toks = [];
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    // H1/H2/H3
    let m = /^(#{1,3})\s+(.*)$/.exec(line);
    if (m) { toks.push({ type: 'h', level: m[1].length, text: m[2].trim() }); i++; continue; }
    // fenced code
    if (/^```/.test(line)) {
      const body = [];
      i++;
      while (i < lines.length && !/^```/.test(lines[i])) { body.push(lines[i]); i++; }
      i++;
      toks.push({ type: 'code', lines: body });
      continue;
    }
    // table: header | ... | then separator row with ---
    if (/\|/.test(line) && i + 1 < lines.length && /^\s*\|?[\s\-:|]+\|?\s*$/.test(lines[i+1]) && /-/.test(lines[i+1])) {
      const rows = [];
      while (i < lines.length && /\|/.test(lines[i])) {
        if (/^\s*\|?[\s\-:|]+\|?\s*$/.test(lines[i]) && /-/.test(lines[i])) { i++; continue; }
        rows.push(splitRow(lines[i]));
        i++;
      }
      toks.push({ type: 'table', rows });
      continue;
    }
    // bullet list
    if (/^\s*[-*]\s+/.test(line)) {
      const items = [];
      while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*[-*]\s+/, ''));
        i++;
      }
      toks.push({ type: 'ul', items });
      continue;
    }
    // numbered list
    if (/^\s*\d+\.\s+/.test(line)) {
      const items = [];
      while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*\d+\.\s+/, ''));
        i++;
      }
      toks.push({ type: 'ol', items });
      continue;
    }
    // blank
    if (/^\s*$/.test(line)) { i++; continue; }
    // paragraph (collect until blank)
    const para = [line];
    i++;
    while (i < lines.length && !/^\s*$/.test(lines[i]) && !/^(#{1,3})\s+/.test(lines[i])
           && !/^\s*[-*]\s+/.test(lines[i]) && !/^\s*\d+\.\s+/.test(lines[i])
           && !/^```/.test(lines[i])) {
      para.push(lines[i]);
      i++;
    }
    toks.push({ type: 'p', text: para.join(' ').trim() });
  }
  return toks;
}

function splitRow(line) {
  let s = line.trim();
  if (s.startsWith('|')) s = s.slice(1);
  if (s.endsWith('|')) s = s.slice(0, -1);
  return s.split('|').map(c => c.trim());
}

// ───────── inline renderer: **bold**, *italic* ─────────
function inlineRuns(text, opts = {}) {
  const runs = [];
  const re = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g;
  let last = 0; let m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) runs.push(new TextRun({ text: text.slice(last, m.index), font: 'Arial', size: opts.size || 22 }));
    const seg = m[0];
    if (seg.startsWith('**')) {
      runs.push(new TextRun({ text: seg.slice(2, -2), bold: true, font: 'Arial', size: opts.size || 22 }));
    } else if (seg.startsWith('`')) {
      runs.push(new TextRun({ text: seg.slice(1, -1), font: 'Consolas', size: opts.size || 22 }));
    } else {
      runs.push(new TextRun({ text: seg.slice(1, -1), italics: true, font: 'Arial', size: opts.size || 22 }));
    }
    last = m.index + seg.length;
  }
  if (last < text.length) runs.push(new TextRun({ text: text.slice(last), font: 'Arial', size: opts.size || 22 }));
  if (runs.length === 0) runs.push(new TextRun({ text: '', font: 'Arial', size: opts.size || 22 }));
  return runs;
}

// ───────── block renderer ─────────
function render(toks) {
  const out = [];
  for (const t of toks) {
    if (t.type === 'h' && t.level === 1) {
      out.push(new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 240 },
        children: [new TextRun({ text: t.text, bold: true, font: 'Arial', size: 32 })]
      }));
    } else if (t.type === 'h' && t.level === 2) {
      out.push(new Paragraph({
        spacing: { before: 360, after: 120 },
        children: [new TextRun({ text: t.text, bold: true, font: 'Arial', size: 26 })]
      }));
    } else if (t.type === 'h' && t.level === 3) {
      out.push(new Paragraph({
        spacing: { before: 240, after: 80 },
        children: [new TextRun({ text: t.text, bold: true, font: 'Arial', size: 23 })]
      }));
    } else if (t.type === 'p') {
      out.push(new Paragraph({
        spacing: { after: 120 },
        children: inlineRuns(t.text)
      }));
    } else if (t.type === 'ul') {
      for (const item of t.items) {
        out.push(new Paragraph({
          bullet: { level: 0 },
          spacing: { after: 60 },
          children: inlineRuns(item)
        }));
      }
    } else if (t.type === 'ol') {
      for (let idx = 0; idx < t.items.length; idx++) {
        out.push(new Paragraph({
          spacing: { after: 60 },
          children: [
            new TextRun({ text: `${idx + 1}. `, bold: true, font: 'Arial', size: 22 }),
            ...inlineRuns(t.items[idx])
          ]
        }));
      }
    } else if (t.type === 'code') {
      for (const line of t.lines) {
        out.push(new Paragraph({
          spacing: { after: 0 },
          children: [new TextRun({ text: line || ' ', font: 'Consolas', size: 20 })]
        }));
      }
      out.push(new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: '' })] }));
    } else if (t.type === 'table') {
      out.push(renderTable(t.rows));
      out.push(new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: '' })] }));
    }
  }
  return out;
}

function renderTable(rows) {
  if (!rows.length) return new Paragraph({ children: [new TextRun({ text: '' })] });
  const cols = rows[0].length;

  // All widths in DXA. Cells sum exactly to CONTENT_WIDTH_DXA so the
  // table spans full content width with no rounding gap. Any leftover
  // DXA from the floor division lands in the last cell.
  const baseCellDxa = Math.floor(CONTENT_WIDTH_DXA / cols);
  const remainderDxa = CONTENT_WIDTH_DXA - baseCellDxa * cols;
  const cellWidthsDxa = Array.from({ length: cols }, (_, idx) =>
    baseCellDxa + (idx === cols - 1 ? remainderDxa : 0));

  const tableRows = rows.map((r, ri) => {
    const cells = r.map((cellText, ci) => new TableCell({
      width: { size: cellWidthsDxa[ci], type: WidthType.DXA },
      shading: ri === 0 ? { type: ShadingType.CLEAR, color: 'auto', fill: 'E7E6E6' } : undefined,
      children: [new Paragraph({
        children: ri === 0
          ? [new TextRun({ text: cellText, bold: true, font: 'Arial', size: 20 })]
          : inlineRuns(cellText, { size: 20 })
      })]
    }));
    return new TableRow({ children: cells });
  });

  // layout: FIXED makes Word honor the DXA cell widths we just set,
  // instead of auto-fitting based on content. Without this, Word can
  // silently collapse or expand columns and the table stops matching
  // its declared width.
  return new Table({
    width: { size: CONTENT_WIDTH_DXA, type: WidthType.DXA },
    columnWidths: cellWidthsDxa,
    layout: TableLayoutType.FIXED,
    borders: {
      top: { style: BorderStyle.SINGLE, size: 4, color: '999999' },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: '999999' },
      left: { style: BorderStyle.SINGLE, size: 4, color: '999999' },
      right: { style: BorderStyle.SINGLE, size: 4, color: '999999' },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 4, color: 'CCCCCC' },
      insideVertical: { style: BorderStyle.SINGLE, size: 4, color: 'CCCCCC' }
    },
    rows: tableRows
  });
}

// ───────── main ─────────
async function main() {
  const { draft, out } = parseArgs();
  if (!fs.existsSync(draft)) die(`draft not found: ${draft}`);
  const md = fs.readFileSync(draft, 'utf-8');

  // Warn on stray placeholders
  const stray = md.match(/\{\{[^}]+\}\}/g);
  if (stray) {
    console.warn('WARN: unresolved placeholders remain:', stray.slice(0, 8).join(', '),
                 stray.length > 8 ? `(+${stray.length - 8} more)` : '');
  }
  const opens = md.match(/\[OPEN:[^\]]+\]/g);
  if (opens) {
    console.warn(`WARN: ${opens.length} [OPEN: ...] markers remain — draft is not final.`);
  }

  const toks = tokenize(md);
  const children = render(toks);

  const doc = new Document({
    creator: 'Newton d.o.o.',
    title: 'AXON Statement of Work',
    styles: {
      default: {
        document: { run: { font: 'Arial', size: 22 } }
      }
    },
    sections: [{
      properties: {
        page: {
          size: { width: 11906, height: 16838 }, // A4
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
        }
      },
      headers: {
        default: new Header({
          children: [new Paragraph({
            alignment: AlignmentType.RIGHT,
            children: [new TextRun({ text: 'AXON Program · Newton d.o.o. × Marina Stores', font: 'Arial', size: 18, color: '666666' })]
          })]
        })
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [
              new TextRun({ text: 'Page ', font: 'Arial', size: 18, color: '666666' }),
              new TextRun({ children: [PageNumber.CURRENT], font: 'Arial', size: 18, color: '666666' }),
              new TextRun({ text: ' / ', font: 'Arial', size: 18, color: '666666' }),
              new TextRun({ children: [PageNumber.TOTAL_PAGES], font: 'Arial', size: 18, color: '666666' })
            ]
          })]
        })
      },
      children
    }]
  });

  fs.mkdirSync(path.dirname(out), { recursive: true });
  const buf = await Packer.toBuffer(doc);
  fs.writeFileSync(out, buf);
  console.log(`wrote ${out} (${buf.length} bytes)`);
}

main().catch(e => { console.error(e); process.exit(1); });

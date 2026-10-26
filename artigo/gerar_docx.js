// Gera o artigo .docx no formato SBC a partir de blocos.json (produzido por tex2json.py)
// Uso: node gerar_docx.js blocos.json pasta_das_figuras saida.docx
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell,
  AlignmentType, WidthType, BorderStyle, LevelFormat, TableLayoutType,
} = require("docx");

const [, , JSON_IN, FIG_DIR, OUT] = process.argv;
const blocos = JSON.parse(fs.readFileSync(JSON_IN, "utf8"));

const LARG = 11906 - 2 * 1701;           // largura útil em DXA (A4, margens 3 cm)
const LARG_PX = Math.round(LARG / 15);   // 1 px = 15 DXA (96 dpi)
const CM = 567;

const corpo = { font: "Times New Roman", size: 24 };
function tr(r, base = {}) {
  const o = { text: r.t, font: base.font || corpo.font, size: base.size || corpo.size };
  if (r.b || base.bold) o.bold = true;
  if (r.i || base.italics) o.italics = true;
  if (r.code) { o.font = "Courier New"; o.size = Math.round((base.size || corpo.size) * 0.85); }
  return new TextRun(o);
}
const runs = (rs, base) => rs.map((r) => tr(r, base));

function pngSize(f) {
  const b = fs.readFileSync(f);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}
function imagem(frac, arq, larguraMax) {
  const f = path.join(FIG_DIR, path.basename(arq) + (arq.endsWith(".png") ? "" : ".png"));
  const { w, h } = pngSize(f);
  const largura = Math.round(frac * (larguraMax || LARG_PX));
  return new ImageRun({ type: "png", data: fs.readFileSync(f),
    transformation: { width: largura, height: Math.round(largura * h / w) } });
}
const legenda = (rs, depois = 240, antes = 0) => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { before: antes, after: depois },
  indent: { left: 454, right: 454 }, keepNext: antes === 0 && depois < 200,
  children: runs(rs, { font: "Arial", size: 20, bold: true }),
});

// larguras das colunas a partir da especificação LaTeX (p{Xcm}, l, c, r)
function colunas(spec, n) {
  const toks = spec.match(/p\{[\d.]+cm\}|[lcr]/g).slice(0, n);
  const fixos = toks.map((t) => { if (!t.startsWith("p")) return null; const cm = parseFloat(t.slice(2)); return (cm < 2 ? cm + 0.5 : cm) * CM; });
  const somaFix = fixos.reduce((a, b) => a + (b || 0), 0);
  const livres = fixos.filter((x) => x === null).length;
  let ws;
  if (livres) {
    const resto = Math.max(LARG - somaFix, livres * 900);
    ws = fixos.map((x) => x || resto / livres);
  } else ws = fixos;
  const total = ws.reduce((a, b) => a + b, 0);
  ws = ws.map((x) => Math.floor(x * LARG / total));
  return { ws, alinh: toks.map((t) => (t === "r" ? AlignmentType.RIGHT : t === "c" ? AlignmentType.CENTER : AlignmentType.LEFT)) };
}
const SEM = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const LINHA = { style: BorderStyle.SINGLE, size: 6, color: "000000" };
function tabela(b) {
  const n = Math.max(...b.rows.map((r) => r.length));
  const { ws, alinh } = colunas(b.spec, n);
  const linhas = b.rows.map((row, i) => new TableRow({
    tableHeader: i === 0, cantSplit: true,
    children: ws.map((w, j) => new TableCell({
      width: { size: w, type: WidthType.DXA },
      margins: { top: 30, bottom: 30, left: 70, right: 70 },
      borders: { left: SEM, right: SEM,
        top: i <= 1 ? LINHA : SEM,
        bottom: i === b.rows.length - 1 || i === 0 ? LINHA : SEM },
      children: [new Paragraph({ alignment: alinh[j], keepNext: i === 0,
        children: runs(row[j] || [], { size: 18, bold: i === 0 }) })],
    })),
  }));
  return new Table({ width: { size: LARG, type: WidthType.DXA }, columnWidths: ws,
    layout: TableLayoutType.FIXED, rows: linhas });
}

const filhos = [];
const centro = (rs, base, after = 0) => new Paragraph({ alignment: AlignmentType.CENTER,
  spacing: { after }, children: runs(rs, base) });

for (const b of blocos) {
  switch (b.type) {
    case "title": filhos.push(centro(b.runs, { size: 32, bold: true }, 80)); break;
    case "title2": filhos.push(centro(b.runs, { size: 28, bold: true }, 240)); break;
    case "authors": filhos.push(centro(b.runs, { bold: true }, 80)); break;
    case "center": filhos.push(centro(b.runs, { size: b.size || 24 }, b.size === 18 ? 240 : 0)); break;
    case "abstract":
      filhos.push(new Paragraph({ alignment: AlignmentType.JUSTIFIED, indent: { left: 454, right: 454 },
        spacing: { before: 120, after: 120 },
        children: [new TextRun({ text: b.label + " ", bold: true, italics: true, ...corpo }), ...runs(b.runs)] }));
      break;
    case "keywords":
      filhos.push(new Paragraph({ alignment: AlignmentType.JUSTIFIED, spacing: { after: 240 }, children: runs(b.runs) }));
      break;
    case "h1": filhos.push(new Paragraph({ keepNext: true, spacing: { before: 240, after: 120 },
      children: runs(b.runs, { size: 26, bold: true }) })); break;
    case "h2": filhos.push(new Paragraph({ keepNext: true, spacing: { before: 200, after: 80 },
      children: runs(b.runs, { bold: true }) })); break;
    case "p": filhos.push(new Paragraph({ alignment: AlignmentType.JUSTIFIED,
      indent: { firstLine: 720 }, spacing: { after: 120 }, children: runs(b.runs) })); break;
    case "bullet": filhos.push(new Paragraph({ alignment: AlignmentType.JUSTIFIED,
      numbering: { reference: "marcadores", level: 0 }, spacing: { after: 80 }, children: runs(b.runs) })); break;
    case "ref": filhos.push(new Paragraph({ alignment: AlignmentType.LEFT,
      indent: { left: 454, hanging: 454 }, spacing: { after: 120 }, children: runs(b.runs) })); break;
    case "figure":
      if (b.imgs.length === 1) {
        filhos.push(new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120, after: 60 },
          children: [imagem(b.imgs[0][0], b.imgs[0][1])] }));
      } else { // duas imagens lado a lado (tabela invisível)
        const w = Math.floor(LARG / b.imgs.length);
        filhos.push(new Table({ width: { size: LARG, type: WidthType.DXA }, columnWidths: b.imgs.map(() => w),
          rows: [new TableRow({ children: b.imgs.map((im, k) => new TableCell({
            width: { size: w, type: WidthType.DXA },
            borders: { top: SEM, bottom: SEM, left: SEM, right: SEM },
            children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [imagem(0.97, im[1], Math.floor(w / 15))] }),
                       new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 },
                         children: runs(b.subcaps[k] || [], { size: 18 }) })] })) })] }));
      }
      filhos.push(legenda(b.caption, 240, 0));
      break;
    case "table":
      filhos.push(new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120, after: 80 },
        indent: { left: 454, right: 454 }, children: runs(b.caption, { font: "Arial", size: 20, bold: true }) }));
      filhos.push(tabela(b));
      filhos.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
      break;
  }
}

const doc = new Document({
  creator: "Jarlisson Brito Santos",
  title: "Integridade e Desempenho no Controle de Ordens de Serviço de uma Oficina Mecânica",
  styles: { default: { document: { run: corpo } } },
  numbering: { config: [{ reference: "marcadores", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•",
    alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 },
      margin: { top: 1984, bottom: 1417, left: 1701, right: 1701 } } },
    children: filhos,
  }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(OUT, buf); console.log("ok", OUT); });

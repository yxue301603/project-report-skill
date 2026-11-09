"""Render a Markdown report into a portable HTML report with data-driven SVG charts."""
from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import math
from pathlib import Path
import re
import sys
import time

try:
    from markdown_it import MarkdownIt
except ImportError:
    raise SystemExit('Missing markdown-it-py. Install this skill\'s requirements.txt in your Python environment.')

ROOT = Path(__file__).resolve().parents[1]
COLORS = ['#1479bd', '#208254', '#ac6318', '#8761b2', '#b43c36', '#16848a']
MARKER = re.compile(r'<!--\s*report:(metrics|table\s+([A-Za-z0-9_-]+))\s*-->\s*\Z')
NUMBER = re.compile(r'[+-]?(?:(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?%?\Z')


def esc(value):
    return html.escape(str(value), quote=True)


def plain(token):
    if not token.children:
        return token.content
    return ''.join(t.content if t.type in ('text', 'code_inline', 'html_inline', 'image')
                   else '\n' if t.type in ('softbreak', 'hardbreak') else '' for t in token.children)


def number(value):
    value = value.strip().replace('−', '-')
    if not NUMBER.fullmatch(value):
        raise ValueError(f'Invalid numeric cell: {value!r}; put units in column names or chart unit.')
    result = float(value.rstrip('%').replace(',', ''))
    if not math.isfinite(result):
        raise ValueError(f'Non-finite numeric cell: {value!r}')
    return result


def fmt(value):
    return f'{value:,.6g}'


def read_table(tokens, start):
    rows, cells = [], []
    index = start + 1
    while tokens[index].type != 'table_close':
        tok = tokens[index]
        if tok.type == 'tr_open':
            cells = []
        elif tok.type == 'inline':
            cells.append(plain(tok).strip())
        elif tok.type == 'tr_close':
            rows.append(cells)
        index += 1
    return rows, index + 1


def chart(spec, tables):
    if not isinstance(spec, dict):
        raise ValueError('report-chart must contain a JSON object')
    required = {'type', 'title', 'table', 'label', 'values'}
    if not required <= spec.keys() or spec.keys() - (required | {'unit'}):
        raise ValueError('Chart requires type/title/table/label/values, with optional unit only')
    if any(not isinstance(spec[k], str) or not spec[k].strip() for k in required - {'values'}):
        raise ValueError('Chart type, title, table and label must be non-empty strings')
    if not isinstance(spec.get('unit', ''), str):
        raise ValueError('Chart unit must be a string')
    if spec['type'] not in ('bar', 'line'):
        raise ValueError('Chart type must be bar or line')
    columns = spec['values']
    if not isinstance(columns, list) or not columns or any(not isinstance(c, str) for c in columns):
        raise ValueError('Chart values must be a non-empty list of column names')
    if len(set(columns)) != len(columns):
        raise ValueError('Duplicate chart series')
    if spec['table'] not in tables:
        raise ValueError(f'Unknown table: {spec["table"]}')
    rows = tables[spec['table']]
    headers = rows[0]
    if len(set(headers)) != len(headers):
        raise ValueError('Referenced table must have unique column headers')
    if len(rows) < 2:
        raise ValueError('Chart table has no data rows')
    for col in [spec['label']] + columns:
        if col not in headers:
            raise ValueError(f'Column {col!r} not found in table {spec["table"]!r}')
    labels = [r[headers.index(spec['label'])] for r in rows[1:]]
    values = [[number(r[headers.index(c)]) for r in rows[1:]] for c in columns]
    raw = [r[headers.index(c)] for c in columns for r in rows[1:]]
    if any(x.endswith('%') for x in raw) and not all(x.endswith('%') for x in raw):
        raise ValueError('Do not mix percentage-formatted and plain numeric cells in one chart')
    unit = spec.get('unit', '') or ('%' if all(x.endswith('%') for x in raw) else '')
    low = min(0, min(min(v) for v in values))
    high = max(0, max(max(v) for v in values))
    if high == low:
        high = low + 1
    span = high - low
    if not math.isfinite(span):
        raise ValueError('Numeric range is too large to plot')
    width, left, right = 860, 210, 760
    elements = []

    def text(x, y, content, size=12, anchor='start'):
        elements.append(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" text-anchor="{anchor}">{esc(content)}</text>')

    def tip(label, col, value):
        return f'<title>{esc(label)} · {esc(col)}: {esc(fmt(value))}{esc(unit)}</title>'

    if spec['type'] == 'bar':
        row_h = 30 * len(columns) + 18
        height = 58 + row_h * len(labels)
        scale = lambda v: left + (v - low) / span * (right - left)
        baseline = scale(0)
        for i in range(5):
            value = low + span * i / 4
            x = scale(value)
            elements.append(f'<line x1="{x:.2f}" x2="{x:.2f}" y1="24" y2="{height-25}" stroke="#e2e8ef"/>')
            text(x, height - 5, fmt(value), 11, 'middle')
        for i, label in enumerate(labels):
            y = 40 + i * row_h
            # Full labels are also retained in the source table and SVG title.
            visible = label if len(label) <= 23 else label[:21] + '…'
            text(left - 12, y + 9, visible, 12, 'end')
            for j, col in enumerate(columns):
                value = values[j][i]
                end = scale(value)
                elements.append(f'<rect x="{min(baseline,end):.2f}" y="{y+j*30-5}" width="{abs(end-baseline):.2f}" height="18" rx="3" fill="{COLORS[j % len(COLORS)]}">{tip(label,col,value)}</rect>')
                text(right + 12, y + j * 30 + 9, fmt(value), 12)
        elements.append(f'<line x1="{baseline:.2f}" x2="{baseline:.2f}" y1="24" y2="{height-25}" stroke="#8493a4"/>')
    else:
        left, right, top, bottom, height = 85, 810, 35, 270, 350
        scale_y = lambda v: bottom - (v - low) / span * (bottom - top)
        scale_x = lambda i: (left + right) / 2 if len(labels) == 1 else left + i * (right-left) / (len(labels)-1)
        for i in range(5):
            value = low + span * i / 4
            y = scale_y(value)
            elements.append(f'<line x1="{left}" x2="{right}" y1="{y:.2f}" y2="{y:.2f}" stroke="#e2e8ef"/>')
            text(left-10, y+4, fmt(value), 11, 'end')
        for j, col in enumerate(columns):
            points = ' '.join(f'{scale_x(i):.2f},{scale_y(v):.2f}' for i,v in enumerate(values[j]))
            color = COLORS[j % len(COLORS)]
            elements.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2.5"/>')
            for i,value in enumerate(values[j]):
                elements.append(f'<circle cx="{scale_x(i):.2f}" cy="{scale_y(value):.2f}" r="4" fill="{color}">{tip(labels[i],col,value)}</circle>')
        stride = max(1, math.ceil(len(labels) / 8))
        for i,label in enumerate(labels):
            if i % stride == 0 or i == len(labels)-1:
                text(scale_x(i), bottom+24, label if len(label)<=10 else label[:9]+'…', 11, 'middle')
    legend = ''.join(f'<span><i style="background:{COLORS[j % len(COLORS)]}"></i>{esc(c)}</span>' for j,c in enumerate(columns))
    note = f'数据表：{spec["table"]}' + (f' · 单位：{unit}' if unit else '')
    if spec['type'] == 'line':
        note += ' · 横轴按数据行等间隔排列'
    return (f'<figure class="chart"><figcaption>{esc(spec["title"])}</figcaption><div class="legend">{legend}</div>'
            f'<div class="chart-scroll"><svg viewBox="0 0 {width} {height}" role="img" aria-label="{esc(spec["title"])}">'
            f'<title>{esc(spec["title"])}</title><desc>{esc(note)}；完整数值见正文数据表。</desc>{"".join(elements)}</svg></div>'
            f'<div class="chart-meta">{esc(note)}</div></figure>')


def render(source: str, source_name: str):
    md = MarkdownIt('commonmark', {'html': True}).enable(['table', 'strikethrough'])
    tokens = md.parse(source)
    tables, table_info, markers, toc = {}, {}, set(), []
    title, pending, heading_count = source_name, None, 0
    for i, tok in enumerate(tokens):
        if tok.type == 'html_block':
            match = MARKER.fullmatch(tok.content.strip())
            if match:
                if i+1 >= len(tokens) or tokens[i+1].type != 'table_open':
                    raise ValueError('report marker must immediately precede a Markdown table')
                pending = ('metrics', None) if match[1] == 'metrics' else ('table', match[2])
                markers.add(i)
            elif 'report:' in tok.content:
                raise ValueError('Malformed report marker')
        elif tok.type == 'table_open':
            rows, end = read_table(tokens, i)
            if pending:
                kind, name = pending
                if kind == 'metrics' and not 2 <= len(rows[0]) <= 3:
                    raise ValueError('Metrics table requires 2 or 3 columns')
                if name:
                    if name in tables:
                        raise ValueError(f'Duplicate table identifier: {name}')
                    tables[name] = rows
                table_info[i] = (rows, end, kind, name)
                pending = None
        elif tok.type == 'heading_open':
            heading_count += 1
            label = plain(tokens[i+1])
            anchor = f'section-{heading_count}'
            tok.attrSet('id', anchor)
            if tok.tag == 'h1' and title == source_name:
                title = label
            if tok.tag in ('h2', 'h3'):
                toc.append(f'<li><a href="#{anchor}">{esc(label)}</a></li>')

    # GitHub-style callouts; only the first inline paragraph is interpreted.
    for i,tok in enumerate(tokens):
        if tok.type == 'blockquote_open' and i+2 < len(tokens) and tokens[i+2].type == 'inline':
            inline = tokens[i+2]
            match = re.match(r'^\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\](?:\n|$)', inline.content)
            if match:
                tok.attrSet('class', 'callout callout-' + match[1].lower())
                inline.content = inline.content[match.end():]
                inline.children = md.parseInline(inline.content)[0].children

    default_fence = md.renderer.rules['fence']

    def fence(items, index, options, env):
        tok = items[index]
        if tok.info.strip() == 'report-chart':
            try:
                spec = json.loads(tok.content)
            except json.JSONDecodeError as exc:
                raise ValueError(f'Invalid report-chart JSON at line {tok.map[0]+1}: {exc.msg}') from exc
            return chart(spec, tables)
        return default_fence(items, index, options, env)

    md.renderer.rules['fence'] = fence
    md.renderer.rules['html_block'] = lambda ts,i,o,e: '<pre class="raw-html">'+esc(ts[i].content)+'</pre>'
    md.renderer.rules['html_inline'] = lambda ts,i,o,e: esc(ts[i].content)
    # Render in chunks so ordinary tables and inline token rules remain standard Markdown.
    result, i = [], 0
    while i < len(tokens):
        if i in markers:
            i += 1
        elif tokens[i].type == 'table_open':
            rows,end = read_table(tokens,i)
            _,_,kind,name = table_info.get(i,(rows,end,'table',None))
            if kind == 'metrics':
                cards = []
                for row in rows[1:]:
                    cards.append(f'<div class="metric"><div class="metric-label">{esc(row[0])}</div><div class="metric-value">{esc(row[1])}</div><div class="metric-note">{esc(row[2] if len(row)>2 else "")}</div></div>')
                result.append('<div class="metrics">'+''.join(cards)+'</div>')
            else:
                attr = f' id="table-{esc(name)}"' if name else ''
                result.append(f'<div class="table-wrap"{attr}>'+md.renderer.render(tokens[i:end],md.options,{})+'</div>')
            i=end
        else:
            result.append(md.renderer.render(tokens[i:i+1],md.options,{}))
            i+=1
    template = (ROOT/'assets'/'report.html').read_text(encoding='utf-8')
    replacements = {
        'TITLE':esc(title), 'BODY':''.join(result),
        'TOC':'<nav aria-label="报告目录"><details><summary>报告目录</summary><ul>'+''.join(toc)+'</ul></details></nav>' if toc else '',
        'SOURCE_NAME':esc(source_name),
        'SOURCE_B64':base64.b64encode(source.encode('utf-8')).decode('ascii'),
        'SOURCE_HASH':hashlib.sha256(source.encode('utf-8')).hexdigest()[:16],
    }
    return re.sub(r'@@([A-Z0-9_]+)@@',lambda m:replacements[m[1]],template)


def build(source_path, output_path):
    source_path, output_path = Path(source_path), Path(output_path)
    if source_path.resolve() == output_path.resolve() or output_path.suffix.lower() not in ('.html','.htm'):
        raise ValueError('Output must be a separate .html or .htm file')
    source = source_path.read_text(encoding='utf-8-sig')
    output = render(source,source_path.name)
    output_path.parent.mkdir(parents=True,exist_ok=True)
    temp = output_path.with_suffix(output_path.suffix+'.tmp')
    temp.write_text(output,encoding='utf-8')
    temp.replace(output_path)
    return output_path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--watch',action='store_true')
    args=parser.parse_args()
    output=args.output or args.source.with_suffix('.html')
    last=None
    try:
        while True:
            try:
                stamp=args.source.stat().st_mtime_ns
                if stamp!=last:
                    last=stamp
                    print(f'Generated: {build(args.source,output)}',flush=True)
            except (ValueError,OSError) as exc:
                print(f'Error: {exc}',file=sys.stderr,flush=True)
                if not args.watch:
                    return 1
            if not args.watch:
                return 0
            time.sleep(1)
    except KeyboardInterrupt:
        return 0


if __name__=='__main__':
    sys.exit(main())

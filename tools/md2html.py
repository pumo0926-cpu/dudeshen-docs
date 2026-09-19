import re, html, os, json, shutil

def inline(s):
    s = html.escape(s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<![\w*])\*([^*\n]+)\*(?![\w*])', r'<em>\1</em>', s)
    return s

def convert(md):
    lines = md.split('\n')
    out, i, n = [], 0, len(lines)
    toc = []; hid = [0]
    while i < n:
        ln = lines[i]
        # fenced code
        if ln.startswith('```'):
            j = i + 1; buf = []
            while j < n and not lines[j].startswith('```'):
                buf.append(lines[j]); j += 1
            out.append('<pre><code>' + html.escape('\n'.join(buf)) + '</code></pre>')
            i = j + 1; continue
        # table
        if ln.startswith('|') and i + 1 < n and re.match(r'^\|[\s:*-]+\|', lines[i+1]):
            def cells(r): return [c.strip() for c in r.strip().strip('|').split('|')]
            head = cells(ln); j = i + 2; rows = []
            while j < n and lines[j].startswith('|'):
                rows.append(cells(lines[j])); j += 1
            t = ['<div class="tw"><table><thead><tr>']
            t += ['<th>' + inline(c) + '</th>' for c in head]
            t.append('</tr></thead><tbody>')
            for r in rows:
                t.append('<tr>' + ''.join('<td>' + inline(c) + '</td>' for c in r) + '</tr>')
            t.append('</tbody></table></div>')
            out.append(''.join(t)); i = j; continue
        # heading
        m = re.match(r'^(#{1,6})\s+(.*)$', ln)
        if m:
            lv = len(m.group(1)); txt = m.group(2).strip()
            hid[0] += 1; aid = 's%d' % hid[0]
            if lv == 2: toc.append((aid, re.sub(r'<[^>]+>', '', inline(txt))))
            out.append('<h%d id="%s">%s</h%d>' % (min(lv,4), aid, inline(txt), min(lv,4)))
            i += 1; continue
        # hr
        if re.match(r'^\s*---+\s*$', ln):
            out.append('<hr>'); i += 1; continue
        # blockquote
        if ln.startswith('>'):
            buf = []
            while i < n and lines[i].startswith('>'):
                buf.append(lines[i].lstrip('>').strip()); i += 1
            txt = '<br>'.join(inline(b) for b in buf if b) or ''
            out.append('<blockquote>' + txt + '</blockquote>'); continue
        # list
        if re.match(r'^\s*[-*]\s+', ln) or re.match(r'^\s*\d+[.)]\s+', ln):
            ordered = bool(re.match(r'^\s*\d+[.)]\s+', ln))
            tag = 'ol' if ordered else 'ul'
            items = []
            while i < n and (re.match(r'^\s*[-*]\s+', lines[i]) or re.match(r'^\s*\d+[.)]\s+', lines[i])):
                items.append(re.sub(r'^\s*(?:[-*]|\d+[.)])\s+', '', lines[i])); i += 1
            out.append('<%s>%s</%s>' % (tag, ''.join('<li>' + inline(x) + '</li>' for x in items), tag))
            continue
        if ln.strip() == '':
            i += 1; continue
        # paragraph
        buf = []
        while i < n and lines[i].strip() and not lines[i].startswith(('#','|','>','```')) \
              and not re.match(r'^\s*---+\s*$', lines[i]) \
              and not re.match(r'^\s*(?:[-*]|\d+[.)])\s+', lines[i]):
            buf.append(lines[i].strip()); i += 1
        out.append('<p>' + '<br>'.join(inline(b) for b in buf) + '</p>')
    return '\n'.join(out), toc

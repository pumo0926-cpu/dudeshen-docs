import sys, os, re, json, shutil, html
# 本脚本位于 <项目根>/h5-docs/tools/ ，路径由脚本位置推出，可在任意 cwd 下运行
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from md2html import convert

OUT = os.path.dirname(_HERE)          # <项目根>/h5-docs  ← 生成的静态站（即 dudeshen-docs 仓库）
SRC = os.path.dirname(OUT)            # <项目根>          ← Markdown 源文件与 content/ 所在目录
if len(sys.argv) > 1: SRC = os.path.abspath(sys.argv[1])
if len(sys.argv) > 2: OUT = os.path.abspath(sys.argv[2])
os.makedirs(OUT,exist_ok=True); os.makedirs(os.path.join(OUT,'md'),exist_ok=True)
os.makedirs(os.path.join(OUT,'content'),exist_ok=True)

DOCS=[
 ("01-竞品分析-Achieve3000.md","01","Achieve3000 竞品分析","定位、场景、要解决的问题、家长预期；含效果证据的真实水位"),
 ("02-Achieve3000-定位总结-人群·价值观·满意度.md","02a","定位总结：人群 · 价值观 · 满意度","四层人群、五条底层信念、四张满意度成绩单；剂量真相 8%"),
 ("02-中国初高中语英阅读产品可行性评估.md","02b","中国初高中语英阅读产品可行性评估","并行会话产出：需求、技术、效果、商业、政策五维评估"),
 ("03-纯C端阅读产品改良方案.md","03","纯 C 端阅读产品改良方案","并行会话产出：用户分层、主题系列化、每周节奏与家长报告"),
 ("04-合规红线与双内核方案（可行性补充）.md","04","合规红线与双内核方案","学科类身份、教育 App 备案、未成年人模式；语文不能分级的论证"),
 ("05-初中语文阅读产品方案-中文五步法.md","05","初中语文阅读产品方案：中文五步法","猜·读·问·辨·写；支架分层、三层追问、承诺边界"),
 ("06-初一首月阅读训练量与分地区内容规格.md","06","初一首月训练量与内容规格","首月 12＋4＋16 的量与排布；出题风格分支首版不实施，见 10"),
 ("07-有效性审查-按机制逐件审.md","07","有效性审查：按机制逐件审","七个零件逐件对证据；一处对 05 的自我纠正"),
 ("08-首月内容库-选文与练习.md","08","首月内容库：选文与练习","16 篇选文全文 ＋ 4 套周测 ＋ 172 道练习，可直接投产"),
 ("09-阅读问题诊断与可训练提升方案.md","09","阅读问题诊断与可训练提升方案","三道闸门、17 个微技能、6 种画像处方；配可试玩 Demo"),
 ("10-地区差异与首版收敛决定.md","10","地区差异与首版收敛决定","教材全国统一、差的是出题风格；课内篇目一律收全文（原型阶段）；同批补齐 4 套周测"),
]

CSS = """
:root{color-scheme:light dark;--plane:#f9f9f7;--surface:#fcfcfb;--surface-2:#f3f2ef;
--ink:#0b0b0b;--ink-2:#52514e;--ink-muted:#898781;--grid:#e1e0d9;--axis:#c3c2b7;
--border:rgba(11,11,11,.10);--accent:#2a78d6;--accent-soft:#86b6ef;--wash:#eaf2fd;--r:14px}
@media (prefers-color-scheme:dark){:root{--plane:#0d0d0d;--surface:#1a1a19;--surface-2:#232321;
--ink:#fff;--ink-2:#c3c2b7;--ink-muted:#898781;--grid:#2c2c2a;--axis:#383835;
--border:rgba(255,255,255,.10);--accent:#3987e5;--accent-soft:#6da7ec;--wash:#141c26}}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{margin:0;padding:0}
body{background:var(--plane);color:var(--ink);font-family:system-ui,-apple-system,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;font-size:16px;line-height:1.85;-webkit-font-smoothing:antialiased}
.wrap{max-width:720px;margin:0 auto;padding:0 18px 80px}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
.top{position:sticky;top:0;z-index:9;background:var(--plane);border-bottom:1px solid var(--border);padding:12px 18px;margin:0 -18px 0}
.top .in{max-width:720px;margin:0 auto;display:flex;align-items:center;gap:12px;font-size:13.5px}
.top b{font-weight:680;font-size:15px}
.top .sp{flex:1}
h1{font-size:30px;font-weight:700;letter-spacing:-.01em;line-height:1.3;margin:30px 0 12px}
h2{font-size:21px;font-weight:660;margin:34px 0 10px;padding-top:6px;border-top:1px solid var(--grid)}
h3{font-size:17px;font-weight:640;margin:24px 0 8px}
h4{font-size:15px;font-weight:620;margin:18px 0 6px;color:var(--ink-2)}
p{margin:0 0 14px;color:var(--ink-2)}
strong{color:var(--ink);font-weight:620}
hr{border:0;border-top:1px solid var(--grid);margin:26px 0}
blockquote{margin:0 0 16px;padding:12px 16px;background:var(--surface);border-left:3px solid var(--accent-soft);border-radius:0 10px 10px 0;color:var(--ink-2);font-size:15px}
blockquote strong{color:var(--ink)}
ul,ol{margin:0 0 16px;padding-left:22px;color:var(--ink-2)}
li{margin:0 0 6px}
code{background:var(--surface-2);border-radius:5px;padding:1px 5px;font-size:13.5px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
pre{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:14px;overflow-x:auto;margin:0 0 16px}
pre code{background:none;padding:0;font-size:12.5px;line-height:1.7}
.tw{overflow-x:auto;margin:0 0 18px;border:1px solid var(--border);border-radius:var(--r);background:var(--surface)}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--grid);color:var(--ink-2);vertical-align:top}
th{font-size:12px;color:var(--ink-muted);font-weight:560;white-space:nowrap;background:var(--surface-2)}
tr:last-child td{border-bottom:0}
td strong{color:var(--ink)}
.toc{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:14px 18px;margin:20px 0 28px}
.toc b{font-size:12px;letter-spacing:.14em;color:var(--ink-muted);text-transform:uppercase;display:block;margin-bottom:8px}
.toc a{display:block;font-size:14px;padding:3px 0;color:var(--ink-2)}
.toc a:hover{color:var(--accent)}
.notice{background:var(--wash);border-radius:10px;padding:11px 14px;font-size:13px;color:var(--ink-2);margin:18px 0}
.foot{border-top:1px solid var(--grid);margin-top:40px;padding-top:20px;font-size:12.5px;color:var(--ink-muted);line-height:1.9}
/* hub */
.hero{padding:44px 0 6px}
.hero .tag{display:inline-block;font-size:12.5px;color:var(--ink-muted);border:1px solid var(--border);border-radius:999px;padding:4px 12px;background:var(--surface)}
.hero h1{font-size:38px;margin:16px 0 10px}
.lead{font-size:17px;color:var(--ink-2);margin:0 0 6px}
.cards{display:grid;gap:12px;margin:14px 0 8px}
@media(min-width:560px){.cards.two{grid-template-columns:1fr 1fr}}
.card{display:block;background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:16px;color:inherit}
.card:hover{border-color:var(--accent-soft);text-decoration:none}
.card .k{font-size:11.5px;letter-spacing:.12em;color:var(--accent);text-transform:uppercase;margin-bottom:6px}
.card b{display:block;font-size:16.5px;font-weight:640;margin-bottom:4px;color:var(--ink)}
.card span{font-size:13.5px;color:var(--ink-muted);line-height:1.7}
.doc{display:flex;gap:14px;align-items:flex-start;background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:14px 16px;color:inherit}
.doc:hover{border-color:var(--accent-soft);text-decoration:none}
.doc .n{flex:0 0 40px;height:40px;border-radius:10px;background:var(--wash);color:var(--accent);display:grid;place-items:center;font-weight:700;font-size:14px}
.doc .t{flex:1;min-width:0}
.doc .t b{display:block;font-size:15.5px;font-weight:620;color:var(--ink)}
.doc .t span{font-size:13px;color:var(--ink-muted)}
.sec-h{font-size:12px;letter-spacing:.14em;color:var(--ink-muted);text-transform:uppercase;margin:34px 0 10px}
"""

def page(title, body, back=True, subtitle=""):
    nav = ('<div class="top"><div class="in"><a href="./">‹ 读得深 · 项目资料</a><span class="sp"></span>'
           '<span style="color:var(--ink-muted)">%s</span></div></div>' % html.escape(subtitle)) if back else ''
    return f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="theme-color" content="#f9f9f7" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0d0d0d" media="(prefers-color-scheme: dark)">
<style>{CSS}</style></head><body>{nav}<div class="wrap">{body}</div></body></html>"""

FOOT = ('<div class="foot">读得深 · 中学生阅读产品项目资料 · 2026-09<br>'
        '内部工作稿，对外公开仅为便于评审；文中数字与结论多为待验证建议，非承诺<br>'
        '名著与古诗文为公有领域作品，原文取自维基文库；原创选文版权自持<br>'
        '<a href="./">返回目录</a></div>')

nav_items=[]
for fn, key, title, desc in DOCS:
    md = open(os.path.join(SRC, fn), encoding='utf-8').read()
    body, toc = convert(md)
    tochtml = ''
    if len(toc) > 2:
        tochtml = '<div class="toc"><b>本篇目录</b>' + ''.join(
            '<a href="#%s">%s</a>' % (a, html.escape(t)) for a, t in toc) + '</div>'
    notice = ('<div class="notice">原始文件：<code>%s</code> · '
              '<a href="md/%s">下载 Markdown</a></div>' % (html.escape(fn), html.escape(fn)))
    out = notice + tochtml + body + FOOT
    open(os.path.join(OUT, 'doc-%s.html' % key), 'w', encoding='utf-8').write(
        page(title + ' · 读得深', out, True, key))
    shutil.copy(os.path.join(SRC, fn), os.path.join(OUT, 'md', fn))
    nav_items.append((key, title, desc))
shutil.copy(os.path.join(SRC,'content','month01.json'), os.path.join(OUT,'content','month01.json'))

hub = f"""<div class="hero">
<span class="tag">项目资料 · 2026-09</span>
<h1>读得深</h1>
<p class="lead">面向 C 端的初中语文阅读能力产品 —— 从 Achieve3000 竞品拆解，到可投产的首月内容库。</p>
<p style="font-size:13.5px;color:var(--ink-muted)">11 份文档 · 3 个可交互 Demo · 16 篇选文 · 120 道练习</p>
</div>

<div class="notice">这是一组<strong>内部工作稿</strong>，公开仅为便于评审。文中的定价、内容量、各项指标均为<strong>待验证建议，不是承诺</strong>；效果数据凡来自厂商宣称的均已标注。</div>

<div class="sec-h">可交互 Demo</div>
<div class="cards two">
  <a class="card" href="https://pumo0926-cpu.github.io/dudeshen-diagnose-demo/"><div class="k">分诊 · 新</div><b>三道闸门：初一分诊与训练</b><span>默认是孩子视角：读一篇、说一遍，再领今天该练的一件事；右上角「给大人看」才展开画像、判定规则与处方（对应文档 09）</span></a>
  <a class="card" href="https://pumo0926-cpu.github.io/dudeshen-reading-h5/"><div class="k">产品方案</div><b>五步法方案 H5</b><span>猜·读·问·辨·写的完整设计，含 Achieve3000 对照与承诺边界</span></a>
  <a class="card" href="https://pumo0926-cpu.github.io/dudeshen-month-demo/"><div class="k">月度 Demo</div><b>初一首月训练</b><span>16 篇选文全部可读，可走完整五步；首版不分地区</span></a>
</div>

<div class="sec-h">文档</div>
<div class="cards">
{''.join('<a class="doc" href="doc-%s.html"><span class="n">%s</span><span class="t"><b>%s</b><span>%s</span></span></a>' % (k, k.upper(), html.escape(t), html.escape(d)) for k, t, d in nav_items)}
</div>

<div class="sec-h">数据</div>
<div class="cards">
  <a class="doc" href="content/month01.json"><span class="n">JSON</span><span class="t"><b>首月内容库</b><span>16 篇选文全文 ＋ 4 套周测 ＋ 172 道练习的机器可读版本</span></span></a>
</div>

<div class="sec-h">怎么读这组文档</div>
<blockquote><strong>只看三篇：</strong>01（对标对象是什么）→ 07（我们这套到底有没有用）→ 08（内容长什么样）。<br>
<strong>关心可行性：</strong>04（合规红线）＋ 02B。<br>
<strong>关心怎么落地：</strong>05（机制）→ 06（规格）→ 09（分诊与疗程）→ 08（成品）。<br>
<strong>想知道最近改了什么：</strong>10（教材全国统一、出题风格才是地区变量；课内篇目放原文与版权处理）。</blockquote>

<div class="notice">02B、03、09 由并行会话产出，与其余各篇在个别判断上存在分歧（例如首批客户应否走学校渠道），分歧点已在 04 开头写明，未作统一。</div>
{FOOT}"""
open(os.path.join(OUT,'index.html'),'w',encoding='utf-8').write(page('读得深 · 中学生阅读产品项目资料', hub, False))
print('生成：', len(DOCS), '篇文档页 + 首页')
for f in sorted(os.listdir(OUT)): print('  ', f)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Une las 3 paginas del material comercial en un solo index.html navegable."""
import io, os, re, sys

# la carpeta del repo (la que contiene _fuente/), esté donde esté
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.path.join(BASE, "_fuente")
OUT  = os.path.join(BASE, "index.html")

def read(p):
    return io.open(p, encoding="utf-8").read()

# ------------------------------------------------------------------ css tools
def split_rules(css):
    """Divide CSS de nivel superior en (prelude, body|None). body None = at-rule sin bloque."""
    rules, buf, depth, i, n = [], [], 0, 0, len(css)
    quote = None
    prelude = None
    while i < n:
        c = css[i]
        if quote:
            buf.append(c)
            if c == "\\":
                if i + 1 < n:
                    buf.append(css[i+1]); i += 2; continue
            elif c == quote:
                quote = None
            i += 1; continue
        if c in "\"'":
            quote = c; buf.append(c); i += 1; continue
        if c == "/" and i + 1 < n and css[i+1] == "*":
            j = css.find("*/", i + 2)
            i = (j + 2) if j != -1 else n
            continue
        if c == "{":
            if depth == 0:
                prelude = "".join(buf).strip(); buf = []
            else:
                buf.append(c)
            depth += 1; i += 1; continue
        if c == "}":
            depth -= 1
            if depth == 0:
                rules.append((prelude, "".join(buf))); buf = []; prelude = None
            else:
                buf.append(c)
            i += 1; continue
        if c == ";" and depth == 0:
            s = "".join(buf).strip()
            if s:
                rules.append((s, None))
            buf = []; i += 1; continue
        buf.append(c); i += 1
    tail = "".join(buf).strip()
    if tail:
        rules.append((tail, None))
    return rules

GLOBAL_SELS = {":root", "html", "body", "*", "html, body", "body, html"}

def scope_css(css, scopes):
    """Prefija cada selector con los scopes dados. Devuelve (css_scoped, css_global)."""
    scoped, glob = [], []
    for prelude, body in split_rules(css):
        if body is None:
            glob.append(prelude + ";")
            continue
        p = prelude.strip()
        if p.startswith("@media") or p.startswith("@supports"):
            inner_s, inner_g = scope_css(body, scopes)
            if inner_s or inner_g:
                scoped.append("%s{%s%s}" % (p, inner_g, inner_s))
            continue
        if p.startswith("@"):          # keyframes, font-face: no se tocan
            glob.append("%s{%s}" % (p, body))
            continue
        parts = [s.strip() for s in p.split(",") if s.strip()]
        if all(s in GLOBAL_SELS for s in parts):
            glob.append("%s{%s}" % (p, body))
            continue
        new = []
        for s in parts:
            if s in GLOBAL_SELS:
                new += ["%s %s" % (sc, s) if s not in ("html", "body", ":root") else sc for sc in scopes]
            else:
                new += ["%s %s" % (sc, s) for sc in scopes]
        scoped.append("%s{%s}" % (",".join(new), body))
    return "\n".join(scoped), "\n".join(glob)

def styles_of(html):
    return "\n".join(re.findall(r"<style>(.*?)</style>", html, re.S))

def container_of(html):
    """Extrae el contenido de <body> sin <noscript>, <script> ni el back-link."""
    m = re.search(r"<body>(.*)</body>", html, re.S)
    b = m.group(1)
    b = re.sub(r"<noscript>.*?</noscript>", "", b, flags=re.S)
    b = re.sub(r"<script>.*?</script>", "", b, flags=re.S)
    b = re.sub(r'<a class="back-link".*?</a>\n?', "", b, flags=re.S)
    return b.strip()

# ------------------------------------------------------------------ fuentes
est = read(os.path.join(SRC, "estrategia.html"))
gui = read(os.path.join(SRC, "guiones.html"))
seg = read(os.path.join(SRC, "seguimiento.html"))

css_est_s, css_est_g = scope_css(styles_of(est), ["#v-estrategia"])
css_gui_s, css_gui_g = scope_css(styles_of(gui), ["#v-guiones"])
css_seg_s, css_seg_g = scope_css(styles_of(seg), ["#v-seguimiento"])

body_est = container_of(est)
body_gui = container_of(gui)
body_seg = container_of(seg)

SCRIPT = re.search(r"<script>(.*?)</script>", seg, re.S).group(1)

# ------------------------------------------------------------------ shell
SHELL_CSS = """
:root {
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --azul: #0C447C; --azul-medio: #1B4F8A; --azul-claro: #E6F1FB;
  --txt: #1a1d29; --txt2: #6b7189; --bg2: #f5f6f9; --bor: #e8eaef;
  color-scheme: light;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html { -webkit-text-size-adjust: 100%; scroll-behavior: auto; }
body { font-family: var(--font-sans); background: #fff; color: var(--txt);
  -webkit-font-smoothing: antialiased; overflow-x: hidden; }
button, input, textarea, select { font-family: inherit; }

/* ---- barra superior ---- */
.app-bar { position: sticky; top: 0; z-index: 50; background: rgba(255,255,255,.94);
  -webkit-backdrop-filter: saturate(180%) blur(10px); backdrop-filter: saturate(180%) blur(10px);
  border-bottom: 0.5px solid var(--bor); padding: env(safe-area-inset-top) 0 0; display: none; }
body.nav-on .app-bar { display: block; }
.app-bar-inner { max-width: 680px; margin: 0 auto; display: flex; align-items: center;
  gap: 6px; padding: 7px 10px; }
.app-home { flex-shrink: 0; width: 34px; height: 34px; border-radius: 9px; border: 0.5px solid var(--bor);
  background: var(--bg2); color: var(--azul-medio); font-size: 17px; line-height: 1;
  display: inline-flex; align-items: center; justify-content: center; cursor: pointer;
  -webkit-tap-highlight-color: transparent; }
.app-home:active { background: var(--azul-claro); }
.app-tabs { display: flex; gap: 5px; overflow-x: auto; -webkit-overflow-scrolling: touch;
  scrollbar-width: none; flex: 1; }
.app-tabs::-webkit-scrollbar { display: none; }
.app-tab { white-space: nowrap; border: 0.5px solid var(--bor); background: var(--bg2);
  color: var(--txt2); font-size: 12.5px; font-weight: 500; padding: 8px 12px; border-radius: 9px;
  cursor: pointer; -webkit-tap-highlight-color: transparent; transition: background .12s, color .12s; }
.app-tab[aria-current="page"] { background: var(--azul-medio); border-color: var(--azul-medio); color: #fff; }

/* ---- vistas ---- */
.vista { display: none; }
.vista.on { display: block; animation: fadein .18s ease; }
@keyframes fadein { from { opacity: 0; } to { opacity: 1; } }

/* ---- menu ---- */
#v-menu .wrap { padding: 1.75rem 1rem 3rem; max-width: 680px; margin: 0 auto; }
#v-menu .head { text-align: center; margin-bottom: 1.5rem; }
#v-menu .head h1 { font-size: 20px; font-weight: 600; margin-bottom: 4px; letter-spacing: -.01em; }
#v-menu .head p { font-size: 13px; color: var(--txt2); }
#v-menu .aviso { background: var(--azul-claro); color: var(--azul); font-size: 12px; line-height: 1.55;
  border-radius: 8px; padding: 10px 14px; margin-bottom: 1.75rem; display: flex; gap: 8px; align-items: flex-start; }
#v-menu .aviso i { margin-top: 1px; flex-shrink: 0; }
#v-menu .seccion { font-size: 11px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase;
  color: var(--azul-medio); margin: 0 0 10px 2px; }
#v-menu .card { display: block; width: 100%; text-align: left; text-decoration: none; color: inherit;
  background: var(--bg2); border: 0.5px solid var(--bor); border-radius: 12px;
  padding: 16px 18px; margin-bottom: 12px; cursor: pointer;
  -webkit-tap-highlight-color: transparent; transition: border-color .15s ease, transform .1s ease; }
#v-menu .card:active { transform: scale(.985); border-color: var(--azul-medio); }
@media (hover: hover) { #v-menu .card:hover { border-color: var(--azul-medio); transform: translateY(-1px); } }
#v-menu .card-top { display: flex; align-items: center; gap: 8px; margin-bottom: 5px; }
#v-menu .card-top i { color: var(--azul-medio); font-size: 17px; }
#v-menu .card h2 { font-size: 15.5px; font-weight: 600; }
#v-menu .card p { font-size: 12.5px; color: var(--txt2); line-height: 1.6; }
#v-menu .abrir { display: inline-block; margin-top: 10px; font-size: 12px; font-weight: 600; color: var(--azul-medio); }
#v-menu .pie { margin-top: 2rem; padding-top: 1rem; border-top: 0.5px solid var(--bor);
  font-size: 11.5px; color: var(--txt2); line-height: 1.6; text-align: center; }
"""

MENU = """<div class="wrap">
<div class="head">
<h1>Material Comercial · Scaling</h1>
<p>Guías de trabajo del proceso comercial</p>
</div>
<div class="aviso">
<i aria-hidden="true" class="ti ti-refresh"></i>
<span><strong>Estas páginas se actualizan.</strong> No guardes copias ni capturas: entra siempre por aquí para tener la última versión.</span>
</div>
<div class="seccion">Proceso de venta</div>
<button class="card" data-go="estrategia" type="button">
<div class="card-top"><i aria-hidden="true" class="ti ti-target-arrow"></i><h2>1. Estrategia Comercial Scaling</h2></div>
<p>¿A quién? ¿Por dónde? — el cliente principal (Humble Hungry Harry) y los canales de interacción, de los más fríos a los más cercanos.</p>
<span class="abrir">Abrir →</span>
</button>
<button class="card" data-go="guiones" type="button">
<div class="card-top"><i aria-hidden="true" class="ti ti-list-check"></i><h2>2. Reuniones</h2></div>
<p>El guion de cada tipo de reunión — pitch de asado, catch up, presentación, diagnóstico, propuesta, seguimiento y cierre — con la metodología Sandler.</p>
<span class="abrir">Abrir →</span>
</button>
<button class="card" data-go="seguimiento" type="button">
<div class="card-top"><i aria-hidden="true" class="ti ti-messages"></i><h2>3. Material seguimiento leads y cliente</h2></div>
<p>Los mensajes listos para copiar por etapa del viaje del lead — de desconocido a excliente — más la base de clientes de referencia agrupada por industria.</p>
<span class="abrir">Abrir →</span>
</button>
<div class="pie">
Material interno de Scaling · No compartir fuera del equipo<br/>
¿Falta algo o hay que corregir un contenido? Avísale a Sofía.
</div>
</div>"""

ROUTER = """
var VISTAS = ['menu','estrategia','guiones','seguimiento'];
var TITULOS = {
  menu: 'Material Comercial · Scaling',
  estrategia: 'Estrategia Comercial · Scaling',
  guiones: 'Reuniones · Scaling',
  seguimiento: 'Material seguimiento leads y cliente · Scaling'
};
function pintar(v) {
  if (VISTAS.indexOf(v) === -1) v = 'menu';
  for (var i = 0; i < VISTAS.length; i++) {
    var el = document.getElementById('v-' + VISTAS[i]);
    if (el) el.classList.toggle('on', VISTAS[i] === v);
  }
  document.body.classList.toggle('nav-on', v !== 'menu');
  var tabs = document.querySelectorAll('.app-tab');
  for (var j = 0; j < tabs.length; j++) {
    if (tabs[j].dataset.v === v) tabs[j].setAttribute('aria-current', 'page');
    else tabs[j].removeAttribute('aria-current');
  }
  document.title = TITULOS[v] || TITULOS.menu;
  window.scrollTo(0, 0);
}
function go(v) {
  if (('#' + v) === window.location.hash) { pintar(v); return; }
  window.location.hash = v;
}
function desdeHash() {
  var h = (window.location.hash || '').replace('#', '');
  if (VISTAS.indexOf(h) !== -1) { pintar(h); return; }
  if (h) {
    var anc = document.getElementById(h);
    if (anc) { anc.scrollIntoView({ behavior: 'smooth', block: 'start' }); return; }
  }
  pintar('menu');
}
window.addEventListener('hashchange', desdeHash);
document.addEventListener('click', function (e) {
  if (!e.target.closest) return;
  var t = e.target.closest('[data-go]');
  if (t) {
    e.preventDefault();
    go(t.dataset.go);
    var stage = t.dataset.stage;
    if (stage) {
      var sr = document.getElementById('stageradio-' + stage);
      if (sr) sr.checked = true;
      setTimeout(function () {
        var sp = document.getElementById('s' + t.dataset.spanel);
        if (sp) sp.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 80);
    }
    var rad = t.dataset.radio;
    if (rad) {
      var rr = document.getElementById(rad);
      if (rr) rr.checked = true;
      setTimeout(function () {
        var dest = document.getElementById(t.dataset.to || rad);
        if (dest) dest.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 250);
    }
    var seg = t.dataset.seg;
    if (seg) {
      var radio = document.getElementById('segradio-' + seg);
      if (radio) radio.checked = true;
      setTimeout(function () {
        var panel = document.getElementById('segpanel-' + seg);
        if (panel) panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 80);
    }
    return;
  }
  var sc = e.target.closest('[data-scroll]');
  if (sc) {
    e.preventDefault();
    var el = document.getElementById(sc.dataset.scroll);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
});
document.addEventListener('DOMContentLoaded', desdeHash);
desdeHash();
"""

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0, viewport-fit=cover" name="viewport"/>
<meta content="noindex, nofollow" name="robots"/>
<meta content="#0C447C" name="theme-color"/>
<meta content="yes" name="mobile-web-app-capable"/>
<meta content="Material Comercial · Scaling" property="og:title"/>
<meta content="Estrategia comercial, guiones de reunión y mensajes de seguimiento. Uso interno." property="og:description"/>
<title>Material Comercial · Scaling</title>
<link href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%230C447C'/%3E%3Ctext x='16' y='22' font-family='Helvetica,Arial' font-size='17' font-weight='bold' fill='white' text-anchor='middle'%3ES%3C/text%3E%3C/svg%3E" rel="icon"/>
<link href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@2.47.0/dist/tabler-icons.min.css" rel="stylesheet"/>
<style>
__SHELL__
/* ===== globales heredados ===== */
__GLOB__
/* ===== estrategia ===== */
__CSS_EST__
/* ===== guiones ===== */
__CSS_GUI__
/* ===== seguimiento ===== */
__CSS_SEG__
</style>
</head>
<body>
<noscript>
<div style="margin: 1rem; padding: 14px; background: #FDF0F0; border: 1px solid #E08787; border-radius: 8px; color: #6B2B2B; font-family: sans-serif; font-size: 14px;">
<strong>Este documento necesita JavaScript activado.</strong><br/>
    Si lo estás viendo dentro de WhatsApp, Gmail u otra vista previa, ábrelo directamente en Chrome o Safari (botón "Abrir en el navegador" o "Compartir → Abrir con...").
  </div>
</noscript>

<div class="app-bar">
<div class="app-bar-inner">
<button aria-label="Volver al inicio" class="app-home" data-go="menu" type="button"><i aria-hidden="true" class="ti ti-home"></i></button>
<nav class="app-tabs">
<button class="app-tab" data-go="estrategia" data-v="estrategia" type="button">1. Estrategia</button>
<button class="app-tab" data-go="guiones" data-v="guiones" type="button">2. Reuniones</button>
<button class="app-tab" data-go="seguimiento" data-v="seguimiento" type="button">3. Seguimiento</button>
</nav>
</div>
</div>

<div class="vista on" id="v-menu">__MENU__</div>
<div class="vista" id="v-estrategia">__BODY_EST__</div>
<div class="vista" id="v-guiones">__BODY_GUI__</div>
<div class="vista" id="v-seguimiento">__BODY_SEG__</div>

<script>
__SCRIPT__
__ROUTER__
</script>
</body>
</html>
"""

glob_all = "\n".join(x for x in (css_est_g, css_gui_g, css_seg_g) if x.strip())
# los globales heredados repiten :root/body/*: los del shell mandan, se dejan antes
out = (HTML
       .replace("__SHELL__", SHELL_CSS)
       .replace("__GLOB__", "")            # el shell ya cubre :root/html/body/*
       .replace("__CSS_EST__", css_est_s)
       .replace("__CSS_GUI__", css_gui_s)
       .replace("__CSS_SEG__", css_seg_s)
       .replace("__MENU__", MENU)
       .replace("__BODY_EST__", body_est)
       .replace("__BODY_GUI__", body_gui)
       .replace("__BODY_SEG__", body_seg)
       .replace("__SCRIPT__", SCRIPT)
       .replace("__ROUTER__", ROUTER))

io.open(OUT, "w", encoding="utf-8").write(out)
print("index.html:", len(out), "bytes")

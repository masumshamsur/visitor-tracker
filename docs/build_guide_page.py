"""Build docs/console-deploy-guide.html from docs/console-deploy-guide.md.

Usage:  python3 docs/build_guide_page.py
The Markdown file is the single source of truth; the HTML page embeds it and
renders one step at a time in the browser.
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
md = (HERE / "console-deploy-guide.md").read_text()

# Inline the architecture diagram (the Markdown links the .svg file, which GitHub renders).
svg = (HERE / "console-architecture.svg").read_text()
svg = "".join(line.strip() for line in svg.splitlines() if line.strip())  # no blank lines inside the HTML block
md = md.replace(
    "![visitor-tracker AWS architecture](console-architecture.svg)",
    '<div class="diagram">' + svg + "</div>",
)
payload = json.dumps(md).replace("</", "<\\/")

TEMPLATE = r"""<meta charset="utf-8">
<title>visitor-tracker Console Guide</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">
<style>
/* Layout: sticky step index on the left, one step at a time on the right; index collapses to a picker on phones. */
:root {
  --bg: #f4f6f8; --panel: #ffffff; --fg: #17202a; --muted: #5a6776; --line: #dde3ea;
  --accent: #0e6e7a; --accent-soft: #e2f1f3; --done: #23803f; --done-soft: #e3f3e8;
  --warn-soft: #fff4dc; --warn-line: #e5b649; --code-bg: #0f1a24; --code-fg: #dbe7f0;
  --font-sans: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #0d1318; --panel: #141c23; --fg: #e3e9ef; --muted: #93a1af; --line: #25313c;
  --accent: #4fb8c4; --accent-soft: #133037; --done: #5ccf80; --done-soft: #12301d;
  --warn-soft: #2e2512; --warn-line: #b38a2c; --code-bg: #0a1016; --code-fg: #d5e2ec; color-scheme: dark; } }
:root[data-theme="dark"] {
  --bg: #0d1318; --panel: #141c23; --fg: #e3e9ef; --muted: #93a1af; --line: #25313c;
  --accent: #4fb8c4; --accent-soft: #133037; --done: #5ccf80; --done-soft: #12301d;
  --warn-soft: #2e2512; --warn-line: #b38a2c; --code-bg: #0a1016; --code-fg: #d5e2ec; color-scheme: dark; }
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--fg); font: 15px/1.6 var(--font-sans); }
.wrap { max-width: 1180px; margin: 0 auto; padding-block: 24px 48px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
.top { display: flex; flex-wrap: wrap; align-items: end; justify-content: space-between; gap: 12px 24px; margin-bottom: 20px; }
.top h1 { margin: 0; font-size: 24px; text-wrap: balance; }
.top p { margin: 2px 0 0; color: var(--muted); }
.progress { min-width: 220px; flex: 0 1 300px; }
.progress .lbl { font-size: 13px; color: var(--muted); display: flex; justify-content: space-between; font-variant-numeric: tabular-nums; }
.bar { height: 8px; border-radius: 4px; background: var(--line); overflow: hidden; margin-top: 4px; }
.bar i { display: block; height: 100%; background: var(--done); width: 0; transition: width .3s; }
.layout { display: grid; grid-template-columns: 280px minmax(0, 1fr); gap: 24px; align-items: start; }
nav.index { position: sticky; top: calc(16px + env(safe-area-inset-top, 0px)); max-height: calc(100vh - 32px); overflow: auto;
  background: var(--panel); border: 1px solid var(--line); border-radius: 10px; padding: 10px 8px; }
nav.index .ph { font-size: 11px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); padding: 12px 10px 4px; }
nav.index a { display: grid; grid-template-columns: 22px 1fr; gap: 6px; align-items: start; padding: 5px 10px; border-radius: 6px;
  color: var(--fg); text-decoration: none; font-size: 14px; line-height: 1.35; }
nav.index a:hover { background: var(--accent-soft); }
nav.index a.cur { background: var(--accent-soft); color: var(--accent); font-weight: 600; }
nav.index a .n { font-family: var(--font-mono); font-size: 12px; color: var(--muted); padding-top: 1px; }
nav.index a.done .n { color: var(--done); }
nav.index a.done .n::before { content: "✓"; }
nav.index a.done .n span { display: none; }
.picker { display: none; }
article { background: var(--panel); border: 1px solid var(--line); border-radius: 10px; padding: 28px 32px; min-width: 0; }
.crumb { font-size: 12px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; color: var(--accent); }
article h2 { font-size: 26px; margin: 4px 0 14px; line-height: 1.25; text-wrap: balance; }
article h1 { font-size: 26px; margin: 0 0 12px; }
article h3 { font-size: 16px; margin: 26px 0 8px; }
article p, article li { max-width: 72ch; }
article ul, article ol { padding-left: 22px; }
article li { margin: 4px 0; }
article li > ul, article li > ol { margin: 4px 0; }
article a { color: var(--accent); }
article strong { font-weight: 600; }
code { font-family: var(--font-mono); font-size: .88em; background: var(--accent-soft); padding: 1px 5px; border-radius: 4px; overflow-wrap: anywhere; }
.codebox { position: relative; margin: 12px 0; }
pre { background: var(--code-bg); color: var(--code-fg); border-radius: 8px; padding: 14px 16px; overflow-x: auto; margin: 0; font-size: 13px; line-height: 1.55; }
pre code { background: none; padding: 0; color: inherit; font-size: inherit; overflow-wrap: normal; }
.copy { position: absolute; top: 8px; right: 8px; font: 500 12px var(--font-sans); padding: 3px 9px; border-radius: 5px; cursor: pointer;
  border: 1px solid #3a4a58; background: #1b2834; color: #cfdbe5; }
.copy:hover { background: #26384a; }
blockquote { margin: 14px 0; padding: 10px 14px; border-left: 4px solid var(--warn-line); background: var(--warn-soft); border-radius: 0 8px 8px 0; }
blockquote p { margin: 4px 0; }
.tablebox { overflow-x: auto; margin: 12px 0; }
.diagram { overflow-x: auto; margin: 14px 0 18px; border: 1px solid var(--line); border-radius: 10px; background: #ffffff; }
.diagram svg { display: block; width: 100%; min-width: 760px; height: auto; }
table { border-collapse: collapse; font-size: 14px; min-width: 100%; }
th, td { text-align: left; padding: 7px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }
th { font-size: 12px; text-transform: uppercase; letter-spacing: .04em; color: var(--muted); }
li.task { list-style: none; margin-left: -22px; }
li.task label { display: flex; gap: 10px; align-items: flex-start; cursor: pointer; padding: 4px 8px; border-radius: 6px; }
li.task label:hover { background: var(--accent-soft); }
li.task input { margin-top: 4px; width: 16px; height: 16px; accent-color: var(--done); flex: none; }
li.task.checked span { color: var(--muted); text-decoration: line-through; text-decoration-color: var(--muted); }
.verify-state { display: inline-block; margin-left: 8px; font-size: 12px; font-weight: 600; padding: 2px 8px; border-radius: 999px; background: var(--line); color: var(--muted); vertical-align: 2px; }
.verify-state.ok { background: var(--done-soft); color: var(--done); }
.pager { display: flex; justify-content: space-between; gap: 12px; margin-top: 32px; padding-top: 18px; border-top: 1px solid var(--line); flex-wrap: wrap; }
.pager button { font: 600 14px var(--font-sans); padding: 10px 16px; border-radius: 8px; cursor: pointer; border: 1px solid var(--accent);
  background: transparent; color: var(--accent); max-width: 100%; text-align: left; }
.pager button.next { background: var(--accent); color: var(--panel); margin-left: auto; }
.pager button:disabled { visibility: hidden; }
.pager small { display: block; font-weight: 400; font-size: 12px; opacity: .85; }
button:focus-visible, a:focus-visible, input:focus-visible, select:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.reset { background: none; border: 0; color: var(--muted); font: 13px var(--font-sans); text-decoration: underline; cursor: pointer; padding: 0; margin-top: 4px; }
@media (max-width: 860px) {
  .layout { grid-template-columns: minmax(0, 1fr); }
  nav.index { display: none; }
  .picker { display: block; margin-bottom: 12px; }
  .picker select { width: 100%; font: 15px var(--font-sans); padding: 10px; border-radius: 8px; border: 1px solid var(--line); background: var(--panel); color: var(--fg); }
  article { padding: 20px 16px; }
  article h2 { font-size: 22px; }
}
@media (prefers-reduced-motion: reduce) { .bar i { transition: none; } }
</style>

<div class="wrap">
  <header class="top">
    <div>
      <h1>visitor-tracker · Infrastructure Guide</h1>
      <p>Attempt 1: AWS Console (Steps 1–31) · Attempt 2: Terraform (Steps T1–T16)</p>
    </div>
    <div class="progress">
      <div class="lbl"><span id="plabel">0 of 0 steps verified</span><span id="ppct">0%</span></div>
      <div class="bar"><i id="pbar"></i></div>
      <button class="reset" id="reset" type="button">Clear my ticks</button>
    </div>
  </header>
  <div class="layout">
    <nav class="index" id="index" aria-label="Steps"></nav>
    <main style="min-width:0">
      <div class="picker"><label for="pick" class="crumb">Jump to step</label><select id="pick"></select></div>
      <article id="view"></article>
    </main>
  </div>
</div>

<script id="guide-md" type="application/json">__PAYLOAD__</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js"></script>
<script>
(function () {
  const md = JSON.parse(document.getElementById("guide-md").textContent);
  const store = {
    get(k) { try { return JSON.parse(localStorage.getItem("cloudops-guide:" + k)); } catch { return null; } },
    set(k, v) { try { localStorage.setItem("cloudops-guide:" + k, JSON.stringify(v)); } catch {} },
  };

  // Split the Markdown into an overview plus steps grouped by phase.
  const pages = [{ id: "overview", num: "", title: "Overview & names", phase: "Start here", body: [] }];
  let phase = "Start here", cur = pages[0];
  for (const line of md.split("\n")) {
    let m;
    if ((m = line.match(/^# ((?:Phase|Attempt) .*)$/))) { phase = m[1]; continue; }
    if (/^# /.test(line)) continue; // document title
    if ((m = line.match(/^## Step ([A-Z]?\d+) · (.*)$/))) {
      cur = { id: "step-" + m[1].toLowerCase(), num: m[1], title: m[2], phase, body: [] };
      pages.push(cur); continue;
    }
    cur.body.push(line);
  }
  const steps = pages.filter(p => p.num);
  const checks = store.get("checks") || {};

  function taskCount(p) { return (p.body.join("\n").match(/^\s*- \[ \]/gm) || []).length; }
  function isDone(p) {
    const n = taskCount(p); if (!n) return false;
    for (let i = 0; i < n; i++) if (!checks[p.id + ":" + i]) return false;
    return true;
  }

  const index = document.getElementById("index"), pick = document.getElementById("pick"), view = document.getElementById("view");
  function buildIndex() {
    index.innerHTML = ""; pick.innerHTML = "";
    let last = null, group = null;
    pages.forEach(p => {
      if (p.phase !== last) {
        last = p.phase;
        const h = document.createElement("div"); h.className = "ph"; h.textContent = p.phase; index.appendChild(h);
        group = document.createElement("optgroup"); group.label = p.phase; pick.appendChild(group);
      }
      const a = document.createElement("a");
      a.href = "#" + p.id; a.dataset.id = p.id;
      a.innerHTML = '<span class="n"><span></span></span><span></span>';
      a.firstChild.firstChild.textContent = p.num || "•";
      a.lastChild.textContent = p.title;
      index.appendChild(a);
      const o = document.createElement("option"); o.value = p.id;
      o.textContent = (p.num ? p.num + ". " : "") + p.title; group.appendChild(o);
    });
  }

  function refreshProgress(activeId) {
    const done = steps.filter(isDone).length;
    document.getElementById("plabel").textContent = done + " of " + steps.length + " steps verified";
    const pct = Math.round(done / steps.length * 100);
    document.getElementById("ppct").textContent = pct + "%";
    document.getElementById("pbar").style.width = pct + "%";
    index.querySelectorAll("a").forEach(a => {
      const p = pages.find(x => x.id === a.dataset.id);
      a.classList.toggle("done", isDone(p));
      a.classList.toggle("cur", a.dataset.id === activeId);
    });
    pick.querySelectorAll("option").forEach(o => {
      const p = pages.find(x => x.id === o.value);
      o.textContent = (isDone(p) ? "✓ " : "") + (p.num ? p.num + ". " : "") + p.title;
    });
    pick.value = activeId;
  }

  function render(id) {
    const i = Math.max(0, pages.findIndex(p => p.id === id));
    const p = pages[i];
    let html = "";
    if (p.num) html += '<div class="crumb">' + p.phase + " · Step " + p.num + " of " + steps.length + "</div><h2></h2>";
    html += marked.parse(p.body.join("\n"), { gfm: true });
    view.innerHTML = html;
    if (p.num) view.querySelector("h2").textContent = p.title;

    // Wrap code blocks with copy buttons and tables with scroll boxes.
    view.querySelectorAll("pre").forEach(pre => {
      const box = document.createElement("div"); box.className = "codebox";
      pre.replaceWith(box); box.appendChild(pre);
      const b = document.createElement("button"); b.className = "copy"; b.type = "button"; b.textContent = "Copy";
      b.onclick = () => {
        const text = pre.innerText.replace(/\n$/, "");
        const ok = () => { b.textContent = "Copied"; setTimeout(() => (b.textContent = "Copy"), 1400); };
        if (navigator.clipboard) navigator.clipboard.writeText(text).then(ok, () => selectText(pre)); else selectText(pre);
      };
      box.appendChild(b);
    });
    view.querySelectorAll("table").forEach(t => { const d = document.createElement("div"); d.className = "tablebox"; t.replaceWith(d); d.appendChild(t); });

    // Make task-list checkboxes interactive and persistent.
    let k = 0;
    view.querySelectorAll("li > input[type=checkbox]").forEach(cb => {
      const li = cb.parentElement, key = p.id + ":" + k++;
      li.classList.add("task");
      const label = document.createElement("label"), span = document.createElement("span");
      while (cb.nextSibling) span.appendChild(cb.nextSibling);
      cb.removeAttribute("disabled"); cb.checked = !!checks[key];
      label.append(cb, span); li.appendChild(label);
      li.classList.toggle("checked", cb.checked);
      cb.onchange = () => {
        checks[key] = cb.checked; store.set("checks", checks);
        li.classList.toggle("checked", cb.checked);
        updateVerifyBadge(p); refreshProgress(p.id);
      };
    });
    updateVerifyBadge(p);

    // Previous / next.
    const pager = document.createElement("div"); pager.className = "pager";
    const prev = pages[i - 1], next = pages[i + 1];
    pager.innerHTML = '<button type="button" class="prev"></button><button type="button" class="next"></button>';
    const [bp, bn] = pager.querySelectorAll("button");
    if (prev) { bp.innerHTML = "<small>Previous</small>"; bp.append("← " + (prev.num ? prev.num + ". " : "") + prev.title); bp.onclick = () => go(prev.id); } else bp.disabled = true;
    if (next) { bn.innerHTML = "<small>" + (p.num && !isDone(p) ? "Next (finish Verify first)" : "Next") + "</small>"; bn.append((next.num ? next.num + ". " : "") + next.title + " →"); bn.onclick = () => go(next.id); } else bn.disabled = true;
    view.appendChild(pager);

    store.set("last", p.id);
    refreshProgress(p.id);
  }

  function updateVerifyBadge(p) {
    const h = [...view.querySelectorAll("h3")].find(x => /^Verify/.test(x.textContent));
    if (!h) return;
    let badge = h.querySelector(".verify-state");
    if (!badge) { badge = document.createElement("span"); badge.className = "verify-state"; h.appendChild(badge); }
    const n = taskCount(p), got = [...Array(n).keys()].filter(i => checks[p.id + ":" + i]).length;
    badge.textContent = got === n ? "All passed" : got + " / " + n;
    badge.classList.toggle("ok", got === n);
  }

  function selectText(el) { const r = document.createRange(); r.selectNodeContents(el); const s = getSelection(); s.removeAllRanges(); s.addRange(r); }
  function go(id) { if (location.hash !== "#" + id) location.hash = id; else render(id); window.scrollTo({ top: 0 }); }

  pick.onchange = () => go(pick.value);
  document.getElementById("reset").onclick = function () {
    if (this.dataset.armed) {
      for (const key in checks) delete checks[key];
      store.set("checks", checks); this.textContent = "Clear my ticks"; delete this.dataset.armed;
      render(location.hash.slice(1) || "overview");
    } else { this.dataset.armed = "1"; this.textContent = "Click again to clear all ticks"; setTimeout(() => { this.textContent = "Clear my ticks"; delete this.dataset.armed; }, 3000); }
  };
  window.addEventListener("hashchange", () => render(location.hash.slice(1)));
  buildIndex();
  render(location.hash.slice(1) || store.get("last") || "overview");
})();
</script>
"""

out = HERE / "console-deploy-guide.html"
def ascii_safe(html):
    """Escape non-ASCII so the page renders correctly even when served without a charset."""
    import re
    def esc(block, kind):
        def one(c):
            if ord(c) < 128:
                return c
            return {"script": "\\u%04x", "style": "\\%x "}.get(kind, "&#x%x;") % ord(c)
        return "".join(one(c) for c in block)
    parts = re.split(r"(<script[^>]*>.*?</script>|<style>.*?</style>)", html, flags=re.S)
    return "".join(esc(x, "script" if x.startswith("<script") else "style" if x.startswith("<style") else "html") for x in parts)


out.write_text(ascii_safe(TEMPLATE.replace("__PAYLOAD__", payload)), encoding="utf-8")
print(f"wrote {out}")

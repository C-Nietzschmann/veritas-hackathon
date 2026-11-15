// TENSEGRITY demo page: asks app/server.py and draws what the engine says, one step at a time.
// No framework: plain DOM and hand-drawn SVG, so every line can be read and explained.

const $ = (selector) => document.querySelector(selector);
const fmt = (n) => Number(n).toLocaleString("en-GB");
const pct = (x) => `${Math.round(x * 100)}%`;
const sleep = (ms) => new Promise((done) => setTimeout(done, ms));
const NS = "http://www.w3.org/2000/svg";

let overview = null;   // the pipeline's own counts (/api/overview)
let current = null;    // the company on screen (/api/company/<number>)
let whatIf = false;    // the "birth month one off" switch in the inspector

async function api(path) {
  const answer = await fetch(path);
  if (!answer.ok) throw new Error(`${path}: ${answer.status}`);
  return answer.json();
}

// --- Views -------------------------------------------------------------------------------

function show(view) {
  document.querySelectorAll(".tabs button").forEach((b) => b.classList.toggle("on", b.dataset.view === view));
  document.querySelectorAll(".view").forEach((v) => v.classList.toggle("on", v.id === `view-${view}`));
  $("#index-mid").textContent = view === "check"
    ? "Did a director of this company run one that went insolvent?"
    : "Six steps from the register to a match score";
  if (view === "how" && !$("#modules").children.length) drawModules();
}
document.querySelectorAll(".tabs button").forEach((b) => b.addEventListener("click", () => show(b.dataset.view)));

// --- 01 / Check: the engine, five steps ----------------------------------------------------

const STEPS = ["Register", "Blocking", "Matcher", "Insolvent", "Answer"];

function drawEngine() {
  $("#engine").innerHTML = STEPS.map((title, i) => `
    <div class="step" id="step-${i}">
      <b class="run"></b>
      <div class="step-head mono"><span>0${i + 1} <i>/</i> <b>${title}</b></span><span class="state">Waiting</span></div>
      <div class="step-value">—</div>
      <div class="step-note"></div>
      ${i === 2 ? '<div class="bars"></div>' : ""}
    </div>`).join("");
}

function countUp(element, to, decimals, unit) {
  // A number that counts up to its value, so a step visibly does its work
  const start = performance.now(), length = 520;
  return new Promise((done) => {
    function frame(now) {
      const t = Math.min((now - start) / length, 1), eased = 1 - Math.pow(1 - t, 3);
      const value = decimals ? (to * eased).toFixed(decimals) : fmt(Math.round(to * eased));
      element.innerHTML = `${value}${unit ? `<small>${unit}</small>` : ""}`;
      if (t < 1) requestAnimationFrame(frame); else done();
    }
    requestAnimationFrame(frame);
  });
}

async function runStep(i, step) {
  const cell = $(`#step-${i}`);
  cell.classList.add("live");
  cell.querySelector(".state").textContent = "Running";
  const value = cell.querySelector(".step-value");
  if (typeof step.value === "string") {
    await sleep(250);
    value.textContent = step.value;
  } else {
    await countUp(value, step.value, step.key === "matcher" ? 2 : 0, step.unit);   // a score always has two decimals
  }
  cell.querySelector(".step-note").textContent = step.note;
  if (step.scores) {   // the matcher's scores for every proposed pair, highest first
    const bars = cell.querySelector(".bars");
    const shown = step.scores.slice(0, 16);   // the 16 highest, enough to see the shape
    bars.innerHTML = shown.map((s) => `<b class="${s >= 0.5 ? "hot" : ""}"></b>`).join("");
    requestAnimationFrame(() => bars.querySelectorAll("b").forEach((b, k) => {
      b.style.height = `${Math.max(3, shown[k] * 46)}px`;
    }));
  }
  if (step.key === "answer" && current.warning) cell.classList.add("alert");
  cell.classList.replace("live", "done");
  cell.querySelector(".state").textContent = "Done";
}

// --- The evidence graph, drawn by hand in SVG ----------------------------------------------

const COLUMNS = { query: 112, director: 420, record: 838, earlier: 1182 };
const ROLE_TITLES = { query: "This company", director: "Its directors", record: "Records elsewhere", earlier: "Earlier companies" };
const BOX = { w: 210, h: 50 };

function el(tag, attributes, parent) {
  const node = document.createElementNS(NS, tag);
  Object.entries(attributes).forEach(([k, v]) => node.setAttribute(k, v));
  if (parent) parent.appendChild(node);
  return node;
}

function layout(nodes) {
  // Each role is a column; the boxes in a column are spaced evenly around the middle
  const place = {};
  Object.keys(COLUMNS).forEach((role) => {
    const column = nodes.filter((n) => n.role === role);
    column.forEach((n, k) => { place[n.id] = { x: COLUMNS[role], y: 196 + (k - (column.length - 1) / 2) * 76 }; });
  });
  return place;
}

function edge(a, b) {
  // From the facing side of one box to the facing side of the other
  const [left, right] = a.x < b.x ? [a, b] : [b, a];
  return { x1: left.x + BOX.w / 2, y1: left.y, x2: right.x - BOX.w / 2, y2: right.y };
}

function drawGraph(graph) {
  const svg = $("#graph");
  svg.innerHTML = "";
  const place = layout(graph.nodes);
  const layers = { lines: el("g", {}, svg), nodes: el("g", {}, svg) };

  Object.entries(ROLE_TITLES).forEach(([role, title]) => {
    if (graph.nodes.some((n) => n.role === role)) {
      el("text", { x: COLUMNS[role], y: 34, class: "role appear", "text-anchor": "middle", "data-stage": stageOf(role) }, svg)
        .textContent = title.toUpperCase();
    }
  });

  graph.lines.forEach((line) => {
    const a = place[line.from], b = place[line.to];
    if (!a || !b) return;
    const g = el("g", { class: "appear", "data-line": line.id, "data-stage": line.kind === "guess" ? 2 : stageOfLine(line, graph) }, layers.lines);
    const e = edge(a, b);
    const strong = line.kind === "guess" && line.p >= 0.5;
    const path = el("line", { ...e, class: `line ${line.kind}${strong ? " strong" : ""}` }, g);
    el("line", { ...e, class: "hit" }, g);
    if (line.kind === "guess") {
      const text = `${line.words.toUpperCase()} · ${line.p.toFixed(2)}`;
      const mx = (e.x1 + e.x2) / 2, my = (e.y1 + e.y2) / 2 - 14;
      el("rect", { x: mx - text.length * 4.2, y: my - 14, width: text.length * 8.4, height: 20, class: "label-back" }, g);
      el("text", { x: mx, y: my, "text-anchor": "middle", class: `label${strong ? " strong" : ""}` }, g).textContent = text;
      path.style.strokeDashoffset = 0;
    }
    g.addEventListener("click", () => pick(line.id));
  });

  graph.nodes.forEach((n) => {
    const p = place[n.id];
    const tall = n.role === "earlier";
    const g = el("g", { class: `node ${n.company ? "company" : ""} ${n.role} appear`, "data-stage": stageOf(n.role),
      transform: `translate(${p.x - BOX.w / 2}, ${p.y - (tall ? 32 : BOX.h / 2)})` }, layers.nodes);
    el("rect", { width: BOX.w, height: tall ? 64 : BOX.h }, g);
    el("text", { x: BOX.w / 2, y: tall ? 27 : 32, "text-anchor": "middle" }, g).textContent = n.label;
    if (tall) el("text", { x: BOX.w / 2, y: 48, "text-anchor": "middle", class: "sub" }, g).textContent = `INSOLVENT ${n.insolvent}`;
  });
}

function stageOf(role) {
  return { query: 0, director: 0, record: 1, earlier: 3 }[role];
}

function stageOfLine(line, graph) {
  // A register fact to an earlier company appears with that company; one to this company, at once
  const target = graph.nodes.find((n) => n.id === line.to);
  return target && target.role === "earlier" ? 3 : 0;
}

function reveal(stage) {
  document.querySelectorAll(`#graph [data-stage="${stage}"]`).forEach((node) => node.classList.add("in"));
}

function emptyGraph(message) {
  $("#graph").innerHTML = `<text x="650" y="196" text-anchor="middle" class="empty">${message.toUpperCase()}</text>`;
}

// --- The inspector: what is behind one line ------------------------------------------------

function pick(lineId) {
  document.querySelectorAll("#graph [data-line]").forEach((g) => g.classList.toggle("pick", g.dataset.line === lineId));
  const item = current.inspect[lineId];
  if (whatIf) {          // a new line undoes the what-if
    whatIf = false;
    drawVerdicts();
  }
  item.kind === "guess" ? inspectGuess(item) : inspectFact(item);
  showResult();
}

function wordsFor(p) {
  return p >= 0.8 ? "likely" : p >= 0.4 ? "possible" : "unlikely";   // the same lines as interface.in_words
}

function withBirthOff(item) {
  // The same pair with the birth month one off: that number becomes 0, so its share of the sum goes
  const birth = item.parts.find((part) => part.feature === "Same birth month and year");
  const p = item.what_if.birth_month_off;
  return { ...item, p, words: wordsFor(p), sum: item.sum - (birth ? birth.product : 0),
    fields: item.fields.map((f) => (f.field.startsWith("Born") ? { ...f, verdict: "one month off" } : f)),
    parts: item.parts.map((part) => (part === birth ? { ...part, value: 0, product: 0 } : part)) };
}

function inspectGuess(item) {
  const shown = whatIf ? withBirthOff(item) : item;
  const all = [{ feature: "Starting point", product: shown.start }, ...shown.parts];
  const scale = Math.max(...[{ product: item.start }, ...item.parts].map((p) => Math.abs(p.product)));
  $("#inspector").innerHTML = `
    <div class="insp-head mono"><span>Dashed line <i>/</i> our guess</span><span>${whatIf ? "What if" : "Same person?"}</span></div>
    <div class="insp-body">
      <div class="insp-score"><b class="${shown.p >= 0.5 ? "strong" : ""}">${shown.p.toFixed(2)}</b>
        <span>match score: ${shown.words} the same person</span></div>
      <div class="fields">${shown.fields.map((f) => `<div>${f.field}<b class="${/different|off/.test(f.verdict) ? "no" : ""}">${f.verdict}</b></div>`).join("")}</div>
      <div class="ledger">
        ${all.map((p) => `<span class="lbl">${p.feature}</span>
          <span class="track"><b class="fill ${p.product < 0 ? "neg" : ""}" data-w="${(Math.abs(p.product) / scale) * 50}"
            style="${p.product < 0 ? "right: 50%" : "left: 50%"}"></b></span>
          <span class="num">${p.product > 0 ? "+" : ""}${p.product.toFixed(2)}</span>`).join("")}
        <span class="lbl sum">Sum, then the logistic curve</span><span class="sum"></span>
        <span class="num sum">${shown.sum > 0 ? "+" : ""}${shown.sum.toFixed(2)}</span>
      </div>
      ${item.what_if.birth_month_off !== null ? `
      <div class="whatif">
        <span class="mono">What if the birth month were one off?</span>
        <span class="out">${whatIf ? `${item.p.toFixed(2)} → ${shown.p.toFixed(2)}` : ""}</span>
        <button type="button" id="whatif" class="${whatIf ? "on" : ""}">${whatIf ? "Undo" : "Try it"}</button>
      </div>` : ""}
    </div>`;
  requestAnimationFrame(() => document.querySelectorAll(".ledger .fill").forEach((b) => { b.style.width = `${b.dataset.w}%`; }));
  const button = $("#whatif");
  if (button) button.addEventListener("click", () => {
    whatIf = !whatIf;
    inspectGuess(item);                       // redo the working with the changed number
    const p = whatIf ? item.what_if.birth_month_off : null;
    showResult(p);
    drawVerdicts(whatIf ? p >= 0.5 : null);
  });
}

function inspectFact(item) {
  const s = item.source;
  $("#inspector").innerHTML = `
    <div class="insp-head mono"><span>Solid line <i>/</i> on the register</span><span>A fact</span></div>
    <div class="insp-body">
      <div class="insp-score"><b>Director of</b></div>
      <p class="insp-empty">Stated by the register itself, not guessed. The fact keeps a fingerprint of the exact file it came from.</p>
      <div class="source-row">
        <span class="mono">Source</span><span>${s.file}</span>
        <span class="mono">Row</span><span>${s.row}</span>
        <span class="mono">SHA-256</span><span class="mono" style="color: var(--ink)">${s.sha}…</span>
        <span class="mono">Check</span><span>${s.verified ? '<span class="verified mono">File unchanged</span>' : "File missing or changed"}</span>
      </div>
    </div>`;
}

// --- The result panel and the verdict strip ------------------------------------------------

function showResult(whatIfScore = null) {
  if (!current) return;
  const warn = whatIfScore === null ? current.warning : whatIfScore >= 0.5;
  const score = whatIfScore === null ? current.score : whatIfScore;
  $("#verdict").className = `verdict${warn ? " warn" : ""}`;
  $("#verdict").innerHTML = (warn ? "Warning" : "No warning") +
    `<small>${warn ? "Check before giving credit." : "No director matches anyone who ran an insolvent company."}</small>`;
  $("#score").innerHTML = whatIfScore === null ? score.toFixed(2) : `<span class="tag mono">What if</span>${score.toFixed(2)}`;
  $("#score-note").textContent = warn ? "Match score · at or above 0.50" : "Closest match score · below 0.50";
}

function drawVerdicts(oursOverride = null, animate = false) {
  $("#verdicts").innerHTML = current.verdicts.map((v, i) => {
    const alarm = v.ours && oursOverride !== null ? oursOverride : v.alarm;
    const word = alarm ? (v.ours ? "Warning" : "Alarm") : "Quiet";
    return `<div class="rule${v.ours ? " ours" : ""}${animate ? " flip" : ""}">
      <div class="rule-head mono"><span>0${i + 1} <i>/</i> ${v.name}</span>${v.ours ? "<span>Ours</span>" : ""}</div>
      <div class="rule-word${alarm ? " alarm" : ""}">${word}</div>
      <div class="rule-why">${v.why}</div></div>`;
  }).join("");
}

function emptyVerdicts() {
  const names = ["The register's own links", "Same name", "Same name and birth date", "Our matcher"];
  $("#verdicts").innerHTML = names.map((name, i) => `<div class="rule${i === 3 ? " ours" : ""}">
    <div class="rule-head mono"><span>0${i + 1} <i>/</i> ${name}</span>${i === 3 ? "<span>Ours</span>" : ""}</div>
    <div class="rule-word">—</div><div class="rule-why">&nbsp;</div></div>`).join("");
}

function resetCheck(state) {
  current = null;
  drawEngine();
  emptyGraph(state);
  emptyVerdicts();
  $("#inspector").innerHTML = `<div class="insp-head mono"><span>Inspector</span><span>Nothing selected</span></div>
    <div class="insp-body"><p class="insp-empty">Run a check, then select any line in the evidence to see what is behind it: the register's own record for a solid line, the matcher's working for a dashed one.</p></div>`;
  $("#verdict").className = "verdict";
  $("#verdict").textContent = "";
  $("#score").textContent = "—";
  $("#score-note").textContent = "";
}

async function check(number) {
  resetCheck("Running the engine");
  $("#result-id").textContent = "•".repeat(number.length);
  $("#result-state").textContent = "Running";
  let data;
  try {
    data = await api(`/api/company/${encodeURIComponent(number)}`);
  } catch (error) {
    $("#result-state").textContent = "Couldn't reach the engine";
    emptyGraph("Start app/server.py, then try again");
    return;
  }
  if (!data.found || !data.enough) {
    $("#result-state").textContent = data.found ? "Not enough evidence" : "Not in our data";
    emptyGraph(data.found ? "No director on record on the day it was formed"
                          : "We cover UK construction companies formed in 2021");
    return;
  }
  current = data;
  $("#result-state").textContent = `Formed ${data.formed} · checked`;
  drawGraph(data.graph);
  for (let i = 0; i < data.steps.length; i++) {   // each step, then its part of the picture
    await runStep(i, data.steps[i]);
    reveal(i);
    await sleep(160);
  }
  const strongest = data.graph.lines.filter((l) => l.kind === "guess").sort((a, b) => b.p - a.p)[0];
  if (strongest) pick(strongest.id);
  showResult();
  drawVerdicts(null, true);
  document.querySelectorAll("#verdicts .flip").forEach((cell, i) => setTimeout(() => cell.classList.add("in"), 120 * i));
}

$("#check-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const number = $("#number").value.trim().toUpperCase();
  if (number) check(number);
});

// --- 02 / How it works: six modules, each with its real code -------------------------------

const MODULES = [
  { key: "crawl", title: "Crawl", value: (o) => fmt(o.crawled), unit: "companies",
    note: "Construction companies formed in 2021 and 2022, from the Companies House API" },
  { key: "register", title: "As of", value: (o) => fmt(o.people), unit: "records",
    note: "Only what the register showed on the day a company was formed" },
  { key: "blocking", title: "Blocking", value: (o) => fmt(o.candidates), unit: "pairs",
    note: (o) => `kept out of ${fmt(o.possible)} possible pairs` },
  { key: "features", title: "Features", value: () => "8", unit: "numbers",
    note: "Name likeness, birth month and year, postcode district, nationality" },
  { key: "matcher", title: "Matcher", value: (o) => fmt(o.training_pairs.same + o.training_pairs.different), unit: "pairs",
    note: "A logistic regression, learned from the register's own links" },
  { key: "test", title: "Test", value: (o) => fmt(o.test.companies), unit: "companies",
    note: "Formed in 2022, opened once, never seen in training" },
];

// Lines worth pointing at in each step's source
const FOCUS = { crawl: /record_ref|provenance/, register: /observed_graph|insolvent =/, blocking: /sharing\(|SIMILAR_SURNAME/,
  features: /SequenceMatcher|features\[column\]/, matcher: /LogisticRegression|\.fit\(/ };

function drawModules() {
  $("#modules").innerHTML = MODULES.map((m, i) => `
    <button type="button" class="module" data-key="${m.key}">
      <div class="m-head mono"><span>0${i + 1} <i>/</i> <b>${m.title}</b></span></div>
      <div class="m-num">${m.value(overview)}<small>${m.unit}</small></div>
      <div class="m-note">${typeof m.note === "function" ? m.note(overview) : m.note}</div>
    </button>`).join("");
  document.querySelectorAll(".module").forEach((b) => b.addEventListener("click", () => openModule(b.dataset.key)));
  openModule("crawl");
}

async function openModule(key) {
  document.querySelectorAll(".module").forEach((b) => b.classList.toggle("on", b.dataset.key === key));
  drawSide(key);
  if (key === "test") return drawTestCode();
  const code = await api(`/api/code/${key}`);
  const lines = code.source.replace(/\s+$/, "").split("\n");
  $("#code-file").textContent = `${code.file} · line ${code.line}`;
  $("#code-name").textContent = `${code.name}()`;
  $("#gutter").textContent = lines.map((_, i) => code.line + i).join("\n");
  $("#source").innerHTML = highlight(lines, FOCUS[key]);
  const first = lines.findIndex((line) => FOCUS[key].test(line));
  const top = Math.max(0, first - 6);   // start a few lines above the first line worth pointing at
  $("#scroller").style.transform = top ? `translateY(${-(top * 25 + 14)}px)` : "translateY(0)";
}

function drawTestCode() {
  // The test has no code of its own on this page: its numbers come from main.ipynb's one test run
  $("#code-file").textContent = "vault/Project/Evaluation.md · final result";
  $("#code-name").textContent = "main.ipynb @ 74d8a97";
  const t = overview.test;
  const lines = [
    "# The test set, opened once (card #45): 2022 companies, never seen in training",
    `companies = ${t.companies}`,
    "",
    "# Links to an earlier insolvent company that the register can't confirm (fewer is better)",
    `same_name.unconfirmed = ${t["same name"].unconfirmed}        # the baseline`,
    `matcher.unconfirmed   = ${t.matcher.unconfirmed}         # ours`,
    "",
    "# The same, for common surnames",
    `same_name.common = ${t["same name"].common}`,
    `matcher.common   = ${t.matcher.common}`,
    "",
    "# Recall against the register: the share of its own links each method still finds",
    `same_name.recall = ${t["same name"].recall}`,
    `matcher.recall   = ${t.matcher.recall}`,
  ];
  $("#gutter").textContent = lines.map((_, i) => i + 1).join("\n");
  $("#source").innerHTML = highlight(lines, /unconfirmed/);
  $("#scroller").style.transform = "translateY(0)";
}

function escape(text) {
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function highlight(lines, focus) {
  // A small Python highlighter: docstrings and strings, comments, keywords, numbers
  const token = /("""[\s\S]*?"""|'''[\s\S]*?''')|(#[^\n]*)|("(?:[^"\\\n]|\\.)*"|'(?:[^'\\\n]|\\.)*')|\b(def|return|for|in|if|elif|else|import|from|as|not|and|or|None|True|False|with|lambda|while|class|try|except|raise|is)\b|\b(\d+(?:\.\d+)?)\b/g;
  const text = lines.join("\n");
  let out = "", last = 0;
  for (const m of text.matchAll(token)) {
    out += escape(text.slice(last, m.index));
    const kind = m[1] ? "s" : m[2] ? "c" : m[3] ? "s" : m[4] ? "k" : "n";
    out += `<span class="${kind}">${escape(m[0])}</span>`;
    last = m.index + m[0].length;
  }
  out += escape(text.slice(last));
  // Mark the focus lines, keeping any span that runs across lines intact
  return out.split("\n").map((line, i) => (focus && focus.test(lines[i]) ? `<span class="hl">${line}</span>` : line)).join("\n");
}

function drawSide(key) {
  const o = overview, t = o.test;
  const head = (left, right) => `<div class="side-head mono"><span>${left}</span><span>${right}</span></div>`;
  const pair = (rows) => `<div class="big-pair">${rows.map(([a, al, b, bl]) =>
    `<div><b>${a}</b><span>${al}</span></div><div><b class="ours">${b}</b><span>${bl}</span></div>`).join("")}</div>`;
  const sides = {
    crawl: head("01 / Crawl", "Our own data") + `<div class="side-body">
      <p>We crawled the register ourselves: each company's profile, its officers and its insolvency history, saved untouched. Every fact keeps the SHA-256 of the file it came from.</p>
      ${pair([[fmt(o.crawled), "query companies crawled", fmt(o.companies), "company records reached"],
              [fmt(o.people), "director records", fmt(o.facts), "register facts, each traceable"]])}</div>`,
    register: head("02 / As of", "No looking ahead") + `<div class="side-body">
      <p>A company formed on day t is judged only on what the register showed on day t. Later appointments and insolvencies are hidden, so the future can't leak into the answer.</p>
      ${current ? `<p>For the company you checked: <b>${current.steps[0].value} ${current.steps[0].unit}</b> on record the day it was formed.</p>` : ""}</div>`,
    blocking: head("03 / Blocking", "Which pairs to compare") + `<div class="side-body">
      <p>Comparing every director record with every other would be ${fmt(o.possible)} pairs. A cheap rule keeps the ones worth comparing: the same surname and first initial, or the same birth month and year and a similar surname.</p>
      ${pair([[fmt(o.possible), "possible pairs", fmt(o.candidates), "pairs kept"],
              ["99.2%", "of the register's own links kept (validation)", (o.candidates / o.possible * 100).toFixed(3) + "%", "of all pairs compared"]])}</div>`,
    features: head("04 / Features", "Eight numbers per pair") + `<div class="side-body">
      <p>Each pair becomes eight numbers: how alike the names are, from 0 to 1, and whether the birth month and year, the postcode district and the nationality agree, each with a flag when a value is missing. Birth dates are compared, never shown.</p>
      ${current && current.inspect ? featureTable() : ""}</div>`,
    matcher: head("05 / Matcher", "A weighted sum") + `<div class="side-body">
      <p>A logistic regression adds up the eight numbers, each times a weight it learned from ${fmt(o.training_pairs.same + o.training_pairs.different)} pairs the register already labels: the same officer id means the same person.</p>
      ${weightLedger()}${curve()}</div>`,
    test: head("06 / Test", "2022, opened once") + `<div class="side-body">
      ${pair([[fmt(t["same name"].unconfirmed), "same name: links the register can't confirm", fmt(t.matcher.unconfirmed), "our matcher"],
              [fmt(t["same name"].common), "same name: common surnames", fmt(t.matcher.common), "our matcher"],
              [pct(t["same name"].recall), "same name: register links found", pct(t.matcher.recall), "our matcher"]])}
      <div class="stress"><div class="h">Where it breaks (validation)</div><div class="h v">Ours</div><div class="h v">Same name</div>
        ${o.stress.map((s) => `<div>${s.change}</div><div class="v ours">${pct(s.matcher)}</div><div class="v">${(s.same_name * 100).toFixed(1)}%</div>`).join("")}</div>
      <p>A link is a reason to check, not a forecast: about 1% of the test companies failed, with a link or without one.</p></div>`,
  };
  $("#side").innerHTML = sides[key];
  requestAnimationFrame(() => document.querySelectorAll("#side .fill").forEach((b) => { b.style.width = `${b.dataset.w}%`; }));
}

function featureTable() {
  const guess = Object.values(current.inspect).find((i) => i.kind === "guess");
  if (!guess) return "";
  return `<div class="fields">${guess.fields.map((f) => `<div>${f.field}<b class="${/different/.test(f.verdict) ? "no" : ""}">${f.verdict}</b></div>`).join("")}</div>`;
}

function weightLedger() {
  const rows = [{ feature: "Starting point", weight: overview.intercept }, ...overview.weights.filter((w) => Math.abs(w.weight) >= 0.05)];
  const scale = Math.max(...rows.map((r) => Math.abs(r.weight)));
  return `<div class="ledger">${rows.map((r) => `<span class="lbl">${r.feature}</span>
    <span class="track"><b class="fill ${r.weight < 0 ? "neg" : ""}" data-w="${(Math.abs(r.weight) / scale) * 50}"
      style="${r.weight < 0 ? "right: 50%" : "left: 50%"}"></b></span>
    <span class="num">${r.weight > 0 ? "+" : ""}${r.weight.toFixed(2)}</span>`).join("")}</div>`;
}

function curve() {
  // The logistic curve that turns the sum into a score, with the checked company's pair on it
  const W = 540, H = 120, x = (s) => 20 + ((s + 8) / 16) * (W - 40), y = (p) => H - 18 - p * (H - 34);
  const points = Array.from({ length: 81 }, (_, i) => { const s = -8 + i * 0.2; return `${x(s)},${y(1 / (1 + Math.exp(-s)))}`; });
  const guess = current && Object.values(current.inspect).find((i) => i.kind === "guess");
  const dot = guess ? `<line class="bar-line" x1="${x(Math.max(-8, Math.min(8, guess.sum)))}" x2="${x(Math.max(-8, Math.min(8, guess.sum)))}" y1="${H - 18}" y2="${y(guess.p)}"/>
    <circle cx="${x(Math.max(-8, Math.min(8, guess.sum)))}" cy="${y(guess.p)}" r="6"/>
    <text x="${x(Math.max(-8, Math.min(8, guess.sum))) + 12}" y="${guess.p >= 0.5 ? y(guess.p) + 20 : y(guess.p) - 12}">SUM ${guess.sum.toFixed(2)} → ${guess.p.toFixed(2)}</text>` : "";
  return `<svg class="curve" viewBox="0 0 ${W} ${H}">
    <line class="axis" x1="20" x2="${W - 20}" y1="${H - 18}" y2="${H - 18}"/><line class="axis" x1="${x(0)}" x2="${x(0)}" y1="10" y2="${H - 18}"/>
    <line class="axis" x1="20" x2="${W - 20}" y1="${y(0.5)}" y2="${y(0.5)}" stroke-dasharray="3 4"/>
    <text x="22" y="${y(0.5) - 6}">0.50: WARNING</text>
    <polyline points="${points.join(" ")}" fill="none" stroke="currentColor" stroke-width="2"/>${dot}</svg>`;
}

// --- Start --------------------------------------------------------------------------------

(async function start() {
  resetCheck("Enter a company number");
  $("#result-state").textContent = "Waiting for a company";
  try {
    overview = await api("/api/overview");
    $("#index-right").textContent = `${fmt(overview.labelled)} companies formed in 2021 · ${fmt(overview.people)} director records`;
  } catch (error) {
    $("#index-right").textContent = "Engine not running";
  }
})();

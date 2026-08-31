#!/usr/bin/env python3
"""生成一场 Captain Free Session 报名页（repo 根目录下的静态 html）。
由 GitHub Actions（.github/workflows/build-event-page.yml）在 repository_dispatch 触发时调用，
从环境变量读参数（Apps Script 的 Events tab 那一行传过来的），不需要本地手改常量。

也可以本地手动跑：把下面这些环境变量 export 了再执行本脚本，等价于原来
`Captain Session 2026/build_page.py` 的手动流程，方便离线预览/调试。

必需环境变量：EVENT_ID, CAPACITY, LABEL, EVENT_DATE, ARRIVE_TIME, ON_WATER_TIME
可选：LOCATION（默认 Simpson Lake）、APPS_SCRIPT_URL（默认用已部署的那个）、OUT_FILENAME（默认 EVENT_ID + ".html"）、
     TSHIRT_SIZES（逗号分隔，比如 "S,M,L,XL,XXL,3XL,4XL,5XL"；留空/不填 = 这场没有 T 恤，表单不显示这一项）、
     NOTES（额外说明框，留空则页面上完全不显示这个框）、
     CANCELLED（"true"/"false"，默认 false——取消状态主要靠 Apps Script doGet 实时下发，这里烘焙进
     首屏快照只是为了离线预览时也能看到效果，线上是否显示取消卡片以 doGet 返回的 cancelled 为准）、
     CANCEL_NOTE（取消时显示的说明文字，比如"已取消，改期到 9/12，见新报名页"）
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.join(HERE, "..")

def env(name, default=None, required=False):
    v = os.environ.get(name, default)
    if required and not v:
        print(f"missing required env var: {name}", file=sys.stderr)
        sys.exit(1)
    return v

EVENT_ID = env("EVENT_ID", required=True)
CAPACITY = int(env("CAPACITY", "20"))
EVENT_DATE = env("EVENT_DATE", required=True)
ARRIVE_TIME = env("ARRIVE_TIME", required=True)
ON_WATER_TIME = env("ON_WATER_TIME", required=True)
LOCATION = env("LOCATION", "Simpson Lake")
WAIVER_URL = env("WAIVER_URL", "https://forms.gle/WrG4zwLNZ4AgkDPA8")
CONTACT_EMAIL = env("CONTACT_EMAIL", "stldragonboatclub@stlcls.org")
APPS_SCRIPT_URL = env(
    "APPS_SCRIPT_URL",
    "https://script.google.com/macros/s/AKfycbxuy_x4MZyhvC-zlCaB-uziV-7AYSZa1h5HIodYU9w0hHSKCRid-HPMkmrdN5cIYulubA/exec",
)
OUT_FILENAME = env("OUT_FILENAME") or (EVENT_ID + ".html")
TSHIRT_SIZES = [s.strip() for s in env("TSHIRT_SIZES", "").split(",") if s.strip()]
NOTES = env("NOTES", "").strip()
CANCELLED = env("CANCELLED", "false").strip().lower() in ("true", "yes", "y", "1")
CANCEL_NOTE = env("CANCEL_NOTE", "").strip()

DATA_URL = APPS_SCRIPT_URL + "?event=" + EVENT_ID
OUT = os.path.join(REPO_ROOT, OUT_FILENAME)
SNAPSHOT = {
    "generated": "preview", "capacity": CAPACITY, "count": 0, "remaining": CAPACITY, "full": False,
    "cancelled": CANCELLED, "cancel_note": CANCEL_NOTE
}

if NOTES:
    NOTES_BOX_HTML = f'<div class="notebox">{NOTES}</div>'
else:
    NOTES_BOX_HTML = ""

if TSHIRT_SIZES:
    TSHIRT_FIELD_HTML = (
        '<div class="field"><label for="tshirt">T-shirt size</label>\n'
        '    <select id="tshirt" name="tshirt">\n'
        '      <option value="">No thanks</option>\n      '
        + "".join(f"<option>{s}</option>" for s in TSHIRT_SIZES)
        + "\n    </select></div>"
    )
    BLURB_SNACKS = "Snacks, drinks, and a few festival t-shirts while they last."
else:
    TSHIRT_FIELD_HTML = ""
    BLURB_SNACKS = "Snacks and drinks provided."

PAGE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Captain Session Sign-Up — __EVENT_DATE__</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,650&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">
<style>
:root{
  --surface:#fdfcf8;--plane:#f4f1e8;--ink:#181611;--ink2:#514c40;--mut:#8d876f;
  --border:rgba(24,22,17,.12);--grid:#e6e1d2;
  --lake:#0f7268;--lake-ink:#08322d;--lake-soft:#e3f0ec;
  --gold:#b9781c;--gold-soft:#f6e9d3;
  --good:#1a8a4c;--crit:#c23b3b;--crit-soft:#fbeaea;
}
@media(prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --surface:#1c1a15;--plane:#131210;--ink:#f6f3ea;--ink2:#c9c3b2;--mut:#948d78;
  --border:rgba(246,243,234,.12);--grid:#2b2820;
  --lake:#3fb3a4;--lake-ink:#d7f3ec;--lake-soft:#173430;
  --gold:#e0a94a;--gold-soft:#332510;
  --good:#4cc785;--crit:#e57171;--crit-soft:#3a1c1c;
}}
:root[data-theme="dark"]{
  --surface:#1c1a15;--plane:#131210;--ink:#f6f3ea;--ink2:#c9c3b2;--mut:#948d78;
  --border:rgba(246,243,234,.12);--grid:#2b2820;
  --lake:#3fb3a4;--lake-ink:#d7f3ec;--lake-soft:#173430;
  --gold:#e0a94a;--gold-soft:#332510;
  --good:#4cc785;--crit:#e57171;--crit-soft:#3a1c1c;
}
*{box-sizing:border-box}
body{margin:0;background:var(--plane);color:var(--ink);
  font:16px/1.55 "Inter",system-ui,-apple-system,"Segoe UI",sans-serif;
  padding:32px 16px 56px}
.wrap{max-width:560px;margin:0 auto}
.eyebrow{font:600 12.5px/1 "Inter",sans-serif;letter-spacing:.09em;text-transform:uppercase;
  color:var(--lake);margin:0 0 10px}
h1{font-family:"Fraunces",Georgia,serif;font-weight:650;font-size:clamp(28px,5.5vw,38px);
  line-height:1.08;letter-spacing:-.01em;margin:0 0 14px;text-wrap:balance}
.essentials{display:grid;grid-template-columns:repeat(2,1fr);gap:1px;background:var(--border);
  border:1px solid var(--border);border-radius:14px;overflow:hidden;margin:0 0 18px}
.ess{background:var(--surface);padding:12px 14px}
.ess .l{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--mut);margin:0 0 3px}
.ess .v{font-size:14.5px;font-weight:600;color:var(--ink)}
.blurb{color:var(--ink2);font-size:14.5px;margin:0 0 22px}
.blurb b{color:var(--ink)}
.capbar-wrap{background:var(--surface);border:1px solid var(--border);border-radius:14px;
  padding:14px 16px;margin:0 0 22px}
.caprow{display:flex;align-items:baseline;justify-content:space-between;gap:10px;margin-bottom:8px}
.capnum{font-family:"IBM Plex Mono",monospace;font-weight:600;font-size:15px;
  font-variant-numeric:tabular-nums}
.capnum .fill{color:var(--lake)}
.captrack{height:8px;border-radius:99px;background:var(--grid);overflow:hidden}
.capfill{height:100%;background:var(--lake);border-radius:99px;transition:width .4s ease}
.capnote{font-size:12.5px;color:var(--mut);margin-top:8px}
form{background:var(--surface);border:1px solid var(--border);border-radius:16px;
  padding:22px;display:flex;flex-direction:column;gap:16px}
.field{display:flex;flex-direction:column;gap:6px}
.field label{font-size:13px;font-weight:600;color:var(--ink)}
.field .opt{font-weight:400;color:var(--mut)}
.field input[type=text],.field input[type=email],.field input[type=tel],.field select,.field textarea{
  font:15px/1.4 "Inter",sans-serif;color:var(--ink);background:var(--plane);
  border:1px solid var(--border);border-radius:9px;padding:10px 12px;width:100%}
.field textarea{resize:vertical;min-height:56px}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.waiver{display:flex;gap:10px;align-items:flex-start;background:var(--gold-soft);
  border:1px solid var(--border);border-radius:10px;padding:12px}
.waiver input{margin-top:3px}
.waiver span{font-size:13px;color:var(--ink2);line-height:1.5}
.waiver a{color:var(--lake-ink);font-weight:600}
button.submit{font:600 15px/1 "Inter",sans-serif;background:var(--lake);color:#fff;
  border:none;border-radius:10px;padding:13px;cursor:pointer}
button.submit:disabled{opacity:.5;cursor:not-allowed}
.msg{border-radius:10px;padding:12px 14px;font-size:14px;display:none}
.msg.show{display:block}
.msg.ok{background:var(--lake-soft);color:var(--lake-ink)}
.msg.err{background:var(--crit-soft);color:var(--crit)}
.full-card{background:var(--surface);border:1px solid var(--border);border-radius:16px;
  padding:26px 22px;text-align:center}
.full-card .big{font-family:"Fraunces",serif;font-weight:650;font-size:22px;margin:0 0 6px}
.full-card p{color:var(--ink2);font-size:14.5px;margin:0}
.full-card a{color:var(--lake-ink);font-weight:600}
.notebox{background:var(--gold-soft);border:1px solid var(--border);border-radius:12px;
  padding:12px 14px;font-size:14px;line-height:1.5;color:var(--ink2);margin:0 0 18px}
.cancelled-card{background:var(--crit-soft);border:1px solid var(--border);border-radius:16px;
  padding:26px 22px;text-align:center}
.cancelled-card .big{font-family:"Fraunces",serif;font-weight:650;font-size:22px;margin:0 0 6px;color:var(--crit)}
.cancelled-card p{color:var(--ink2);font-size:14.5px;margin:0}
.cancelled-card a{color:var(--lake-ink);font-weight:600}
footer{margin-top:26px;font-size:12.5px;color:var(--mut);text-align:center}
footer a{color:var(--ink2)}
@media(max-width:480px){.essentials{grid-template-columns:1fr 1fr}.row2{grid-template-columns:1fr}}
</style></head><body><div class="wrap">
<p class="eyebrow">Gateway Dragon Boat Festival · Thank-You Session</p>
<h1>On-water session for our festival captains 🐉</h1>
<div class="essentials">
  <div class="ess"><div class="l">Date</div><div class="v">__EVENT_DATE__</div></div>
  <div class="ess"><div class="l">Arrive</div><div class="v">__ARRIVE_TIME__</div></div>
  <div class="ess"><div class="l">On the water</div><div class="v">__ON_WATER_TIME__</div></div>
  <div class="ess"><div class="l">Location</div><div class="v">__LOCATION__</div></div>
</div>
__NOTES_BOX__
<p class="blurb">As thanks for captaining a boat (or repping a sponsor team) at the festival, the
St. Louis Dragon Boat Club is hosting a free session just for you — <b>30 min warm-up, an hour on the
water, 15 min recap</b>. __BLURB_SNACKS__ Open to the first
<b>__CAPACITY__</b> sign-ups.</p>
<div class="capbar-wrap">
  <div class="caprow"><span>Spots filled</span>
    <span class="capnum"><span class="fill" id="capFilled">0</span> / <span id="capTotal">__CAPACITY__</span></span></div>
  <div class="captrack"><div class="capfill" id="capBar" style="width:0%"></div></div>
  <div class="capnote" id="capNote">Loading current sign-ups…</div>
</div>

<form id="signupForm">
  <div class="field"><label for="name">Name</label>
    <input type="text" id="name" name="name" required autocomplete="name"></div>
  <div class="row2">
    <div class="field"><label for="email">Email</label>
      <input type="email" id="email" name="email" required autocomplete="email"></div>
    <div class="field"><label for="phone">Phone <span class="opt">(optional)</span></label>
      <input type="tel" id="phone" name="phone" autocomplete="tel"></div>
  </div>
  <div class="field"><label for="team">Boat / sponsor team <span class="opt">(optional)</span></label>
    <input type="text" id="team" name="team" placeholder="e.g. Bayer, Team Dragon Warriors"></div>
  __TSHIRT_FIELD__
  <div class="field"><label for="notes">Notes <span class="opt">(optional)</span></label>
    <textarea id="notes" name="notes" placeholder="Anything we should know?"></textarea></div>
  <label class="waiver">
    <input type="checkbox" id="waiver" name="waiver" required>
    <span>I understand this is an on-water paddling activity and have signed (or will sign before
      boarding) the club's liability waiver. <a href="__WAIVER_URL__" target="_blank">Sign / view waiver</a></span>
  </label>
  <button class="submit" type="submit" id="submitBtn">Reserve my spot</button>
  <div class="msg" id="formMsg"></div>
</form>

<div class="full-card" id="fullCard" style="display:none">
  <div class="big">All __CAPACITY__ spots are filled 🎉</div>
  <p>Thanks for your interest! Email <a href="mailto:__CONTACT_EMAIL__">__CONTACT_EMAIL__</a>
    to be added to the waitlist in case of cancellations.</p>
</div>

<div class="cancelled-card" id="cancelledCard" style="display:none">
  <div class="big">This session has been cancelled</div>
  <p id="cancelledNote"></p>
</div>

<footer>Questions? <a href="mailto:__CONTACT_EMAIL__">__CONTACT_EMAIL__</a> ·
  Data: <span id="dataStamp">—</span></footer>
</div>
<script>
const DATA_URL = "__DATA_URL__";
const EVENT_ID = "__EVENT_ID__";
const SNAPSHOT = __SNAPSHOT__;

function paint(d){
  document.getElementById("dataStamp").textContent = d.generated || "—";
  if (d.cancelled) {
    document.querySelector(".capbar-wrap").style.display = "none";
    document.getElementById("signupForm").style.display = "none";
    document.getElementById("fullCard").style.display = "none";
    document.getElementById("cancelledNote").textContent = d.cancel_note || "Check back for updates, or email us with questions.";
    document.getElementById("cancelledCard").style.display = "block";
    return;
  }
  const cap = d.capacity ?? 20, count = d.count ?? 0, remaining = Math.max(0, cap-count);
  document.getElementById("capFilled").textContent = count;
  document.getElementById("capTotal").textContent = cap;
  document.getElementById("capBar").style.width = Math.min(100, (count/cap)*100) + "%";
  document.getElementById("capNote").textContent = d.full
    ? "Full — see below to join the waitlist."
    : remaining <= 5 ? `Only ${remaining} spot${remaining===1?"":"s"} left — sign up soon!`
    : `${remaining} spots remaining.`;
  if (d.full) {
    document.getElementById("signupForm").style.display = "none";
    document.getElementById("fullCard").style.display = "block";
  }
}
async function load(){
  if (!DATA_URL) { paint(SNAPSHOT); return; }
  try {
    const r = await fetch(DATA_URL);
    const j = await r.json();
    paint(j);
  } catch(e) { paint(SNAPSHOT); }
}
load();

document.getElementById("signupForm").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const btn = document.getElementById("submitBtn");
  const msg = document.getElementById("formMsg");
  msg.className = "msg"; msg.textContent = "";
  const payload = {
    event: EVENT_ID,
    name: document.getElementById("name").value.trim(),
    email: document.getElementById("email").value.trim(),
    phone: document.getElementById("phone").value.trim(),
    team: document.getElementById("team").value.trim(),
    tshirt: document.getElementById("tshirt") ? document.getElementById("tshirt").value : "",
    waiver: document.getElementById("waiver").checked,
    notes: document.getElementById("notes").value.trim()
  };
  if (!payload.name || !payload.email || !payload.waiver) {
    msg.textContent = "Please fill in your name, email, and check the waiver box."; msg.className = "msg err show"; return;
  }
  if (!DATA_URL) {
    msg.textContent = "Sign-ups aren't live yet — this is a design preview."; msg.className = "msg err show"; return;
  }
  btn.disabled = true; btn.textContent = "Submitting…";
  try {
    const r = await fetch(DATA_URL, {method:"POST", headers:{"Content-Type":"text/plain;charset=utf-8"},
      body: JSON.stringify(payload)});
    const j = await r.json();
    if (j.ok) {
      document.getElementById("signupForm").reset();
      msg.textContent = "You're in! See you __EVENT_DATE__ at __ARRIVE_TIME__."; msg.className = "msg ok show";
      load();
    } else if (j.error === "full") {
      load();
    } else if (j.error === "cancelled") {
      load();
    } else if (j.error === "duplicate_email") {
      msg.textContent = "That email is already signed up."; msg.className = "msg err show";
    } else {
      msg.textContent = "Something went wrong — please try again or email us."; msg.className = "msg err show";
    }
  } catch(e) {
    msg.textContent = "Something went wrong — please try again or email us."; msg.className = "msg err show";
  } finally {
    btn.disabled = false; btn.textContent = "Reserve my spot";
  }
});
</script></body></html>"""

html = (PAGE
    .replace("__DATA_URL__", DATA_URL)
    .replace("__EVENT_ID__", EVENT_ID)
    .replace("__EVENT_DATE__", EVENT_DATE)
    .replace("__ARRIVE_TIME__", ARRIVE_TIME)
    .replace("__ON_WATER_TIME__", ON_WATER_TIME)
    .replace("__CAPACITY__", str(CAPACITY))
    .replace("__LOCATION__", LOCATION)
    .replace("__WAIVER_URL__", WAIVER_URL)
    .replace("__CONTACT_EMAIL__", CONTACT_EMAIL)
    .replace("__TSHIRT_FIELD__", TSHIRT_FIELD_HTML)
    .replace("__BLURB_SNACKS__", BLURB_SNACKS)
    .replace("__NOTES_BOX__", NOTES_BOX_HTML)
    .replace("__SNAPSHOT__", json.dumps(SNAPSHOT)))
open(OUT, "w", encoding="utf-8").write(html)
print("written:", os.path.abspath(OUT))

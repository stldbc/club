#!/usr/bin/env python3
"""同步一场活动的卡片到 announcements.html 和 index.html 的 Recent Announcements 区。

每次点「发布页面」都会跑（见 .github/workflows/build-event-page.yml），不区分新活动/改已有活动
——因为改已有活动（比如改错的 label、改时间）也应该让卡片文字跟着刷新，不能假装没发生。

每个目标文件独立判断，同一套逻辑：
  - CANCELLED=true 且 CANCEL_SILENTLY=true（活动在真正公开公布之前就取消了）：
    这场活动**不应该出现**——卡片存在就删掉，不存在就什么都不做，不留"已取消"提示
  - 卡片已存在（不管是不是取消）：原地整块替换成最新内容（标题/日期/说明文字/取消状态都刷新）
  - 卡片不存在：插入一张新卡片（取消了就直接是"已取消"样式）

幂等：上面每一种分支重复跑结果都一样，不会越跑越多张卡片。

必需环境变量：EVENT_ID, LABEL, EVENT_DATE, ARRIVE_TIME, ON_WATER_TIME
可选：LOCATION（默认 Simpson Lake）、CAPACITY（默认 20）、OUT_FILENAME（默认 EVENT_ID + ".html"）、
     CANCELLED（"true"/"false"）、CANCEL_NOTE、CANCEL_SILENTLY（"true"/"false"）
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.join(HERE, "..")

# (文件路径, 卡片列表容器的开始标签) —— 两个文件都用同样的 .post-card 卡片结构，
# 只是外层容器 class 名不同（announcements.html 用 post-grid，index.html 首页用 recent-grid）。
TARGETS = [
    (os.path.join(REPO_ROOT, "announcements.html"), '<div class="post-grid">'),
    (os.path.join(REPO_ROOT, "index.html"), '<div class="recent-grid">'),
]


def env(name, default=None, required=False):
    v = os.environ.get(name, default)
    if required and not v:
        print(f"missing required env var: {name}", file=sys.stderr)
        sys.exit(1)
    return v


EVENT_ID = env("EVENT_ID", required=True)
LABEL = env("LABEL", required=True)
EVENT_DATE = env("EVENT_DATE", required=True)
ARRIVE_TIME = env("ARRIVE_TIME", required=True)
ON_WATER_TIME = env("ON_WATER_TIME", required=True)
LOCATION = env("LOCATION", "Simpson Lake") or "Simpson Lake"
CAPACITY = env("CAPACITY", "20") or "20"
OUT_FILENAME = env("OUT_FILENAME") or (EVENT_ID + ".html")
CANCELLED = env("CANCELLED", "false").strip().lower() in ("true", "yes", "y", "1")
CANCEL_NOTE = env("CANCEL_NOTE", "").strip()
CANCEL_SILENTLY = env("CANCEL_SILENTLY", "false").strip().lower() in ("true", "yes", "y", "1")

CARD_BLOCK_RE = re.compile(
    r'\n?\s*<a class="post-card"[^>]*href="' + re.escape(OUT_FILENAME) + r'"[^>]*>.*?</a>\n?',
    re.DOTALL,
)


def build_card():
    if CANCELLED:
        badge = '<span class="post-type type-club" style="background:rgba(194,59,59,0.20);color:#e57171;">Cancelled</span>'
        summary = CANCEL_NOTE or "This session has been cancelled. Check back for updates."
    else:
        badge = '<span class="post-type type-club" style="background:rgba(15,114,104,0.22);color:#3fb3a4;">Captain Training</span>'
        summary = f"{LOCATION} · arrive {ARRIVE_TIME} · on the water {ON_WATER_TIME}. Open to the first {CAPACITY} sign-ups."
    return f"""
    <a class="post-card" href="{OUT_FILENAME}" data-type="club">
      <div>
        <div class="post-meta">
          {badge}
          <span class="post-date">{EVENT_DATE}</span>
        </div>
        <div class="post-title">{LABEL}</div>
        <div class="post-summary">{summary}</div>
      </div>
      <div class="post-arrow">→</div>
    </a>
"""


def sync_file(path, container_marker):
    name = os.path.basename(path)
    html = open(path, encoding="utf-8").read()
    href_marker = f'href="{OUT_FILENAME}"'

    if CANCELLED and CANCEL_SILENTLY:
        if href_marker not in html:
            print(f"skip: {name} has no card for {OUT_FILENAME} to remove (cancel_silently)")
            return
        new_html, count = CARD_BLOCK_RE.subn("\n", html, count=1)
        if count == 0:
            print(f"could not locate existing card block for {OUT_FILENAME} in {name}", file=sys.stderr)
            sys.exit(1)
        open(path, "w", encoding="utf-8").write(new_html)
        print(f"{name}: removed card for {OUT_FILENAME} (cancelled before it was ever announced)")
        return

    if href_marker in html:
        new_html, count = CARD_BLOCK_RE.subn(build_card(), html, count=1)
        if count == 0:
            print(f"could not locate existing card block for {OUT_FILENAME} in {name}", file=sys.stderr)
            sys.exit(1)
        open(path, "w", encoding="utf-8").write(new_html)
        print(f"{name}: updated card for {OUT_FILENAME}" + (" (cancelled)" if CANCELLED else ""))
        return

    idx = html.find(container_marker)
    if idx == -1:
        print(f"could not find {container_marker!r} in {name}", file=sys.stderr)
        sys.exit(1)
    insert_at = idx + len(container_marker)
    html = html[:insert_at] + build_card() + html[insert_at:]
    open(path, "w", encoding="utf-8").write(html)
    print(f"{name}: inserted card for {OUT_FILENAME}" + (" (cancelled)" if CANCELLED else ""))


for path, marker in TARGETS:
    sync_file(path, marker)

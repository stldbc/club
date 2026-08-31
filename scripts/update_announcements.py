#!/usr/bin/env python3
"""给 announcements.html 自动插入/更新一张活动的公告卡片。

调用时机（见 .github/workflows/build-event-page.yml 的 "Add/update announcements" 步骤）：
  1. 这是一个全新的活动页面（git 里这个 html 文件是 untracked），或
  2. 这次发布把活动标记成了取消（CANCELLED=true）——不管卡片存不存在都要同步"已取消"状态
除此之外（比如只是改一个已有活动的人数/时间，没有取消），这个脚本根本不会被调用，
announcements.html 不会被碰。

幂等：
  - 非取消场景：如果 announcements.html 里已经有这个页面文件名的卡片，直接跳过，不重复插入
  - 取消场景：如果卡片已存在，原地替换成"已取消"版本；如果还不存在（比如活动一发布就立刻被取消），
    直接插入一张已经是"已取消"样式的卡片

必需环境变量：EVENT_ID, LABEL, EVENT_DATE, ARRIVE_TIME, ON_WATER_TIME
可选：LOCATION（默认 Simpson Lake）、CAPACITY（默认 20）、OUT_FILENAME（默认 EVENT_ID + ".html"）、
     CANCELLED（"true"/"false"）、CANCEL_NOTE
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.join(HERE, "..")
ANNOUNCEMENTS = os.path.join(REPO_ROOT, "announcements.html")


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


html = open(ANNOUNCEMENTS, encoding="utf-8").read()
href_marker = f'href="{OUT_FILENAME}"'

if href_marker in html:
    if not CANCELLED:
        print(f"skip: announcements.html already has a card for {OUT_FILENAME}")
        sys.exit(0)
    # Replace the existing <a class="post-card" href="OUT_FILENAME" ...> ... </a> block in place.
    pattern = re.compile(
        r'\n?\s*<a class="post-card"[^>]*href="' + re.escape(OUT_FILENAME) + r'"[^>]*>.*?</a>\n?',
        re.DOTALL,
    )
    new_html, count = pattern.subn(build_card(), html, count=1)
    if count == 0:
        print(f"could not locate existing card block for {OUT_FILENAME} to update", file=sys.stderr)
        sys.exit(1)
    open(ANNOUNCEMENTS, "w", encoding="utf-8").write(new_html)
    print(f"updated announcement card for {OUT_FILENAME} (cancelled)")
    sys.exit(0)

marker = '<div class="post-grid">'
idx = html.find(marker)
if idx == -1:
    print('could not find <div class="post-grid"> in announcements.html', file=sys.stderr)
    sys.exit(1)
insert_at = idx + len(marker)
html = html[:insert_at] + build_card() + html[insert_at:]

open(ANNOUNCEMENTS, "w", encoding="utf-8").write(html)
print(f"inserted announcement card for {OUT_FILENAME}" + (" (cancelled)" if CANCELLED else ""))

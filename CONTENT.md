# STL Dragon Boat Club — Website Content Guide

> 本文件是网站内容的人工可读参考。  
> 如需修改文字、链接、日期，先在这里找到对应条目，再去对应 HTML 文件做精准修改。  
> 长期目标：内容统一维护在此，由脚本生成 HTML；目前页面不多，直接对照本文件改 HTML 即可。

---

## 文件结构

```
website/
├── index.html                        ← 主页
├── announcements.html                ← 所有公告列表
├── style.css                         ← 全站共用样式（勿轻易改）
├── CONTENT.md                        ← 本文件（内容参考）
└── posts/
    ├── season-2026.html              ← 2026 赛季详情（已归档/关闭注册，见下方换季说明）
    ├── season-2027.html              ← 2027 赛季页（⚠️ 目前是"筹备中"占位页，没有真实日期/价格）
    ├── open-house-2026-05-16.html    ← Open House（已过期，保留存档）
    └── safety.html                   ← 安全指南（双语）
```

> **2026-08-30 状态**：9/20 队长体验课临时取消改期 9/12，趁手动关闭了 2026 赛季注册/drop-in
> （表单不再从网站任何地方可点，`posts/season-2026.html` 顶部加了"已结束"提示条），首页/公告页主推
> 改成 `posts/season-2027.html`——但这只是一个"筹备中"占位页（没有编日期/地址/价格），
> 等 Jing/Gu 拿到 2027 真实训练日期后，还是要走下面「年度换季 Checklist」把占位内容换成正式内容。

---

## 年度换季 Checklist（Season Rollover）

> 目的：每年开新赛季前，把"网站上所有写死当季年份/日期/届数的地方"过一遍，不用每年重新摸索一次。
> 触发时机：Jing/Gu 拿到新一季的训练日期、地址、价格之后（往年经验是每年初才定，不用抢跑）。
> 下面给的是**发现方法**（grep 命令）而不是写死的行号——行号会随内容变动漂移，命令不会。

### Step 0 — 先决定这轮怎么处理旧内容
- 旧赛季详情页（如 `posts/season-2026.html`）**复制成新文件**（如 `posts/season-2027.html`），
  旧文件保留不删——参考 `posts/open-house-2026-05-16.html` 的归档模式（顶部加"已结束"提示条，链回新版）。
- 全站所有指向旧赛季页的链接改指向新文件（下面 Step 1 的 grep 会把这些点位都列出来）。

### Step 1 — 找到所有需要看一眼的硬编码点
```bash
cd website
grep -rn "2026" --include="*.html" .                 # 年份/文件名里带年份的引用
grep -rn "20th\|21st\|届" --include="*.html" .        # 节庆届数（20th → 21st 这类需要顺延确认，不要自己猜）
grep -rn "© 20" --include="*.html" .                  # 页脚版权年份
grep -rn "August 15\|Aug 15\|Aug<br" --include="*.html" .   # 节庆日期（每年不一定还是8/15，需跟 STLDBF 那边核实）
grep -rln "Marshall Rd\|TBD\|占位" --include="*.html" .     # 已知占位符（比如 season 页地址一直没填真实地址）
```
每一条命中的地方逐个判断：这是"应该跟着换季"的内容，还是"跟当季无关的历史记录"（比如已归档的
open-house/duanwu 页面，是保留原年份的存档，不用改）。

### Step 2 — 逐项更新（都在新复制出来的 `season-20XX.html` 和 `index.html`/`announcements.html` 里）
- `index.html`：导航栏 "20XX Club" 文字+链接、Hero 按钮文字、About 段落里的届数/日期、统计数字区
  （Training Sessions 次数、Festival Race Day 日期）、底部 sessions 日期数组（`<script>` 里的
  `var sessions = [...]`）、footer 版权年份、Recent Announcements 卡片（换成新赛季公告，旧的移除或标 past）
- `posts/season-20XX.html`（新文件）：训练日历表格 + 底部 `<script>` 的 sessions 数组（两处必须一致，
  见文件里已有的"修改训练日期"说明）、两队时间、费用、地点地址（**这一项去年一直是占位符没填，
  今年记得顺手核实真实地址**）、Good to Know 卡片如有变化
- `announcements.html`：标题文案里的届数、footer 版权年份、插入一张新赛季公告卡片
- `CONTENT.md`（本文件）：把"现有卡片/文件结构"表里的年份也同步改一下，不然下次看这份文档会误导

### Step 3 — Google Form（会员注册 / Drop-in）
两个表单都是**编辑同一个 forms.gle 链接**换季，不是每年建新表单换新链接（网站上的链接不用改）。
- Drop-in Form：照 `posts/dropin-form-spec.md` 最后的"每年初更新 Checklist"操作（日期选项、价格、Zelle账号、Waiver链接）
- Membership Registration Form：目前没有单独的 spec 文档，谷贺/Jing 直接在 Google Form 后台改里面的
  日期/价格选项即可，逻辑跟 Drop-in 一样
- Claude 拿不到 Google Form 后台编辑权限，这一步只能提醒/核对，不能代为操作

### Step 4 — 过渡期（旧赛季已结束、新赛季日期还没定）怎么办
不要提前瞎填占位日期。可以先把网站上的注册 CTA 按钮文案临时改成"2027 赛季筹备中，请关注公告"
之类的过渡文案，等 Step 2 的真实数据到位后再一次性替换成正式内容，避免出现一个短期内就要再改一次的假日期。

### 不用管的部分（已经自动化）
- **Captain training 报名页 → announcements.html**：已自动化（见
  `Captain Session 2026/apps_script.gs` 顶部注释 + `.github/workflows/build-event-page.yml`）。
  Sheet 里发布一场全新活动会自动加公告卡片，换季时不用管这块。

---

## TODO / 待完成项

| 位置 | 内容 | 状态 |
|------|------|------|
| `index.html` L233、`season-2026.html` L276、L501 | Drop-In Google Form URL（现为占位符 `#`） | ⚠️ 待填入 |
| `season-2026.html` 地址栏 | Simpson Lake 实际地址（目前为 1234 Marshall Rd 占位） | ⚠️ 待确认 |
| `season-2026.html` 地图链接 | Google Maps 链接需和实际地址一致 | ⚠️ 待确认 |

---

## 主页 (`index.html`)

### 导航栏按钮
| 按钮文字 | 链接 |
|----------|------|
| STL Dragon Boat Club（Logo） | `index.html` |
| News | `announcements.html` |
| 2027 Club | `posts/season-2027.html`（筹备中占位页） |
| 2027 Season → | `posts/season-2027.html` |

### 自动提示条（"Next Training Session"）
- 位置：Hero 图和快捷图标栏之间
- 内容由 JavaScript 自动计算，从训练日期列表中取最近的未来日期显示
- 无需手动改；如训练日期有变动，见下方"修改训练日期"

### 快捷图标栏（5 格）
| 图标 | 文字 | 链接 |
|------|------|------|
| 🏊 | Join the Club | `posts/season-2027.html` |
| 📢 | Announcements | `announcements.html` |
| 📝 | 2027 Registration | `posts/season-2027.html`（**2026-08-30 起改指向占位页，不再直连 Google Form**） |
| 🚣 | 2027 Drop-In | `posts/season-2027.html`（同上） |
| ✉️ | Contact Us | `mailto:stldragonboatclub@stlcls.org` |

### About 文字（2026-08-30 起用过去式，因为 8/15 节庆已经办完）
```
The St. Louis Dragon Boat Club (STLDBC) brings together paddlers of all 
backgrounds on the water every Saturday. No experience needed — just the 
spirit to paddle.

This past summer, our members competed and volunteered at the 20th 
Gateway Dragon Boat Festival on August 15 at Creve Coeur Lake — organized 
by the St. Louis Dragon Boat Foundation (STLDBF).
```

### 统计数字
| 数字 | 说明 |
|------|------|
| 10 | Training Sessions |
| 2 | Teams (A & B) |
| Aug 15 | Festival Race Day |

### 近期公告卡片（Recent Announcements）
- 2027 Season — Details Coming Soon → `posts/season-2027.html`（置顶，占位页）
- Open House（5/16）— 已标记为 Past，灰色不可点
- 2026 Season — Join the Crew → `posts/season-2026.html`（**2026-08-30 起也标记为 Past**，注册已关闭）

### 页脚 Festival Callout
- 标题：20th Gateway Dragon Boat Festival
- 日期地点：Creve Coeur Lake · Maryland Heights, MO · 6 AM – 4 PM
- 按钮："Festival Website →" → `https://gatewaydragonboat.com`；"Join Our Club Team" → `posts/season-2027.html`

---

## 2026 赛季详情页 (`posts/season-2026.html`) — ⚠️ 2026-08-30 起已关闭/归档

顶部加了"已结束"提示条（链去 `season-2027.html`），Membership Registration / Drop In 按钮
换成不可点的"Registration Closed for 2026"文字 + 一个"See 2027 Season →"按钮；Sign Waiver 按钮
保留没关（免责声明常年可签）。下面这些小节描述的是**关闭前**的赛季内容，仅供以后复制到
新赛季页时参考数字/文案，不代表现在网站上还能报名。

### 训练日历（10 次）
| 日期 | 备注 |
|------|------|
| May 16 | Season Opener 🎉（已过，JS 自动变灰） |
| May 30 | Saturday |
| Jun 13 | Saturday |
| Jun 20 | Saturday |
| Jun 27 | Saturday |
| Jul 11 | Saturday |
| Jul 18 | Saturday |
| Jul 25 | Saturday |
| Aug 8  | Final Practice |
| Sep 12 | Season Finale |

> **修改训练日期**：需同时改三处
> 1. `posts/season-2026.html` — HTML 中 `.schedule-grid` 内的 `.date-chip` 列表（视觉日历）
> 2. `posts/season-2026.html` — 底部 `<script>` 中 `var sessions = [...]` 数组（自动标灰逻辑）
> 3. `index.html` — 底部 `<script>` 中 `var sessions = [...]` 数组（Next Session 提示条）

### 两支队伍
| 队伍 | 时间 | 语言 |
|------|------|------|
| Team A | 8:30–10:30 AM | Mandarin/English |
| Team B | 9:30–11:30 AM | English |

### 每节训练结构
30min 陆地热身 → 60min 水上训练 → 30min 总结

### 费用
| 选项 | 价格 | 说明 |
|------|------|------|
| Full Season Membership | $160 | 全10次 + 8/15 节庆赛报名（价值$50）+ 2张访客券 + 装备 |
| Single Session Drop-In | $20 | 单次，不含节庆赛报名，装备提供 |

> **修改价格**：`posts/season-2026.html` → `.fees-grid` 区域

### 主要按钮（关闭前）
| 按钮 | 链接 |
|------|------|
| Membership Registration → | `https://forms.gle/tLAdZCFNJEY5kxLi6`（**已关闭，见上方"2026-08-30 起已关闭"**） |
| Drop In ($20) → | `https://forms.gle/FFkiSjefEo54VpdU6`（同上，已关闭） |
| Sign Waiver | `https://forms.gle/WrG4zwLNZ4AgkDPA8`（仍在用，没关） |

### 地点
- Simpson Lake, Blue Heron Shelter
- 地址：本页 `<address>` 块目前写的是 "1234 Marshall Rd, St. Louis, MO 63088"；
  但 8/27 有一次自动发布把 captain session 页面的地址改成了
  "1234 Marshall Rd, Valley Park, MO 63088"（城市不同）——**两边不一致，下次动这个页面时
  找 Jing/Gu 确认哪个是真实地址，统一改掉，不要再当占位符忽略**
- 地图链接：和地址一起更新

### Good to Know 卡片
- 🦺 Gear Provided：PFD 和 paddle 提供，个人 PFD 需符合 USCG 标准
- 👕 Club Attire：统一穿俱乐部 T 恤，新成员免费获赠
- 📋 Waiver Required：第一次上船前必须签免责声明
- 🔰 Safety First：第一次训练前看安全简介视频

### 联系方式
- 📧 stldragonboatclub@stlcls.org
- 🌐 www.stlcls.org/dragonboat
- 👥 Facebook Group：`https://www.facebook.com/groups/9592205354148705`

---

## 公告列表页 (`announcements.html`)

### 现有卡片（最新在前）
| 标签 | 标题 | 状态 |
|------|------|------|
| Club Info | 2027 Season — Details Coming Soon | 置顶，占位页 |
| Captain Training | Free On-Water Session for Festival Captains | ⚠️ 9/20 已取消改期 9/12，卡片文字待 Sheet 那边点发布后自动同步 |
| Club Info | 2026 Season — Join the Crew | **2026-08-30 起标 Past**，注册已关闭 |
| Club Info | Safety Guidelines 安全指南 | 常驻 |
| Open House (Past) | Free Trial Open House — May 16 | 已过期，灰色 |

> **新增公告**：在 `announcements.html` 的 `<div class="post-grid">` 开头插入新 `.post-card`，格式照现有卡片；同时在 `posts/` 下新建对应 HTML 文件；如需在主页"Recent Announcements"展示，也在 `index.html` 的 `.recent-grid` 区域更新。

---

## Open House 存档页 (`posts/open-house-2026-05-16.html`)

- 顶部有"This event has ended"提示条，链去 `season-2027.html`（2026-08-30 起从 season-2026 改指过来）
- 页面内容保留作参考，不再对外主推
- 如举办新一轮 Open House，可复制此文件改日期

---

## 2027 赛季占位页 (`posts/season-2027.html`)

- 2026-08-30 新建，纯"筹备中"占位内容，**没有真实训练日期/地址/价格**——不要照抄这页的数字当正式内容
- 内容：一句话说明 2026 已结束、2027 还在筹备；三张"待定"卡片（日期/地点/价格）；
  引导去 Announcements 或邮件联系，没有报名按钮
- 拿到 2027 真实数据后，参照本文件最上面的「年度换季 Checklist」，把这页正文换成完整赛季页
  （训练日历/两队时间/费用/地点/Good to Know，格式照抄旧版 `season-2026.html` 关闭前的版本）

---

## 安全指南 (`posts/safety.html`)

- 双语（英/中）安全清单
- 训练前必读，开放日和正式训练均引用此页
- 内容如有更新（规则变化、新装备要求），直接改此文件

---

## 全局链接速查

| 用途 | 链接 |
|------|------|
| 会员注册 Google Form（**2026-08-30 起已从网站全部下线，2026 赛季关闭**） | `https://forms.gle/tLAdZCFNJEY5kxLi6` |
| Drop-In Form（**同上，已下线**） | `https://forms.gle/FFkiSjefEo54VpdU6` |
| 免责声明 Waiver（仍在用，没关） | `https://forms.gle/WrG4zwLNZ4AgkDPA8` |
| Open House 报名（已过期） | `https://forms.gle/CXkVZdp7e4Khgyr68` |
| 节庆官网 | `https://gatewaydragonboat.com` |
| Facebook 群组 | `https://www.facebook.com/groups/9592205354148705` |
| 俱乐部邮箱 | stldragonboatclub@stlcls.org |
| STLCLS 俱乐部页 | `https://www.stlcls.org/school/page/dragonboat` |

> 上面两个表单的链接本身没删，只是网站上暂时不再放出口。2027 赛季重新开放注册时，
> 大概率是复用同一个 forms.gle 链接（编辑表单里的日期/价格），照 [[website-season-rollover]]
> 的 Step 3 走，然后把 `posts/season-2027.html` 上的占位内容换成真的按钮。

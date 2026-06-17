# Hermes AI 速报

基于 Garry Tan 的 gstack + 大黑AI速报风格的 AI 编程工具版本更新日报。

**每 4 小时**自动生成一期精美的速报截图，包含：
- 🛠️ **AI 编程工具版本更新**（Claude Code / Codex / OpenClaw / OpenCode / Gemini CLI）
- 🔥 **Hacker News AI 热点**
- 🎨 大黑AI速报风格的排版设计

## 运行方式

### GitHub Actions（推荐 — 免费，24h 在线）

1. Fork 或 Clone 本仓库
2. （可选）在仓库 Settings → Secrets and variables → Actions 中添加：
   - `WECHAT_WEBHOOK_URL` — 微信推送 Webhook（Server酱 / PushPlus / 企业微信机器人）
3. Actions 自动每 4 小时运行一次

### 本地运行

```bash
pip install playwright
playwright install chromium
python briefing.py
```

输出在 `~/briefings/` 目录下（html + png）。

## 信源

- 大黑AI速报 RSS：news.daheiai.com/changelog_rss.php
- Hacker News API：hacker-news.firebaseio.com

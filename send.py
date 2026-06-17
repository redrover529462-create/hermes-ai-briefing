#!/usr/bin/env python3
"""发送速报到 Server酱"""
import os, json, urllib.request, sys

webhook = os.environ.get('WEBHOOK')
if not webhook:
    print("No WEBHOOK env var, skipping")
    sys.exit(0)

title = os.environ.get('TITLE', 'Hermes AI 速报')
run_url = os.environ.get('RUN_URL', '')
art_url = os.environ.get('ART_URL', '')

msg = f"""## 🤖 Hermes AI 速报

本期速报已自动生成！

[📥 查看速报截图(Artifact)]({art_url})

[🔗 查看 GitHub Actions 运行日志]({run_url})

---
*信源：大黑AI速报 + Hacker News*
*每 4 小时自动更新*"""

data = json.dumps({'title': title, 'desp': msg}).encode('utf-8')
req = urllib.request.Request(webhook, data=data, headers={'Content-Type': 'application/json'})
resp = urllib.request.urlopen(req, timeout=15)
print(f"Sent! Status: {resp.status}")

#!/usr/bin/env python3
"""Send to Server酱 WeChat"""
import os, json, urllib.request, sys

# 列出所有环境变量（调试用）
print("WEBHOOK present:", 'WEBHOOK' in os.environ)

webhook = os.environ.get('WEBHOOK', '')
if not webhook:
    print("No WEBHOOK, skip")
    sys.exit(0)

print(f"Webhook starts with: {webhook[:20]}...")

title = "Hermes AI 速报"
run_url = os.environ.get('RUN_URL', '')
art_url = os.environ.get('ART_URL', '')

msg = f"""## 🤖 Hermes AI 速报

本期速报已自动生成！

[📥 查看速报截图(Artifact)]({art_url})

[🔗 查看运行日志]({run_url})

---
*信源：大黑AI速报 + Hacker News*
*每 4 小时自动更新*"""

data = json.dumps({'title': title, 'desp': msg}).encode('utf-8')
req = urllib.request.Request(webhook, data=data, headers={'Content-Type': 'application/json'})
try:
    resp = urllib.request.urlopen(req, timeout=15)
    print(f"Sent! HTTP {resp.status}")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(0)

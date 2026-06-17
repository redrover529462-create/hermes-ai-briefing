#!/usr/bin/env python3
"""Hermes AI 速报 — 独立版。抓数据→生成HTML→Playwright截图"""
import subprocess, os, json, sys
from datetime import datetime
from xml.etree import ElementTree as ET
from pathlib import Path

OUTPUT_DIR = os.environ.get('BRIEFING_OUTPUT', str(Path.home() / 'briefings'))
IN_GITHUB = os.environ.get('GITHUB_ACTIONS') == 'true'

def curl(url, t=15):
    try:
        r = subprocess.run(["curl","-sL","--max-time",str(t),url], capture_output=True, text=True, timeout=t+5)
        return r.stdout if r.returncode == 0 else ""
    except: return ""

def fetch_tools():
    xml = curl("https://news.daheiai.com/changelog_rss.php")
    tools = {}
    if not xml.strip(): return tools
    root = ET.fromstring(xml)
    for item in root.findall('.//item')[:25]:
        t = (item.find('title').text or '?') if item.find('title') is not None else '?'
        c = (item.find('category').text or '其他') if item.find('category') is not None else '其他'
        d = (item.find('description').text or '') if item.find('description') is not None else ''
        l = (item.find('link').text or '') if item.find('link') is not None else ''
        ds = ''.join([x for x in d.strip().split('\n') if x.strip() and not x.strip().startswith('##')])[:250] if d else ''
        tools.setdefault(c, []).append({'title':t,'desc':ds,'link':l})
    return tools

def fetch_hn():
    try:
        hn = curl("https://hacker-news.firebaseio.com/v0/topstories.json",10)
        ids = json.loads(hn)[:30]
        items = []
        kw = ['ai','llm','gpt','claude','model','openai','anthropic','gemini','deepseek','qwen','llama','mistral','transformer','agent','copilot','coding','neural','codex']
        for sid in ids:
            s = curl(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",8)
            if not s: continue
            j = json.loads(s)
            title = j.get('title','')
            if any(k in title.lower() for k in kw):
                items.append({'title':title,'url':j.get('url',f"https://news.ycombinator.com/item?id={sid}"),'score':j.get('score',0)})
        items.sort(key=lambda x:-x['score'])
        return items[:8]
    except: return []

def hl(text):
    if not text: return '(暂无内容)'
    ks = ['Claude Code','GLM','MIT','Agent Arena','Terminal-Bench','Code Arena','OpenAI','DeepSeek','Anthropic','MiniMax','Qwen','Gemini CLI','OpenClaw','OpenCode','Codex']
    for k in ks:
        if k.lower() in text.lower():
            i = text.lower().index(k.lower())
            orig = text[i:i+len(k)]
            text = text.replace(orig, '<span class="hl">'+orig+'</span>', 1)
    return text

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M")
    period = now.strftime('%Y%m%d%H%M')
    
    print(f"[{now.strftime('%H:%M')}] Fetching data...")
    tools = fetch_tools()
    hn = fetch_hn()
    
    tm = {'Claude Code':'CLAUDE','Codex':'OPENAI','OpenClaw':'OPENCLAW','OpenCode':'OPENCODE','Gemini CLI':'GOOGLE'}
    highlights = [tools[c][0]['title'] for c in ['Claude Code','OpenCode','OpenClaw','Codex','Gemini CLI'] if c in tools and tools[c]]
    mu = [{'tag':'CLAUDE','title':i['title'],'body':hl(i['desc'][:200])} for i in tools.get('Claude Code',[])[:4]]
    ti = [{'tag':tm.get(c,c.upper()),'title':i['title'],'body':hl(i['desc'][:180])} for c in ['Codex','OpenClaw','OpenCode','Gemini CLI'] if c in tools for i in tools[c][:2]]
    
    # Build HTML
    sh = ''
    if highlights:
        hls = '；'.join('<span class="hl">'+h+'</span>' for h in highlights[:4])
        sh = '<div class="sb"><div class="l">AI 速报</div><p>本期重点：'+hls+'</p></div>'
    
    def card(items):
        return ''.join('<div class="it"><div class="tg">'+i['tag']+'</div><div class="tl">'+i['title']+'</div><div class="bd">'+i['body']+'</div></div>' for i in items)
    
    def sec(title, items):
        if not items: return ''
        return '<div class="st"><span class="b"></span><h2>'+title+'</h2></div>'+card(items)
    
    hn_html = ''
    if hn:
        rows = ''.join('<div class="hn"><div class="hs">'+str(i['score'])+'</div><div class="ht"><a href="'+i['url']+'">'+i['title']+'</a></div></div>' for i in hn[:8])
        hn_html = '<div class="st"><span class="b"></span><h2>Hacker News 热点</h2></div>'+rows
    
    html = '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Hermes AI 速报</title>\n<style>\n*{margin:0;padding:0;box-sizing:border-box}\nbody{font-family:-apple-system,PingFang SC,Microsoft YaHei,sans-serif;background:#fff;display:flex;justify-content:center}\n.w{max-width:640px;width:100%;padding:32px 32px 20px;position:relative}\n.wm{position:absolute;top:0;left:0;right:0;height:360px;overflow:hidden;pointer-events:none;z-index:0}\n.wm span{position:absolute;font-size:40px;font-weight:900;color:rgba(0,0,0,0.02);white-space:nowrap;transform:rotate(-10deg);letter-spacing:8px}\n.c{position:relative;z-index:1}\n.hd{margin-bottom:18px}\n.hd h1{font-size:24px;font-weight:800;color:#111}\n.hd .sub{font-size:12px;color:#999;margin-top:2px}\n.sb{border-left:3px solid #ff6a00;padding:8px 0 8px 14px;margin-bottom:20px}\n.sb .l{font-size:12px;font-weight:700;color:#ff6a00;margin-bottom:6px}\n.sb p{font-size:13px;line-height:1.8;color:#333}\n.sb .hl{color:#ff6a00;font-weight:600}\n.st{display:flex;align-items:center;gap:8px;margin:26px 0 12px}\n.st .b{width:3px;height:16px;background:#ff6a00;border-radius:1px}\n.st h2{font-size:16px;font-weight:700;color:#111}\n.it{margin-bottom:14px;padding:12px 16px;background:#fafbfc;border:1px solid #f0f0f0;border-radius:8px}\n.tg{font-size:10px;font-weight:700;letter-spacing:1px;color:#d94671;text-transform:uppercase}\n.tl{font-size:14px;font-weight:700;color:#111;line-height:1.5;margin:2px 0 5px}\n.bd{font-size:12.5px;line-height:1.75;color:#555}\n.bd .hl{color:#ff6a00;font-weight:600}\n.hn{display:flex;align-items:baseline;gap:8px;padding:7px 0;border-bottom:1px solid #f0f0f0}\n.hn:last-child{border-bottom:none}\n.hs{font-size:12px;font-weight:700;color:#ccc;min-width:30px;text-align:right}\n.ht{font-size:12.5px;line-height:1.6;color:#444}\n.ht a{color:#444;text-decoration:none}\n.ft{text-align:center;padding:24px 0 4px;font-size:11px;color:#ccc;line-height:2}\nhr{border:none;border-top:1px solid #f0f0f0;margin:8px 0}\n</style>\n</head>\n<body><div class="w">\n<div class="wm"><span style="top:10px;left:-10px">Zhipu</span><span style="top:46px;left:148px">MiniMax</span><span style="top:82px;left:288px">OpenAI</span><span style="top:118px;left:-30px">Claude</span><span style="top:154px;left:178px">DeepSeek</span><span style="top:190px;left:348px">Qwen</span></div>\n<div class="c">\n<div class="hd"><h1>Hermes AI 速报</h1><div class="sub">'+date_str+' - 第'+period+'期</div></div>\n'+sh+'\n'+sec('模型动态',mu)+'\n'+sec('产品工具',ti)+'\n'+hn_html+'\n<hr><div class="ft">由 Hermes Agent 自动生成<br>'+date_str+' | 信源：大黑AI速报 + Hacker News | 每 4h 更新</div>\n</div></div></body>\n</html>'
    
    ts = now.strftime('%Y%m%d-%H%M')
    hp = os.path.join(OUTPUT_DIR, f"briefing-{ts}.html")
    pp = os.path.join(OUTPUT_DIR, f"briefing-{ts}.png")
    
    with open(hp, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"HTML: {hp}")
    
    print("Screenshotting...")
    if IN_GITHUB:
        subprocess.run(["pip","install","playwright"], capture_output=True)
        subprocess.run(["playwright","install","chromium"], capture_output=True)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width":680,"height":800})
        page.goto(f"file://{os.path.abspath(hp)}", wait_until="networkidle")
        page.wait_for_timeout(2000)
        page.screenshot(path=pp, full_page=True)
        browser.close()
    print(f"PNG: {pp}")
    
    if IN_GITHUB:
        with open(os.environ['GITHUB_ENV'], 'a') as f:
            f.write(f"BRIEFING_PNG={pp}\n")
            f.write(f"BRIEFING_DATE={date_str}\n")

if __name__ == '__main__':
    main()

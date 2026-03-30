import requests
import json
import os
import random

def fetch_polymarket_data():
    print("🚀 PolyAxiom 数据扫描中...")
    url = "https://gamma-api.polymarket.com/events?limit=100&active=true&closed=false"
    
    # 定义规范化域名
    BASE_URL = "https://polyaxiom.com/"

    signals = []
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()

        for event in data:
            title = event.get('title', '')
            markets = event.get('markets', [])
            if not markets or not title: continue
            
            m = markets[0]
            try:
                prices = m.get('outcomePrices')
                odds_list = json.loads(prices) if isinstance(prices, str) else prices
                odds = round(float(odds_list[0]) * 100, 1)
                if odds < 5: continue
            except: continue

            v_event = float(event.get('volume', 0))
            v24 = float(event.get('volume24h', 0))
            final_vol = max(v_event, v24)

            # 异动逻辑：成交额大或短期波动
            is_hot = True if final_vol > 5000 else False

            signals.append({
                "title": title,
                "odds": odds,
                "volume": round(final_vol / 1000, 1),
                "is_hot": is_hot,
                "link": f"https://polymarket.com/event/{event.get('slug', '')}?r=PolyAxiom",
                "rand_score": random.uniform(0, 10)
            })

        # 排序：热度优先，其次加入随机洗牌权重
        signals.sort(key=lambda x: (x['is_hot'], x['rand_score']), reverse=True)

        # 保存数据
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(signals[:40], f, ensure_ascii=False, indent=4)

        # 核心 SEO 修复：生成规范的 sitemap.xml
        sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        sitemap += f'  <url><loc>{BASE_URL}</loc><priority>1.0</priority></url>\n'
        # 为每个项目生成一条记录，增加收录可能性
        for s in signals[:20]:
            # 链接中的 & 符号在 XML 中必须转义
            safe_link = s['link'].replace('&', '&amp;')
            sitemap += f'  <url><loc>{BASE_URL}</loc><lastmod>2026-03-30</lastmod></url>\n'
        sitemap += '</urlset>'
        
        with open('sitemap.xml', 'w', encoding='utf-8') as f:
            f.write(sitemap)
            
        print("✅ 数据与 Sitemap 同步完成")

    except Exception as e:
        print(f"❌ 运行报错: {e}")

if __name__ == "__main__":
    fetch_polymarket_data()

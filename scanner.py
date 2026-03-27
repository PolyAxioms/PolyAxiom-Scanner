import requests
import json
import os
from datetime import datetime

def generate_seo_files():
    """自动化生成 SEO 辅助文件"""
    # 1. 生成 robots.txt
    robots_content = "User-agent: *\nAllow: /\nSitemap: https://polyaxiom.com/sitemap.xml"
    with open('robots.txt', 'w') as f:
        f.write(robots_content)
    
    # 2. 生成简单的 sitemap.xml
    now = datetime.now().strftime('%Y-%m-%d')
    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://polyaxiom.com/</loc>
    <lastmod>{now}</lastmod>
    <changefreq>hourly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>"""
    with open('sitemap.xml', 'w') as f:
        f.write(sitemap_content)
    print("✅ SEO 文件 (robots/sitemap) 已自动更新")

def fetch_polymarket_data():
    print("🚀 PolyAxiom 数据引擎启动...")
    url = "https://gamma-api.polymarket.com/events?limit=40&active=true&closed=false"
    
    signals = []
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        for event in data:
            title = event.get('title', '')
            markets = event.get('markets', [])
            if not markets or not title: continue
            
            m = markets[0]
            raw_prices = m.get('outcomePrices')
            odds = 0.0
            
            try:
                if isinstance(raw_prices, list) and len(raw_prices) > 0:
                    odds = float(raw_prices[0])
                elif isinstance(raw_prices, str):
                    odds = float(json.loads(raw_prices)[0])
                
                # 百分比转换 (0.545 -> 54.5)
                if 0 < odds <= 1.0:
                    odds = odds * 100
            except:
                continue
            
            link = f"https://polymarket.com/event/{event.get('slug', '')}?r=PolyAxiom"
            
            signals.append({
                "title": title,
                "odds": round(odds, 1),
                "link": link,
                "category": event.get('groupItemTitle', '预测市场')
            })
            
        # 按胜率降序排列
        signals.sort(key=lambda x: x['odds'], reverse=True)
        
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(signals, f, ensure_ascii=False, indent=4)
        print(f"✅ 数据已更新，保存了 {len(signals)} 条信号")
        
        # 执行 SEO 文件生成
        generate_seo_files()
        
    except Exception as e:
        print(f"❌ 运行报错: {e}")

if __name__ == "__main__":
    fetch_polymarket_data()

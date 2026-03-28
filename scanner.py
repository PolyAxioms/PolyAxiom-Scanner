import requests
import json
import os
from datetime import datetime

def fetch_polymarket_data():
    print("🚀 PolyAxiom 动态热度扫描启动...")
    url = "https://gamma-api.polymarket.com/events?limit=50&active=true&closed=false"
    
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
            prices = m.get('outcomePrices')
            volume = float(event.get('volume24h', 0)) 
            
            try:
                # 兼容不同格式的胜率数据
                odds_list = json.loads(prices) if isinstance(prices, str) else prices
                odds = float(odds_list[0])
                if 0 < odds <= 1.0: odds *= 100
            except: continue
            
            link = f"https://polymarket.com/event/{event.get('slug', '')}?r=PolyAxiom"
            
            signals.append({
                "title": title,
                "odds": round(odds, 1),
                "volume": round(volume / 1000, 1), 
                "link": link,
                "category": event.get('groupItemTitle', '预测市场')
            })
            
        # 混合排序：交易量优先
        signals.sort(key=lambda x: (x['volume'] > 5, x['odds']), reverse=True)
        
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(signals[:30], f, ensure_ascii=False, indent=4)
        
        # 自动生成 SEO 文件
        with open('robots.txt', 'w') as f:
            f.write("User-agent: *\nAllow: /\nSitemap: https://polyaxiom.com/sitemap.xml")
            
        print(f"✅ 成功更新 {len(signals)} 条信号")
        
    except Exception as e:
        print(f"❌ 运行报错: {e}")
        exit(1) # 确保错误能被 Actions 捕获

if __name__ == "__main__":
    fetch_polymarket_data()

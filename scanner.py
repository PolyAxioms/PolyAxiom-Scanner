import requests
import json
import os

def fetch_polymarket_data():
    print("🔍 正在抓取 Polymarket 实时预测数据...")
    url = "https://gamma-api.polymarket.com/events?limit=15&active=true&closed=false"
    
    signals = []
    try:
        response = requests.get(url, timeout=15)
        # 如果返回不是 200，记录错误
        response.raise_for_status()
        data = response.json()
        
        for event in data:
            title = event.get('title', '未知事件')
            markets = event.get('markets', [{}])
            outcome_prices = markets[0].get('outcomePrices', ['0.5', '0.5'])
            odds = float(outcome_prices[0])
            slug = event.get('slug', '')
            link = f"https://polymarket.com/event/{slug}?r=PolyAxiom"
            
            signals.append({
                "title": title,
                "odds": odds,
                "link": link,
                "category": event.get('groupItemTitle', '预测市场')
            })
        print(f"✅ 成功抓取 {len(signals)} 条实时信号")
        
    except Exception as e:
        print(f"❌ 抓取过程中出现问题: {e}")
        # 保底数据，防止 Action 报错
        if not signals:
            signals = [{
                "title": "数据正在努力同步中，请稍后再试...",
                "odds": 0.0,
                "link": "#",
                "category": "系统状态"
            }]

    # 无论如何，一定要生成这个文件！
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(signals, f, ensure_ascii=False, indent=4)
    print("🚀 data.json 文件已生成并保存")

if __name__ == "__main__":
    fetch_polymarket_data()

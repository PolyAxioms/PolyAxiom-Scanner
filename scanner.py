import requests
import json
import os

def fetch_polymarket_data():
    print("🚀 PolyAxiom 高胜率引擎启动 (过滤 <5% 项目)...")
    url = "https://gamma-api.polymarket.com/events?limit=100&active=true&closed=false"
    
    old_data = {}
    if os.path.exists('data.json'):
        try:
            with open('data.json', 'r', encoding='utf-8') as f:
                old_list = json.load(f)
                old_data = {item['title']: item['odds'] for item in old_list}
        except: pass

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
                
                # 【关键过滤逻辑】胜率低于 5% 的直接跳过，不存入 json
                if odds < 5: continue
                
            except: continue
            
            # 交易量补全逻辑
            v24 = float(event.get('volume24h', 0))
            v_event = float(event.get('volume', 0))
            final_vol = max(v24, v_event)
            
            # 异动检测 (波动 >5%)
            is_hot = False
            if title in old_data:
                if abs(odds - old_data[title]) >= 5: is_hot = True

            signals.append({
                "title": title,
                "odds": odds,
                "volume": round(final_vol / 1000, 1),
                "is_hot": is_hot,
                "link": f"https://polymarket.com/event/{event.get('slug', '')}?r=PolyAxiom",
                "category": event.get('groupItemTitle', '预测市场')
            })
            
        # 排序：异动项目 -> 90%以上高胜率 -> 交易量
        signals.sort(key=lambda x: (x['is_hot'], x['odds'] >= 90, x['odds']), reverse=True)
        
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(signals[:40], f, ensure_ascii=False, indent=4)
        print(f"✅ 更新完成。已过滤掉低胜率干扰项。")
        
    except Exception as e:
        print(f"❌ 出错: {e}")

if __name__ == "__main__":
    fetch_polymarket_data()

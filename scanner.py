import os
import requests
from supabase import create_client

# 1. 强制打印环境检查（不打印具体的 Key，只看存不存在）
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

print(f"--- 检查钥匙 ---")
print(f"URL 是否存在: {'✅' if url else '❌'}")
print(f"KEY 是否存在: {'✅' if key else '❌'}")
print(f"--- 检查结束 ---")

if not url or not key:
    raise ValueError("钥匙缺失，请检查 GitHub Settings -> Secrets！")

supabase = create_client(url, key)

def run_scanner():
    print("🚀 开始抓取数据...")
    response = requests.get("https://gamma-api.polymarket.com/events?active=true&limit=20")
    markets = response.json()
    print(f"找到 {len(markets)} 个市场")
    
    for m in markets:
        title = m.get('title')
        row = {
            "title": title,
            "odds": 0.5,
            "ai_summary": "数据同步测试",
            "referral_link": f"https://polymarket.com/event/{m.get('slug')}?r=PolyAxiom"
        }
        # 尝试写入并打印结果
        try:
            res = supabase.table("alpha_signals").upsert(row, on_conflict="title").execute()
            print(f"写入成功: {title}")
        except Exception as e:
            print(f"❌ 写入失败: {title}, 原因: {e}")

if __name__ == "__main__":
    run_scanner()

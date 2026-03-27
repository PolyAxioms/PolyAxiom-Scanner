import os
import requests
from supabase import create_client

# 1. 获取钥匙并进行安全检查
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
ds_api_key = os.environ.get("DEEPSEEK_API_KEY")

# 如果没拿到钥匙，脚本会直接报错提醒，方便我们排查
if not url or not key:
    raise ValueError("❌ 错误：GitHub Secrets 里的 SUPABASE_URL 或 SUPABASE_KEY 没配置好！")

supabase = create_client(url, key)

def analyze_with_ai(title):
    """调用 DeepSeek 进行中文解析"""
    if not ds_api_key:
        return "请查看详情分析..."
    try:
        headers = {"Authorization": f"Bearer {ds_api_key}", "Content-Type": "application/json"}
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一个专业的预测市场分析师。"},
                {"role": "user", "content": f"请用一句话简要分析这个预测市场的中文背景：{title}"}
            ]
        }
        res = requests.post("https://api.deepseek.com/chat/completions", json=data, headers=headers, timeout=20)
        return res.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"AI 分析出错: {e}")
        return "点击查看详情分析..."

def run_scanner():
    print("🚀 开始扫描 Polymarket...")
    try:
        # 获取最热门的 20 个活跃市场
        response = requests.get("https://gamma-api.polymarket.com/events?active=true&limit=20")
        markets = response.json()
        
        for m in markets:
            title = m.get('title')
            slug = m.get('slug')
            if not title or not slug: continue
            
            # 让 AI 生成中文简评
            ai_msg = analyze_with_ai(title)
            
            # 准备存入数据库的数据
            row = {
                "title": title,
                "odds": 0.5, # 后续可接入具体赔率计算
                "ai_summary": ai_msg,
                "referral_link": f"https://polymarket.com/event/{slug}?r=PolyAxiom"
            }
            
            # 存入 Supabase (如果标题重复则更新)
            supabase.table("alpha_signals").upsert(row, on_conflict="title").execute()
            print(f"✅ 已同步: {title}")
    except Exception as e:
        print(f"扫描出错: {e}")

if __name__ == "__main__":
    run_scanner()

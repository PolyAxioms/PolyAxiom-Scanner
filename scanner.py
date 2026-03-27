import os
import requests
from supabase import create_client, Client

# 1. 配置 Supabase 连接
# 这些变量会自动读取你刚才在 GitHub Settings > Secrets 里设置的值
SUPABASE_URL = os.environ.get("SUPABASE_URL")
# 这里的 SUPABASE_KEY 现在是你提供的 sb_secret_... 开头的 service_role key
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ 错误: 未能在环境变量中找到 Supabase 配置，请检查 GitHub Secrets")
    exit(1)

# 初始化 Supabase 客户端 (上帝模式)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_polymarket_signals():
    """
    模拟抓取 Polymarket 数据的逻辑
    实际使用时，这里应该是你抓取 API 或 网页的代码
    """
    print("🔍 开始扫描 Polymarket...")
    # 这里是演示数据，实际运行时会由你的爬虫逻辑生成
    signals = [
        {
            "title": "NBA: Lakers vs Warriors - Market Analysis",
            "ai_summary": "AI 监测到大额资金流入 Lakers 胜盘，当前胜率赔率存在错位。",
            "referral_link": "https://polymarket.com/event/lakers-vs-warriors?referral=XXYY"
        },
        {
            "title": "Fed Interest Rate Cut in May?",
            "ai_summary": "预测市场显示 5 月降息概率升至 65%，波动率正在放大。",
            "referral_link": "https://polymarket.com/event/fed-cut-may?referral=XXYY"
        }
    ]
    return signals

def save_to_supabase(signals):
    """
    将信号保存到数据库
    由于使用了 service_role key，这里将绕过所有 RLS 策略
    """
    for signal in signals:
        try:
            # 执行插入操作
            result = supabase.table("alpha_signals").insert(signal).execute()
            print(f"✅ 成功写入信号: {signal['title']}")
        except Exception as e:
            # 如果还是报错，会打印详细原因
            print(f"❌ 写入失败: {str(e)}")

if __name__ == "__main__":
    # 执行流程
    found_signals = get_polymarket_signals()
    if found_signals:
        save_to_supabase(found_signals)
    else:
        print("📭 本次扫描未发现新信号")

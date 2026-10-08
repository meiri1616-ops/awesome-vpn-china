import os
import requests
import yaml
from datetime import datetime

WEIGHTS = {
    "security": 0.30,
    "stability": 0.25,
    "speed": 0.20,
    "payment": 0.15,
    "value": 0.10
}

def calculate_score(tool):
    score = (
        tool["security_score"] * WEIGHTS["security"] +
        tool["stability_score"] * WEIGHTS["stability"] +
        tool["speed_score"] * WEIGHTS["speed"] +
        tool["payment_score"] * WEIGHTS["payment"] +
        tool["value_score"] * WEIGHTS["value"]
    ) * 10
    return round(score, 1)

def get_latest_github_release(repo_name):
    try:
        url = f"https://api.github.com/repos/{repo_name}/releases/latest"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json().get("tag_name", "未知")
    except Exception as e:
        print(f"获取 {repo_name} Release 失败: {e}")
    return "保持关注"

def fetch_gemini_monthly_brief(current_date, singbox_ver, clash_ver):
    api_key = os.getenv("GEMINI_API_KEY")
    default_text = "本月跨国网络链路运行平稳，建议保持开源客户端内核更新，并常备具备混淆伪装特征的专有协议以应对临时探测。"
    
    if not api_key:
        return default_text

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    prompt = (
        f"今天是 {current_date}。最新版本：Sing-box 为 {singbox_ver}，Clash Verge Rev 为 {clash_ver}。"
        "请作为长期研究跨境网络的网络安全工程师，写一段 80~120 字的月度跨境网络态势简报。"
        "面向中国出海与科研用户，重点提醒如何利用抗审查协议规避网络波动，并提醒更新客户端。"
        "全中文，客观中立，无废话，直接输出正文。"
    )
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        res = requests.post(url, json=payload, headers=headers, timeout=20)
        if res.status_code == 200:
            data = res.json()
            candidates = data.get("candidates", [])
            if candidates:
                return candidates[0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"Gemini API 异常: {e}")
        
    return default_text

def build_readme():
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    with open("data/vpn_tools.yml", "r", encoding="utf-8") as f:
        tools = yaml.safe_load(f)

    for tool in tools:
        tool["composite_score"] = calculate_score(tool)
    tools = sorted(tools, key=lambda x: x["composite_score"], reverse=True)

    singbox_ver = get_latest_github_release("SagerNet/sing-box")
    clash_ver = get_latest_github_release("clash-verge-rev/clash-verge-rev")
    ai_brief = fetch_gemini_monthly_brief(current_date, singbox_ver, clash_ver)

    table_rows = []
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    for i, tool in enumerate(tools[:10]):
        rank_badge = medals[i]
        table_rows.append(
            f"| {rank_badge} **{tool['name']}** | **{tool['composite_score']}** | "
            f"{tool['authority_rating']} | `{tool['protocols']}` | "
            f"{tool['pricing_desc']} | {tool['payments']} | "
            f"[{tool['name']} 官网]({tool['affiliate_link']}) |"
        )
    table_content = "\n".join(table_rows)

    cards = []
    for i, tool in enumerate(tools[:10]):
        open_status = "✅ 100% 代码开源" if tool['open_source'] else "🔒 专有闭源商业架构"
        card = f"""### {medals[i]} {tool['name']} (加权总分: {tool['composite_score']})

- **法区背景与合规**：{tool['headquarters']} · {open_status} · {tool['audited']}
- **协议与穿透特性**：`{tool['protocols']}`
- **支持付款与设备**：{tool['payments']}（支持最多 **{tool['devices_limit']}**）
- **参考定价与方案**：{tool['pricing_desc']}
- **极客深度点评**：{tool['summary']}
- 🔗 **安全官方通道**：[直达 {tool['name']} 官网优惠 ({tool['pricing_desc']})]({tool['affiliate_link']})

---"""
        cards.append(card)
    cards_content = "\n\n".join(cards)

    # 替换为专注 awesomevpnchina 的纯净模板
    readme_template = f"""<div align="center">

# 🌐 跨境网络与科学上网全景指南 (TOP 10 天梯榜)

> **基于权威科技媒体年度评级、开源隐私安全审计、穿透算法加权与自动化健康监测**  
> 专为中国大陆出海从业者、跨境远程办公、海外学者及极客量身打造

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![Telegram Channel](https://img.shields.io/badge/Telegram-跨境网络情报局-2CA5E0?logo=telegram&logoColor=white)](https://t.me/awesomevpnchina)

[💬 订阅官方 Telegram 频道 (实时节点失效/官方大促通报)](https://t.me/awesomevpnchina)

</div>

---

### 📢 跨境阻断突发情报与应急通道
> ⚠️ **特殊时期网络提醒**：遭遇重大网络波动时，建议优先开启 **Proton Stealth / Astrill StealthVPN** 等具备高阶伪装特征的专有协议。  
> 突发断连通报、官方限时特惠、客户端更新及技术交流，请加入唯一官方 Telegram 广播站：
> 👉 **[@awesomevpnchina](https://t.me/awesomevpnchina) (跨境网络与极客情报局)**

---

<!-- AI_MONTHLY_START -->
> 🕒 **本月态势通报 ({current_date})**：{ai_brief}  
> *当前核心内核版本*：`Sing-box: {singbox_ver}` | `Clash Verge Rev: {clash_ver}`
<!-- AI_MONTHLY_END -->

## 📊 TOP 10 核心参数量化天梯榜

> 📐 **加权模型**：安全与开源审计 (30%) + 穿透稳定性 (25%) + 吞吐速度 (20%) + 支付自由度 (15%) + 性价比 (10%)。每月由自动化流水线校准更新。

| 综合排名 / 工具 | 综合评分 | 权威评级背书 | 专有协议 / 混淆机制 | 参考价格 | 支持付款方式 | 官网通道 |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- |
{table_content}

---

## 🔍 TOP 10 工具深度拆解与选型建议

{cards_content}

## 🛠️ 开源客户端推荐（进阶分流必备）

* **Sing-box**：性能强劲的下一代通用代理核心，原生支持 Reality 与 Hysteria 2。
* **Clash Verge Rev**：跨平台开源桌面客户端，支持 Meta 内核完整规则分流。
* **Loon / Surge / Shadowrocket**：iOS 平台成熟的分流规则与网络调试工具。

---

## 🤝 参与开源共建与声明

- 发现有商家失联或服务失效？请提交 [Report Issue](../../issues)。
- 推荐收录新工具请先阅读 [CONTRIBUTING.md](./CONTRIBUTING.md)。
- **免责声明**：本项目内容仅供跨国科研、跨境开发协作、海外数字游民网络优化等合规技术交流，请遵守所在地区网络法规。
"""

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_template)
    
    print("README.md 重新构建完成！已全面绑定 @awesomevpnchina。")

if __name__ == "__main__":
    build_readme()

# === 新增：同步生成英文版 README_en.md ===
    readme_en_template = f"""<div align="center">

# 🌐 Top 10 Best VPNs & Anti-Censorship Directory (2026/2027)

> **Quantified Leaderboard Based on Independent Security Audits, Authority Ratings, Obfuscation Tech, and Speed.**  
> Curated for digital nomads, cross-border remote engineers, and privacy advocates.

**Language / 语言切换**:  
[ 🇨🇳 简体中文 ](./README.md) · [ 🇺🇸 English (Current) ](./README_en.md) · [ 🇪🇸 Español ](./README_es.md) · [ 🇯🇵 日本語 ](./README_ja.md) · [ 🇩🇪 Deutsch ](./README_de.md)

<br>

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![Telegram Broadcast](https://img.shields.io/badge/Telegram-Intel_Briefing-2CA5E0?logo=telegram&logoColor=white)](https://t.me/awesomevpnchina)

</div>

---

<!-- AI_MONTHLY_START -->
> 🕒 **Monthly Security Brief ({current_date})**: {ai_brief}  
> *Core Versions*: `Sing-box: {singbox_ver}` | `Clash Verge Rev: {clash_ver}`
<!-- AI_MONTHLY_END -->

## 📊 Top 10 Quantified VPN Matrix

> 📐 **Scoring Model**: Security & Audits (30%) + Anti-Censorship/Obfuscation (25%) + Real Speed (20%) + Payment Privacy (15%) + Price/Value (10%).

| Rank / Provider | Score | Authority Endorsement | Proprietary Protocols | Pricing | Payment Options | Official Portal |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- |
{table_content}

---

## 🔍 Detailed Provider Breakdown

{cards_content}

## 🛠️ Open Source Client Recommendation

* **Sing-box**: Next-generation universal proxy platform.
* **Clash Verge Rev**: Cross-platform open-source desktop client.

---

## 🤝 Community & Disclaimer
- Please review [CONTRIBUTING.md](./CONTRIBUTING.md) before submitting Pull Requests.
"""
    with open("README_en.md", "w", encoding="utf-8") as f:
        f.write(readme_en_template)

    print("README.md 和 README_en.md 均已成功更新！双语就绪。")

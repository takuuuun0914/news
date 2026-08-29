import os
import feedparser
from pathlib import Path
from openai import OpenAI


# ============================================================
# OpenAI
# ============================================================

api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY が設定されていません。"
        "GitHub Secretsを確認してください。"
    )

client = OpenAI(api_key=api_key)

# コストを抑えるためLunaを使用
MODEL = "gpt-5.6-luna"


# ============================================================
# RSS
# ============================================================

RSS_FEEDS = {
    "AI": "https://www.technologyreview.com/feed/",
    "Microsoft Security":
        "https://www.microsoft.com/en-us/security/blog/feed/",
}


# ============================================================
# あなたの興味分野
# ============================================================

KEYWORDS = [
    "AI",
    "artificial intelligence",
    "generative AI",
    "generative artificial intelligence",
    "LLM",
    "large language model",
    "AI agent",
    "agentic AI",
    "MCP",
    "model context protocol",

    "cybersecurity",
    "cyber security",
    "security",
    "SOC",
    "SIEM",
    "SOAR",

    "Microsoft Sentinel",
    "Sentinel",
    "Security Copilot",
    "Microsoft Defender",
    "Defender",

    "CrowdStrike",
    "Palo Alto",
    "Splunk",

    "threat intelligence",
    "malware",
    "ransomware",
]


# ============================================================
# RSSニュース取得
# ============================================================

def get_news():

    news = []

    for category, url in RSS_FEEDS.items():

        print(f"RSS取得: {category}")

        feed = feedparser.parse(url)

        print(f"  {len(feed.entries)}件")

        for entry in feed.entries[:15]:

            title = entry.get("title", "")
            summary = entry.get("summary", "")
            link = entry.get("link", "")

            news.append({
                "category": category,
                "title": title,
                "summary": summary,
                "url": link
            })

    return news


# ============================================================
# Pythonによる一次フィルター
# ============================================================

def keyword_filter(news):

    filtered = []

    for item in news:

        text = (
            item["title"] + " " +
            item["summary"]
        ).lower()

        matched = False

        for keyword in KEYWORDS:

            if keyword.lower() in text:
                matched = True
                break

        if matched:
            filtered.append(item)

    # 最大15件
    return filtered[:15]


# ============================================================
# LLMでニュース選別
# ============================================================

def select_news(news):

    if not news:
        return "今日は対象ニュースがありませんでした。"

    news_text = "\n\n".join(
        f"""
【ニュース】

タイトル:
{item["title"]}

カテゴリ:
{item["category"]}

概要:
{item["summary"]}

URL:
{item["url"]}
"""
        for item in news
    )

    prompt = f"""
あなたは私専属のニュースキュレーターです。

以下のニュースから、
私にとって重要度の高いニュースを最大5件選んでください。

私の主な関心分野：

・生成AI
・LLM
・AI Agent
・MCP
・AI SOC
・サイバーセキュリティ
・SOC
・SIEM
・Microsoft Sentinel
・Microsoft Defender
・Security Copilot
・CrowdStrike
・Palo Alto
・Splunk

特に以下を高く評価してください。

1. 現在の仕事に役立つ
2. AI SOCに利用できる
3. 新しいAI技術
4. サイバーセキュリティへの影響
5. Microsoft Securityへの影響
6. キャリアアップにつながる
7. 将来のビジネスにつながる
8. 実際に試してみる価値がある

以下の形式で回答してください。

【1位】
タイトル：
重要度：
理由：
仕事への活用：
今日やると良いこと：

【2位】
...

最大5位まで。

ニュース：

{news_text}
"""

    print("LLMにニュース選別を依頼しています...")

    response = client.responses.create(
        model=MODEL,
        input=prompt
    )

    return response.output_text


# ============================================================
# Podcast台本生成
# ============================================================

def create_script(selected_news):

    prompt = f"""
あなたはIT・サイバーセキュリティ専門の
Podcastパーソナリティです。

以下のニュース選定結果をもとに、
日本語のPodcast台本を作成してください。

目安：
8～10分

対象：
・ITエンジニア
・サイバーセキュリティ担当者
・AIに興味がある人

特に、
AI SOC
Security Copilot
Microsoft Sentinel
AI Agent
LLM
サイバーセキュリティ

について理解が深まる内容にしてください。

構成：

【オープニング】

「おはようございます。
今日のAI・サイバーセキュリティニュースです。」

【今日のTOPニュース】

重要度順に紹介。

各ニュースについて、

・何が起きたのか
・なぜ重要なのか
・技術的には何がポイントなのか
・SOC/AIにどう影響するのか
・仕事でどう使えそうか

を分かりやすく説明。

【今日の注目ポイント】

今日一番重要なニュースを1つ選ぶ。

【今日やること】

ニュースを踏まえて、
仕事で実際に試してみると良いことを1つ提案。

【エンディング】

明日につながる一言で終了。

文章は音声で自然に聞こえるようにしてください。

ニュース：

{selected_news}
"""

    print("Podcast台本を作成しています...")

    response = client.responses.create(
        model=MODEL,
        input=prompt
    )

    return response.output_text


# ============================================================
# TTS
# ============================================================

def create_audio(script):

    output = Path("ai_news.mp3")

    print("Podcast音声を生成しています...")

    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=script
    ) as response:

        response.stream_to_file(output)

    return output


# ============================================================
# メイン
# ============================================================

def main():

    print("=" * 60)
    print("AI News Podcast START")
    print("=" * 60)

    # --------------------------------
    # 1. RSS
    # --------------------------------

    print("\n[1] ニュース取得")

    news = get_news()

    print(f"\n合計 {len(news)}件取得")


    # --------------------------------
    # 2. Pythonフィルター
    # --------------------------------

    print("\n[2] キーワードフィルター")

    filtered_news = keyword_filter(news)

    print(
        f"{len(news)}件 → "
        f"{len(filtered_news)}件"
    )

    if not filtered_news:

        print("対象ニュースがありません。")

        Path("script.txt").write_text(
            "本日は対象ニュースがありませんでした。",
            encoding="utf-8"
        )

        return


    # --------------------------------
    # 3. LLM選別
    # --------------------------------

    print("\n[3] LLMニュース選別")

    selected_news = select_news(filtered_news)

    print("\n--- 選別結果 ---")

    print(selected_news)

    print("--- 選別結果終了 ---")


    # --------------------------------
    # 4. 台本
    # --------------------------------

    print("\n[4] Podcast台本作成")

    script = create_script(selected_news)

    Path("script.txt").write_text(
        script,
        encoding="utf-8"
    )

    print("script.txt 保存完了")


    # --------------------------------
    # 5. 音声
    # --------------------------------

    print("\n[5] 音声生成")

    audio = create_audio(script)

    print(f"MP3完成: {audio}")


    # --------------------------------
    # 完了
    # --------------------------------

    print("\n" + "=" * 60)
    print("AI News Podcast COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()

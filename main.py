import os
import feedparser
from pathlib import Path
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)


RSS_FEEDS = {
    "AI": "https://www.technologyreview.com/feed/",
    "Microsoft Security":
        "https://www.microsoft.com/en-us/security/blog/feed/",
}


def get_news():

    news = []

    for category, url in RSS_FEEDS.items():

        feed = feedparser.parse(url)

        for entry in feed.entries[:10]:

            news.append({
                "category": category,
                "title": entry.get("title", ""),
                "summary": entry.get("summary", ""),
                "url": entry.get("link", "")
            })

    return news


def select_news(news):

    text = "\n\n".join(
        f"""
タイトル: {n["title"]}
カテゴリ: {n["category"]}
概要: {n["summary"]}
URL: {n["url"]}
"""
        for n in news
    )

    prompt = f"""
あなたは私専属のニュースキュレーターです。

以下のニュースから、
私にとって重要なニュースを5件選んでください。

私の関心：

- AI
- 生成AI
- AI Agent
- MCP
- AI SOC
- サイバーセキュリティ
- SOC
- Microsoft Sentinel
- Security Copilot
- CrowdStrike
- Palo Alto
- Splunk
- LLM

特に、

1. 仕事に役立つ
2. AI SOCに使える
3. 新しい技術
4. セキュリティ業界への影響
5. キャリアアップ
6. 将来のビジネス

につながるニュースを優先してください。

重要度順に5件選び、
「なぜ重要なのか」も説明してください。

ニュース：

{text}
"""

    response = client.responses.create(
        model="gpt-5.6",
        input=prompt
    )

    return response.output_text


def create_script(selected):

    prompt = f"""
以下のニュースを使って、
日本語のニュースPodcast台本を作成してください。

10分程度。

対象：
ITエンジニア
サイバーセキュリティ担当者
AIに興味がある人

構成：

1. オープニング
2. 今日のニュースTOP5
3. 各ニュースの概要
4. なぜ重要なのか
5. AI/SOCへの影響
6. 仕事でどう使えるか
7. 今日のアクション
8. エンディング

ニュース：

{selected}
"""

    response = client.responses.create(
        model="gpt-5.6",
        input=prompt
    )

    return response.output_text


def create_audio(script):

    output = Path("ai_news.mp3")

    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=script
    ) as response:

        response.stream_to_file(output)

    return output


def main():

    print("ニュース取得")

    news = get_news()

    print(f"{len(news)}件取得")

    print("ニュース選別")

    selected = select_news(news)

    print("Podcast台本作成")

    script = create_script(selected)

    print("音声化")

    create_audio(script)

    Path("script.txt").write_text(
        script,
        encoding="utf-8"
    )

    print("完成")


if __name__ == "__main__":
    main()

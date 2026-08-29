from openai import OpenAI
from pathlib import Path

client = OpenAI()

text = """
おはようございます。
あなた専用のAIニュースラジオです。

今日のテーマはAI、サイバーセキュリティ、
AI SOC、Microsoft Security Copilot、MCPです。

今回のニュースを仕事にどう活かせるかという視点で、
最新情報をわかりやすく解説していきます。

今日も一日頑張りましょう。
"""

output_file = Path("ai_news.mp3")

with client.audio.speech.with_streaming_response.create(
    model="gpt-4o-mini-tts",
    voice="alloy",
    input=text,
) as response:
    response.stream_to_file(output_file)

print(f"MP3 generated: {output_file}")

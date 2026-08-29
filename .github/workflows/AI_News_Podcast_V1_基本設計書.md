# AI News Podcast Version 1 基本設計書

## 1. 文書概要

### 1.1 目的

RSSからAI・サイバーセキュリティ関連のニュースを自動取得し、OpenAI APIを利用してユーザーにとって重要なニュースを選別・要約したうえで、Podcast用の台本を生成し、音声ファイル（MP3）として出力する。

本システムでは、GitHub Actionsを利用して一連の処理を自動実行する。

### 1.2 対象範囲

Version 1では以下の機能を対象とする。

* RSSニュース取得
* Pythonによるキーワードフィルタリング
* LLMによるニュース選別
* Podcast台本生成
* TTSによる音声生成
* MP3ファイル生成
* GitHub Actionsによる定期実行
* GitHub Actions Artifactへの成果物保存

### 1.3 Version 1のゴール

毎朝決められた時間にGitHub Actionsを自動起動し、

```text
RSS
 ↓
ニュース取得
 ↓
キーワードフィルター
 ↓
LLMによる重要ニュース選定
 ↓
Podcast台本生成
 ↓
TTS音声生成
 ↓
MP3
```

までを自動化する。

---

# 2. システム概要

## 2.1 全体構成

```text
                    GitHub Actions
                          │
                     毎朝5:00 JST
                          │
                          ▼
                 ┌─────────────────┐
                 │     main.py     │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │   RSS取得処理   │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Pythonフィルター│
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ OpenAI API      │
                 │ ニュース選別    │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ OpenAI API      │
                 │ 台本生成        │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ OpenAI TTS      │
                 │ 音声生成        │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ ai_news.mp3     │
                 │ script.txt      │
                 └────────┬────────┘
                          │
                          ▼
                 GitHub Actions
                    Artifact
```

---

# 3. システム構成

## 3.1 使用技術

| 項目       | 技術                      |
| -------- | ----------------------- |
| 開発言語     | Python 3.12             |
| ソースコード管理 | GitHub                  |
| バッチ実行    | GitHub Actions          |
| ニュース取得   | RSS                     |
| RSS解析    | feedparser              |
| LLM      | OpenAI API              |
| ニュース選別   | GPT-5.6 Luna            |
| 台本生成     | GPT-5.6 Luna            |
| 音声生成     | OpenAI TTS              |
| 音声形式     | MP3                     |
| 成果物保存    | GitHub Actions Artifact |

---

# 4. GitHubリポジトリ構成

```text
ai-news-podcast/
│
├── main.py
├── requirements.txt
├── README.md
│
└── .github/
    └── workflows/
        └── podcast.yml
```

### 各ファイルの役割

| ファイル             | 役割               |
| ---------------- | ---------------- |
| main.py          | メイン処理            |
| requirements.txt | Pythonライブラリ定義    |
| README.md        | システム説明           |
| podcast.yml      | GitHub Actions定義 |

---

# 5. 処理方式

## 5.1 処理フロー

### STEP 1：GitHub Actions起動

GitHub Actionsのschedule機能により、毎日自動実行する。

日本時間5:00に実行する場合：

```yaml
schedule:
  - cron: "0 20 * * *"
```

GitHub ActionsのcronはUTCで指定するため、

```text
20:00 UTC
=
05:00 JST（翌日）
```

となる。

また、GitHub画面から手動実行できるように`workflow_dispatch`を設定する。

---

# 6. RSSニュース取得

## 6.1 概要

登録したRSS Feedからニュースを取得する。

### Version 1 RSS

```text
AI
Microsoft Security
```

### RSS定義例

```python
RSS_FEEDS = {
    "AI":
        "https://www.technologyreview.com/feed/",

    "Microsoft Security":
        "https://www.microsoft.com/en-us/security/blog/feed/",
}
```

---

## 6.2 取得項目

ニュース1件について以下の情報を取得する。

| 項目       | 内容       |
| -------- | -------- |
| category | RSSカテゴリ  |
| title    | ニュースタイトル |
| summary  | ニュース概要   |
| url      | 元記事URL   |

データ例：

```text
category:
AI

title:
Example AI News

summary:
AIに関するニュース概要

url:
https://example.com/news
```

---

## 6.3 取得件数

Version 1ではRSS Feedごとに最大15件取得する。

```python
for entry in feed.entries[:15]:
```

RSSが2つの場合、最大30件程度を取得する。

---

# 7. キーワードフィルター

## 7.1 目的

すべてのニュースをLLMに送信すると不要なAPI利用が発生するため、Pythonで一次フィルタリングを行う。

## 7.2 主なキーワード

### AI

```text
AI
Artificial Intelligence
Generative AI
LLM
AI Agent
Agentic AI
MCP
Model Context Protocol
```

### Cybersecurity

```text
Cybersecurity
Cyber Security
Security
SOC
SIEM
SOAR
Malware
Ransomware
Threat Intelligence
```

### Microsoft Security

```text
Microsoft Sentinel
Sentinel
Security Copilot
Microsoft Defender
Defender
```

### Security Vendor

```text
CrowdStrike
Palo Alto
Splunk
```

---

## 7.3 フィルタリング方式

ニュースのタイトルと概要を連結し、キーワードが含まれるニュースだけを残す。

```text
タイトル
+
概要
 ↓
小文字化
 ↓
キーワード検索
 ↓
該当ニュースのみ採用
```

最大15件をLLM処理対象とする。

---

# 8. LLMニュース選別

## 8.1 目的

単純なキーワード検索ではなく、ユーザーにとって本当に重要なニュースをLLMで判断する。

## 8.2 使用モデル

```text
GPT-5.6 Luna
```

モデル名はAPI仕様変更に応じて変更可能とする。

---

## 8.3 選別基準

以下の観点でニュースを評価する。

1. 現在の仕事に役立つ
2. AI SOCに利用できる
3. 新しいAI技術
4. サイバーセキュリティへの影響
5. Microsoft Securityへの影響
6. キャリアアップへの影響
7. 将来のビジネスへの可能性
8. 実際に試す価値

---

## 8.4 出力件数

最大5件。

重要度順にランキングする。

```text
1位
2位
3位
4位
5位
```

---

## 8.5 LLM出力項目

各ニュースについて以下を生成する。

```text
タイトル
重要度
重要な理由
仕事への活用方法
今日やると良いこと
```

---

# 9. Podcast台本生成

## 9.1 目的

ニュース選別結果を、音声で聞きやすいPodcast形式に変換する。

## 9.2 想定時間

約8～10分。

---

## 9.3 Podcast構成

```text
オープニング
 ↓
今日のTOPニュース
 ↓
ニュース1
 ↓
ニュース2
 ↓
ニュース3
 ↓
ニュース4
 ↓
ニュース5
 ↓
今日の注目ポイント
 ↓
今日やること
 ↓
エンディング
```

---

## 9.4 各ニュースの説明項目

各ニュースについて、

* 何が起きたのか
* なぜ重要なのか
* 技術的なポイント
* SOC/AIへの影響
* 仕事での活用方法

を説明する。

---

# 10. 音声生成

## 10.1 方式

Podcast台本をOpenAI TTSへ送信し、音声を生成する。

```text
script.txt
    ↓
OpenAI TTS
    ↓
ai_news.mp3
```

## 10.2 出力ファイル

```text
ai_news.mp3
```

---

# 11. 成果物

GitHub Actions実行後、以下を生成する。

```text
ai_news.mp3
script.txt
```

### ai_news.mp3

Podcast音声ファイル。

### script.txt

Podcast生成に使用した台本。

---

# 12. GitHub Actions

## 12.1 実行タイミング

### 自動実行

毎日5:00 JST。

### 手動実行

GitHub Actions画面から実行可能。

```yaml
workflow_dispatch:
```

---

## 12.2 実行ステップ

```text
1. GitHub Repository Checkout
        ↓
2. Python 3.12セットアップ
        ↓
3. ライブラリインストール
        ↓
4. main.py実行
        ↓
5. Podcast生成
        ↓
6. Artifact保存
```

---

# 13. APIキー管理

OpenAI APIキーはソースコードに直接記載しない。

GitHub Secretsを利用する。

## Secret名

```text
OPENAI_API_KEY
```

Pythonからは環境変数として取得する。

```python
api_key = os.environ.get("OPENAI_API_KEY")
```

---

# 14. セキュリティ設計

## 14.1 APIキー

以下を禁止する。

```text
main.pyへのAPIキー直接記載
```

```text
README.mdへのAPIキー記載
```

```text
GitHub RepositoryへのAPIキーCommit
```

GitHub Secretsを利用する。

---

## 14.2 GitHub Secrets

```text
Settings
 ↓
Secrets and variables
 ↓
Actions
 ↓
New repository secret
```

以下を登録する。

```text
Name:
OPENAI_API_KEY

Value:
OpenAI API Key
```

---

# 15. エラー処理

Version 1では、GitHub Actionsのログからエラー原因を確認できるようにする。

## 15.1 APIキー未設定

以下のエラーを表示する。

```text
OPENAI_API_KEY が設定されていません。
GitHub Secretsを確認してください。
```

---

## 15.2 API利用制限

OpenAI APIが利用できない場合、GitHub Actionsを失敗させる。

例：

```text
429
insufficient_quota
```

この場合はOpenAI APIのBillingおよび利用状況を確認する。

---

## 15.3 RSS取得失敗

RSS Feedが取得できない場合は、GitHub Actionsログに対象RSSを表示する。

---

# 16. コスト設計

## 16.1 コスト発生箇所

主に以下。

```text
OpenAI API
 ├── ニュース選別
 ├── Podcast台本生成
 └── TTS音声生成
```

RSS取得、Python処理、GitHub Actions自体は基本的に追加料金を発生させない構成とする。

---

## 16.2 コスト削減方針

以下の方法でAPI利用量を抑える。

### ① Pythonによる一次フィルター

LLMへ送信するニュース数を削減する。

```text
30記事
 ↓
Python
 ↓
最大15記事
```

### ② LLMによる選別

重要ニュースのみPodcast台本に利用する。

```text
15記事
 ↓
TOP5
```

### ③ Podcast時間を制御

Podcastを約8～10分にする。

---

# 17. 非機能要件

## 17.1 自動実行

毎日自動実行する。

## 17.2 手動実行

GitHub Actionsから任意のタイミングで実行できること。

## 17.3 再実行

失敗した場合、GitHub Actionsから再実行できること。

## 17.4 セキュリティ

APIキーをGitHub Repositoryに保存しないこと。

## 17.5 保守性

RSS Feed、キーワード、LLMモデルを`main.py`から変更可能とする。

---

# 18. Version 1の制約

Version 1では以下を対象外とする。

* 過去ニュースとの重複チェック
* ニュースの永続データベース
* Google Driveへの自動保存
* メール配信
* Spotify等への自動公開
* YouTubeへの自動公開
* Podcast RSS Feedの生成
* ユーザーからのフィードバック学習
* ニュースの真偽確認
* Web検索による追加情報取得

---

# 19. Version 2以降の拡張案

## Version 2

### ニュース重複防止

```text
RSS
 ↓
過去7日間のニュースと比較
 ↓
既出ニュース除外
 ↓
LLM
```

---

## Version 3

### Web検索による情報補完

```text
RSS
 ↓
ニュース取得
 ↓
Web検索
 ↓
複数ソース確認
 ↓
LLM
```

これによりニュースの内容をより正確に把握する。

---

## Version 4

### パーソナライズ強化

ユーザーの関心度を蓄積する。

```text
AI SOC
★★★★★

Security Copilot
★★★★★

AI Agent
★★★★★

MCP
★★★★☆

一般AIニュース
★★★☆☆
```

ニュース選別の精度を向上させる。

---

## Version 5

### 配信自動化

```text
GitHub Actions
      ↓
Podcast生成
      ↓
Google Drive
      ↓
メール通知
      ↓
スマートフォン
      ↓
通勤中に再生
```

---

# 20. Version 1 完成イメージ

最終的に毎朝、

```text
05:00
 ↓
GitHub Actions起動
 ↓
AI/Securityニュース取得
 ↓
Pythonフィルター
 ↓
LLMがあなた向けにTOP5選定
 ↓
Podcast台本生成
 ↓
TTS
 ↓
ai_news.mp3
 ↓
GitHub Artifact
```

となる。

## 期待する成果

ユーザーが毎朝大量のニュースを読むことなく、

**「自分にとって重要なAI・サイバーセキュリティニュース」**

を音声で効率的にインプットできる環境を構築する。

また、将来的にはニュースだけでなく、

* 今日仕事で試すこと
* AI SOCへの活用方法
* キャリアアップにつながる情報
* 新しい副業アイデア

まで自動生成する「パーソナルAIニュースエージェント」へ拡張する。

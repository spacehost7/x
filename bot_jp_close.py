import os
import datetime
import tweepy
from anthropic import Anthropic

# ===== 設定 =====
CLAUDE_MODEL = "claude-haiku-4-5"  # Haiku 4.5 固定

# X API keys（GitHub Secrets 経由）
X_API_KEY = os.environ["X_API_KEY"]
X_API_SECRET = os.environ["X_API_SECRET"]
X_ACCESS_TOKEN = os.environ["X_ACCESS_TOKEN"]
X_ACCESS_TOKEN_SECRET = os.environ["X_ACCESS_TOKEN_SECRET"]

# Claude client
CLAUDE_API_KEY = os.environ["CLAUDE_API_KEY"]
client = Anthropic(api_key=CLAUDE_API_KEY)


def generate_text_with_claude(prompt: str) -> str:
    resp = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=512,
        temperature=0.7,
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    content = resp.content
    if isinstance(content, list) and len(content) > 0:
        part = content[0]
        if isinstance(part, dict) and "text" in part:
            return part["text"].strip()
        if hasattr(part, "text"):
            return part.text.strip()
    if hasattr(resp, "text"):
        return resp.text.strip()
    return str(resp)


def post_to_x(text: str) -> None:
    auth = tweepy.OAuth1UserHandler(
        X_API_KEY,
        X_API_SECRET,
        X_ACCESS_TOKEN,
        X_ACCESS_TOKEN_SECRET,
    )
    api = tweepy.API(auth)
    api.update_status(status=text)


def main() -> None:
    today = datetime.datetime.now(datetime.timezone.utc).astimezone(
        datetime.timezone(datetime.timedelta(hours=9))
    )
    date_str = today.strftime("%Y-%m-%d（%a）")

    prompt = f"""
あなたは日本の株式市場とマクロ環境に詳しいアナリストです。
日本時間の大引け後に、Xに投稿する1ポスト分の文章を日本語で作成してください。

条件:
- 日付を先頭に入れる（例: {date_str}）
- 1日の相場のざっくりした振り返り（上げ/下げ要因、主なセクター）
- 140文字以内を目安に、やや砕けた口調で
- ハッシュタグは最大2個まで
- 絵文字は使わない

出力はそのままXに投稿される本文だけにしてください。
"""

    text = generate_text_with_claude(prompt)
    print("Generated text (close):", text)
    post_to_x(text)


if __name__ == "__main__":
    main()

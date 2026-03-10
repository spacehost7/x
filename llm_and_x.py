# llm_and_x.py

import os
from datetime import datetime, timedelta, timezone

import tweepy

# ===== 時刻（JST） =====

JST = timezone(timedelta(hours=9))

def now_jst() -> datetime:
    return datetime.now(JST)

# ===== X クライアント =====

API_KEY = os.getenv("X_API_KEY")
API_SECRET = os.getenv("X_API_SECRET")
ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")

client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
)

def post_to_x(text: str):
    print("POST_TO_X_CALLED")
    print(
        "ENV_CHECK:",
        (API_KEY or "")[:4],
        (ACCESS_TOKEN or "")[:4],
    )
    print("TEXT_LEN:", len(text))
    print("TEXT:", text)

    resp = client.create_tweet(text=text)
    print("CREATE_TWEET_RESPONSE:", resp)
    return resp

# ===== LLM ダミー =====
# ここは後で Claude 連携に差し替えればOK

def generate_with_claude(prompt: str) -> str:
    # とりあえず動作確認用の固定文
    print("GENERATE_WITH_CLAUDE_CALLED")
    return "テスト: 日本株 市場概況。詳細なコメントは後日対応予定。"

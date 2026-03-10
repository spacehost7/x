import os
import json
from datetime import datetime, timedelta, timezone

import requests
import anthropic
import tweepy

JST = timezone(timedelta(hours=9))
STATE_FILE = "state_jp_close.json"


def now_jst():
    return datetime.now(JST)


def today_str():
    return now_jst().strftime("%Y-%m-%d")


def already_posted_today():
    if not os.path.exists(STATE_FILE):
        return False
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("last_post_date") == today_str()
    except Exception:
        return False


def mark_posted_today():
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_post_date": today_str()}, f, ensure_ascii=False)


def fetch_tokyo_close_data():
    """
    NOTE:
      ここもダミーデータです。
      実際には日経平均・TOPIXの終値と前日比を取得できるAPIに置き換えてください。
    """
    return {
        "nikkei_close": 39200,
        "nikkei_change": +300,
        "nikkei_change_pct": +0.77,
        "topix_close": 2820,
        "topix_change": +20,
        "topix_change_pct": +0.71,
    }


def build_claude_prompt(market):
    direction_emoji = ""
    if market["nikkei_change"] > 0 and market["topix_change"] > 0:
        direction_emoji = "📈"
    elif market["nikkei_change"] < 0 and market["topix_change"] < 0:
        direction_emoji = "📉"

    prompt = f"""
あなたは「投資家カナ」という日本人の女性個人投資家です。
フォロワーに向けて、東京市場の1日の動きを日本語で短く総括します。

条件:
- ですます調で落ち着いたトーン
- 文字数はおおよそ120〜200文字
- ハッシュタグは付けない
- 絵文字は使っても1つだけ。相場が上昇なら {direction_emoji}、下落なら📉、方向感が薄ければ絵文字なしでもよい
- 投資助言ではなく「今日こういう一日でした」という振り返りにする

終値データ:
- 日経平均: {market['nikkei_close']}円 ({market['nikkei_change']}円, {market['nikkei_change_pct']}%)
- TOPIX: {market['topix_close']}ポイント ({market['topix_change']}ポイント, {market['topix_change_pct']}%)

これらを踏まえて、「投資家カナ」として1日の総括コメントを1つだけ出力してください。
本文のみを出力し、前後に説明文は付けないでください。
"""
    return prompt.strip()


def generate_text_with_claude(prompt: str) -> str:
    api_key = os.environ["CLAUDE_API_KEY"]
    client = anthropic.Anthropic(api_key=api_key)

    resp = client.messages.create(
        model="claude-3-5-haiku-latest",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text.strip()


def post_to_x(text: str):
    api_key = os.environ["X_API_KEY"]
    api_secret = os.environ["X_API_SECRET"]
    access_token = os.environ["X_ACCESS_TOKEN"]
    access_token_secret = os.environ["X_ACCESS_TOKEN_SECRET"]

    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
    api = tweepy.API(auth)
    api.update_status(status=text)


def main():
    now = now_jst()

    # JSTで15:30以降のみ投稿対象にする（保険）
    if now.hour < 15 or (now.hour == 15 and now.minute < 30):
        return

    if already_posted_today():
        return

    market = fetch_tokyo_close_data()
    prompt = build_claude_prompt(market)
    text = generate_text_with_claude(prompt)

    post_to_x(text)
    mark_posted_today()


if __name__ == "__main__":
    main()

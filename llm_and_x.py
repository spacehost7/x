import os
import datetime
import tweepy
from anthropic import Anthropic

CLAUDE_MODEL = "claude-haiku-4-5"

CLAUDE_API_KEY = os.environ["CLAUDE_API_KEY"]
client_llm = Anthropic(api_key=CLAUDE_API_KEY)

X_API_KEY = os.environ["X_API_KEY"]
X_API_SECRET = os.environ["X_API_SECRET"]
X_ACCESS_TOKEN = os.environ["X_ACCESS_TOKEN"]
X_ACCESS_TOKEN_SECRET = os.environ["X_ACCESS_TOKEN_SECRET"]

def generate_with_claude(prompt: str) -> str:
    resp = client_llm.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=260,
        temperature=0.7,
        messages=[{"role": "user", "content": prompt}],
    )

    content = resp.content
    if isinstance(content, list) and content:
        part = content[0]
        if isinstance(part, dict) and "text" in part:
            return part["text"].strip()
        if hasattr(part, "text"):
            return part.text.strip()
    if hasattr(resp, "text"):
        return resp.text.strip()
    return str(resp)

def post_to_x(text: str) -> None:
    client = tweepy.Client(
        consumer_key=X_API_KEY,
        consumer_secret=X_API_SECRET,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_TOKEN_SECRET,
    )
    client.create_tweet(text=text)  # [web:489][web:512]

def now_jst() -> datetime.datetime:
    jst = datetime.timezone(datetime.timedelta(hours=9))
    return datetime.datetime.now(datetime.timezone.utc).astimezone(jst)

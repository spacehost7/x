# llm_and_x.py

import os
import tweepy

bearer_token = None  # 使ってないなら None でOK
api_key = os.getenv("X_API_KEY")
api_secret = os.getenv("X_API_SECRET")
access_token = os.getenv("X_ACCESS_TOKEN")
access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

client = tweepy.Client(
    consumer_key=api_key,
    consumer_secret=api_secret,
    access_token=access_token,
    access_token_secret=access_token_secret,
    bearer_token=bearer_token
)

def post_to_x(text: str):
    print("POST_TO_X_CALLED")
    print("ENV_CHECK:",
          (api_key or "")[:4],
          (access_token or "")[:4])

    try:
        resp = client.create_tweet(text=text)
        print("CREATE_TWEET_RESPONSE:", resp)
    except Exception as e:
        print("CREATE_TWEET_ERROR:", repr(e))
        raise

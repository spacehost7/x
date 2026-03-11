def post_to_x(text: str) -> None:
    client = tweepy.Client(
        consumer_key=X_API_KEY,
        consumer_secret=X_API_SECRET,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_TOKEN_SECRET,
    )
    try:
        client.create_tweet(text=text)
    except Exception as e:
        print("X API error:", repr(e))
        raise

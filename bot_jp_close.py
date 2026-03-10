# llm_and_x.py

def post_to_x(text: str):
    print("POST_TO_X_TEXT_LEN:", len(text))
    print("POST_TO_X_TEXT:", text)

    try:
        resp = client.create_tweet(text=text)
        print("CREATE_TWEET_RESPONSE:", resp)
    except Exception as e:
        print("CREATE_TWEET_ERROR:", repr(e))
        raise

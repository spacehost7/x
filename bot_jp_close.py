# bot_jp_close.py

from datetime import datetime
from llm_and_x import post_to_x

def build_safe_close_text() -> str:
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M")
    return f"日本株 後場テスト投稿（{date_str}）"

def main():
    print("ENTRY_CLOSE")              # ログ確認用
    text = build_safe_close_text()
    print("TEXT_LEN_CLOSE:", len(text))
    print("TEXT_CLOSE:", text)
    post_to_x(text)
    print("END_CLOSE")

if __name__ == "__main__":
    main()

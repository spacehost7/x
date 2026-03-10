# bot_jp_close.py

from llm_and_x import now_jst, generate_with_claude, post_to_x

def build_close_text() -> str:
    now = now_jst()
    date_str = now.strftime("%Y-%m-%d")
    header = f"日本株 後場まとめ（{date_str}）\n"
    body = generate_with_claude("日本株 後場のテスト要約を80文字以内で作成して。")
    full = header + body
    return full[:260]

def main():
    print("ENTRY_CLOSE")
    text = build_close_text()
    print("CLOSE_TEXT_LEN:", len(text))
    print("CLOSE_TEXT:", text)
    post_to_x(text)
    print("END_CLOSE")

if __name__ == "__main__":
    main()

# bot_jp_morning.py

from llm_and_x import now_jst, generate_with_claude, post_to_x

def build_morning_text() -> str:
    now = now_jst()
    date_str = now.strftime("%Y-%m-%d")
    header = f"日本株 前場まとめ（{date_str}）\n"
    body = generate_with_claude("日本株 前場のテスト要約を80文字以内で作成して。")
    full = header + body
    return full[:260]  # 余裕を持ってカット

def main():
    print("ENTRY_MORNING")
    text = build_morning_text()
    print("MORNING_TEXT_LEN:", len(text))
    print("MORNING_TEXT:", text)
    post_to_x(text)
    print("END_MORNING")

if __name__ == "__main__":
    main()

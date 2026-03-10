from llm_and_x import generate_with_claude, post_to_x, now_jst


def main() -> None:
    now = now_jst()
    date_str = now.strftime("%Y-%m-%d（%a）")

    prompt = f"""
あなたは日本の株式市場とマクロ環境に詳しいアナリストです。
日本時間の大引け後に、Xに投稿する1ポスト分の文章を日本語で作成してください。

条件:
- 日付を先頭に入れる（例: {date_str}）
- 1日の相場のざっくりした振り返り（上げ/下げ要因、主なセクター）を一般論レベルでまとめる
- 140文字以内を目安に、やや砕けた口調で
- ハッシュタグは最大2個まで
- 絵文字は使わない
- 個別銘柄名や誤解を招く具体数値は出さない

出力はそのままXに投稿される本文だけにしてください。
"""

    text = generate_with_claude(prompt)
    print("=== Close generated ===")
    print(text)
    url = post_to_x(text)
    print("Posted:", url)


if __name__ == "__main__":
    main()

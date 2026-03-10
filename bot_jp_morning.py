from llm_and_x import generate_with_claude, post_to_x, now_jst


def main() -> None:
    now = now_jst()
    date_str = now.strftime("%Y-%m-%d（%a）")

    prompt = f"""
あなたは日本の株式市場とマクロ環境に詳しいアナリストです。
日本時間の前場寄りに、Xに投稿する1ポスト分の文章を日本語で作成してください。

条件:
- 日付を先頭に入れる（例: {date_str}）
- 日本株市場全体の雰囲気、注目セクター、為替や金利などをコンパクトに触れる
- 140文字以内を目安に、やや砕けた口調で
- ハッシュタグは最大2個まで
- 絵文字は使わない
- 事実関係は2024年以降も通用するような一般論にとどめる（具体的な数値や銘柄名は避ける）

出力はそのままXに投稿される本文だけにしてください。
"""

    text = generate_with_claude(prompt)
    print("=== Morning generated ===")
    print(text)
    url = post_to_x(text)
    print("Posted:", url)


if __name__ == "__main__":
    main()

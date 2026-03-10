from market_data import get_market_snapshot
from llm_and_x import generate_with_claude, post_to_x, now_jst


def main() -> None:
    now = now_jst()
    date_str = now.strftime("%Y-%m-%d（%a）")
    snapshot = get_market_snapshot()

    nk = snapshot["core"]["nk225"]
    uj = snapshot["core"]["usd_jpy"]
    eu = snapshot["core"]["eur_usd"]

    opt = snapshot["optional"]

    special_lines = []
    for key in ["gold", "crude", "btc", "eur_jpy", "gbp_jpy", "aud_jpy"]:
        a = opt[key]
        if not (a.big_move or a.crossed_level):
            continue
        if a.direction == "up":
            icon = "📈"
            status = "急騰"
        elif a.direction == "down":
            icon = "📉"
            status = "急落"
        else:
            icon = ""
            status = ""
        extra = f"（{a.crossed_level}）" if a.crossed_level else ""
        line = f"{a.name}: {a.value:.2f} ({a.diff:+.2f}, {a.diff_pct:+.2f}%) {status}{icon}{extra}"
        special_lines.append(line)

    special_text = "\n".join(special_lines) if special_lines else "なし"

    prompt = f"""
あなたは日本市場の引け後短観を書くアナリストです。
以下に、本日の終値ベースのデータを与えます。

【コア指標】（必ずコメントに含めること）
- 日経平均: 終値 {nk.value:.2f}、前日比 {nk.diff:+.2f} ({nk.diff_pct:+.2f}%)
- ドル円: 終値 {uj.value:.3f}、前日比 {uj.diff:+.3f} ({uj.diff_pct:+.2f}%)
- ユーロドル: 終値 {eu.value:.5f}、前日比 {eu.diff:+.5f} ({eu.diff_pct:+.2f}%)

【急騰・急落・節目関連】（ここに列挙されたものは、必ずひと言以上触れること）
{special_text}

ルール:
- 上記の数値データ【だけ】を前提に、1日の相場を振り返る短いコメントを1本だけ作成してください。
- 自分で新しい数値を作ったり、別のデータソースを参照したりしてはいけません。
- 急騰・急落フラグが立っている資産、または節目を越えた資産については、
  「急騰」「急落」という言葉と、対応するアイコン（📈または📉）を必ず本文中に含めてください。
- データがないことを理由に断ったり、謝罪文・注意喚起を書いてはいけません。

出力条件:
- 1行目は日付だけを書く（例: {date_str}）
- 2行目以降で、日本株全体の1日の動き、為替の動き、急騰・急落/節目越えの資産を手短にまとめてください。
- 全体で140文字以内を目安にする。
- 口調はやや砕けた日本語にする。
- 個別銘柄名は出さない。
- 絵文字は📈と📉以外は使わない。
- ハッシュタグは最大2個まで。

出力フォーマット:
- 不要な説明は一切書かず、Xに投稿する本文だけを出力してください。
"""

    text = generate_with_claude(prompt)
    post_to_x(text)


if __name__ == "__main__":
    main()

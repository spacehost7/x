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
        line = (
            f"{a.name}: 終値 {a.value:.2f}, 前日比 {a.diff:+.2f} "
            f"({a.diff_pct:+.2f}%) {status}{icon}{extra}"
        )
        special_lines.append(line)

    special_text = "\n".join(special_lines) if special_lines else "なし"

    prompt = f"""
あなたは日本市場の「前場の短観」を書くアナリストです。
以下に、日足終値ベースのデータを与えます。

【終値ベースのコア指標】（方向感の説明に必ず使うこと）
- 日経平均 終値: {nk.value:.2f}, 前日比: {nk.diff:+.2f} ({nk.diff_pct:+.2f}%)
- ドル円 終値: {uj.value:.3f}, 前日比: {uj.diff:+.3f} ({uj.diff_pct:+.2f}%)
- ユーロドル 終値: {eu.value:.5f}, 前日比: {eu.diff:+.5f} ({eu.diff_pct:+.2f}%)

【急騰・急落・節目関連の資産】（列挙されているものは、必ずひと言以上触れること）
{special_text}

重要ルール:
- 上記の数値データ【だけ】を前提に、前場時点の日本市場の雰囲気を日本語で短く要約してください。
- あなた自身は本文の中に具体的な価格やパーセンテージを書いてはいけません。
  数値は頭の中だけで使い、「大幅高」「重い」「しっかり」などの言葉で方向感だけを表現してください。
- 日付については、必ず1行目にちょうど「{date_str}」とだけ書いてください。
  それ以外の日付や形式にしてはいけません。

急騰・急落・節目について:
- 「急騰」フラグがある資産は、本文で必ずその資産名と「急騰」という言葉と📈をセットで書いてください。
- 「急落」フラグがある資産は、本文で必ずその資産名と「急落」という言葉と📉をセットで書いてください。
- 節目越えの説明がある資産は、その節目（●●ドルを上抜け、××円割れなど）に触れつつ、
  対応する📈または📉を一緒に書いてください。
- アイコンは📈と📉だけを使い、それ以外の絵文字は一切使ってはいけません。

ハッシュタグについて:
- ハッシュタグは0〜2個までにしてください。
- 暗号資産に関するハッシュタグ（例: #BTC, #bitcoin, #仮想通貨 など）は一切使ってはいけません。

出力フォーマット:
- 1行目: ちょうど「{date_str}」だけを書く。
- 2行目以降: 日経平均と為替を中心に、日本市場全体の方向感と
  急騰・急落／節目越えの資産の状況を、140文字以内でやや砕けた日本語でまとめてください。
- 個別銘柄名は出さない。
- 出力はXにそのまま投稿される本文だけとし、説明や注意書きは一切付けないでください。
"""

    text = generate_with_claude(prompt)
    post_to_x(text)


if __name__ == "__main__":
    main()

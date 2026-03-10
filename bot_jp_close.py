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

    # 上部に載せる終値数値行（Python側で固定生成）
    header_lines = [
        f"{date_str}",
        (
            f"日経平均 終値 {nk.value:.2f} 前日比 {nk.diff:+.2f} "
            f"({nk.diff_pct:+.2f}%)"
        ),
        (
            f"ドル円 終値 {uj.value:.3f} 前日比 {uj.diff:+.3f} "
            f"({uj.diff_pct:+.2f}%), "
            f"ユーロドル 終値 {eu.value:.5f} 前日比 {eu.diff:+.5f} "
            f"({eu.diff_pct:+.2f}%)"
        ),
    ]
    header_text = "\n".join(header_lines)

    # 急騰・急落／節目越え資産の要約（LLMへのヒント用）
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
あなたは日本市場の「引け後短観」を書くアナリストです。
以下に、本日の終値ベースのデータを与えます。

【終値ベースのコア指標】（方向感の説明に必ず使うこと）
- 日経平均 終値: {nk.value:.2f}, 前日比: {nk.diff:+.2f} ({nk.diff_pct:+.2f}%)
- ドル円 終値: {uj.value:.3f}, 前日比: {uj.diff:+.3f} ({uj.diff_pct:+.2f}%)
- ユーロドル 終値: {eu.value:.5f}, 前日比: {eu.diff:+.5f} ({eu.diff_pct:+.2f}%)

【急騰・急落・節目関連の資産】（列挙されたものは、必ずひと言以上触れること）
{special_text}

重要ルール:
- あなたは、上記の数値データ【だけ】を前提に、1日の日本市場を振り返る短いコメントを日本語で1本だけ作成してください。
- あなた自身は本文の中に、一切具体的な価格やパーセンテージを書いてはいけません。
  価格や％はヘッダーの数値に任せ、本文では「大幅高」「小反落」「しっかり」「重い」など
  言葉による方向感の説明だけを行ってください。
- 日付や終値の具体的数字は、本文中には書かないでください（ヘッダー部分でのみ表示されます）。

急騰・急落・節目について:
- 「急騰」フラグがある資産は、本文で必ずその資産名と「急騰」という言葉と📈をセットで書いてください。
- 「急落」フラグがある資産は、本文で必ずその資産名と「急落」という言葉と📉をセットで書いてください。
- 節目越え（例: 70000ドルを上抜け、87ドル割れ）がある資産は、その節目に触れつつ、
  対応する📈または📉を一緒に書いてください。
- アイコンは📈と📉だけを使い、それ以外の絵文字は一切使ってはいけません。

ハッシュタグについて:
- ハッシュタグは0〜2個までにしてください。
- 暗号資産に関するハッシュタグ（例: #BTC, #bitcoin, #仮想通貨 など）は一切使ってはいけません。

出力フォーマット:
- 出力するのは「ヘッダーの下に続く本文」だけです。
- ヘッダー部分（{date_str} や終値の数値行）は、こちらで既に用意してあるので出力しないでください。
- 本文は日本語で、140文字以内を目安に、やや砕けた口調で1日の相場をまとめてください。
- 個別銘柄名は出さない。
"""

    body = generate_with_claude(prompt)
    full_text = f"{header_text}\n{body.strip()}"
    post_to_x(full_text)


if __name__ == "__main__":
    main()

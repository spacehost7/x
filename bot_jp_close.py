from market_data import get_market_snapshot
from llm_and_x import generate_with_claude, post_to_x, now_jst


def _format_jp_date_for_close(now) -> str:
    # 例: 3月10日(火)
    youbi = "月火水木金土日"[now.weekday()]
    return f"{now.month}月{now.day}日({youbi})"


def _arrow_for_nk(diff_pct: float) -> str:
    # 日経: ±2%以上でマーク
    if diff_pct >= 2.0:
        return "📈"
    if diff_pct <= -2.0:
        return "📉"
    return ""


def _arrow_for_usdjpy(diff: float) -> str:
    # ドル円: ±0.50円以上でマーク
    if diff >= 0.50:
        return "📈"
    if diff <= -0.50:
        return "📉"
    return ""


def _arrow_for_eurusd(diff: float) -> str:
    # ユーロドル: ±0.05ドル以上でマーク
    if diff >= 0.05:
        return "📈"
    if diff <= -0.05:
        return "📉"
    return ""


def main() -> None:
    now = now_jst()
    date_str = _format_jp_date_for_close(now)

    snapshot = get_market_snapshot()
    nk = snapshot["core"]["nk225"]
    uj = snapshot["core"]["usd_jpy"]
    eu = snapshot["core"]["eur_usd"]
    opt = snapshot["optional"]

    # ヘッダー行のマーク判定
    nk_arrow = _arrow_for_nk(nk.diff_pct)
    uj_arrow = _arrow_for_usdjpy(uj.diff)
    eu_arrow = _arrow_for_eurusd(eu.diff)

    # 2行目: 日経平均 終値＋前日比（条件付き📈📉）
    if nk_arrow:
        nk_label = f"{nk_arrow}日経"
    else:
        nk_label = "日経"

    header_line2 = (
        f"{nk_label} 終値 {nk.value:.2f} "
        f"前日比 {nk.diff:+.2f} ({nk.diff_pct:+.2f}%)"
    )

    # 3行目: ドル円・ユーロドル 終値＋前日比（条件付き📈📉）
    if uj_arrow:
        uj_label = f"{uj_arrow}ドル円"
    else:
        uj_label = "ドル円"

    if eu_arrow:
        eu_label = f"{eu_arrow}ユーロドル"
    else:
        eu_label = "ユーロドル"

    header_line3 = (
        f"{uj_label} 終値 {uj.value:.3f} "
        f"前日比 {uj.diff:+.3f} ({uj.diff_pct:+.2f}%), "
        f"{eu_label} 終値 {eu.value:.5f} "
        f"前日比 {eu.diff:+.5f} ({eu.diff_pct:+.2f}%)"
    )

    header_text = f"{date_str}\n{header_line2}\n{header_line3}"

    # 急な動き・節目越え資産（本文用ヒント）
    special_lines = []
    for key in ["gold", "crude", "btc", "eur_jpy", "gbp_jpy", "aud_jpy"]:
        a = opt[key]
        if not (a.big_move or a.crossed_level):
            continue
        line = (
            f"{a.name}: 終値 {a.value:.2f}, 前日比 {a.diff:+.2f} "
            f"({a.diff_pct:+.2f}%)"
        )
        if a.crossed_level:
            line += f"（{a.crossed_level}）"
        special_lines.append(line)

    special_text = "\n".join(special_lines) if special_lines else "なし"

    prompt = f"""
あなたは日本市場の「引け後短観」を書くアナリストです。
以下に、本日の終値ベースのデータを与えます。

【終値ベースのコア指標】
- 日経平均 終値: {nk.value:.2f}, 前日比: {nk.diff:+.2f} ({nk.diff_pct:+.2f}%)
- ドル円 終値: {uj.value:.3f}, 前日比: {uj.diff:+.3f} ({uj.diff_pct:+.2f}%)
- ユーロドル 終値: {eu.value:.5f}, 前日比: {eu.diff:+.5f} ({eu.diff_pct:+.2f}%)

【急な動きや節目越えの資産】（列挙されているものがあれば、必ずひと言以上触れること）
{special_text}

重要ルール:
- 出力の先頭3行はすでにこちらで用意したヘッダー（日付と終値・前日比）として扱います。
  あなたはヘッダーを書かず、その下に続く本文だけを書いてください。
- 本文の中で、具体的な価格やパーセンテージを書いてはいけません。
  価格や％の情報はヘッダーに任せ、本文では「大幅高」「小反落」「重い」など
  言葉で方向感と雰囲気だけを説明してください。
- 本文中で絵文字を使う場合は、上昇には📈、下落には📉だけを使ってもかまいません。
  それ以外の絵文字は使わないでください。
- 本文は日本語で、やや砕けた口調で1日の相場を140文字以内にまとめてください。
- 個別銘柄名は出さないでください。
- ハッシュタグは0〜2個まで。仮想通貨関連のハッシュタグ（#BTC, #bitcoin, #仮想通貨など）は禁止です。

出力フォーマット:
- ヘッダーはすでに存在するとみなし、あなたは「4行目以降に続く本文」だけを出力してください。
- 説明文や前置きは不要で、Xにそのまま投稿される本文だけを出してください。
"""

    body = generate_with_claude(prompt)
    full_text = f"{header_text}\n{body.strip()}"
    post_to_x(full_text)


if __name__ == "__main__":
    main()

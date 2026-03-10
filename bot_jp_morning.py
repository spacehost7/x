from market_data import get_market_snapshot
from llm_and_x import generate_with_claude, post_to_x, now_jst


def _format_jp_datetime_for_morning(now) -> str:
    # 例: 3月10日(火)11:30現在
    youbi = "月火水木金土日"[now.weekday()]
    # 前場引けは 11:30 固定で出す（実際の取得時刻とは切り離す）
    return f"{now.month}月{now.day}日({youbi})11:30現在"


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
    header_date = _format_jp_datetime_for_morning(now)

    snapshot = get_market_snapshot()
    nk = snapshot["core"]["nk225"]
    uj = snapshot["core"]["usd_jpy"]
    eu = snapshot["core"]["eur_usd"]
    opt = snapshot["optional"]

    # 2行目ヘッダー: 指数・為替（条件付き📈📉）
    nk_arrow = _arrow_for_nk(nk.diff_pct)
    uj_arrow = _arrow_for_usdjpy(uj.diff)
    eu_arrow = _arrow_for_eurusd(eu.diff)

    # 日経
    if nk_arrow:
        nk_part = f"{nk_arrow}日経 {nk.value:.2f}"
    else:
        nk_part = f"日経 {nk.value:.2f}"

    # ドル円
    if uj_arrow:
        uj_part = f"{uj_arrow}ドル円 {uj.value:.3f}"
    else:
        uj_part = f"ドル円 {uj.value:.3f}"

    # ユーロドル
    if eu_arrow:
        eu_part = f"{eu_arrow}ユーロドル {eu.value:.5f}"
    else:
        eu_part = f"ユーロドル {eu.value:.5f}"

    header_line2 = f"{nk_part}, {uj_part}, {eu_part}"

    header_text = f"{header_date}\n{header_line2}"

    # 急騰・急落／節目越え資産（本文用ヒント）
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
あなたは日本市場の「前場の短観」を書くアナリストです。
以下に、日足終値ベースのデータと、前場時点のざっくりした状況を与えます。

【日経平均・為替の終値ベースデータ】
- 日経平均 終値: {nk.value:.2f}, 前日比: {nk.diff:+.2f} ({nk.diff_pct:+.2f}%)
- ドル円 終値: {uj.value:.3f}, 前日比: {uj.diff:+.3f} ({uj.diff_pct:+.2f}%)
- ユーロドル 終値: {eu.value:.5f}, 前日比: {eu.diff:+.5f} ({eu.diff_pct:+.2f}%)

【急な動きや節目に関係する資産】（列挙されているものがあれば、必ずひと言以上触れること）
{special_text}

重要ルール:
- 出力の1〜2行目は、すでにこちらで用意したヘッダー（日時と指数・為替の数値）として扱います。
  あなたはヘッダーを書かず、その下に続く本文だけを書いてください。
- 本文の中では、具体的な価格やパーセンテージを書いてはいけません。
  「大幅高」「小幅安」「落ち着いた動き」など、言葉で雰囲気を説明してください。
- 本文中で絵文字を使う場合は、上昇には📈、下落には📉だけを使ってもかまいません。
  それ以外の絵文字は使わないでください。
- 本文は日本語で、やや砕けた口調で前場の雰囲気を140文字以内にまとめてください。
- 個別銘柄名は書かないでください。
- ハッシュタグは0〜2個まで。仮想通貨関連のハッシュタグ（#BTC, #bitcoin, #仮想通貨など）は禁止です。

出力フォーマット:
- ヘッダーはすでに存在するとみなし、あなたは「3行目以降に続く本文」だけを出力してください。
- 説明文や前置きは不要で、Xにそのまま投稿される本文だけを出してください。
"""

    body = generate_with_claude(prompt)
    full_text = f"{header_text}\n{body.strip()}"
    post_to_x(full_text)


if __name__ == "__main__":
    main()

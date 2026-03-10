# bot_us_close.py

from datetime import datetime
from typing import List

from market_data import get_market_snapshot, AssetMove
from llm_and_x import generate_with_claude, post_to_x, now_jst


def format_pct(value: float) -> str:
    return f"{value:.2f}%"


def format_abs_change(value: float) -> str:
    sign = "+" if value >= 0 else "-"
    return f"{sign}{abs(value):.2f}"


def build_header_lines() -> List[str]:
    snapshot = get_market_snapshot()
    us = snapshot["us"]
    optional = snapshot["optional"]
    core = snapshot["core"]

    djia: AssetMove = us["djia"]
    nasdaq: AssetMove = us["nasdaq"]
    sp500: AssetMove = us["sp500"]

    usd_jpy: AssetMove = core["usd_jpy"]
    eur_usd: AssetMove = core["eur_usd"]

    jst_now = now_jst()
    # 1行目: 日付＋曜日（日本版と同じ形式）
    weekday_map = ["月", "火", "水", "木", "金", "土", "日"]
    w = weekday_map[jst_now.weekday()]
    line1 = f"{jst_now.month}月{jst_now.day}日({w})"

    # 2行目: ダウ平均 終値＋前日比（絶対値＋％）、±2%以上でアイコン
    icon_djia = ""
    if abs(djia.change_pct) >= 2.0:
        icon_djia = "📈" if djia.change_pct > 0 else "📉"

    line2 = (
        f"{icon_djia}ダウ平均 終値 {djia.current:.2f} "
        f"({format_abs_change(djia.change_abs)}, {format_pct(djia.change_pct)})"
    )

    # 3行目: ナスダック・S&P500 終値＋前日比、各々 ±2%以上でアイコン
    icon_nasdaq = ""
    if abs(nasdaq.change_pct) >= 2.0:
        icon_nasdaq = "📈" if nasdaq.change_pct > 0 else "📉"

    icon_sp500 = ""
    if abs(sp500.change_pct) >= 2.0:
        icon_sp500 = "📈" if sp500.change_pct > 0 else "📉"

    line3 = (
        f"{icon_nasdaq}ナスダック {nasdaq.current:.2f} "
        f"({format_abs_change(nasdaq.change_abs)}, {format_pct(nasdaq.change_pct)}) / "
        f"{icon_sp500}S&P500 {sp500.current:.2f} "
        f"({format_abs_change(sp500.change_abs)}, {format_pct(sp500.change_pct)})"
    )

    # 4行目: 為替（ドル円・ユーロドル）、日本版クローズと同じルールを流用
    icon_usd_jpy = ""
    if abs(usd_jpy.change_abs) >= 0.50:
        icon_usd_jpy = "📈" if usd_jpy.change_abs > 0 else "📉"

    icon_eur_usd = ""
    if abs(eur_usd.change_abs) >= 0.05:
        icon_eur_usd = "📈" if eur_usd.change_abs > 0 else "📉"

    line4 = (
        f"{icon_usd_jpy}ドル円 {usd_jpy.current:.3f} "
        f"({format_abs_change(usd_jpy.change_abs)}) / "
        f"{icon_eur_usd}ユーロドル {eur_usd.current:.5f} "
        f"({format_abs_change(eur_usd.change_abs)})"
    )

    return [line1, line2, line3, line4], snapshot


def build_special_text(snapshot) -> str:
    optional = snapshot["optional"]

    watch_keys = ["gold", "crude", "btc", "eur_jpy", "gbp_jpy", "aud_jpy"]
    lines: List[str] = []

    for key in watch_keys:
        asset: AssetMove = optional[key]
        if asset.big_move or asset.crossed_level:
            status = "大きな動き" if asset.big_move else "節目を通過"
            extra = ""
            if asset.crossed_levels:
                levels_str = ", ".join(str(lv) for lv in asset.crossed_levels)
                extra = f"（{levels_str} 付近）"
            lines.append(f"- {asset.name}: {status}{extra}")

    if not lines:
        return "特筆すべき急騰急落や節目越えはありません。"

    return "\n".join(lines)


def build_llm_prompt(header_lines, snapshot) -> str:
    us = snapshot["us"]
    core = snapshot["core"]

    djia: AssetMove = us["djia"]
    nasdaq: AssetMove = us["nasdaq"]
    sp500: AssetMove = us["sp500"]
    usd_jpy: AssetMove = core["usd_jpy"]
    eur_usd: AssetMove = core["eur_usd"]

    special_text = build_special_text(snapshot)

    header_preview = "\n".join(header_lines)

    prompt = f"""
あなたは日本の個人投資家向けに、市場の一言コメントを書くアナリストです。

すでにヘッダー3〜4行は生成済みです。ヘッダーは次のとおりです：

{header_preview}

このヘッダーを前提にして、US株式市場の引け後短観の「本文」だけを日本語で書いてください。

【USコア指標】
- ダウ平均
- ナスダック総合
- S&P500
- ドル円
- ユーロドル

【急な動きや節目越えの資産】
{special_text}

執筆ルール：
- ヘッダー部分はすでにあるので、本文では繰り返しません。
- 本文では具体的な価格や％などの数字は書かないでください。
- ダウ平均・ナスダック・S&P500・主要通貨の方向感や一日の流れを、短く分かりやすくまとめてください。
- 急騰急落・節目越えとして列挙された資産には必ずひと言以上触れてください。
- 絵文字は 📈 / 📉 のみ使用可能ですが、なくても構いません。
- 日本時間の投資家が朝にざっと読んで、相場の雰囲気をつかめるようなトーンで書いてください。

本文のみを出力してください。
"""
    return prompt.strip()


def main() -> None:
    header_lines, snapshot = build_header_lines()
    prompt = build_llm_prompt(header_lines, snapshot)
    body = generate_with_claude(prompt)
    text = "\n".join(header_lines) + "\n" + body.strip()
    post_to_x(text)


if __name__ == "__main__":
    main()

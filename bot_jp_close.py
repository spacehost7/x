from datetime import datetime

def build_safe_close_text(summary: str) -> str:
    date_str = datetime.now().strftime("%Y-%m-%d")
    base = f"日本株 後場まとめ（{date_str}）\n"
    # summary は 50〜80文字くらいに事前に切り詰める
    body = summary[:80]
    return base + body

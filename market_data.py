import datetime
from dataclasses import dataclass
from typing import Optional, Dict

import yfinance as yf


@dataclass
class Asset:
    name: str
    value: float
    diff: float
    diff_pct: float
    big_move: bool
    crossed_level: Optional[str] = None


def _safe_latest_close(series) -> float:
    """
    yfinance の戻りが Series / DataFrame / MultiIndex でも、
    最後の終値を float で安全に取るユーティリティ。
    """
    # DataFrame の場合（複数列）
    if hasattr(series, "columns"):
        # 最後の列を取り、さらに最後の行を取る
        s = series.iloc[:, -1]
        return float(s.dropna().iloc[-1])

    # 普通の Series の場合
    s = series.dropna()
    return float(s.iloc[-1])


def _safe_prev_close(series) -> float:
    """
    1本前の終値を安全に取る。
    """
    if hasattr(series, "columns"):
        s = series.iloc[:, -1]
    else:
        s = series
    s = s.dropna()
    if len(s) < 2:
        # データが足りないときは最新値を返す（差分0扱い）
        return float(s.iloc[-1])
    return float(s.iloc[-2])


def _build_asset(
    name: str,
    ticker: str,
    big_move_threshold_pct: float = 0.0,
    level_thresholds: Optional[Dict[str, float]] = None,
) -> Asset:
    """
    1銘柄分の Asset を組み立てる。
    JP/US どちらから呼ばれても動くように yfinance の戻りを防御的に処理。
    """
    data = yf.download(ticker, period="5d")

    close_series = data["Close"]

    current = _safe_latest_close(close_series)
    prev = _safe_prev_close(close_series)

    diff = current - prev
    diff_pct = (diff / prev) * 100 if prev != 0 else 0.0

    big_move = abs(diff_pct) >= big_move_threshold_pct if big_move_threshold_pct > 0 else False

    crossed_level = None
    if level_thresholds:
        for label, level in level_thresholds.items():
            # シンプルに「境界をまたいだか」で判定
            if (prev < level <= current) or (prev > level >= current):
                crossed_level = label
                break

    return Asset(
        name=name,
        value=current,
        diff=diff,
        diff_pct=diff_pct,
        big_move=big_move,
        crossed_level=crossed_level,
    )


def _now_jst() -> datetime.datetime:
    jst = datetime.timezone(datetime.timedelta(hours=9))
    return datetime.datetime.now(datetime.timezone.utc).astimezone(jst)


def get_market_snapshot():
    """
    日本・米国・為替・コモディティなどのスナップショットをまとめて返す。
    JP/US 両方の bot からこの構造を前提に使う。
    """
    now = _now_jst()

    # コア指標（JP bot も US bot も共通で使う）
    nk225 = _build_asset("日経平均", "^N225", big_move_threshold_pct=2.0)
    usd_jpy = _build_asset("ドル円", "JPY=X", big_move_threshold_pct=0.5)
    eur_usd = _build_asset("ユーロドル", "EURUSD=X", big_move_threshold_pct=0.05)

    # 追加指標（ゴールド、原油、BTC、クロス円など）
    gold = _build_asset(
        "金先物",
        "GC=F",
        big_move_threshold_pct=2.0,
    )
    crude = _build_asset(
        "原油先物",
        "CL=F",
        big_move_threshold_pct=3.0,
    )
    btc = _build_asset(
        "ビットコイン",
        "BTC-USD",
        big_move_threshold_pct=5.0,
        level_thresholds={
            "50000ドル台乗せ": 50000,
            "60000ドル台乗せ": 60000,
        },
    )
    eur_jpy = _build_asset(
        "ユーロ円",
        "EURJPY=X",
        big_move_threshold_pct=1.0,
    )
    gbp_jpy = _build_asset(
        "ポンド円",
        "GBPJPY=X",
        big_move_threshold_pct=1.0,
    )
    aud_jpy = _build_asset(
        "豪ドル円",
        "AUDJPY=X",
        big_move_threshold_pct=1.0,
    )

    snapshot = {
        "timestamp": now.isoformat(),
        "core": {
            "nk225": nk225,
            "usd_jpy": usd_jpy,
            "eur_usd": eur_usd,
        },
        "optional": {
            "gold": gold,
            "crude": crude,
            "btc": btc,
            "eur_jpy": eur_jpy,
            "gbp_jpy": gbp_jpy,
            "aud_jpy": aud_jpy,
        },
    }

    return snapshot

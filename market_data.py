from dataclasses import dataclass
from typing import Optional, Dict, List
import datetime
import yfinance as yf

@dataclass
class AssetMove:
    name: str
    symbol: str
    value: float
    prev_value: float
    diff: float
    diff_pct: float
    big_move: bool = False
    crossed_level: Optional[str] = None
    direction: Optional[str] = None  # "up" / "down" / None

def _now_jst() -> datetime.datetime:
    jst = datetime.timezone(datetime.timedelta(hours=9))
    return datetime.datetime.now(datetime.timezone.utc).astimezone(jst)

def _latest_trading_day_jst() -> datetime.date:
    now = _now_jst()
    return now.date()

def _fetch_series(symbol: str, days: int = 5):
    d = _latest_trading_day_jst()
    start = d - datetime.timedelta(days=days)
    end = d + datetime.timedelta(days=1)
    hist = yf.Ticker(symbol).history(start=start, end=end)
    if hist.empty or len(hist) < 2:
        raise RuntimeError(f"No enough data for {symbol}")
    last = hist.iloc[-1]
    prev = hist.iloc[-2]
    return float(last["Close"]), float(prev["Close"])

def _build_asset(
    name: str,
    symbol: str,
    big_move_threshold_pct: Optional[float] = None,
    levels: Optional[List[float]] = None,
) -> AssetMove:
    value, prev_value = _fetch_series(symbol)
    diff = value - prev_value
    diff_pct = diff / prev_value * 100 if prev_value != 0 else 0.0
    direction = "up" if diff > 0 else "down" if diff < 0 else None

    big_move = False
    if big_move_threshold_pct is not None and abs(diff_pct) >= big_move_threshold_pct:
        big_move = True

    crossed_txt = None
    if levels:
        for lv in levels:
            if prev_value < lv <= value:
                crossed_txt = f"{lv}を上抜け"
            elif value <= lv < prev_value:
                crossed_txt = f"{lv}を割り込む"
            if crossed_txt:
                break

    return AssetMove(
        name=name,
        symbol=symbol,
        value=value,
        prev_value=prev_value,
        diff=diff,
        diff_pct=diff_pct,
        big_move=big_move,
        crossed_level=crossed_txt,
        direction=direction,
    )

def get_market_snapshot() -> Dict[str, Dict[str, AssetMove]]:
    # 日本株
    nk225 = _build_asset("日経平均", "^N225")

    # 為替コア
    usd_jpy = _build_asset("ドル円", "JPY=X")
    eur_usd = _build_asset("ユーロドル", "EURUSD=X")

    # コモディティ・仮想通貨・その他
    gold = _build_asset("金先物", "GC=F", big_move_threshold_pct=2.0,
                        levels=[2000, 2100, 2200])
    crude = _build_asset("原油先物", "CL=F", big_move_threshold_pct=3.0)
    btc = _build_asset("ビットコイン", "BTC-USD", big_move_threshold_pct=5.0,
                       levels=[60000, 65000, 70000])

    eur_jpy = _build_asset("ユーロ円", "EURJPY=X", big_move_threshold_pct=2.0)
    gbp_jpy = _build_asset("ポンド円", "GBPJPY=X", big_move_threshold_pct=2.0)
    aud_jpy = _build_asset("豪ドル円", "AUDJPY=X", big_move_threshold_pct=2.0)

    return {
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

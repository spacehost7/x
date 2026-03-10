# market_data.py

from dataclasses import dataclass
from typing import Dict, Optional
import datetime as dt
import yfinance as yf

# ここは既存と同じ仮定
@dataclass
class AssetMove:
    name: str
    symbol: str
    current: float
    prev_close: float
    change_abs: float
    change_pct: float
    big_move: bool
    crossed_level: bool
    crossed_levels: Optional[list] = None

def _build_asset(
    name: str,
    symbol: str,
    big_move_threshold_pct: Optional[float] = None,
    levels: Optional[list[float]] = None,
) -> AssetMove:
    # 既存実装を想定（終値2本から前日比など算出）
    end = dt.datetime.utcnow()
    start = end - dt.timedelta(days=5)
    data = yf.download(symbol, start=start, end=end, progress=False)
    if data.empty or len(data["Close"]) < 2:
        raise RuntimeError(f"not enough data for {symbol}")

    current = float(data["Close"].iloc[-1])
    prev_close = float(data["Close"].iloc[-2])
    change_abs = current - prev_close
    change_pct = (change_abs / prev_close) * 100

    big_move = False
    if big_move_threshold_pct is not None:
        big_move = abs(change_pct) >= big_move_threshold_pct

    crossed_level = False
    crossed_levels: list[float] = []
    if levels:
        for lv in levels:
            # 前日終値と当日終値でまたいだかどうか
            if (prev_close < lv <= current) or (prev_close > lv >= current):
                crossed_level = True
                crossed_levels.append(lv)

    return AssetMove(
        name=name,
        symbol=symbol,
        current=current,
        prev_close=prev_close,
        change_abs=change_abs,
        change_pct=change_pct,
        big_move=big_move,
        crossed_level=crossed_level,
        crossed_levels=crossed_levels,
    )

def get_market_snapshot() -> Dict[str, Dict[str, AssetMove]]:
    # 既存: 日本コア
    nk225 = _build_asset("日経平均", "^N225", big_move_threshold_pct=2.0)
    usd_jpy = _build_asset("ドル円", "JPY=X")  # 閾値は利用側で判定
    eur_usd = _build_asset("ユーロドル", "EURUSD=X")

    # 既存: オプショナル
    gold = _build_asset(
        "金先物",
        "GC=F",
        big_move_threshold_pct=2.0,
        levels=[2000, 2100, 2200],
    )
    crude = _build_asset("原油先物", "CL=F", big_move_threshold_pct=3.0)
    btc = _build_asset(
        "ビットコイン",
        "BTC-USD",
        big_move_threshold_pct=5.0,
        levels=[60000, 65000, 70000],
    )
    eur_jpy = _build_asset("ユーロ円", "EURJPY=X", big_move_threshold_pct=2.0)
    gbp_jpy = _build_asset("ポンド円", "GBPJPY=X", big_move_threshold_pct=2.0)
    aud_jpy = _build_asset("豪ドル円", "AUDJPY=X", big_move_threshold_pct=2.0)

    # ★追加: US 株指数
    djia = _build_asset("ダウ平均", "^DJI", big_move_threshold_pct=2.0)
    nasdaq = _build_asset("ナスダック総合", "^IXIC", big_move_threshold_pct=2.0)
    sp500 = _build_asset("S&P500", "^GSPC", big_move_threshold_pct=2.0)

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
        # ★追加: US セクション
        "us": {
            "djia": djia,
            "nasdaq": nasdaq,
            "sp500": sp500,
        },
    }

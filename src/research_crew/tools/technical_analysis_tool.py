import yfinance as yf
import pandas as pd
import numpy as np
from crewai.tools import tool
from ta.trend import SMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from scipy.signal import find_peaks

def _identify_chart_patterns(close: np.ndarray):
    patterns = []
    # head & shoulders (very naive)
    peaks, _ = find_peaks(close, distance=20)
    if len(peaks) >= 3:
        ls, hd, rs = peaks[-3], peaks[-2], peaks[-1]
        if close[hd] > close[ls] and close[hd] > close[rs]:
            patterns.append("Head and Shoulders")
    # double top
    if len(peaks) >= 2:
        a, b = close[peaks[-2]], close[peaks[-1]]
        if abs(b - a) / a < 0.03:
            patterns.append("Double Top")
    # double bottom
    troughs, _ = find_peaks(-close, distance=20)
    if len(troughs) >= 2:
        a, b = close[troughs[-2]], close[troughs[-1]]
        if abs(b - a) / a < 0.03:
            patterns.append("Double Bottom")
    return patterns

@tool
def technical_analysis(ticker: str, period: str = "1y"):
    """
    Perform technical assessment for a given stock.
    
    Args:
        ticker (str): The stock ticker symbol.
        period (str): Time period for analysis. (default: "1y")
    
    Returns:
        dict: Technical assessment results.
    """
    stock = yf.Ticker(ticker)
    df = stock.history(period=period, interval="1d", auto_adjust=True)

    if df.empty or len(df) < 210:  # need enough for SMA200
        raise ValueError(f"Not enough data for {ticker} over period '{period}'")

    # Indicators (only ones we need)
    close = df["Close"]
    high, low = df["High"], df["Low"]
    sma50 = SMAIndicator(close, window=50).sma_indicator()
    sma200 = SMAIndicator(close, window=200).sma_indicator()
    rsi = RSIIndicator(close, window=14).rsi()
    macd_diff = MACD(close).macd_diff()
    bb = BollingerBands(close)
    bb_hi_ind = bb.bollinger_hband_indicator()   # 1 if close > upper band
    bb_lo_ind = bb.bollinger_lband_indicator()   # 1 if close < lower band
    atr = AverageTrueRange(high, low, close, window=14).average_true_range()

    # Custom extras
    volatility = close.pct_change().rolling(20).std() * np.sqrt(252)
    momentum = close - close.shift(20)

    calc = pd.DataFrame({
        "Close": close,
        "sma_50": sma50,
        "sma_200": sma200,
        "rsi": rsi,
        "macd": macd_diff,
        "bollinger_hband": bb_hi_ind,
        "bollinger_lband": bb_lo_ind,
        "atr": atr,
        "volatility": volatility,
        "momentum": momentum,
        "High": high,
        "Low": low
    }).dropna(subset=["sma_50","sma_200","rsi","macd","bollinger_hband","bollinger_lband","atr","volatility","momentum"])

    if calc.empty:
        raise ValueError("Indicators could not be computed (try a longer period, e.g. '2y' or '5y').")

    # Support / resistance from cleaned series
    close_clean = calc["Close"].values
    peaks, _ = find_peaks(close_clean, distance=20)
    troughs, _ = find_peaks(-close_clean, distance=20)
    support_levels = close_clean[troughs][-3:].tolist() if len(troughs) else []
    resistance_levels = close_clean[peaks][-3:].tolist() if len(peaks) else []

    patterns = _identify_chart_patterns(close_clean)

    last = calc.iloc[-1]
    return {
        "ticker": ticker,
        "current_price": float(last["Close"]),
        "sma_50": float(last["sma_50"]),
        "sma_200": float(last["sma_200"]),
        "rsi": float(last["rsi"]),
        "macd": float(last["macd"]),
        "bollinger_hband": int(last["bollinger_hband"]),
        "bollinger_lband": int(last["bollinger_lband"]),
        "atr": float(last["atr"]),
        "volatility": float(last["volatility"]),
        "momentum": float(last["momentum"]),
        "support_levels": support_levels,
        "resistance_levels": resistance_levels,
        "identified_patterns": patterns
    }

if __name__ == "__main__":
    out = technical_analysis.func("AAPL")
    for k, v in out.items():
        print(k, "=>", v)

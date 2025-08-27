import pandas as pd


def wealth_path(rets: pd.Series, start: float = 10000.0) -> pd.Series:
    return start * (1 + rets.fillna(0)).cumprod()


def max_drawdown(wealth: pd.Series) -> float:
    peak = wealth.cummax()
    dd = (wealth - peak) / peak
    return float(dd.min())


def cagr(wealth: pd.Series) -> float:
    n = len(wealth)
    start, end = float(wealth.iloc[0]), float(wealth.iloc[-1])
    return (end / start) ** (1 / n) - 1


def ann_vol(rets: pd.Series) -> float:
    return float(rets.std())

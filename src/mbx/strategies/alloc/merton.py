import pandas as pd

def ecy_from_cape(cape: pd.Series) -> pd.Series:
    return 1.0 / cape.astype(float)

def mu_ex_from_ecy(ecy: pd.Series, mu0: float) -> pd.Series:
    med = ecy.median()
    return mu0 * (ecy / med)

def rolling_vol(ret: pd.Series, window: int, floor: float) -> pd.Series:
    v = ret.rolling(window).std()
    return v.fillna(v.mean()).clip(lower=floor)

def merton_weight(mu_ex, sigma, gamma: float, clamp=(0.0,1.0)):
    w = mu_ex / (gamma * (sigma**2))
    return w.clip(lower=clamp[0], upper=clamp[1])

def compute_weights_annual(spx: pd.DataFrame, cape: pd.DataFrame, rf: pd.DataFrame, params: dict) -> pd.DataFrame:
    df = spx.merge(cape, on='year', how='left').merge(rf, on='year', how='left')
    volw = int(params.get('vol_window_years', 5))
    floor = float(params.get('vol_floor', 0.10))
    gamma = float(params.get('gamma', 2.0))
    mu0 = float(params.get('mu0', 0.05))
    clamp = tuple(params.get('clamp', (0.0,1.0)))
    use_rf = bool(params.get('use_rf_as_cash', True))

    ecy = ecy_from_cape(df['cape'])
    mu_ex = mu_ex_from_ecy(ecy, mu0)
    sigma = rolling_vol(df['ret'], volw, floor)
    w = merton_weight(mu_ex, sigma, gamma, clamp=clamp)

    cash_r = df['rf'] if use_rf and 'rf' in df else 0.0
    port_r = w * df['ret'] + (1 - w) * cash_r

    out = pd.DataFrame({
        'year': df['year'],
        'spx_ret': df['ret'],
        'rf': cash_r,
        'cape': df['cape'],
        'ecy': ecy,
        'mu_ex': mu_ex,
        'sigma': sigma,
        'w_equity': w,
        'port_ret': port_r
    })
    return out

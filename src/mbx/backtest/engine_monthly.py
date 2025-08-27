import io, fsspec, pandas as pd, yaml
from mbx.utils.logging import get_logger
from mbx.storage.fs import resolve_path
from mbx.data.loaders.ff_monthly import load_ff_factors_monthly
from mbx.data.loaders.shiller_cape_monthly import load_cape_monthly
from mbx.strategies.alloc.merton import rolling_vol, ecy_from_cape, mu_ex_from_ecy, merton_weight
from mbx.backtest.metrics import wealth_path, max_drawdown, cagr, ann_vol

log = get_logger(__name__)

def run_backtest_monthly(cfg: dict):
    dcfg, params, outcfg = cfg['data'], cfg['params'], cfg['outputs']
    ff = load_ff_factors_monthly(dcfg['ff_factors_monthly'])
    cape = load_cape_monthly(dcfg['cape_monthly'])

    df = pd.merge_asof(ff.sort_values('Date'), cape.sort_values('Date'),
                       on='Date', direction='backward')

    df['mkt_ret'] = df['Mkt-RF'] + df['RF']

    volw = int(params.get('vol_window_months', 60))
    floor = float(params.get('vol_floor', 0.10))
    gamma = float(params.get('gamma', 2.0))
    mu0 = float(params.get('mu0', 0.05))
    clamp = tuple(params.get('clamp', (0.0, 1.0)))
    use_rf = bool(params.get('use_rf_as_cash', True))
    dca_amt = float(params.get('dca_monthly', 0.0))

    sigma_m = df['mkt_ret'].rolling(volw).std()
    sigma = (sigma_m * (12 ** 0.5)).fillna(sigma_m.mean()).clip(lower=floor)

    ecy = ecy_from_cape(df['CAPE'])
    mu_ex = mu_ex_from_ecy(ecy, mu0)
    w = merton_weight(mu_ex, sigma, gamma, clamp=clamp)

    cash_r = df['RF'] if use_rf else 0.0
    strat_ret = w * df['mkt_ret'] + (1 - w) * cash_r

    panel = pd.DataFrame({
        'Date': df['Date'],
        'mkt_ret': df['mkt_ret'],
        'rf': df['RF'],
        'CAPE': df['CAPE'],
        'ecy': ecy,
        'mu_ex': mu_ex,
        'sigma_ann': sigma,
        'w_equity': w,
        'port_ret': strat_ret
    }).dropna()

    panel['wealth_strategy'] = wealth_path(panel['port_ret'], start=10000.0)
    panel['wealth_mkt'] = wealth_path(panel['mkt_ret'], start=10000.0)

    if dca_amt > 0:
        wealth = 0.0; ws = []
        for r in panel['port_ret']:
            wealth = (wealth + dca_amt) * (1 + r); ws.append(wealth)
        panel['wealth_strategy_dca'] = ws

        wealth = 0.0; wm = []
        for r in panel['mkt_ret']:
            wealth = (wealth + dca_amt) * (1 + r); wm.append(wealth)
        panel['wealth_mkt_dca'] = wm

    summary = pd.DataFrame({
        'metric': ['CAGR','AnnVol','MaxDD','TerminalWealth'],
        'buy_hold_mkt': [
            cagr(panel['wealth_mkt']),
            ann_vol(panel['mkt_ret'] * (12**0.5)),
            max_drawdown(panel['wealth_mkt']),
            float(panel['wealth_mkt'].iloc[-1])
        ],
        'strategy': [
            cagr(panel['wealth_strategy']),
            ann_vol(panel['port_ret'] * (12**0.5)),
            max_drawdown(panel['wealth_strategy']),
            float(panel['wealth_strategy'].iloc[-1])
        ]
    })

    outdir = resolve_path(outcfg['dir'])
    fs, _, _ = fsspec.get_fs_token_paths(outdir)
    fs.makedirs(outdir, exist_ok=True)
    with fs.open(f"{outdir}/panel_monthly.csv","wb") as f:
        panel.to_csv(io.TextIOWrapper(f, encoding='utf-8'), index=False)
    with fs.open(f"{outdir}/summary_monthly.csv","wb") as f:
        summary.to_csv(io.TextIOWrapper(f, encoding='utf-8'), index=False)
    return outdir

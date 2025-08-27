import io

import fsspec
import pandas as pd
import yaml

from mbx.backtest.metrics import ann_vol, cagr, max_drawdown, wealth_path
from mbx.data.loaders.ken_french_rf import load_rf_annual
from mbx.data.loaders.shiller_cape import load_cape_annual
from mbx.data.loaders.spx_tr import load_spx_annual
from mbx.storage.fs import resolve_path
from mbx.strategies.alloc.merton import compute_weights_annual
from mbx.utils.logging import get_logger

log = get_logger(__name__)


def run_backtest(config_path: str):
    with open(config_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    dcfg, params, outcfg = cfg["data"], cfg["params"], cfg["outputs"]

    cape = load_cape_annual(dcfg["cape"])
    rf = load_rf_annual(dcfg["rf"])
    spx = load_spx_annual(dcfg["spx"])

    panel = compute_weights_annual(spx, cape, rf, params)
    panel["wealth_strategy"] = wealth_path(panel["port_ret"])
    panel["wealth_bh"] = wealth_path(panel["spx_ret"])

    summary = pd.DataFrame(
        {
            "metric": ["CAGR", "AnnVol", "MaxDD", "TerminalWealth"],
            "buy_hold": [
                cagr(panel["wealth_bh"]),
                ann_vol(panel["spx_ret"]),
                max_drawdown(panel["wealth_bh"]),
                float(panel["wealth_bh"].iloc[-1]),
            ],
            "strategy": [
                cagr(panel["wealth_strategy"]),
                ann_vol(panel["port_ret"]),
                max_drawdown(panel["wealth_strategy"]),
                float(panel["wealth_strategy"].iloc[-1]),
            ],
        }
    )

    outdir = resolve_path(outcfg["dir"])
    fs, _, _ = fsspec.get_fs_token_paths(outdir)
    fs.makedirs(outdir, exist_ok=True)
    with fs.open(f"{outdir}/panel.csv", "wb") as f:
        panel.to_csv(io.TextIOWrapper(f, encoding="utf-8"), index=False)
    with fs.open(f"{outdir}/summary.csv", "wb") as f:
        summary.to_csv(io.TextIOWrapper(f, encoding="utf-8"), index=False)
    log.info("Backtest complete → %s", outdir)

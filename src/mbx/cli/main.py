import typer
import yaml

from mbx.backtest.engine import run_backtest as run_backtest_annual
from mbx.backtest.engine_monthly import run_backtest_monthly
from mbx.data.fetch_public import fetch_ff_factors_monthly, fetch_shiller_cape_monthly

app = typer.Typer(add_completion=False, help="mbx — backtests and tools")


@app.command("run-backtest")
def run_backtest_cmd(config: str = typer.Argument(..., help="Path to YAML config")):
    with open(config, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    mode = cfg["params"].get("rebalance", "A").upper()
    if mode.startswith("M"):
        outdir = run_backtest_monthly(cfg)
        typer.echo(f"[mbx] Monthly backtest complete → {outdir}")
    else:
        run_backtest_annual(config)
        typer.echo("[mbx] Annual backtest complete.")


@app.command("fetch-public")
def fetch_public_cmd():
    p1 = fetch_shiller_cape_monthly()
    p2 = fetch_ff_factors_monthly()
    typer.echo(f"[mbx] Wrote: {p1}")
    typer.echo(f"[mbx] Wrote: {p2}")


@app.callback()
def main():
    return

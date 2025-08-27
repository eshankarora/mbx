import typer
from mbx.backtest.engine import run_backtest

app = typer.Typer(add_completion=False, help="mbx — backtests and tools")

@app.command("run-backtest")
def run_backtest_cmd(c: str):
    """Run a backtest from a YAML config path."""
    run_backtest(c)

if __name__ == "__main__":
    app()

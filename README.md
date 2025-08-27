<<<<<<< HEAD
# mbx
=======
# mbx — Missing Billionaires eXperimental

Valuation-aware Kelly/Merton allocator, feature-engine foundation, and a minimal backtesting runner.
Cloud-portable via `fsspec` (local folder now; S3/GS later). Code under Apache-2.0.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -e .

# point data to a local folder
export MBX_DATA_URI="file://$(pwd)/_mbxdata"
mkdir -p _mbxdata/datasets
cp -r data/samples/* _mbxdata/datasets/

# run smoke backtest (annual US Kelly/Merton-lite with ECY=1/CAPE)
mbx run-backtest -c config/backtests/us_kelly.yaml
```

Outputs: `_mbxdata/runs/us_kelly/{panel.csv,summary.csv}`

## Cloud note
Set `MBX_DATA_URI=s3://your-bucket/mbx` (requires AWS creds). All IO is via `fsspec`.
>>>>>>> init mbx scaffold

import pandas as pd
from mbx.storage.fs import open_file

def load_cape_monthly(path: str) -> pd.DataFrame:
    with open_file(path, 'rb') as f:
        df = pd.read_csv(f, parse_dates=['Date'])
    return df[['Date','CAPE']].sort_values('Date').reset_index(drop=True)

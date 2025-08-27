import pandas as pd

from mbx.storage.fs import open_file


def load_rf_annual(path: str) -> pd.DataFrame:
    with open_file(path, "rb") as f:
        df = pd.read_csv(f)
    df["year"] = df["year"].astype(int)
    df = df.rename(columns={"rf": "rf"})
    return df[["year", "rf"]]

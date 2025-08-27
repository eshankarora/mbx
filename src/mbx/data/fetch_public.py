import io, zipfile, pandas as pd, requests
from mbx.storage.fs import resolve_path
import fsspec

def fetch_shiller_cape_monthly(to_path: str = "datasets/shiller/cape_monthly.csv"):
    url = "https://www.econ.yale.edu/~shiller/data/ie_data.xls"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    xls = pd.read_excel(io.BytesIO(r.content), sheet_name="Data", skiprows=0)
    if "Date" in xls.columns and "CAPE" in xls.columns:
        df = xls[["Date","CAPE"]].dropna()
    elif "P/E10" in xls.columns:
        df = xls[["Date","P/E10"]].rename(columns={"P/E10":"CAPE"}).dropna()
    else:
        raise RuntimeError("Could not find CAPE column in Shiller file")
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    out = resolve_path(to_path)
    fs, _, _ = fsspec.get_fs_token_paths(out)
    fs.makedirs(out.rsplit("/",1)[0], exist_ok=True)
    with fs.open(out, "wb") as f:
        df.to_csv(io.TextIOWrapper(f, encoding="utf-8"), index=False)
    return out

def fetch_ff_factors_monthly(to_path: str = "datasets/ken_french/ff_factors_monthly.csv"):
    url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_CSV.zip"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    name = [n for n in z.namelist() if n.endswith(".CSV")][0]
    content = z.read(name).decode("utf-8", errors="ignore").splitlines()
    start_idx = next(i for i,l in enumerate(content) if len(l)>=6 and l[:6].isdigit())
    end_idx = next(i for i in range(start_idx, len(content)) if content[i].lower().startswith("annual factors"))
    data_lines = content[start_idx:end_idx]
    import csv
    reader = csv.reader(data_lines)
    rows = list(reader)
    header = rows[0]
    data = rows[1:]
    import pandas as pd
    df = pd.DataFrame(data, columns=header)
    df = df.rename(columns={header[0]: "Date"})
    df = df[df["Date"].str.len()==6]
    df["Date"] = pd.to_datetime(df["Date"], format="%Y%m")
    for col in ["Mkt-RF","RF"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")/100.0
    df = df[["Date","Mkt-RF","RF"]].dropna().sort_values("Date")
    out = resolve_path(to_path)
    fs, _, _ = fsspec.get_fs_token_paths(out)
    fs.makedirs(out.rsplit("/",1)[0], exist_ok=True)
    with fs.open(out, "wb") as f:
        df.to_csv(io.TextIOWrapper(f, encoding="utf-8"), index=False)
    return out

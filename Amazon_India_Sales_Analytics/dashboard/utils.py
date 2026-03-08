import pandas as pd


def month_sort_key(df: pd.DataFrame) -> pd.DataFrame:
    if "month" in df.columns:
        return df.sort_values(["year", "month"])
    return df


def add_month_label(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["month_label"] = pd.to_datetime(dict(year=out["year"], month=out["month"], day=1))
    return out
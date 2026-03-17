"""
Smart data loader — loads local CSVs if available,
otherwise fetches & processes fresh data from the Chicago API.
Used by all Streamlit pages.
"""

import pandas as pd
import numpy as np
import requests
from io import StringIO
import streamlit as st
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings("ignore")

CLUSTERED_CSV = "chicago_crimes_clustered.csv"
CLEAN_CSV     = "chicago_crimes_clean.csv"
API_URL       = "https://data.cityofchicago.org/resource/ijzp-q8t2.csv"
SAMPLE_SIZE   = 100000   # smaller for cloud deployment


def _fetch_from_api(n=SAMPLE_SIZE):
    params = {"$limit": n, "$where": "year>=2022", "$order": "date DESC"}
    r = requests.get(API_URL, params=params, timeout=120)
    return pd.read_csv(StringIO(r.text))


def _clean(df):
    df = df.drop_duplicates(subset=["case_number"])
    df.dropna(subset=["latitude", "longitude"], inplace=True)
    df["location_description"] = df["location_description"].fillna("UNKNOWN")
    df["ward"]           = df["ward"].fillna(df["ward"].median())
    df["community_area"] = df["community_area"].fillna(df["community_area"].median())
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Temporal features
    df["hour"]        = df["date"].dt.hour
    df["day_of_week"] = df["date"].dt.day_name()
    df["day_num"]     = df["date"].dt.dayofweek
    df["month"]       = df["date"].dt.month
    df["month_name"]  = df["date"].dt.month_name()
    df["year"]        = df["date"].dt.year
    df["is_weekend"]  = df["day_num"].isin([5, 6]).astype(int)
    df["season"]      = df["month"].apply(_season)

    # Severity
    df["crime_severity_score"] = df["primary_type"].map(_severity()).fillna(2)

    # Clean strings
    for col in ["primary_type", "description", "location_description", "block"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()

    df.drop(columns=[c for c in ["location", "updated_on"] if c in df.columns], inplace=True)
    return df.reset_index(drop=True)


def _cluster(df):
    le = LabelEncoder()
    df["crime_type_encoded"]    = le.fit_transform(df["primary_type"].astype(str))
    df["location_type_encoded"] = le.fit_transform(df["location_description"].astype(str))
    df["lat_bin"] = pd.cut(df["latitude"],  bins=20, labels=False)
    df["lon_bin"] = pd.cut(df["longitude"], bins=20, labels=False)

    sc  = StandardScaler()
    geo = sc.fit_transform(df[["latitude", "longitude"]])
    df["geo_cluster"] = KMeans(n_clusters=7, random_state=42, n_init=10).fit_predict(geo)

    tmp_feats = ["hour", "day_num", "month", "is_weekend", "crime_severity_score"]
    tmp       = sc.fit_transform(df[tmp_feats].fillna(0))
    df["temporal_cluster"] = KMeans(n_clusters=4, random_state=42, n_init=10).fit_predict(tmp)

    label_map = {0: "Weekend Afternoon", 1: "Weekday Evening",
                 2: "Weekday Afternoon",  3: "Late Night"}
    df["temporal_label"] = df["temporal_cluster"].map(label_map)

    sc2 = StandardScaler()
    df[["lat_norm", "lon_norm"]] = sc2.fit_transform(df[["latitude", "longitude"]])
    return df


def _season(m):
    if m in [12, 1, 2]:  return "Winter"
    elif m in [3, 4, 5]: return "Spring"
    elif m in [6, 7, 8]: return "Summer"
    else:                 return "Fall"


def _severity():
    return {
        "HOMICIDE": 10, "CRIM SEXUAL ASSAULT": 9, "KIDNAPPING": 9,
        "HUMAN TRAFFICKING": 9, "ROBBERY": 8, "ASSAULT": 7, "BATTERY": 7,
        "ARSON": 7, "WEAPONS VIOLATION": 6, "BURGLARY": 6,
        "MOTOR VEHICLE THEFT": 5, "THEFT": 5, "STALKING": 5,
        "CRIMINAL DAMAGE": 4, "SEX OFFENSE": 4, "NARCOTICS": 3,
        "DECEPTIVE PRACTICE": 3, "CRIMINAL TRESPASS": 2,
        "PUBLIC PEACE VIOLATION": 2, "LIQUOR LAW VIOLATION": 2,
        "GAMBLING": 1, "OBSCENITY": 1,
    }


@st.cache_data(show_spinner="Loading crime data...")
def load_data():
    """Load clustered data — from local CSV or fresh from API."""
    try:
        df = pd.read_csv(CLUSTERED_CSV, parse_dates=["date"])
        return df
    except FileNotFoundError:
        pass

    try:
        df = pd.read_csv(CLEAN_CSV, parse_dates=["date"])
        return _cluster(df)
    except FileNotFoundError:
        pass

    # Fetch from Chicago API
    raw = _fetch_from_api()
    df  = _clean(raw)
    df  = _cluster(df)
    return df

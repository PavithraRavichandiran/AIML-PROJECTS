import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Amazon India Executive Dashboard", layout="wide")

DB_PATH = Path(__file__).resolve().parents[1] / "AmazonIndia.db"
DATA_CLEANED_PATH = Path(__file__).resolve().parents[1] / "data" / "cleaned"


def query_df(sql: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    try:
        return pd.read_sql_query(sql, conn)
    finally:
        conn.close()


def read_csv_df(file_name: str) -> pd.DataFrame:
    file_path = DATA_CLEANED_PATH / file_name
    return pd.read_csv(file_path)
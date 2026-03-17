import pandas as pd
import numpy as np

print("=" * 60)
print("PATROLIQ - DATA PREPROCESSING")
print("=" * 60)

# ── 1. Load ──────────────────────────────────────────────────
df = pd.read_csv("chicago_crimes_500k.csv")
print(f"\n[1] Loaded dataset: {df.shape[0]:,} rows x {df.shape[1]} columns")

# ── 2. Drop duplicates ───────────────────────────────────────
before = len(df)
df.drop_duplicates(subset=["case_number"], inplace=True)
print(f"\n[2] Removed {before - len(df):,} duplicate case numbers")
print(f"    Remaining: {len(df):,} rows")

# ── 3. Handle missing values ─────────────────────────────────
print(f"\n[3] Missing values before cleaning:")
print(df.isnull().sum()[df.isnull().sum() > 0])

# Drop rows missing coordinates (critical for geographic analysis)
df.dropna(subset=["latitude", "longitude", "x_coordinate", "y_coordinate"], inplace=True)
print(f"\n    After dropping missing coordinates: {len(df):,} rows")

# Fill missing location_description with 'UNKNOWN'
df["location_description"] = df["location_description"].fillna("UNKNOWN")

# Fill missing ward and community_area with median
df["ward"] = df["ward"].fillna(df["ward"].median())
df["community_area"] = df["community_area"].fillna(df["community_area"].median())

print(f"    Missing values after cleaning:")
print(df.isnull().sum()[df.isnull().sum() > 0])
print("    No missing values remaining." if df.isnull().sum().sum() == 0 else "")

# ── 4. Fix data types ─────────────────────────────────────────
print(f"\n[4] Fixing data types...")

df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["updated_on"] = pd.to_datetime(df["updated_on"], errors="coerce")
df["ward"] = df["ward"].fillna(df["ward"].median()).astype(int)
df["community_area"] = df["community_area"].fillna(df["community_area"].median()).astype(int)
df["district"] = df["district"].astype(int)
df["beat"] = df["beat"].astype(int)

print("    date, updated_on -> datetime")
print("    ward, community_area, district, beat -> int")

# ── 5. Extract temporal features ─────────────────────────────
print(f"\n[5] Extracting temporal features...")

df["hour"]        = df["date"].dt.hour
df["day_of_week"] = df["date"].dt.day_name()
df["day_num"]     = df["date"].dt.dayofweek   # 0=Mon, 6=Sun
df["month"]       = df["date"].dt.month
df["month_name"]  = df["date"].dt.month_name()
df["year"]        = df["date"].dt.year
df["is_weekend"]  = df["day_num"].isin([5, 6]).astype(int)

def get_season(month):
    if month in [12, 1, 2]:  return "Winter"
    elif month in [3, 4, 5]:  return "Spring"
    elif month in [6, 7, 8]:  return "Summer"
    else:                      return "Fall"

df["season"] = df["month"].apply(get_season)

print("    Created: hour, day_of_week, day_num, month, month_name, is_weekend, season")

# ── 6. Crime severity score ───────────────────────────────────
print(f"\n[6] Creating crime severity score...")

severity_map = {
    "HOMICIDE": 10,
    "CRIM SEXUAL ASSAULT": 9,
    "KIDNAPPING": 9,
    "HUMAN TRAFFICKING": 9,
    "ROBBERY": 8,
    "ASSAULT": 7,
    "BATTERY": 7,
    "ARSON": 7,
    "WEAPONS VIOLATION": 6,
    "BURGLARY": 6,
    "MOTOR VEHICLE THEFT": 5,
    "THEFT": 5,
    "STALKING": 5,
    "INTIMIDATION": 4,
    "CRIMINAL DAMAGE": 4,
    "SEX OFFENSE": 4,
    "OFFENSE INVOLVING CHILDREN": 4,
    "NARCOTICS": 3,
    "DECEPTIVE PRACTICE": 3,
    "CRIMINAL TRESPASS": 2,
    "PUBLIC PEACE VIOLATION": 2,
    "LIQUOR LAW VIOLATION": 2,
    "GAMBLING": 1,
    "OBSCENITY": 1,
    "INTERFERENCE WITH PUBLIC OFFICER": 1,
}

df["crime_severity_score"] = df["primary_type"].map(severity_map).fillna(2)
print("    Created: crime_severity_score (1=minor -> 10=critical)")

# ── 7. Validate geographic bounds ────────────────────────────
print(f"\n[7] Validating geographic boundaries (Chicago bounds)...")

chicago_bounds = {
    "lat_min": 41.6, "lat_max": 42.1,
    "lon_min": -87.95, "lon_max": -87.5
}

invalid_geo = (
    (df["latitude"] < chicago_bounds["lat_min"]) |
    (df["latitude"] > chicago_bounds["lat_max"]) |
    (df["longitude"] < chicago_bounds["lon_min"]) |
    (df["longitude"] > chicago_bounds["lon_max"])
)

print(f"    Records outside Chicago bounds: {invalid_geo.sum():,}")
df = df[~invalid_geo]
print(f"    Remaining after geo validation: {len(df):,} rows")

# ── 8. Clean string columns ───────────────────────────────────
print(f"\n[8] Cleaning string columns...")
for col in ["primary_type", "description", "location_description", "block"]:
    df[col] = df[col].str.strip().str.upper()
print("    Stripped whitespace and uppercased: primary_type, description, location_description, block")

# ── 9. Drop unnecessary columns ──────────────────────────────
print(f"\n[9] Dropping unnecessary columns...")
drop_cols = ["location", "updated_on"]
df.drop(columns=drop_cols, inplace=True)
print(f"    Dropped: {drop_cols}")

# ── 10. Summary ───────────────────────────────────────────────
print(f"\n{'=' * 60}")
print("FINAL DATASET SUMMARY")
print(f"{'=' * 60}")
print(f"Shape          : {df.shape[0]:,} rows x {df.shape[1]} columns")
print(f"Date range     : {df['date'].min()} -> {df['date'].max()}")
print(f"Missing values : {df.isnull().sum().sum()}")
print(f"Crime types    : {df['primary_type'].nunique()} unique")
print(f"Districts      : {df['district'].nunique()} unique")
print(f"\nFeature list:")
for col in df.columns:
    print(f"  - {col} ({df[col].dtype})")

# ── 11. Save ──────────────────────────────────────────────────
df.to_csv("chicago_crimes_clean.csv", index=False)
print(f"\n[SAVED] chicago_crimes_clean.csv")
print("Preprocessing complete!")

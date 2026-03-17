import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os

# ── Setup ─────────────────────────────────────────────────────
sns.set_theme(style="darkgrid", palette="muted")
os.makedirs("eda_plots", exist_ok=True)

print("=" * 60)
print("PATROLIQ - EXPLORATORY DATA ANALYSIS")
print("=" * 60)

df = pd.read_csv("chicago_crimes_clean.csv", parse_dates=["date"])
print(f"\nLoaded: {df.shape[0]:,} rows x {df.shape[1]} columns\n")

# ═══════════════════════════════════════════════════════════════
# 1. CRIME TYPE DISTRIBUTION
# ═══════════════════════════════════════════════════════════════
print("[1] Crime Type Distribution")

crime_counts = df["primary_type"].value_counts()
print(crime_counts.to_string())

fig, ax = plt.subplots(figsize=(14, 8))
colors = sns.color_palette("Reds_r", len(crime_counts))
bars = ax.barh(crime_counts.index, crime_counts.values, color=colors)
ax.set_xlabel("Number of Crimes", fontsize=12)
ax.set_title("Crime Type Distribution (Top 31)", fontsize=14, fontweight="bold")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
for bar, val in zip(bars, crime_counts.values):
    ax.text(bar.get_width() + 200, bar.get_y() + bar.get_height()/2,
            f"{val:,}", va="center", fontsize=7)
plt.tight_layout()
plt.savefig("eda_plots/01_crime_type_distribution.png", dpi=150)
plt.close()
print("    Saved: eda_plots/01_crime_type_distribution.png\n")

# ═══════════════════════════════════════════════════════════════
# 2. TEMPORAL ANALYSIS
# ═══════════════════════════════════════════════════════════════
print("[2] Temporal Analysis")

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle("Temporal Crime Patterns", fontsize=16, fontweight="bold")

# Hourly
hourly = df.groupby("hour").size()
axes[0, 0].plot(hourly.index, hourly.values, color="crimson", linewidth=2.5, marker="o", markersize=4)
axes[0, 0].fill_between(hourly.index, hourly.values, alpha=0.2, color="crimson")
axes[0, 0].set_title("Crimes by Hour of Day")
axes[0, 0].set_xlabel("Hour (0-23)")
axes[0, 0].set_ylabel("Crime Count")
axes[0, 0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
peak_hour = hourly.idxmax()
axes[0, 0].axvline(x=peak_hour, color="navy", linestyle="--", alpha=0.7, label=f"Peak: {peak_hour}:00")
axes[0, 0].legend()

# Day of week
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
daily = df.groupby("day_of_week").size().reindex(day_order)
bar_colors = ["#e74c3c" if d in ["Saturday", "Sunday"] else "#3498db" for d in day_order]
axes[0, 1].bar(daily.index, daily.values, color=bar_colors)
axes[0, 1].set_title("Crimes by Day of Week")
axes[0, 1].set_xlabel("Day")
axes[0, 1].set_ylabel("Crime Count")
axes[0, 1].tick_params(axis="x", rotation=30)
axes[0, 1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

# Monthly
month_order = ["January","February","March","April","May","June",
               "July","August","September","October","November","December"]
monthly = df.groupby("month_name").size().reindex(month_order)
axes[1, 0].bar(range(1, 13), monthly.values, color=sns.color_palette("coolwarm", 12))
axes[1, 0].set_xticks(range(1, 13))
axes[1, 0].set_xticklabels([m[:3] for m in month_order], rotation=30)
axes[1, 0].set_title("Crimes by Month")
axes[1, 0].set_xlabel("Month")
axes[1, 0].set_ylabel("Crime Count")
axes[1, 0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

# Seasonal
seasonal = df.groupby("season").size().reindex(["Winter", "Spring", "Summer", "Fall"])
season_colors = ["#3498db", "#2ecc71", "#e74c3c", "#f39c12"]
wedges, texts, autotexts = axes[1, 1].pie(
    seasonal.values, labels=seasonal.index,
    colors=season_colors, autopct="%1.1f%%",
    startangle=90, textprops={"fontsize": 11}
)
axes[1, 1].set_title("Crimes by Season")

plt.tight_layout()
plt.savefig("eda_plots/02_temporal_patterns.png", dpi=150)
plt.close()
print(f"    Peak crime hour: {peak_hour}:00")
print(f"    Peak crime day : {daily.idxmax()}")
print(f"    Peak crime month: {monthly.idxmax()}")
print(f"    Peak crime season: {seasonal.idxmax()}")
print("    Saved: eda_plots/02_temporal_patterns.png\n")

# ═══════════════════════════════════════════════════════════════
# 3. GEOGRAPHIC DISTRIBUTION
# ═══════════════════════════════════════════════════════════════
print("[3] Geographic Distribution")

fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle("Geographic Crime Distribution", fontsize=14, fontweight="bold")

# Scatter plot of all crimes
sample = df.sample(min(50000, len(df)), random_state=42)
scatter = axes[0].scatter(
    sample["longitude"], sample["latitude"],
    c=sample["crime_severity_score"], cmap="YlOrRd",
    s=0.5, alpha=0.4
)
plt.colorbar(scatter, ax=axes[0], label="Severity Score")
axes[0].set_title("Crime Locations (50K sample)")
axes[0].set_xlabel("Longitude")
axes[0].set_ylabel("Latitude")

# Crimes by district
district_counts = df.groupby("district").size().sort_values(ascending=False)
axes[1].bar(district_counts.index.astype(str), district_counts.values,
            color=sns.color_palette("Reds_r", len(district_counts)))
axes[1].set_title("Crimes by Police District")
axes[1].set_xlabel("District")
axes[1].set_ylabel("Crime Count")
axes[1].tick_params(axis="x", rotation=45)
axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

plt.tight_layout()
plt.savefig("eda_plots/03_geographic_distribution.png", dpi=150)
plt.close()
print(f"    Top district by crime: District {district_counts.idxmax()} ({district_counts.max():,} crimes)")
print("    Saved: eda_plots/03_geographic_distribution.png\n")

# ═══════════════════════════════════════════════════════════════
# 4. ARREST & DOMESTIC RATES
# ═══════════════════════════════════════════════════════════════
print("[4] Arrest & Domestic Rates")

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle("Arrest & Domestic Incident Analysis", fontsize=14, fontweight="bold")

# Arrest rate by top 15 crime types
top15 = crime_counts.head(15).index
arrest_rate = (df[df["primary_type"].isin(top15)]
               .groupby("primary_type")["arrest"]
               .mean()
               .sort_values(ascending=True) * 100)

bars = axes[0].barh(arrest_rate.index, arrest_rate.values,
                    color=["#e74c3c" if v < 20 else "#f39c12" if v < 40 else "#2ecc71"
                           for v in arrest_rate.values])
axes[0].set_xlabel("Arrest Rate (%)")
axes[0].set_title("Arrest Rate by Crime Type (Top 15)")
axes[0].axvline(x=arrest_rate.mean(), color="navy", linestyle="--",
                label=f"Avg: {arrest_rate.mean():.1f}%")
axes[0].legend()
for bar, val in zip(bars, arrest_rate.values):
    axes[0].text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                 f"{val:.1f}%", va="center", fontsize=8)

# Overall arrest vs domestic
overall = {
    "Arrest Made": df["arrest"].mean() * 100,
    "No Arrest": (1 - df["arrest"].mean()) * 100,
}
domestic = {
    "Domestic": df["domestic"].mean() * 100,
    "Non-Domestic": (1 - df["domestic"].mean()) * 100,
}

x = np.arange(2)
width = 0.35
axes[1].bar(x - width/2, [overall["Arrest Made"], domestic["Domestic"]],
            width, label=["Arrests", "Domestic"], color=["#e74c3c", "#3498db"])
axes[1].bar(x + width/2, [overall["No Arrest"], domestic["Non-Domestic"]],
            width, color=["#95a5a6", "#bdc3c7"])
axes[1].set_xticks(x)
axes[1].set_xticklabels(["Arrest Status", "Domestic Status"])
axes[1].set_ylabel("Percentage (%)")
axes[1].set_title("Overall Arrest & Domestic Rates")
for i, (yes, no) in enumerate(zip(
    [overall["Arrest Made"], domestic["Domestic"]],
    [overall["No Arrest"], domestic["Non-Domestic"]]
)):
    axes[1].text(i - width/2, yes + 0.5, f"{yes:.1f}%", ha="center", fontsize=10, fontweight="bold")
    axes[1].text(i + width/2, no + 0.5, f"{no:.1f}%", ha="center", fontsize=10)

plt.tight_layout()
plt.savefig("eda_plots/04_arrest_domestic_rates.png", dpi=150)
plt.close()
print(f"    Overall arrest rate   : {df['arrest'].mean()*100:.1f}%")
print(f"    Overall domestic rate : {df['domestic'].mean()*100:.1f}%")
print("    Saved: eda_plots/04_arrest_domestic_rates.png\n")

# ═══════════════════════════════════════════════════════════════
# 5. CRIME HEATMAP (Hour x Day)
# ═══════════════════════════════════════════════════════════════
print("[5] Crime Heatmap - Hour vs Day of Week")

pivot = df.pivot_table(index="day_of_week", columns="hour",
                       values="id", aggfunc="count")
pivot = pivot.reindex(day_order)

fig, ax = plt.subplots(figsize=(18, 6))
sns.heatmap(pivot, cmap="YlOrRd", ax=ax, fmt=",d", annot=False,
            linewidths=0.3, cbar_kws={"label": "Crime Count"})
ax.set_title("Crime Heatmap: Hour of Day vs Day of Week", fontsize=14, fontweight="bold")
ax.set_xlabel("Hour of Day (0-23)")
ax.set_ylabel("Day of Week")
plt.tight_layout()
plt.savefig("eda_plots/05_heatmap_hour_day.png", dpi=150)
plt.close()
print("    Saved: eda_plots/05_heatmap_hour_day.png\n")

# ═══════════════════════════════════════════════════════════════
# 6. CRIME SEVERITY DISTRIBUTION
# ═══════════════════════════════════════════════════════════════
print("[6] Crime Severity Distribution")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

severity_dist = df["crime_severity_score"].value_counts().sort_index()
axes[0].bar(severity_dist.index, severity_dist.values,
            color=sns.color_palette("RdYlGn_r", len(severity_dist)))
axes[0].set_title("Crime Severity Score Distribution")
axes[0].set_xlabel("Severity Score (1=Minor, 10=Critical)")
axes[0].set_ylabel("Count")
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

avg_severity = df.groupby("primary_type")["crime_severity_score"].mean().sort_values(ascending=False).head(15)
axes[1].barh(avg_severity.index, avg_severity.values,
             color=sns.color_palette("Reds_r", 15))
axes[1].set_title("Top 15 Crime Types by Avg Severity")
axes[1].set_xlabel("Average Severity Score")
plt.tight_layout()
plt.savefig("eda_plots/06_severity_distribution.png", dpi=150)
plt.close()
print(f"    Average severity score: {df['crime_severity_score'].mean():.2f}")
print("    Saved: eda_plots/06_severity_distribution.png\n")

# ═══════════════════════════════════════════════════════════════
# 7. STATISTICAL SUMMARY
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("EDA STATISTICAL SUMMARY")
print("=" * 60)
print(f"Total crimes analysed   : {len(df):,}")
print(f"Date range              : {df['date'].min().date()} to {df['date'].max().date()}")
print(f"Crime types             : {df['primary_type'].nunique()}")
print(f"Top crime               : {crime_counts.idxmax()} ({crime_counts.max():,})")
print(f"Peak hour               : {peak_hour}:00")
print(f"Peak day                : {daily.idxmax()}")
print(f"Peak season             : {seasonal.idxmax()}")
print(f"Arrest rate             : {df['arrest'].mean()*100:.1f}%")
print(f"Domestic rate           : {df['domestic'].mean()*100:.1f}%")
print(f"Top district            : District {district_counts.idxmax()}")
print(f"Avg severity score      : {df['crime_severity_score'].mean():.2f} / 10")
print(f"\nAll plots saved in: eda_plots/")
print("EDA complete!")

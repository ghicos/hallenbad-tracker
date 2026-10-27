import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

CSV_FILE = "pool_visitors.csv"
OUTPUT_IMAGE = "best_times_heatmap.png"
TIME_GRANULARITY = "Slot_30m"  # Change to "Slot_15m" or "Slot_5m" anytime in the future

def generate_heatmap():
    if not os.path.isfile(CSV_FILE):
        return

    df = pd.read_csv(CSV_FILE).dropna(subset=["Visitors"])
    if df.empty:
        return

    df["Visitors"] = pd.to_numeric(df["Visitors"])
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    pivot = df.pivot_table(
        index=TIME_GRANULARITY, 
        columns="Day_of_Week", 
        values="Visitors", 
        aggfunc="mean"
    )
    
    existing_days = [d for d in days_order if d in pivot.columns]
    pivot = pivot[existing_days]

    plt.figure(figsize=(12, 10))
    sns.heatmap(
        pivot, 
        cmap="RdYlGn_r", # Green = Quietest, Red = Busiest
        annot=True, 
        fmt=".0f", 
        linewidths=0.5,
        cbar_kws={"label": "Average Number of Guests"}
    )
    
    plt.title("Hallenbad City – Best Times to Swim (Average Guests)", fontsize=14, pad=15)
    plt.xlabel("Day of the Week", fontsize=12)
    plt.ylabel("Time of Day", fontsize=12)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(OUTPUT_IMAGE, dpi=150)

if __name__ == "__main__":
    generate_heatmap()

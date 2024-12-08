import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results" / "charts"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def run_ea(df):
    print("Starting EA")

    df['issue_date'] = pd.to_datetime(df['issue_date'], errors='coerce')
    df['fine_amount'] = pd.to_numeric(df['fine_amount'], errors='coerce')
    df['issue_time'] = pd.to_datetime(df['issue_time'], format='%H%M', errors='coerce').dt.hour + \
                       pd.to_datetime(df['issue_time'], format='%H%M', errors='coerce').dt.minute / 60

    summary_stats = df.describe()
    median = df.median(numeric_only=True)
    mode = df.mode(numeric_only=True).iloc[0]
    avg_issue_time = df['issue_time'].mean()
    avg_issue_time_hour = int(avg_issue_time)
    avg_issue_time_minute = round((avg_issue_time - avg_issue_time_hour) * 60)
    avg_issue_time_str = f"{avg_issue_time_hour:02d}:{avg_issue_time_minute:02d}"

    summary_stats.loc['median'] = median
    summary_stats.loc['mode'] = mode
    summary_stats.loc['average_issue_time'] = avg_issue_time_str
    summary_stats.to_csv(RESULTS_DIR / "statistical_summary.csv")

    regions_bounds = {
        "Downtown LA": {"lat_min": 34.040, "lat_max": 34.090, "long_min": -118.290, "long_max": -118.220},
        "Hollywood": {"lat_min": 34.090, "lat_max": 34.140, "long_min": -118.350, "long_max": -118.290},
    }

    for region, bounds in regions_bounds.items():
        region_data = df[
            (df['loc_lat'] >= bounds['lat_min']) & (df['loc_lat'] <= bounds['lat_max']) &
            (df['loc_long'] >= bounds['long_min']) & (df['loc_long'] <= bounds['long_max'])
        ]

        if not region_data.empty:
            region_summary = region_data.describe()
            region_summary.loc['median'] = region_data.median(numeric_only=True)
            region_summary.loc['mode'] = region_data.mode(numeric_only=True).iloc[0]
            region_summary.loc['average_issue_time'] = avg_issue_time_str
            region_summary.to_csv(RESULTS_DIR / f"statistical_summary_{region.lower().replace(' ', '_')}.csv")

            daily_citations = region_data.groupby(region_data['issue_date'].dt.date).size()
            smoothed_citations = daily_citations.rolling(window=7).mean()
            plt.figure(figsize=(12, 6))
            plt.plot(smoothed_citations.index, smoothed_citations, label="7-Day Trendline", color='red')
            plt.title(f"Trendline of Daily Citations in {region}")
            plt.xlabel("Date")
            plt.ylabel("Number of Citations")
            plt.legend()
            plt.tight_layout()
            plt.savefig(RESULTS_DIR / f"trendline_daily_citations_{region.lower().replace(' ', '_')}.png")
            plt.close()

            daily_fines = region_data.groupby(region_data['issue_date'].dt.date)['fine_amount'].mean()
            smoothed_fines = daily_fines.rolling(window=7).mean()
            plt.figure(figsize=(12, 6))
            plt.plot(smoothed_fines.index, smoothed_fines, label="7-Day Trendline", color='orange')
            plt.title(f"Trendline of Average Daily Fine Amount in {region}")
            plt.xlabel("Date")
            plt.ylabel("Average Fine ($)")
            plt.legend()
            plt.tight_layout()
            plt.savefig(RESULTS_DIR / f"trendline_average_daily_fines_{region.lower().replace(' ', '_')}.png")
            plt.close()

    neighborhoods_bounds = {
        "Central LA": {"lat_min": 34.040, "lat_max": 34.090, "long_min": -118.290, "long_max": -118.220},
        "South Central LA": {"lat_min": 33.920, "lat_max": 34.000, "long_min": -118.310, "long_max": -118.240},
        "Hollywood": {"lat_min": 34.090, "lat_max": 34.140, "long_min": -118.350, "long_max": -118.290},
        "West Hollywood": {"lat_min": 34.080, "lat_max": 34.100, "long_min": -118.380, "long_max": -118.340},
        "Santa Monica": {"lat_min": 34.000, "lat_max": 34.050, "long_min": -118.520, "long_max": -118.450},
        "Beverly Hills": {"lat_min": 34.060, "lat_max": 34.090, "long_min": -118.420, "long_max": -118.380},
        "The Valley": {"lat_min": 34.170, "lat_max": 34.250, "long_min": -118.480, "long_max": -118.380},
    }

    neighborhood_stats = []
    for name, bounds in neighborhoods_bounds.items():
        neighborhood_data = df[
            (df['loc_lat'] >= bounds['lat_min']) & (df['loc_lat'] <= bounds['lat_max']) &
            (df['loc_long'] >= bounds['long_min']) & (df['loc_long'] <= bounds['long_max'])
        ]
        citations_count = len(neighborhood_data)
        avg_fine = neighborhood_data['fine_amount'].mean() if citations_count > 0 else 0
        neighborhood_stats.append({"Neighborhood": name, "Citations": citations_count, "Avg Fine": avg_fine})

    neighborhood_stats_df = pd.DataFrame(neighborhood_stats)

    plt.figure(figsize=(12, 6))
    plt.bar(neighborhood_stats_df['Neighborhood'], neighborhood_stats_df['Citations'], color='steelblue')
    plt.title("Frequency of Citations by Neighborhood")
    plt.xlabel("Neighborhood")
    plt.ylabel("Number of Citations")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "citations_by_neighborhood.png")
    plt.close()

    plt.figure(figsize=(12, 6))
    plt.bar(neighborhood_stats_df['Neighborhood'], neighborhood_stats_df['Avg Fine'], color='darkorange')
    for i, value in enumerate(neighborhood_stats_df['Avg Fine']):
        plt.text(i, value + 1, f"${value:.2f}", ha='center', fontsize=10)
    plt.title("Average Fine Amount by Neighborhood")
    plt.xlabel("Neighborhood")
    plt.ylabel("Average Fine ($)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "avg_fine_by_neighborhood.png")
    plt.close()

    combined_violations = df['violation_description'].value_counts()
    combined_violations = combined_violations[~combined_violations.index.str.contains("Unknown", na=False)].head(5)
    plt.figure(figsize=(12, 6))
    combined_violations.plot(kind='bar', color='teal')
    plt.title("Top 5 Violation Descriptions Across All Regions")
    plt.xlabel("Violation Description")
    plt.ylabel("Frequency")
    plt.xticks(rotation=45)
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "top_violations_combined.png")
    plt.close()

    for region, bounds in regions_bounds.items():
        region_data = df[
            (df['loc_lat'] >= bounds['lat_min']) & (df['loc_lat'] <= bounds['lat_max']) &
            (df['loc_long'] >= bounds['long_min']) & (df['loc_long'] <= bounds['long_max'])
        ]
        if not region_data.empty:
            region_violations = region_data['violation_description'].value_counts()
            region_violations = region_violations[~region_violations.index.str.contains("Unknown", na=False)].head(5)
            plt.figure(figsize=(12, 6))
            region_violations.plot(kind='bar', color='purple')
            plt.title(f"Top 5 Violation Descriptions in {region}")
            plt.xlabel("Violation Description")
            plt.ylabel("Frequency")
            plt.xticks(rotation=45)
            plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))
            plt.tight_layout()
            plt.savefig(RESULTS_DIR / f"top_violations_{region.lower().replace(' ', '_')}.png")
            plt.close()

    print("Explroatroy Analysis done ")

if __name__ == "__main__":
    import requests
    from io import StringIO

    API_URL = "https://data.lacity.org/resource/4f5p-udkv.csv?$where=issue_date between '2023-01-01T00:00:00' and '2024-12-31T23:59:59'"
    print("Fetching data from API")
    response = requests.get(API_URL)
    response.raise_for_status()
    df = pd.read_csv(StringIO(response.text))
    run_ea(df)

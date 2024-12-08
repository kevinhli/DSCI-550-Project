import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from pre_processing.retrieval import fetch_data_parallel
from pre_processing.cleaning import clean_and_map_data
from analysis.exploratory_analysis import run_ea
from analysis.visualization import generate_overall_heatmap
from analysis.predictive_modeling import train_model

def main():
    print("Step 1: Fetching data dynamically")
    api_url = "https://data.lacity.org/resource/4f5p-udkv.csv?$where=issue_date between '2023-01-01T00:00:00' and '2024-12-31T23:59:59'"
    raw_data = fetch_data_parallel(api_url) 

    if raw_data.empty:
        print("No data found or unable to fetch data. Exiting.")
        return

    print("Step 2: Cleaning and mapping")
    violation_codes_filepath = Path(__file__).resolve().parent.parent / "violation codes.csv"
    cleaned_data = clean_and_map_data(raw_data, violation_codes_filepath)

    print("\nStep 3: Running exploratory analysis")
    run_ea(cleaned_data)

    print("\nStep 4: Generating heatmap")
    generate_overall_heatmap(cleaned_data)

    print("\nStep 5: Running predictive model")
    train_model(cleaned_data)

    print("\nDone")

if __name__ == "__main__":
    main()

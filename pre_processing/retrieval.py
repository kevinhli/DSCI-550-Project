import requests
import pandas as pd
from io import StringIO
from concurrent.futures import ThreadPoolExecutor

CSV_API_URL = "https://data.lacity.org/resource/4f5p-udkv.csv?$where=issue_date between '2023-01-01T00:00:00' and '2024-12-31T23:59:59'"

def fetch_batch(api_url, offset, batch_size):
    paginated_url = f"{api_url}&$limit={batch_size}&$offset={offset}"
    try:
        response = requests.get(paginated_url)
        response.raise_for_status()
        batch_data = pd.read_csv(StringIO(response.text))
        print(f"Retrieved {len(batch_data)} rows from the offset {offset}.")
        return batch_data
    except Exception as e:
        print(f"Error fetching batch at offset {offset}: {e}")
        return pd.DataFrame()

def fetch_data_parallel(api_url, batch_size=50000, max_workers=8):
    offsets = range(0, 3500000, batch_size)
    all_data = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(lambda offset: fetch_batch(api_url, offset, batch_size), offsets)
        all_data.extend(results)
    return pd.concat(all_data, ignore_index=True)

def load_violation_codes(filepath):
    try:
        codes_df = pd.read_csv(filepath)
        print(f"Loaded {len(codes_df)} violation codes.")
        return codes_df
    except Exception as e:
        print(f"Error loading violation codes: {e}")
        return pd.DataFrame()

def map_violation_codes(df, codes_df):
    code_mapping = codes_df.set_index('Section')['Description'].to_dict()
    df['violation_description'] = df['violation_code'].map(
        lambda x: code_mapping.get(str(x).split('+')[0], 'Unknown') if pd.notnull(x) else 'Unknown'
    )
    print("Violation codes mapped to descriptions.")
    return df

def fetch_and_map_data(api_url, codes_filepath):
    data = fetch_data_parallel(api_url)
    print(f"Total rows retrieved: {len(data)}")
    codes_df = load_violation_codes(codes_filepath)
    data = map_violation_codes(data, codes_df)
    return data

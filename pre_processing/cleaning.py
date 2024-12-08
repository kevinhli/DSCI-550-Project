import pandas as pd
from pathlib import Path
import re
from rapidfuzz import process, fuzz

def normalize_code(violation_code):
    normalized = re.sub(r'[^\w.]', '', str(violation_code))
    return normalized.lower()

def load_violation_codes(filepath):
    try:
        codes_df = pd.read_csv(filepath)
        if 'Section' in codes_df.columns:
            codes_df['normalized_section'] = codes_df['Section'].apply(normalize_code)
        else:
            raise ValueError("Missing  column in violation codes CSV.")
        return codes_df
    except Exception as e:
        print(f"Error loading violation codes: {e}")
        return pd.DataFrame()

def map_violation_codes(df, codes_df, threshold=90):
    df['normalized_violation_code'] = df['violation_code'].apply(normalize_code)
    code_mapping = codes_df.set_index('normalized_section')['Description'].to_dict()

    def fuzzy_match(x):
        if pd.notnull(x):
            if x in code_mapping:
                return code_mapping[x]
            closest_match, score, _ = process.extractOne(x, code_mapping.keys(), scorer=fuzz.ratio)
            if score >= threshold:
                return code_mapping[closest_match]
        return 'Unknown'

    df['violation_description'] = df['normalized_violation_code'].apply(fuzzy_match)
    unmatched = df[df['violation_description'] == 'Unknown']['normalized_violation_code'].unique()
    print(f"Unmatched Codes: {unmatched}")
    print(f"Mapped {len(df[df['violation_description'] != 'Unknown'])} codes successfully.")
    print(f"Failed to mapthe {len(df[df['violation_description'] == 'Unknown'])} codes.")
    return df

def clean_data(df):
    print(f"Initial rows: {len(df)}")
    df = df.drop_duplicates()
    print(f"After dropping: {len(df)}")
    df = df.dropna(subset=['issue_date', 'fine_amount', 'location'])
    print(f"After dropping missing: {len(df)}")
    df['issue_date'] = pd.to_datetime(df['issue_date'], errors='coerce')
    df['fine_amount'] = pd.to_numeric(df['fine_amount'], errors='coerce')
    df = df.dropna(subset=['loc_lat', 'loc_long'])
    print(f"After dropping invalid coordinates: {len(df)}")
    print("Data cleaned")
    return df

def clean_and_map_data(raw_data, codes_filepath):
    cleaned_data = clean_data(raw_data)
    codes_df = load_violation_codes(codes_filepath)
    if not codes_df.empty:
        cleaned_data = map_violation_codes(cleaned_data, codes_df)
    return cleaned_data

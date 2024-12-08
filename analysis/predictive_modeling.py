from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results" / "modeling"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def train_model(df):
    df = df.copy()
    df['issue_time'] = pd.to_numeric(df['issue_time'], errors='coerce')
    df['loc_lat'] = pd.to_numeric(df['loc_lat'], errors='coerce')
    df['loc_long'] = pd.to_numeric(df['loc_long'], errors='coerce')
    df['fine_amount'] = pd.to_numeric(df['fine_amount'], errors='coerce')
    df = df.dropna(subset=['issue_time', 'loc_lat', 'loc_long', 'fine_amount'])

    if len(df) < 10:
        print("Not enough data")
        return

    df.loc[:, 'hour'] = (df['issue_time'] // 100).astype(int)
    df.loc[:, 'day_of_week'] = pd.to_datetime(df['issue_date']).dt.dayofweek

    X = df[['loc_lat', 'loc_long', 'hour', 'day_of_week']]
    y = (df['fine_amount'] > 100).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    cm = confusion_matrix(y_test, predictions, labels=[0, 1])
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Low Fine", "High Fine"])
    fig, ax = plt.subplots(figsize=(8, 6))
    disp.plot(ax=ax, cmap='Blues', values_format='d')
    plt.title("Confusion Matrix: High-Fine Prediction")
    plt.savefig(RESULTS_DIR / "confusion_matrix.png")
    plt.close()

if __name__ == "__main__":
    import requests
    from io import StringIO

    API_URL = "https://data.lacity.org/resource/4f5p-udkv.csv?$where=issue_date between '2023-01-01T00:00:00' and '2024-12-31T23:59:59'"
    print("Fetching data from API")
    response = requests.get(API_URL)
    response.raise_for_status()
    df = pd.read_csv(StringIO(response.text))
    train_model(df)

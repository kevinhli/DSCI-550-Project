DSCI 550 Project Fall 2024:

Contributors:
Kevin Liu, Chris Carlson, Nick Ratliff, Tae Woo Kang

Brief summary:

This project's goal is to predict high-fine and high-frequency parking citations in Los Angeles neighborhoods using data from LADOT's Parking Citation API. 
It identifies patterns in parking violations, enabling insights for optimized enforcement and better urban planning.

How to run the file:

1. Install requirements mentioned in requirements.txt
2. Execute the main.py script to perform the following tasks:
    Data retrieval from the LADOT API
    Data cleaning and preprocessing
    Exploratory data analysis (charts output)
    Visualizations (heatmap)
    Predictive modeling (confusion matrix)

Overall file structure:

DSCI 550 Project/
├── analysis/

│   ├── exploratory_analysis.py  # EDA functions

│   ├── main.py                  # Main pipeline execution

│   ├── predictive_modeling.py   # Predictive model training

│   └── visualization.py         # Visualization scripts

├── pre-processing/

│   ├── cleaning.py              # Data cleaning

│   └── retrieval.py             # API data retrieval

├── results/

│   ├── charts/                  # Bar charts, time-series plots

│   └── heatmaps/                # Heatmap visualizations

|   └── modeling /               # Counfusion Matrix output

├── requirements.txt             # Python dependencies

└── README.md                    # Documentation

└── violation codes.csv          # reference codes for description of parking violations

└── Example Data.csv             # Small csv file to show how data is formatted in API

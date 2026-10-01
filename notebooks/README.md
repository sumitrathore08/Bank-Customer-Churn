# Step 2: Data understanding

The companion script `../src/understand_data.py` prints the shape, duplicate checks, target distribution, and variable types. It writes detailed schema and descriptive-statistic tables into `../reports/`.

## What to look for

- **Rows and columns:** the dataset size and number of recorded fields.
- **Data types:** numbers support calculations; text fields are categories.
- **Missing values:** gaps may need treatment before analysis or modeling.
- **Duplicates:** repeated records can distort counts and model evaluation.
- **Target distribution:** `Churn=1` means churned; `Churn=0` means retained. Unequal class counts mean accuracy alone will be insufficient later.
- **Unique values:** helps identify identifier-like columns and unexpected categories.

The raw data is synthetic and generated with a fixed random seed for reproducibility. It is designed to contain plausible relationships, but it does not represent actual bank customers.

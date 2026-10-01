"""Run first-pass data checks and write concise, reviewable summary tables."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "bank_customers.csv"
REPORT_DIR = ROOT / "reports"


def summarize(path: Path = DATA_PATH) -> dict[str, object]:
    """Load data and report shape, schema, completeness, uniqueness and target."""
    df = pd.read_csv(path)
    REPORT_DIR.mkdir(exist_ok=True)
    schema = pd.DataFrame({
        "dtype": df.dtypes.astype(str),
        "missing_count": df.isna().sum(),
        "missing_pct": (df.isna().mean() * 100).round(2),
        "unique_count": df.nunique(dropna=False),
    }).rename_axis("column")
    schema.to_csv(REPORT_DIR / "data_dictionary_profile.csv")
    df.describe(include="all").transpose().to_csv(REPORT_DIR / "descriptive_statistics.csv")
    categorical = df.select_dtypes(include=["object", "category"]).columns.tolist()
    numeric = df.select_dtypes(include="number").columns.tolist()
    target_counts = df["Churn"].value_counts(dropna=False).sort_index().to_dict()
    result = {
        "shape": df.shape,
        "duplicate_rows": int(df.duplicated().sum()),
        "duplicate_customer_ids": int(df["CustomerID"].duplicated().sum()),
        "categorical_columns": categorical,
        "numeric_columns": numeric,
        "target_counts": target_counts,
        "target_rate": float(df["Churn"].mean()),
    }
    print(f"Rows, columns: {result['shape']}")
    print(f"Duplicate records: {result['duplicate_rows']}; duplicate IDs: {result['duplicate_customer_ids']}")
    print(f"Churn counts (0=retained, 1=churned): {target_counts}")
    print(f"Synthetic churn rate: {result['target_rate']:.1%}")
    print(f"Categorical fields ({len(categorical)}): {', '.join(categorical)}")
    print(f"Numeric fields ({len(numeric)}): {', '.join(numeric)}")
    print(f"Wrote profiling tables to {REPORT_DIR}")
    return result


if __name__ == "__main__":
    summarize()

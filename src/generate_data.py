"""Generate reproducible, behaviorally plausible synthetic banking customers."""
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
N_CUSTOMERS = 12_000
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "bank_customers.csv"


def generate_customers(n: int = N_CUSTOMERS, seed: int = SEED) -> pd.DataFrame:
    """Create a synthetic cross-sectional customer snapshot with a defined label."""
    rng = np.random.default_rng(seed)
    customer_id = np.arange(100_001, 100_001 + n)
    age = np.clip(np.rint(rng.normal(42, 12, n)), 18, 85).astype(int)
    gender = rng.choice(["Female", "Male"], n, p=[0.48, 0.52])
    geography = rng.choice(["France", "Germany", "Spain"], n, p=[0.50, 0.25, 0.25])
    tenure = rng.integers(0, 11, n)
    credit_score = np.clip(np.rint(rng.normal(650, 85, n)), 300, 850).astype(int)
    estimated_salary = np.clip(rng.lognormal(np.log(62_000), 0.55, n), 12_000, 250_000).round(2)
    has_balance = rng.random(n) < 0.68
    balance = np.where(has_balance, rng.gamma(2.1, 42_000, n), 0).clip(0, 250_000).round(2)
    num_products = rng.choice([1, 2, 3, 4], n, p=[0.51, 0.43, 0.05, 0.01])
    has_card = rng.binomial(1, 0.71, n)
    is_active = rng.binomial(1, 0.57, n)

    # Engagement is generated from a shared latent behavior and then expressed
    # through several observable, correlated banking channels.
    digital_score = np.clip(rng.normal(55 + 18 * is_active, 17, n), 0, 100).round(1)
    monthly_tx = np.clip(rng.poisson(np.maximum(2, 7 + 0.15 * digital_score + 3 * is_active)), 0, 65)
    avg_tx_value = np.clip(rng.lognormal(np.log(105 + balance / 6000), 0.55, n), 5, 2_500).round(2)
    branch_visits = np.clip(rng.poisson(np.maximum(0.4, 2.5 - digital_score / 55)), 0, 18)
    complaints = np.clip(rng.poisson(0.18 + 0.35 * (1 - is_active) + 0.15 * (digital_score < 25)), 0, 6)
    service_calls = np.clip(rng.poisson(0.6 + 1.1 * complaints + 0.4 * (1 - is_active)), 0, 12)
    last_tx_days = np.clip(rng.gamma(2.0, 13, n) + 12 * (1 - is_active) + 5 * complaints, 0, 180).round().astype(int)
    loan_amount = np.where(rng.random(n) < 0.27, rng.gamma(2.0, 18_000, n), 0).clip(0, 300_000).round(2)
    credit_card_spend = np.where(has_card == 1, (monthly_tx * avg_tx_value * rng.uniform(0.15, 0.65, n)), 0).round(2)
    savings_balance = (balance * rng.uniform(0.25, 0.75, n)).round(2)
    investment_balance = np.where(age >= 30, rng.gamma(0.8, 18_000, n), rng.gamma(0.3, 5_000, n)).round(2)
    account_type = rng.choice(["Standard", "Premium", "Student"], n, p=[0.68, 0.22, 0.10])
    total_tx_amount = (monthly_tx * avg_tx_value * 12).round(2)

    # Label probabilities encode plausible risk associations. The label is a
    # synthetic historical outcome for learning, not a real-world causal claim.
    logit = (
        -2.65
        + 0.62 * (geography == "Germany")
        + 0.42 * (age > 60)
        + 0.55 * (num_products == 1)
        + 0.95 * (num_products >= 3)
        + 0.82 * (is_active == 0)
        + 0.24 * complaints
        + 0.055 * np.maximum(last_tx_days - 25, 0)
        - 0.022 * monthly_tx
        - 0.018 * (digital_score - 50)
        + 0.000003 * np.maximum(balance - 80_000, 0)
        + rng.normal(0, 0.28, n)
    )
    churn_prob = 1 / (1 + np.exp(-logit))
    churn = rng.binomial(1, churn_prob)

    return pd.DataFrame({
        "CustomerID": customer_id, "Age": age, "Gender": gender, "Geography": geography,
        "Tenure": tenure, "CreditScore": credit_score, "EstimatedSalary": estimated_salary,
        "Balance": balance, "NumOfProducts": num_products, "HasCrCard": has_card,
        "IsActiveMember": is_active, "MonthlyTransactions": monthly_tx,
        "AverageTransactionValue": avg_tx_value, "DigitalUsageScore": digital_score,
        "BranchVisits": branch_visits, "CustomerServiceCalls": service_calls,
        "Complaints": complaints, "LoanAmount": loan_amount, "CreditCardSpend": credit_card_spend,
        "SavingsBalance": savings_balance, "InvestmentBalance": investment_balance,
        "LastTransactionDays": last_tx_days, "TotalTransactionAmount": total_tx_amount,
        "AccountType": account_type, "Churn": churn,
    })


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    customers = generate_customers()
    customers.to_csv(OUTPUT, index=False)
    print(f"Saved {len(customers):,} synthetic customer records to {OUTPUT}")
    print(f"Synthetic churn rate: {customers['Churn'].mean():.1%}")


if __name__ == "__main__":
    main()

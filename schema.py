"""
Pandera schema for raw churn dataset.
Acts as a hard gate: raw_data -> validate() -> feature_engineering.py
Adjust column names/dtypes below to match your actual CSV.
"""

import pandera.pandas as pa
from pandera.pandas import Column, DataFrameSchema, Check

raw_churn_schema = DataFrameSchema(
    {
        "customer_id": Column(str, nullable=False, unique=True),

        "signup_date": Column("datetime64[ns]", nullable=False),

        "last_login_date": Column("datetime64[ns]", nullable=False),

        "monthly_charges": Column(
            float,
            checks=Check.in_range(0, 10000),
            nullable=False,
        ),

        "tenure_months": Column(
            int,
            checks=Check.in_range(0, 600),  # 0 to 50 years, sanity cap
            nullable=False,
        ),

        "contract_type": Column(
            str,
            checks=Check.isin(["month-to-month", "one-year", "two-year"]),
            nullable=False,
        ),

        "churn": Column(
            int,
            checks=Check.isin([0, 1]),
            nullable=False,
        ),
    },
    strict=False,  # set True once you've confirmed the full real column list
    coerce=True,
)


def validate_raw(df):
    """Validate raw dataframe. Raises pandera.errors.SchemaError on failure."""
    return raw_churn_schema.validate(df, lazy=True)


if __name__ == "__main__":
    import sys
    import pandas as pd

    if len(sys.argv) != 2:
        print("Usage: python schema.py <path_to_csv>")
        sys.exit(1)

    df = pd.read_csv(sys.argv[1], parse_dates=["signup_date", "last_login_date"])

    try:
        validate_raw(df)
        print(f"PASS: {sys.argv[1]} conforms to schema ({len(df)} rows).")
    except pa.errors.SchemaErrors as e:
        print("FAIL: schema validation errors:")
        print(e.failure_cases)
        sys.exit(1)

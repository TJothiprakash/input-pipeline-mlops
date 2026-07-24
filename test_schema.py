"""
Proves the schema actually gates bad data.
Run: pytest test_schema.py -v
"""

import pandas as pd
import pandera.pandas as pa
import pytest

from schema import validate_raw


def _good_row():
    return {
        "customer_id": "CUST001",
        "signup_date": pd.Timestamp("2023-01-01"),
        "last_login_date": pd.Timestamp("2024-01-01"),
        "monthly_charges": 49.99,
        "tenure_months": 12,
        "contract_type": "month-to-month",
        "churn": 0,
    }


def test_valid_data_passes():
    df = pd.DataFrame([_good_row()])
    # should not raise
    validate_raw(df)


def test_wrong_dtype_fails():
    row = _good_row()
    row["monthly_charges"] = "not_a_number"  # str instead of float
    df = pd.DataFrame([row])
    with pytest.raises(pa.errors.SchemaErrors):
        validate_raw(df)


def test_out_of_range_value_fails():
    row = _good_row()
    row["monthly_charges"] = -50.0  # negative charge, outside Check.in_range(0, 10000)
    df = pd.DataFrame([row])
    with pytest.raises(pa.errors.SchemaErrors):
        validate_raw(df)


def test_unseen_categorical_level_fails():
    row = _good_row()
    row["contract_type"] = "lifetime"  # not in isin(["month-to-month", "one-year", "two-year"])
    df = pd.DataFrame([row])
    with pytest.raises(pa.errors.SchemaErrors):
        validate_raw(df)


def test_bad_churn_label_fails():
    row = _good_row()
    row["churn"] = 2  # not in isin([0, 1])
    df = pd.DataFrame([row])
    with pytest.raises(pa.errors.SchemaErrors):
        validate_raw(df)

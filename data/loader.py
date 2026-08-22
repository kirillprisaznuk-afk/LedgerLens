"""Loads a transactions CSV into the database:
- validates/cleans rows
- auto-categorizes by keyword matching on the description
- inserts into the transactions table
"""
import pandas as pd
from datetime import datetime
from data.database import get_session, init_db
from data.models import Account, Category, Transaction

# keyword -> category name (simple rule-based categorizer for MVP)
KEYWORD_MAP = {
    "rent": "Rent",
    "salary": "Salaries",
    "ads": "Marketing",
    "campaign": "Marketing",
    "subscription": "Software & Subscriptions",
    "saas": "Software & Subscriptions",
    "electricity": "Utilities",
    "water bill": "Utilities",
    "office supplies": "Office Supplies",
    "trip": "Travel",
    "flight": "Travel",
    "hotel": "Travel",
    "tax": "Taxes & Fees",
    "invoice": "Sales Revenue",
    "product sale": "Sales Revenue",
    "consulting": "Sales Revenue",
    "refund": "Other Income",
}


def categorize(description: str) -> str:
    text = description.lower()
    for keyword, category in KEYWORD_MAP.items():
        if keyword in text:
            return category
    return "Other Income" if "income" in text else "Office Supplies"


def load_csv(path: str):
    init_db()
    session = get_session()

    df = pd.read_csv(path)

    before = len(df)
    df = df.dropna(subset=["date", "amount", "account"])
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df = df.drop_duplicates(subset=["date", "description", "amount", "account"])
    after = len(df)
    print(f"Validation: {before - after} rows dropped, {after} rows valid.")

    accounts = {a.name: a for a in session.query(Account).all()}
    categories = {c.name: c for c in session.query(Category).all()}

    inserted = 0
    for _, row in df.iterrows():
        account = accounts.get(row["account"])
        if account is None:
            continue

        category_name = categorize(str(row["description"]))
        category = categories.get(category_name)

        txn = Transaction(
            date=row["date"].date(),
            amount=float(row["amount"]),
            description=str(row["description"]),
            account_id=account.id,
            category_id=category.id if category else None,
        )
        session.add(txn)
        inserted += 1

    session.commit()
    session.close()
    print(f"Inserted {inserted} transactions into the database.")


if __name__ == "__main__":
    load_csv("transactions.csv")
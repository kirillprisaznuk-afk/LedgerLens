"""Generates a synthetic CSV of transactions, simulating a raw bank export
that a real business owner would upload into FinOps.
Columns: date, description, amount, account
"""
import csv
import random
from datetime import date, timedelta

random.seed(42)

ACCOUNTS = ["Main Bank Account", "Cash Register"]

# (description keyword, amount range, sign) -- used later by the loader
# to auto-categorize transactions by matching description text.
EXPENSE_PATTERNS = [
    ("Rent payment - office", (-1800, -1500)),
    ("Salary payment - staff", (-4500, -3800)),
    ("Facebook Ads campaign", (-600, -150)),
    ("Google Ads campaign", (-500, -120)),
    ("Software subscription - SaaS tools", (-120, -40)),
    ("Electricity bill", (-220, -90)),
    ("Water bill", (-60, -25)),
    ("Office supplies purchase", (-150, -30)),
    ("Business trip - flights/hotel", (-800, -200)),
    ("Tax payment - quarterly", (-1200, -400)),
]

INCOME_PATTERNS = [
    ("Client payment - invoice", (500, 6000)),
    ("Product sale - online store", (50, 1200)),
    ("Consulting fee received", (300, 3000)),
    ("Refund received", (20, 300)),
]


def random_amount(rng):
    low, high = rng
    return round(random.uniform(low, high), 2)


def generate(start_year=2024, start_month=9, months=24, out_path="transactions.csv"):
    start = date(start_year, start_month, 1)
    rows = []

    for m in range(months):
        month_date = start + timedelta(days=30 * m)
        month_start = date(month_date.year, month_date.month, 1)

        for _ in range(random.randint(3, 6)):
            desc, rng = random.choice(INCOME_PATTERNS)
            d = month_start + timedelta(days=random.randint(0, 27))
            rows.append([d.isoformat(), desc, random_amount(rng), random.choice(ACCOUNTS)])

        for desc, rng in EXPENSE_PATTERNS:
            if random.random() < 0.85:
                d = month_start + timedelta(days=random.randint(0, 27))
                rows.append([d.isoformat(), desc, random_amount(rng), random.choice(ACCOUNTS)])

    rows.sort(key=lambda r: r[0])

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "description", "amount", "account"])
        writer.writerows(rows)

    print(f"Generated {len(rows)} synthetic transactions into {out_path}")


if __name__ == "__main__":
    generate()
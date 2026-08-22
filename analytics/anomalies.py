"""Anomaly detection on transactions using Isolation Forest.
Flags transactions whose amount is unusual relative to their category's
typical spending pattern - e.g. a rent payment 3x larger than usual.
"""
import pandas as pd
from sklearn.ensemble import IsolationForest
from data.database import get_session
from data.models import Transaction, Category


def detect_anomalies(contamination: float = 0.05) -> pd.DataFrame:
    """Returns a DataFrame of transactions flagged as anomalies.
    `contamination` is the expected proportion of outliers (5% default).
    """
    session = get_session()
    rows = (
        session.query(
            Transaction.id,
            Transaction.date,
            Transaction.description,
            Transaction.amount,
            Category.name,
        )
        .join(Category, Transaction.category_id == Category.id)
        .all()
    )
    session.close()

    df = pd.DataFrame(rows, columns=["id", "date", "description", "amount", "category"])
    if df.empty:
        return df

    df["abs_amount"] = df["amount"].abs()
    flagged_frames = []

    # Run anomaly detection per category, since "unusual" is relative
    # to that category's normal range (e.g. rent vs. office supplies
    # have very different typical amounts).
    for category, group in df.groupby("category"):
        if len(group) < 5:
            continue  # not enough data points to judge what's "normal"

        model = IsolationForest(contamination=contamination, random_state=42)
        preds = model.fit_predict(group[["abs_amount"]])
        group = group.copy()
        group["is_anomaly"] = preds == -1
        flagged_frames.append(group)

    result = pd.concat(flagged_frames) if flagged_frames else df
    return result[result["is_anomaly"] == True].sort_values("abs_amount", ascending=False)


if __name__ == "__main__":
    anomalies = detect_anomalies()
    if anomalies.empty:
        print("No anomalies detected.")
    else:
        print(f"Found {len(anomalies)} anomalies:")
        print(anomalies[["date", "description", "amount", "category"]].to_string(index=False))
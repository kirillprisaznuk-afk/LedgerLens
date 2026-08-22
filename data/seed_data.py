"""Seeds reference tables (accounts, categories) with starter data."""
from data.database import get_session, init_db
from data.models import Account, Category

ACCOUNTS = [
    {"name": "Main Bank Account", "type": "bank", "currency": "EUR"},
    {"name": "Cash Register", "type": "cash", "currency": "EUR"},
]

CATEGORIES = [
    {"name": "Sales Revenue", "type": "income"},
    {"name": "Other Income", "type": "income"},
    {"name": "Rent", "type": "expense"},
    {"name": "Salaries", "type": "expense"},
    {"name": "Marketing", "type": "expense"},
    {"name": "Software & Subscriptions", "type": "expense"},
    {"name": "Utilities", "type": "expense"},
    {"name": "Office Supplies", "type": "expense"},
    {"name": "Travel", "type": "expense"},
    {"name": "Taxes & Fees", "type": "expense"},
]


def seed():
    init_db()
    session = get_session()

    if session.query(Account).count() == 0:
        for a in ACCOUNTS:
            session.add(Account(**a))

    if session.query(Category).count() == 0:
        for c in CATEGORIES:
            session.add(Category(**c))

    session.commit()
    session.close()
    print("Seed complete: accounts and categories added.")


if __name__ == "__main__":
    seed()
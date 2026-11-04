"""Finance data: accounts -> transactions (balance never goes negative)"""
import random
from datetime import date, timedelta
from faker import Faker
from config import write_csv

random.seed(99)
Faker.seed(99)
fake = Faker("en_IN")
DB = "finance_db"
TODAY = date(2026, 11, 1)
N_ACCOUNTS = 2000

credit_types = ["deposit", "salary", "refund"]
debit_types = ["withdrawal", "purchase", "bill_payment"]
categories = ["Groceries", "Travel", "Dining", "Shopping", "Utilities", "Rent", "Health", "Entertainment"]

accounts, transactions = [], []
txn_id = 1
for acc_id in range(1, N_ACCOUNTS + 1):
    opened = TODAY - timedelta(days=random.randint(90, 4 * 365))
    balance = 0.0

    # random dates after the account was opened, sorted so the running balance makes sense
    n_txn = random.randint(30, 120)
    dates = sorted(opened + timedelta(days=random.randint(0, (TODAY - opened).days)) for _ in range(n_txn))
    dates[0] = opened                                      # first transaction = opening deposit

    for i, d in enumerate(dates):
        amount = round(min(max(random.lognormvariate(7, 1), 100), 150000), 2)
        if i == 0 or random.random() < 0.4:                # ~40% credits
            direction, txn_type, cat = "CR", random.choice(credit_types), "Income"
        else:
            direction, txn_type, cat = "DR", random.choice(debit_types), random.choice(categories)
            if amount > balance:                           # logical constraint: no overdraft
                direction, txn_type, cat = "CR", "deposit", "Income"
        balance += amount if direction == "CR" else -amount
        balance = round(balance, 2)
        transactions.append([txn_id, acc_id, d, txn_type, direction, amount, cat, balance])
        txn_id += 1

    accounts.append([acc_id, fake.name(), random.choice(["savings", "current"]), opened,
                     random.choices(["active", "closed", "frozen"], [93, 5, 2])[0], balance])

write_csv(DB, "accounts", ["account_id", "holder_name", "account_type", "opened_date", "status", "balance"], accounts)
write_csv(DB, "transactions", ["txn_id", "account_id", "txn_date", "txn_type", "direction", "amount",
                               "category", "balance_after"], transactions)

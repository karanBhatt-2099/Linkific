CREATE TABLE accounts (
    account_id    SERIAL PRIMARY KEY,
    holder_name   VARCHAR(100) NOT NULL,
    account_type  VARCHAR(20)  NOT NULL,
    opened_date   DATE NOT NULL,
    status        VARCHAR(15) NOT NULL,
    balance       NUMERIC(14,2) NOT NULL CHECK (balance >= 0)
);
CREATE TABLE transactions (
    txn_id        SERIAL PRIMARY KEY,
    account_id    INT NOT NULL REFERENCES accounts(account_id),
    txn_date      DATE NOT NULL,
    txn_type      VARCHAR(20) NOT NULL,
    direction     CHAR(2) NOT NULL CHECK (direction IN ('CR','DR')),
    amount        NUMERIC(12,2) NOT NULL CHECK (amount > 0),
    category      VARCHAR(30),
    balance_after NUMERIC(14,2) NOT NULL
);

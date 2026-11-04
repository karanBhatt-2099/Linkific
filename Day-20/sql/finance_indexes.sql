CREATE INDEX idx_txn_account ON transactions(account_id);
CREATE INDEX idx_txn_date    ON transactions(txn_date);
CREATE INDEX idx_txn_type    ON transactions(txn_type);

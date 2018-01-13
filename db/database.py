import records
import time


class FaucetDB():
    def __init__(self, connection):
        self.db = records.Database(connection)

    def setup(self):
        self.db.query("CREATE TABLE 'transactions' ( \
                      'id' INT NOT NULL AUTO_INCREMENT \
                      'timestamp' DECIMAL(12, 6), \
                      'tailtx' CHAR(81), \
                      'confirmed' BOOLEAN \
                      )")

        self.db.query("CREATE TABLE 'seeds' ( \
                      'id' INT NOT NULL AUTO_INCREMENT \
                      'seed' CHAR(81), \
                      'balance' BIGINT, \
                      'timescanned' BIGINT, \
                      'stale' BOOLEAN \
                      )")

        self.db.query("CREATE TABLE 'txs_queue' ( \
                      'id' INT NOT NULL AUTO_INCREMENT \
                      'timestamp' DECIMAL(12, 6), \
                      'trytes' CHAR(2673), \
                      'bundle' CHAR(81), \
                      'seed' CHAR(81), \
                      'tasktime' BIGINT, \
                      'pow' BOOLEAN \
                      )")

        self.db.query("CREATE TABLE 'payouts' ( \
                      'timestamp' DECIMAL(12, 6), \
                      'address' CHAR(81), \
                      'amount' BIGINT \
                      )")

    def payout(self, address, amount):
        self.db.query("INSERT INTO 'payouts' ('timestamp','address','amount') \
                      VALUES (:timestamp, :addr, :amt);",
                      timestamp=time.time(), addr=address, amt=amount)

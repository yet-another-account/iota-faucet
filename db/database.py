import records
import time


class FaucetDB():
    def __init__(self, connection):
        self.db = records.Database(connection)

    def setup(self):
        self.db.query("CREATE TABLE 'transactions' ("
                      "'timestamp' BIGINT,"
                      "'tailtx' CHAR(81),"
                      "'confirmed' BOOL"
                      ")")

        self.db.query("CREATE TABLE 'seeds' ("
                      "'seed' CHAR(81),"
                      "'balance' BIGINT,"
                      "'timescanned' BIGINT,"
                      "'stale' BOOL"
                      ")")

        self.db.query("CREATE TABLE 'txs_nopow' ("
                      "'timestamp' BIGINT,"
                      "'trytes' CHAR(2673),"
                      "'bundle' CHAR(81),"
                      "'seed' CHAR(81),"
                      "'tasktime' BIGINT,"
                      ")")

        self.db.query("CREATE TABLE 'payouts' ("
                      "'timestamp' BIGINT,"
                      "'address' CHAR(81),"
                      "'amount' BIGINT,"
                      ")")

    def payout(self, address, amount):
        self.db.query("INSERT INTO 'payouts' ('timestamp','address','amount') \
                      VALUES (:timestamp, :addr, :amt);",
                      timestamp=time.time(), addr=address, amt=amount)

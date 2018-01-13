import records
import time
import settings
import iota


class FaucetDB():
    def __init__(self, connection, api):
        self.db = records.Database(connection)
        self.api = api

    def setup(self):
        self.db.query("CREATE TABLE 'addresses' ( \
                      'index' INT NOT NULL UNIQUE, \
                      'address' CHAR(81) NOT NULL \
                      'used' BOOLEAN NOT NULL \
                      )")

        self.db.query("CREATE TABLE 'transactions' ( \
                      'id' INT NOT NULL AUTO_INCREMENT \
                      'tailtx' CHAR(81), NOT NULL \
                      'confirmed' BOOLEAN NOT NULL \
                      )")

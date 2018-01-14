import records
from .. import config
import logging


class FaucetDB():
    def __init__(self, connection, api, clean=False):
        self.db = records.Database(connection)
        self.api = api

        # warning: do NOT enable in prod!
        if clean:
            self._clean()

        # create tables if nonexistant
        if not self.db.query("SHOW TABLES LIKE 'addresses'").first():
            logging.info("New database detected. Building tables...")
            self.setup()

    def setup(self):
        self.db.query("CREATE TABLE addresses ( \
                      idx INT PRIMARY KEY, \
                      address CHAR(81), \
                      spent BOOLEAN, \
                      received BOOLEAN, \
                      balance INT \
                      )")

        self.db.query("CREATE TABLE transactions ( \
                      id INT PRIMARY KEY AUTO_INCREMENT, \
                      tailtx CHAR(81), \
                      confirmed BOOLEAN \
                      )")

    def gen_addrs(self):
        lastaddr = self.db.query("SELECT * FROM addresses \
                                 ORDER BY idx DESC \
                                 LIMIT 1")

        # first time making addresses
        if not lastaddr.first():
            addrs = self.api.get_new_addresses(
                count=config.ADDR_BATCH)['addresses']
            idx = 0
        else:
            addrs = self.api.get_new_addresses(count=config.ADDR_BATCH,
                                               index=lastaddr[0].idx + 1)['addresses']
            idx = lastaddr[0].idx + 1

        for addr in addrs:
            self.db.query("INSERT INTO addresses (idx, address, spent, \
                          received, balance) \
                          VALUES (:idx, :address, false, false, 0)",
                          idx=idx, address=addr)
            idx += 1

    def check_addrs(self):
        addrs = self.db.query("SELECT * FROM addresses WHERE spent=FALSE")

        addrs = [a.address for a in addrs]

        bals = self.api.get_balances(addrs, threshold=1)['balances']

        for addr, bal in zip(addrs, bals):
            if not bal == 0:
                self.db.query("UPDATE addresses SET balance=:bal, received=TRUE \
                              WHERE address=:addr",
                              addr=addr, bal=bal)

    def num_addrs(self):
        return self.db.query("SELECT COUNT(*) as k FROM addresses")[0].k

    def _clean(self):
        self.db.query("DROP TABLE IF EXISTS transactions")
        self.db.query("DROP TABLE IF EXISTS addresses")

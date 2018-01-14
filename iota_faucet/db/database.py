import records
from .. import config
import logging


class FaucetDB():
    def __init__(self, connection, api):
        self.db = records.Database(connection)
        self.api = api

        # create tables if nonexistant
        if not self.db.query("SHOW TABLES LIKE 'addresses'").first():
            logging.info("New database detected. Building tables...")
            self.setup()

    def setup(self):
        self.db.query("CREATE TABLE addresses ( \
                      idx INT PRIMARY KEY, \
                      address CHAR(81), \
                      used BOOLEAN \
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
            self.db.query("INSERT INTO addresses (idx, address, used) \
                          VALUES (:idx, :address, false)",
                          idx=idx, address=addr)
            idx += 1

    def num_addrs(self):
        return self.db.query("SELECT COUNT(*) as k FROM addresses")[0].k

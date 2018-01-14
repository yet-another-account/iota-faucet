import records
from .. import config
import logging
from iota import ProposedTransaction, Address


class FaucetDB():
    def __init__(self, connection, api, clean=False):
        self.db = records.Database(connection)
        self.api = api

        # warning: do NOT enable in prod!
        if clean:
            self._clear()

        # create tables if nonexistant
        if not self.db.query("SHOW TABLES LIKE 'addresses'").first():
            logging.info("New database detected. Building tables...")
            self.setup()

    def setup(self):
        self.db.query("CREATE TABLE addresses ( \
                      idx INT PRIMARY KEY, \
                      address CHAR(81) UNIQUE KEY, \
                      spent BOOLEAN, \
                      received BOOLEAN, \
                      balance INT \
                      )")

        self.db.query("CREATE TABLE transactions ( \
                      id INT PRIMARY KEY AUTO_INCREMENT, \
                      timestamp BIGINT, \
                      tailtx CHAR(81), \
                      confirmed BOOLEAN \
                      )")

    def gen_addrs(self, num=config.ADDR_BATCH):
        lastaddr = self.db.query("SELECT * FROM addresses \
                                 ORDER BY idx DESC \
                                 LIMIT 1")

        # first time making addresses
        if not lastaddr.first():
            addrs = self.api.get_new_addresses(
                count=config.ADDR_BATCH)['addresses']
            idx = 0
        else:
            addrs = self.api.get_new_addresses(count=num, index=lastaddr[0].idx
                                               + 1)['addresses']
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

    def get_change_address(self):
        c = self.db.query("SELECT * FROM addresses WHERE spent=FALSE \
                          AND received=FALSE AND balance=0 LIMIT 1")

        if c.first():
            self.db.query("UPDATE addresses SET receive=TRUE \
                          WHERE address=:addr",
                          addr=c.first.address)
            return c.first().address
        else:
            # generate more addresses and then recurse, now that there are
            # fresh addresses to return.
            self.gen_addrs()
            return self.get_change_address()

    def payout(self, address, amount):
        inputs = []

        inpq = self.db.query("SELECT * FROM addresses WHERE spent=FALSE AND \
                             balance > 0 ORDER BY idx ASC")

        needed = amount
        for inp in inpq:
            needed -= inp.balance
            inputs.append(Address(inp.address, key_index=inp.idx,
                                  security_level=2, balance=inp.balance))

            if needed <= 0:
                break

        # do we have change?
        if needed < 0:
            chaddr = self.get_change_address()
        elif needed == 0:
            chaddr = None
        else:
            # not enough balance!
            return None

        return self.api.prepare_transfer([
            ProposedTransaction(Address(address), amount)
        ], inputs=inputs, change_address=chaddr)

    def _clear(self):
        self.db.query("DROP TABLE IF EXISTS transactions")
        self.db.query("DROP TABLE IF EXISTS addresses")

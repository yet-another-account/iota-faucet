from unittest import TestCase
from iota_faucet.db.database import FaucetDB
from iota import Iota

from iota_faucet import config


class AddressGeneration(TestCase):
    def test_gen_addr(self):
        db = FaucetDB("mysql://root:abc123@localhost:3306/test",
                      Iota('http://node.lukaseder.de:14265',
                           seed='A' * 81))

        db.gen_addrs()
        self.assertEqual(db.num_addrs(), config.ADDR_BATCH)
        db.gen_addrs()
        self.assertEqual(db.num_addrs(), 2 * config.ADDR_BATCH)

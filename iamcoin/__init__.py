import logging
import sys
import os

from . import block
from . import blockchain
from . import p2p
from . import transaction
from . import wallet
from . import transact_pool

LOG_DIR = "/var/log/iamcoin.log" if  len(sys.argv) == 1 else "/var/log/iamcoin-replica.log"
PORT = 5000 if len(sys.argv) == 1 else sys.argv[1]
PK_LOC = os.path.expanduser("~/iamcoin/private_key") if len(sys.argv) == 1  else \
         os.path.expanduser("~/iamcoin/private_replica_key")


logging.basicConfig(format='[%(asctime)s] [%(threadName)s:%(name)s] [%(levelname)s] : %(message)s',
                    filename=LOG_DIR, level=logging.INFO)

log = logging.getLogger(__name__)

log.info("Let's roll the coin, shall we?")
log.info("Initializing genesis block")
blockchain.blockchain.append(block.get_genesis_block())
log.info("Initialized blockchain with genesis block")

log.info("Initializing wallet")
wallet.init_wallet()
log.info("Wallet initialized")
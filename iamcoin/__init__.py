import logging

from . import block
from . import blockchain
from . import p2p
from . import transaction
from . import wallet


logging.basicConfig(format='[%(asctime)s] [%(threadName)s:%(name)s] [%(levelname)s] : %(message)s',
                    filename='/var/log/iamcoin.log', level=logging.INFO)

log = logging.getLogger(__name__)

log.info("Let's roll the coin, shall we?")
log.info("Initializing genesis block")
blockchain.blockchain.append(block.get_genesis_block())
log.info("Initialized blockchain with genesis block")

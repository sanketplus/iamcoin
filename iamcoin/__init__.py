import logging

from block import *
from blockchain import *

logging.basicConfig(format='[%(asctime)s] [%(threadName)s:%(name)s] [%(levelname)s] : %(message)s',filename='/var/log/iamcoin.log',
                    level=logging.INFO)

log = logging.getLogger(__name__)

log.info("Let's roll the coin, shall we?")
log.info("Initializing genesis block")
blockchain.append( block.get_genesis_block() )
log.info("Initialized blockchain with genesis block")
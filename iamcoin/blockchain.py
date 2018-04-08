import logging

from . import block
from . import transaction
from . import transact_pool
from . import p2p

log = logging.getLogger(__name__)

blockchain = [ ]
utxo = []


def get_blockchain():
    return blockchain


def is_valid_chain(chain):
    """

    :param chain: current blockchain
    :return:
    """
    log.info("Checking if chain is valid.")
    if str(chain[0]) != str(blockchain[0]):
        log.info("It was not valid")
        return False

    a_utxo = []

    for i in range(1,len(chain)):
        cur_block = chain[i]
        if not block.is_valid_block(chain[i],chain[i-1]):
            log.info("It was not valid")
            return False

        a_utxo = transaction.process_transactions(cur_block.data, a_utxo, cur_block.index)

        if not a_utxo:
            log.error("Not a valid block in chain")
            return False


    log.info("It is valid")
    return a_utxo


async def replace_chain(new_chain):
    """
    if newly received chain is valid and longer than current one then replace current one
    :param new_chain:
    :return:
    """
    log.info("Replacing chain")
    global blockchain, utxo
    a_utxo = is_valid_chain(new_chain)
    valid_chain = True if a_utxo else False

    if valid_chain and len(new_chain) > len(get_blockchain()):
        log.info("New chain is valid and larger, replacing")
        blockchain = new_chain
        utxo = a_utxo
        transact_pool.update_transact_pool(utxo)
        await p2p.broadcast_latest()
    else:
        log.info("Not replacing")

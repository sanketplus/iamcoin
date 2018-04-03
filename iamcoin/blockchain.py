import logging

from . import block

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

    for i in range(1,len(chain)):
        if not block.is_valid_block(chain[i],chain[i-1]):
            log.info("It was not valid")
            return False

    log.info("It is valid")
    return True


def replace_chain(new_chain):
    """
    if newly received chain is valid and longer than current one then replace current one
    :param new_chain:
    :return:
    """
    log.info("Replacing chain")
    global blockchain
    if is_valid_chain(new_chain) and len(new_chain) > len(get_blockchain()):
        log.info("New chain is valid and larger, replacing")
        blockchain = new_chain
        # broadcast
    else:
        log.info("Not replacing")

import block

blockchain = [ ]

def get_blockchain():
    return blockchain


def is_valid_chain(chain):
    """

    :param chain: current blockchain
    :return:
    """
    if str(chain[0]) != str(blockchain[0]):
        return False

    for i in range(1,len(chain)):
        if not block.is_valid_block(chain[i],chain[i-1]):
            return False

    return True


def replace_chain(new_chain):
    global blockchain
    if is_valid_chain(new_chain) and len(new_chain) > len(get_blockchain()):
        blockchain = new_chain
        # broadcast
    else:
        pass

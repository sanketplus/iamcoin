import hashlib
import time
import blockchain


class Block(object):
    """
    The heart of iamcoin, stores 5 basic params. Data for now is string but later we may switch it to JSON
    """

    def __init__(self,index,hash,prev_hash,timestamp,data):
        self.index = index
        self.hash = hash
        self.prev_hash = prev_hash
        self.timestamp = timestamp
        self.data = data

    def __str__(self):
        return "%s%s%s%s%s" % (self.index, self.hash, self.prev_hash, self.timestamp, self.data)


def calculate_hash(index,prev_hash,timestamp,data):
    """
    concat the fields and calculates SHA256 of it.

    :param index: integer
    :param prev_hash: str
    :param timestamp: epoch timestamp
    :param data: str
    :return: hexdigest in form of string
    """
    str = "%s%s%s%s" % (index, prev_hash, timestamp, data)
    return hashlib.sha256(str).hexdigest()


def calculate_block_hash(block):
    return calculate_hash(block.index, block.prev_hash, block.timestamp, block.data)


def get_genesis_block():
    """
    hash of block is calculated 'by-hand', prev_hash is an empty string ''
    :return: Block object
    """
    return Block(0,'cf27a50a6d231c5482bb358a8be3c71d935c5a4826b55ebb5141cda7ea3afe38', None, 1522085107, "I AM COIN :D")


def generate_next_block(data):
    """
    Gets prev block info from last blockchain block and generates a new block

    :param data: data that would go into block
    :return:
    """
    latest_block = blockchain.blockchain[-1]
    next_index = latest_block.index + 1
    next_timestamp = int(time.time())
    next_hash = calculate_hash(next_index, latest_block.hash, next_timestamp, data)

    return Block(next_index, next_hash, latest_block.hash, next_timestamp, data)


def is_valid_block(block, pre_block):
    """

    :param block: block to be verified
    :param pre_block: previous block
    :return:
    """
    if block.index != pre_block.index + 1:
        return False
    elif pre_block.hash != block.prev_hash:
        return False
    elif calculate_block_hash(block) != block.hash:
        return False
    else:
        return True


def get_lastest_block():
    """
    :return: last block in blockchain
    """
    return  blockchain.blockchain[-1]


def add_block_to_blockchain(block):
    """
    Checks if block is valid and appends it to chain
    :param block:
    :return:
    """
    if is_valid_block(block, get_lastest_block()):
        blockchain.blockchain.append(block)
    else:
        pass
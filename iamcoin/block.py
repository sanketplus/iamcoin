import hashlib
import time
from . import blockchain
from . import transaction
from . import wallet
from . import p2p

import logging
import json

log = logging.getLogger(__name__)


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

    def to_json(self):
        """

        :return: json string of object
        """
        return {
                "index": self.index,
                "hash": self.hash,
                "prev_hash": self.prev_hash,
                "timestamp": self.timestamp,
                "data": [_.to_json() for _ in self.data]
                }


def generate_block_from_json(blk_json):
    """

    :param json_str: json str dump of Block
    :return: Block object
    """

    return Block(blk_json['index'],
                 blk_json['hash'],
                 blk_json['prev_hash'],
                 blk_json['timestamp'],
                 transaction.Transaction.from_json(blk_json["data"])
                 )


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
    return hashlib.sha256(bytes(str, encoding="UTF-8")).hexdigest()


def calculate_block_hash(block):
    log.info("Calculating block hash")
    return calculate_hash(block.index, block.prev_hash, block.timestamp, block.data)


def get_genesis_block():
    """
    hash of block is calculated 'by-hand', prev_hash is an empty string ''
    :return: Block object
    """
    log.info("Generating and returning genesis block.")
    return Block(0,'cf27a50a6d231c5482bb358a8be3c71d935c5a4826b55ebb5141cda7ea3afe38', None, 1522085107, [])


async def generate_raw_next_block(data):
    """
    Gets prev block info from last blockchain block and generates a new block

    :param data: data that would go into block
    :return:
    """
    log.info("Generating next/new block")
    latest_block = blockchain.blockchain[-1]
    next_index = latest_block.index + 1
    next_timestamp = int(time.time())
    # txs = [transaction.Transaction.from_json(_) for _ in data]
    txs = data
    next_hash = calculate_hash(next_index, latest_block.hash, next_timestamp, txs)

    new_blk = Block(next_index, next_hash, latest_block.hash, next_timestamp, txs)

    if add_block_to_blockchain(new_blk):
        await p2p.broadcast_latest()
        return new_blk
    else:
        return None


async def generate_next_block():
    """
    generates next block with coinbase transacttion
    :return:
    """
    coinbase_tx = transaction.get_coinbse_tx(wallet.get_pubkey_from_wallet(), get_latest_block().index+1)
    data = [coinbase_tx]
    return await generate_raw_next_block(data)


async def generate_next_block_with_tx(recv_addr, amount):
    """
    Generates block with coinbase and given tx
    :param recv_addr:
    :param amount:
    :return:
    """
    coinbase_tx = transaction.get_coinbse_tx(wallet.get_pubkey_from_wallet(), get_latest_block().index+1)
    tx = wallet.create_transaction(recv_addr, amount, wallet.get_pubkey_from_wallet(), blockchain.utxo)
    data = [coinbase_tx, tx]
    return await generate_raw_next_block(data)


def is_valid_block(block, pre_block):
    """

    :param block: block to be verified
    :param pre_block: previous block
    :return:
    """
    log.info("Checking if block is valid")
    if block.index != pre_block.index + 1:
        return False
    elif pre_block.hash != block.prev_hash:
        return False
    elif calculate_block_hash(block) != block.hash:
        return False
    else:
        log.info("Block is valid")
        return True


def get_latest_block():
    """
    :return: last block in blockchain
    """
    log.info("Returning latest block")
    return  blockchain.blockchain[-1]


def add_block_to_blockchain(block):
    """
    Checks if block is valid and appends it to chain
    :param block:
    :return:
    """
    log.info("Adding block to blockchain")
    if is_valid_block(block, get_latest_block()):
        new_utxo = transaction.process_transactions(block.data, blockchain.utxo, block.index)
        if new_utxo:
            blockchain.utxo = new_utxo
            blockchain.blockchain.append(block)
            log.info("Block was valid and added to chain")
            return True
    else:
        log.info("Block was not added to chain")
        return False
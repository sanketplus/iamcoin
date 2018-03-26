import hashlib
import time


class Block(object):

    def __init__(self,index,hash,prev_hash,timestamp,data):
        self.index = index
        self.hash = hash
        self.prev_hash = prev_hash
        self.timestamp = timestamp
        self.data = data


def calculate_block_hash(index,prev_hash,timestamp,data):
    str = "%s%s%s%s" % (index, prev_hash, timestamp, data)
    return hashlib.sha256(str).hexdigest()


def get_genesis_block():
    return Block(0,'cf27a50a6d231c5482bb358a8be3c71d935c5a4826b55ebb5141cda7ea3afe38', None, 1522085107, "I AM COIN :D")


def get_next_block(data):
    latest_block = blockchain[-1]
    next_index = latest_block.index + 1
    next_timestamp = int(time.time())
    next_hash = calculate_block_hash(next_index, latest_block.hash, next_timestamp, data)

    return Block(next_index, next_hash, latest_block.hash, next_timestamp, data)

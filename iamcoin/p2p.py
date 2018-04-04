import logging
import json


from . import block
from . import blockchain
# from .block import get_latest_block, generate_block_from_json, add_block_to_blockchain, is_valid_block
# from .blockchain import blockchain, replace_chain
from aiohttp import web

log = logging.getLogger(__name__)
peers = {}


class msg_type(object):
    QUERY_LATEST = 0
    QUERY_ALL = 1
    RESPONSE_BLOCKCHAIN = 2


class msg(object):
    def __init__(self, type, data):
        self.type = type
        self.data = data

    def to_json(self):
        return json.dumps({
            "type": self.type,
            "data": self.data
        })

# msg object to query all block
query_all_msg = msg(msg_type.QUERY_ALL, data=None).to_json()

# msg object to query latest block
query_latest_msg = msg(msg_type.QUERY_LATEST, data=None).to_json()


def get_msg_from_json(json_str):
    msg_json = json.loads(json_str)
    return msg(msg_json['type'], msg_json['data'])


def resp_latest_message():
    """

    :return: msg object with lastest block-json as data
    """
    log.info("Generating latest block response json")
    return msg(msg_type.RESPONSE_BLOCKCHAIN,
               [ block.get_latest_block().to_json() ]
               ).to_json()


def resp_chain_message():
    """

    :return: msg object with list if json-blocks as data
    """
    log.info("Generating blockchain response json")
    return msg(msg_type.RESPONSE_BLOCKCHAIN,
               [b.to_json() for b in blockchain.blockchain]
               ).to_json()



async def handle_blockchain_resp(new_chain):
    if len(new_chain) == 0:
        log.info("New received chain len is 0")
        return

    our_last_blk = block.get_latest_block()
    got_last_blk = new_chain[-1]

    # if more blocks in new chain
    if our_last_blk.index < got_last_blk.index:
        log.info("Got new chain with len: {}, ours is: {}".format(len(new_chain), len(blockchain.blockchain)))

        if our_last_blk.hash == got_last_blk.prev_hash:
            log.info("We were one block behind, adding new block")
            block.add_block_to_blockchain(got_last_blk)
            await broadcast_latest()
        elif len(new_chain) == 1:
            log.info("Got just one block. gonna query whole chain")
            await broadcast( query_all_msg )
        else:
            log.info("Received longer chain, replacing")
            blockchain.replace_chain(new_chain)
    else:
        log.info("Shorter blockchain received, do nothing")


async def handle_peer_msg(key, ws):
    async for ws_msg in ws:
        if ws_msg.type == web.WSMsgType.text:
            msg_data = ws_msg.data
            log.info("Got message: {}".format(msg_data))
            recv_msg = get_msg_from_json(msg_data)

            # responding according to message types
            if recv_msg.type == msg_type.QUERY_LATEST:
                await ws.send_str( resp_latest_message() )

            elif recv_msg.type == msg_type.QUERY_ALL:
                await ws.send_str( resp_chain_message() )

            elif recv_msg.type == msg_type.RESPONSE_BLOCKCHAIN:
                new_chain = [ block.generate_block_from_json(b) for b in recv_msg.data ]
                await handle_blockchain_resp(new_chain)

        elif ws_msg.type == web.WSMsgType.binary:
            log.info("Binary message; ignoring...")
        elif ws_msg.type in [web.WSMsgType.close, web.WSMsgType.error]:
            log.info("WS close or err: closing connection")
            peers[key].close()
            del peers[key]


async def broadcast(data):
    log.info(data)
    for p in peers:
        await peers[p].send_str(data)


async def broadcast_latest():
    log.info("Broadcasting latest block")
    data = resp_latest_message()
    await broadcast(data)
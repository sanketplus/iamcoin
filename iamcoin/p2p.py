import logging
import json


from .block import get_lastest_block
from aiohttp import web

log = logging.getLogger(__name__)
peers = {}


class msg_type(object):
    QUERY_LATEST = 0,
    QUERY_ALL = 1,
    RESPONSE_BLOCKCHAIN = 2,


class msg(object):
    def __init__(self, type, data):
        self.type = type
        self.data = data

    def to_json(self):
        return json.dumps({
            "type": self.type,
            "data": self.data
        })


def get_msg_from_json(json_str):
    msg_json = json.loads(json_str)
    return msg(msg_json['type'], msg_json['data'])


def resp_latest_message():
    log.info("Generating latest block response json")
    return msg(msg_type.RESPONSE_BLOCKCHAIN,
               get_lastest_block().to_json()
               ).to_json()

async def handle_peer_msg(key, ws):
    async for msg in ws:
        if msg.type == web.WSMsgType.text:
            log.info("Got message: {}".format(msg.data))
            # await ws.send_str("Did you just say, {}".format(msg.data))
        elif msg.type == web.WSMsgType.binary:
            await ws.send_bytes(msg.data)
        elif msg.type in [web.WSMsgType.close, web.WSMsgType.error]:
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
import iamcoin
import logging

from aiohttp import web,ClientSession
from .p2p import peers, handle_peer_msg

log = logging.getLogger(__name__)


async def api_get_block_count(request):
    log.info("Get block count API request.")
    return web.Response(text=str({'count': len(iamcoin.blockchain)}),content_type='application/json')


async def api_add_block(request):

    data = await request.post()

    if request.method == "POST":
        block = iamcoin.generate_next_block(data.get('data'))
        iamcoin.add_block_to_blockchain(block)
    return web.json_response({"response": "success!"})


async def api_add_peer(request):

    data = await request.post()

    if request.method == "POST":
        peer_addr = data.get('peer')
        session = ClientSession()
        async with session.ws_connect(peer_addr) as ws:
            peers.append(ws)
            await ws.send_str("Hello mofo")
            await handle_peer_msg(ws)
    return web.json_response({"response": "success!"})


async def wshandle(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    log.info("Incoming WS connection...")
    peers.append(ws)
    await handle_peer_msg(ws)

    return ws


app = web.Application(logger=log)
app.add_routes([web.get('/blockcount', api_get_block_count),
                web.post("/addblock", api_add_block),
                web.post("/addpeer", api_add_peer),
                web.get('/ws', wshandle)])

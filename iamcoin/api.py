import iamcoin
import logging
import asyncio

from aiohttp import web,ClientSession
from .p2p import peers, handle_peer_msg, broadcast_latest

log = logging.getLogger(__name__)


async def api_get_block_count(request):
    log.info("Get block count API request.")
    return web.Response(text=str({'count': len(iamcoin.blockchain.blockchain)}),content_type='application/json')


async def api_get_peers(request):
    resp=[]
    for p in peers.keys():
        resp.append(p)

    return web.json_response({"peers":resp})


async def api_add_block(request):

    data = await request.post()

    if request.method == "POST":
        block = iamcoin.block.generate_next_block(data.get('data'))
        iamcoin.block.add_block_to_blockchain(block)
        await broadcast_latest()
    return web.json_response({"response": "success!"})


async def api_add_peer(request):

    data = await request.post()

    if request.method == "POST":
        peer_addr = data.get('peer')
        log.info("Adding peer: {}".format(peer_addr))
        loop.create_task(add_peer(peer_addr))
        return web.json_response({"response": "success!"})


async def add_peer(peer_addr):
    async  with ClientSession() as session:
        async with session.ws_connect(peer_addr) as ws:
            log.info("{}".format(ws.get_extra_info('peername')))
            key = ws.get_extra_info('peername')[0]
            peers[key] = ws
            log.info("Added peer.")
            await handle_peer_msg(key,ws)
    # except Exception:
    #     session.close()
    log.info("Closing and Removing peer: {}".format(peer_addr))
    await peers[key].close()
    del peers[key]
    log.info("Removed peer {}".format(peer_addr))


async def wshandle(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    log.info("Incoming WS connection...")
    key = request.transport.get_extra_info('peername')[0]
    peers[key]=ws
    await handle_peer_msg(key, ws)
    log.info("Incoming is in...")
    return ws


app = web.Application(logger=log)
app.add_routes([web.get('/blockcount', api_get_block_count),
                web.post("/addblock", api_add_block),
                web.post("/addpeer", api_add_peer),
                web.get("/peers", api_get_peers),
                web.get('/ws', wshandle)])


loop = asyncio.get_event_loop()
handler = app.make_handler()
server = loop.create_server(handler, "0.0.0.0", 5000)
loop.run_until_complete(server)
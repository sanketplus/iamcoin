import iamcoin
import logging

from aiohttp import web


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



async def wshandle(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == web.WSMsgType.text:
            await ws.send_str("Hello, {}".format(msg.data))
        elif msg.type == web.WSMsgType.binary:
            await ws.send_bytes(msg.data)
        elif msg.type == web.WSMsgType.close:
            break

    return ws


app = web.Application(logger=log)
app.add_routes([web.get('/blockcount', api_get_block_count),
                web.post("/addblock", api_add_block),
                web.get('/echo', wshandle)])

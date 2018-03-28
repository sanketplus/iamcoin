import flask
import blockchain
import logging

log = logging.getLogger(__name__)
app= flask.Flask('iamcoin')

@app.route('/blockcount')
def api_get_block_count():
    log.info("Get block count API request.")
    return flask.jsonify({'count': len(blockchain.blockchain)})
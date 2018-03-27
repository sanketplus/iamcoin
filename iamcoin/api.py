import flask
import blockchain

app= flask.Flask('iamcoin')

@app.route('/blockcount')
def api_get_block_count():
    return flask.jsonify({'count': len(blockchain.blockchain)})
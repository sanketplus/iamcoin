from flask import Flask, request, jsonify
import iamcoin
import logging

log = logging.getLogger(__name__)
app= Flask('iamcoin')

@app.route('/blockcount')
def api_get_block_count():
    log.info("Get block count API request.")
    return jsonify({'count': len(iamcoin.blockchain)})

@app.route("/addblock",methods=["POST"])
def api_add_block():
    if request.method == "POST":
        block = iamcoin.generate_next_block(request.data)
        iamcoin.add_block_to_blockchain(block)
    return jsonify({"response": "success!"})
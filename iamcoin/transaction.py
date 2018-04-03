import hashlib
import logging
import ecdsa


log = logging.getLogger(__name__)
COINBASE_AMT = 100


class Utxo(object):
    def __init__(self, txout_id, txout_index, address, amount):
        self.txout_id = txout_id
        self.txout_index = txout_index
        self.address = address
        self.amount = amount


class TxIn(object):
    def __init__(self, txout_id, txout_index, signature):
        self.txout_id = txout_id
        self.txout_index = txout_index
        self.signature = signature

    def __str__(self):
        return "{}{}{}".format(self.txout_id, self.txout_index, self.signature)

    def to_json(self):
        return {"txout_id": self.txout_id,
                "txout_index": self.txout_index,
                "signature": self.signature
                }

    @staticmethod
    def from_json(j):
        return TxIn(j["txout_id"], j["txout_index"], j["signature"])


class TxOut(object):
    def __init__(self, address, amount):
        self.address = address
        self.amount = amount

    def __str__(self):
        return "{}{}".format(self.address, self.amount)

    def to_json(self):
        return {"address": self.address,
                "amount": self.amount
                }

    @staticmethod
    def from_json(j):
        return TxOut(j['address'], j['amount'])


class Transaction(object):
    def __init__(self, id, txins, txouts):
        self.id = id
        self.txins = txins
        self.txouts = txouts

    def __str__(self):
        tx_str = "{}".format(self.id)
        for t in self.txins:
            tx_str += t

        for r in self.txouts:
            tx_str += t

        return tx_str

    def to_json(self):
        return {"id": self.id,
                "txins": [t.to_json() for t in self.txins],
                "txouts": [t.to_json() for t in self.txouts]
                }

    @staticmethod
    def from_json(j):
        return Transaction(j["id"],
                           [TxIn.from_json(_) for _ in j["txins"]],
                           [TxOut.from_json(_) for _ in j["txouts"]]
                           )


def get_transaction_id(tx):
    log.info("Generating tx id")
    txin_context = ""
    for t in tx.txins:
        txin_context += "{}{}".format(t.txout_id, t.txout_index)

    txout_content = ""
    for t in tx.txouts:
        txout_content += "{}{}".format(t.address, t.amount)

    return hashlib.sha256(bytes(txin_context+txout_content, encoding="UTF-8")).hexdigest()


def validate_transaction(tx, utxos):
    log.info("Validating tx")

    if tx.id != get_transaction_id(tx):
        log.info("Tx id not valid")
        return False

    for t in tx.txins:
        if not is_valid_txin(t):
            log.info("Not a valid In Tx")
            return False

    txin_amount = 0
    for t in tx.txins:
        txin_amount += get_txin_amt(t, utxos)

    txout_amount = 0
    for t in tx.txouts:
        txout_amount += t.amount

    if txin_amount != txout_amount:
        log.info("in amt != out amt")
        return False

    return True


def validate_block_transactions(txs, utxos, block_index):
    coinbase_tx = txs[0]
    if not is_valid_coinbase_tx(coinbase_tx, block_index):
        log.info("Invalid coinbase tx")
        return False

    txout_ids=[]
    for t in txs:
        txout_ids.extend(t.txins)

    if len(txout_ids) != len(set(txout_ids)):
        log.info("Same txin multiple times")
        return False

    for t in txs[1:]:
        if not validate_transaction(t):
            log.info("Invalid tx detected")
            return False

    return True


def is_valid_coinbase_tx(tx, index):
    log.info("Validating coinbase tx")

    if tx == None:
        log.info("the first transaction in the block must be coinbase transaction")
        return False

    if get_transaction_id(tx) != tx.id:
        log.info("Tx id do not match: {} :: {}".format(get_transaction_id(tx), tx.id))
        return False

    if len(tx.txins) != 1:
        log.info("One txin must be sepcified in coinbase tx")

    if len(tx.txouts) != 1:
        log.info("One txout must be sepcified in coinbase tx")
        return False

    if tx.txouts[0].amount != COINBASE_AMT:
        log.info("Coinbase tx amount does not match")
        return False

    return True


def is_valid_txin(txin, tx, utxos):
    ref_utxo = None
    for t in utxos:
        if t.txout_id == txin.txout_id and t.txout_index == txin.txout_index:
            ref_utxo = t

    if ref_utxo == None:
        log.info("Ref utxo not found")
        return False

    address = ref_utxo.address

    key = ecdsa.VerifyingKey.from_string(address, ecdsa.SECP256k1)
    return key.verify(txin.signature, tx.id)


def get_txin_amt(txin, utxos):
    return find_utxo(txin.txout_id, txin.txout_index, utxos).amount


def find_utxo(tid, index, utxos):
    for t in utxos:
        if t.txout_id == tid and t.txout_index == index:
            return t

def get_coinbse_tx(address, index):
    log.info("Generating coinbase tx")
    txin = TxIn("", index, "")
    txout = TxOut(address,COINBASE_AMT)
    t= Transaction("", [txin], [txout])
    t.id = get_transaction_id(t)
    t = Transaction()

    return t


def sign_tx(tx, txin_index, pk, utxos):
    log.info("Signing tx")
    txin = tx.txins[txin_index]
    data = tx.id
    ref_utxo = find_utxo(txin.id, txin.txout_index, utxos)

    if not ref_utxo:
        log.info("Could not find ref utxo")
        raise

    address = ref_utxo.address

    if get_public_key(pk) != address:
        log.info("Trying to sign tx with pk that does not match with pubkey of txin")
        raise

    key = ecdsa.VerifyingKey.from_string(pk, curve=ecdsa.SECP256k1)
    signature = key.sign(data).hex()

    return signature


def update_utxos(txs, utxos):
    new_utxo = []
    for tx in txs:
        for index,t in enumerate(tx.txouts):
            new_utxo.append(Utxo(tx.id, index, t.address, t.amount))

    used_utxo = []
    for tx in txs:
        for t in tx.txins:
            used_utxo.append(Utxo(t.txout_id, t.txout_index, '', 0))

    result_utxo = [t for t in utxos if not find_utxo(t.txout_id, t.txout_index, used_utxo) ]
    result_utxo.extend(new_utxo)

    return result_utxo


def process_transactions(txs, utxos, block_index):
    if not validate_block_transactions(txs, utxos, block_index):
        log.info("txs not valid in block")
        return

    return update_utxos(txs, utxos)


def get_public_key(pk):
    return ecdsa.SigningKey.from_string(pk, curve=ecdsa.SECP256k1).get_verifying_key()



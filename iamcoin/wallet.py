import ecdsa
import binascii
import os
import logging
import iamcoin

from . import transaction
from . import blockchain
from . import transact_pool
from . import p2p


PK_LOCATION = None
log = logging.getLogger(__name__)


def get_pk_from_wallet():
    """
    Read the pk file and returns contents as-is
    :return:
    """
    with open(PK_LOCATION) as f:
        return bytes(''.join(f.readlines()), encoding="utf-8")


def get_pubkey_from_wallet():
    """
    Reads private key from file and makes an Signkey object.
    Gets a public key from that object and return hexlified version of it
    :return:
    """
    kp = ecdsa.SigningKey.from_pem(get_pk_from_wallet())
    pub_key = kp.get_verifying_key().to_string().hex()

    return pub_key


def generate_pk():
    """
    Generates pk and return PEM version of it

    :return:
    """
    kp = ecdsa.SigningKey.generate()
    pk = kp.to_pem()
    return pk


def init_wallet():
    """
    If pk files does not exist, creates one and writes it to file (in PEM format)

    :return:
    """
    global PK_LOCATION
    PK_LOCATION = iamcoin.PK_LOC
    if os.path.isfile(PK_LOCATION):
        return

    new_pk = generate_pk()

    key_dir = "/".join(os.path.expanduser(PK_LOCATION).split("/")[:-1])
    if not os.path.isdir(key_dir):
        os.mkdir(key_dir)

    with open(PK_LOCATION, "w") as f:
        f.write(new_pk.decode())
    log.info("Initialized new wallet with a private key")


def get_balance(address, utxos):
    """
    Traverses utxos and sum amount for given address

    :param address:
    :param utxos:
    :return:
    """
    amt = 0
    for t in utxos:
        if t.address == address:
            amt += t.amount
    return amt


def get_account_balance():
    return get_balance(get_pubkey_from_wallet(), blockchain.utxo)


def find_txouts_for_amt(amount, my_utxos):
    """
    A wallet/address can have coins from multiple inputs, returns a list of those inputs for spending X number of coins
    Also returns what is the remaining balance

    :param amount:
    :param my_utxos:
    :return:
    """

    cur_amt = 0
    included_txout = []

    for t in my_utxos:
        included_txout.append(t)
        cur_amt += t.amount
        if cur_amt > amount:
            left_amt = cur_amt - amount
            return(included_txout, left_amt)

    log.error("Not enough coins to send")
    raise Exception


def create_txouts(recv_addr, my_addr, amount, left_amt):
    """
    create txout objects, one to the dest address and one to self if there is leftover amt

    :param recv_addr:
    :param my_addr:
    :param amount:
    :param left_amt:
    :return:
    """

    txout1 = transaction.TxOut(recv_addr, amount)

    if left_amt == 0:
        return [txout1]
    else:
        leftover_tx = transaction.TxOut(my_addr, left_amt)
        return [txout1, leftover_tx]


def filter_txpool_txs(utxo, pool):
    txins = []
    for tx in pool:
        txins.extend(tx.txins)

    removable = []

    for utx in utxo:
        for tin in txins:
            if tin.txout_index == utx.txout_index and tin.txout_id == utx.txout_id:
                removable.append(utx)
                break

    return [t for t in utxo if t not in removable]


def create_transaction(recv_addr, amount, pk, utxos, pool):
    """

    :param recv_addr:
    :param amount:
    :param pk:
    :param utxos:
    :return:
    """

    my_addr = transaction.get_public_key(pk)

    my_utxos_a = [t for t in utxos if t.address == my_addr]

    my_utxos = filter_txpool_txs(my_utxos_a, pool)

    included_txout, left_amt = find_txouts_for_amt(amount, my_utxos)

    def to_tx_unsigned(utxo):
        return transaction.TxIn(utxo.txout_id, utxo.txout_index, "")

    unsigned_txins = [to_tx_unsigned(t) for t in included_txout]

    # creating final transaction with TxIn as txout of my address and txout which we got from function call
    tx = transaction.Transaction("", unsigned_txins, create_txouts(recv_addr, my_addr, amount, left_amt))

    # setting txid
    tx.id = transaction.get_transaction_id(tx)

    # signing tx's txins
    # tx.txins = [transaction.sign_tx(tx, index, pk, utxos) for index, t in enumerate(tx.txins)]
    singned_txins = []
    for index, t in enumerate(tx.txins):
        sign = transaction.sign_tx(tx, index, pk, utxos)
        t.signature = sign
        singned_txins.append(t)

    tx.txins = singned_txins

    return tx



async def send_transaction(data):
    try:
        tx = create_transaction(data["address"], data["amount"], get_pk_from_wallet(), blockchain.utxo, transact_pool.transact_pool)
        transact_pool.add_to_transact_pool(tx, blockchain.utxo)
        await p2p.broadcast_txpool()
        return True
    except Exception:
        return False
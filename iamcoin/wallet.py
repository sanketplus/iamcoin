import ecdsa
import binascii
import os
import logging

from . import transaction


PK_LOCATION = "~/iamcoin/private_key"
log = logging.getLogger(__name__)


def get_pk_from_wallet():
    """
    Read the pk file and returns contents as-is
    :return:
    """
    with open(PK_LOCATION) as f:
        return f.read()


def get_pubkey_from_wallet():
    """
    Reads private key from file and makes an Signkey object.
    Gets a public key from that object and return hexlified version of it
    :return:
    """
    kp = ecdsa.SigningKey.from_pem(get_pk_from_wallet())
    pub_key = kp.get_verifying_key().to_string()

    return binascii.hexlify(pub_key)


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
    if os.path.isfile(PK_LOCATION):
        return

    new_pk = generate_pk()
    with open(PK_LOCATION, "w") as f:
        f.write(new_pk)
    log.info("Initialized new wallet with a private key")


def get_balance(address, utxos):
    """
    Traverses utxos and sum amount for given address

    :param address:
    :param utxos:
    :return:
    """
    amt=0
    for t in utxos:
        if t.address == address:
            amt += t.amount
    return amt


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
            return (included_txout, left_amt)

    log.error("Not enough coins to send")
    raise


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


def create_transaction(recv_addr, amount, pk, utxos):
    """

    :param recv_addr:
    :param amount:
    :param pk:
    :param utxos:
    :return:
    """

    my_addr = transaction.get_public_key(pk)
    my_addr_hex = binascii.hexlify(my_addr.to_string())

    my_utxos = [t for t in utxos if t.address == my_addr_hex]

    included_txout, left_amt = find_txouts_for_amt(amount, my_utxos)

    def to_tx_unsigned(utxo):
        return transaction.TxIn(utxo.txout_id, utxo.txout_index, "")

    unsigned_txins = [to_tx_unsigned(t) for t in included_txout]

    # creating final transaction with TxIn as txout of my address and txout which we got from function call
    tx = transaction.Transaction("",unsigned_txins, create_txouts(recv_addr, my_addr, amount, left_amt))

    #setting txid
    tx.id = transaction.get_transaction_id(tx)

    #signing tx's txins
    tx.txins = [transaction.sign_tx(t, index, pk, utxos) for t in enumerate(tx.txins)]

    return tx

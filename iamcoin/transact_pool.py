import copy
import logging

from . import transaction

transact_pool = []
log = logging.getLogger(__name__)


def get_transact_pool():
    """

    :return: Deep copy of transact pool list
    """
    return copy.deepcopy(transact_pool)


def add_to_transact_pool(tx, utxos):
    """
    Checks if tx it self is valid and if it is valid for pool to be included in

    :param tx: transact to be added
    :param utxos:
    :return: nothing, raises Exception
    """

    log.info("Adding transaction to pool")

    if not transaction.validate_transaction(tx, utxos):
        log.error("Not a valid transaction")
        raise Exception

    if not is_valid_tx_for_pool(tx, transact_pool):
        log.error("Not valid tx to be included in pool")
        raise Exception

    transact_pool.append(tx)
    log.info("Tx added to pool")


def has_txin(tx, utxos):
    """
    True if tx is in utxo, else false.

    :param tx:
    :param utxos:
    :return:
    """
    for t in utxos:
        if t.txout_id == tx.txout_id and t.txout_index == tx.txout_index:
            return True

    return False


def update_transact_pool(utxo):

    log.info("Updating transaction pool")
    global transact_pool
    invalid_tx = []

    for tx in transact_pool:
        for tin in tx.txins:
            if not has_txin(tin, utxo):
                invalid_tx.append(tx)

    if len(invalid_tx)>0:
        transact_pool = [t for t in transact_pool if t not in invalid_tx]


def get_txpool_ins(pool):
    ins = []
    for t in pool:
        ins.extend(t.txins)
    return ins


def is_valid_tx_for_pool(tx, pool):

    log.info("Checking if given tx can be included in pool")
    txpool_ins = get_txpool_ins(pool)
    # def has_tx(tx, pool):
    #     for txx in pool:
    #         for t in txx.txins:
    #             if t.txout_id == tx.txout_id and t.txout_index == tx.txout_index:


    for tin in tx.txins:
        if has_txin(tin, txpool_ins):
            log.error("Txin of given tx alreday found in pool")
            return False

    log.info("It can be included in pool")
    return True

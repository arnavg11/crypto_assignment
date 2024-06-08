import os
import json
import hashlib
import time

VERSION = 1
PREV_BLOCK_HASH = "0000111100000000000000000000000000000000000000000000000000000000"
DIFFICULTY_TARGET = "0000ffff00000000000000000000000000000000000000000000000000000000"
COINBASE_TX = {
    "txid": "coinbase",
    "vout": 50,
    "prevout": 0
}

def readTransactions(mempool_folder):
    transactions = []
    for filename in os.listdir(mempool_folder):
        if filename.endswith('.json'):
            with open(os.path.join(mempool_folder, filename), 'r') as file:
                transactions.append(json.load(file))
    return transactions

def validateTransaction(tx):
    return tx["vin"][0]['txid'] and tx["vin"][0]['prevout']["value"] > tx["vin"][0]['vout']

def getMerkleRoot(txids):
    if len(txids) == 1:
        return txids[0]
    new_txids = []
    for i in range(0, len(txids), 2):
        left = txids[i]
        right = txids[i + 1] if i + 1 < len(txids) else left
        new_txids.append(hashlib.sha256((left + right).encode('utf-8')).hexdigest())
    return getMerkleRoot(new_txids)

def hashBlock(header):
    return hashlib.sha256(header.encode('utf-8')).hexdigest()

def mineBlock(header):
    nonce = 0
    while True:
        header_with_nonce = header + str(nonce)
        block_hash = hashBlock(header_with_nonce)
        if block_hash < DIFFICULTY_TARGET:
            return nonce, block_hash
        nonce += 1

transactions = readTransactions("mempool")
valid_txs = [tx for tx in transactions if validateTransaction(tx)]
txids = [tx["vin"][0]['txid'] for tx in valid_txs]
merkle_root_hash = getMerkleRoot(txids)
timestamp = int(time.time())
block_header = f"{VERSION}{PREV_BLOCK_HASH}{merkle_root_hash}{timestamp}{DIFFICULTY_TARGET}"

nonce, block_hash = mineBlock(block_header)

with open('output.txt', 'w') as file:
        file.write(f"{VERSION}\n")
        file.write(f"{PREV_BLOCK_HASH}\n")
        file.write(f"{merkle_root_hash}\n")
        file.write(f"{timestamp}\n")
        file.write(f"{DIFFICULTY_TARGET}\n")
        file.write(f"{nonce}\n")
        file.write(json.dumps(COINBASE_TX) + '\n')
        for txid in txids:
            file.write(txid + '\n')

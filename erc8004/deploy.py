#!/usr/bin/env python3
"""
ERC-8004 Deployment Script
Deploys MediatorCanonizerRegistry to Base
Operator: 0xeb65c54ee09AAc48612Dc77e6d106005547dF67A
"""

import json
import os
from web3 import Web3

# Base mainnet
BASE_RPC = "https://mainnet.base.org"
OPERATOR = "0xeb65c54ee09AAc48612Dc77e6d106005547dF67A"

# ABI for the registry contract
ABI = [
    {"inputs": [], "stateMutability": "nonpayable", "type": "constructor"},
    {"inputs": [{"name": "domain", "type": "string"}, {"name": "status", "type": "string"}, {"name": "hash", "type": "bytes32"}, {"name": "cite_as", "type": "string"}], "name": "registerArtifact", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "hash", "type": "bytes32"}], "name": "verify", "outputs": [{"name": "exists", "type": "bool"}, {"name": "domain", "type": "string"}, {"name": "status", "type": "string"}, {"name": "timestamp", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "totalArtifacts", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "operator", "outputs": [{"name": "", "type": "address"}], "stateMutability": "view", "type": "function"},
    {"anonymous": False, "inputs": [{"indexed": True, "name": "hash", "type": "bytes32"}, {"name": "domain", "type": "string"}, {"name": "status", "type": "string"}, {"name": "timestamp", "type": "uint256"}, {"name": "cite_as", "type": "string"}], "name": "ArtifactFrozen", "type": "event"}
]

def connect():
    w3 = Web3(Web3.HTTPProvider(BASE_RPC))
    if w3.is_connected():
        print(f"Connected to Base mainnet")
        print(f"Operator: {OPERATOR}")
        bal = w3.eth.get_balance(OPERATOR)
        print(f"Balance: {w3.from_wei(bal, 'ether'):.6f} ETH")
    else:
        print("Failed to connect to Base")
    return w3

def register_artifact(w3, contract_address, private_key, domain, status, hash_hex, cite_as):
    contract = w3.eth.contract(address=contract_address, abi=ABI)
    hash_bytes = bytes.fromhex(hash_hex.replace("0x", ""))
    tx = contract.functions.registerArtifact(domain, status, hash_bytes, cite_as).build_transaction({
        "from": OPERATOR,
        "nonce": w3.eth.get_transaction_count(OPERATOR),
        "gas": 200000,
        "gasPrice": w3.eth.gas_price,
    })
    signed = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"TX: {tx_hash.hex()}")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Confirmed in block: {receipt.blockNumber}")
    return receipt

if __name__ == "__main__":
    w3 = connect()

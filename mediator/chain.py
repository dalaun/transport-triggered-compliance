import os
from web3 import Web3

CONTRACT_ADDRESS = "0xf2325531264CA4Fc2cEC5D661E2200eA8013b091"
BASE_RPC = "https://mainnet.base.org"

ABI = [
    {"inputs": [{"name": "domain", "type": "string"}, {"name": "status", "type": "string"}, {"name": "hash", "type": "bytes32"}, {"name": "cite_as", "type": "string"}], "name": "registerArtifact", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "hash", "type": "bytes32"}], "name": "verify", "outputs": [{"name": "exists", "type": "bool"}, {"name": "domain", "type": "string"}, {"name": "status", "type": "string"}, {"name": "timestamp", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "totalArtifacts", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
]

def register_on_chain(domain, status, hash_hex, cite_as, private_key):
    try:
        w3 = Web3(Web3.HTTPProvider(BASE_RPC))
        if not w3.is_connected():
            print("Chain registration skipped: not connected to Base")
            return None
        account = w3.eth.account.from_key(private_key)
        contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)
        hash_bytes = bytes.fromhex(hash_hex.replace("0x", ""))
        tx = contract.functions.registerArtifact(domain, status, hash_bytes, cite_as).build_transaction({
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gas": 200000,
            "gasPrice": w3.eth.gas_price,
        })
        signed = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return {
            "tx": tx_hash.hex(),
            "block": receipt.blockNumber,
            "contract": CONTRACT_ADDRESS,
            "basescan": f"https://basescan.org/tx/{tx_hash.hex()}"
        }
    except Exception as e:
        print(f"Chain registration error: {e}")
        return None

def verify_on_chain(hash_hex):
    try:
        w3 = Web3(Web3.HTTPProvider(BASE_RPC))
        contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)
        hash_bytes = bytes.fromhex(hash_hex.replace("0x", ""))
        exists, domain, status, timestamp = contract.functions.verify(hash_bytes).call()
        return {"exists": exists, "domain": domain, "status": status, "timestamp": timestamp}
    except Exception as e:
        return {"exists": False, "error": str(e)}

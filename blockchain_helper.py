"""
blockchain_helper.py
=====================
This module is the communication bridge between the Flask application
and the Ethereum-compatible blockchain (Remix IDE / Hardhat / Ganache).

It calls the functions on the HealthcareRecord smart contract:
    - storeHash(patientId, recordHash)  -> writes hash + timestamp + caller address
    - getHash(patientId)                -> reads back the stored hash
    - getRecordDetails(patientId)       -> reads hash, timestamp, and caller address
    - hasHash(patientId)                -> checks whether an ID exists on-chain

Supported Environments:
    1. Remix IDE (via Dev - Hardhat Provider or Localhost RPC: http://127.0.0.1:8545)
    2. Local Hardhat node (started with: npx hardhat node)
    3. Ganache / Custom RPC testnets
"""

import json
import os
from web3 import Web3

# ------------------------------------------------------------
# RPC Endpoint for local blockchain (Hardhat, Ganache, or Remix Local Node)
# ------------------------------------------------------------
RPC_URL = os.environ.get("BLOCKCHAIN_RPC_URL", "http://127.0.0.1:8545")

# Account #0 from standard local dev networks (Hardhat / Ganache)
# PUBLIC test private key for local development only - do NOT use with real funds.
DEPLOYER_PRIVATE_KEY = os.environ.get(
    "DEPLOYER_PRIVATE_KEY",
    "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
)

DEPLOYMENT_FILE = os.path.join(os.path.dirname(__file__), "blockchain", "deployment.json")


def is_blockchain_connected():
    """Checks if the Web3 provider is reachable."""
    try:
        w3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={"timeout": 3}))
        connected = w3.is_connected()
        block_number = w3.eth.block_number if connected else None
        return connected, block_number
    except Exception as e:
        return False, str(e)


def _load_contract():
    """
    Reads deployment.json (contract address + ABI) and returns
    a ready-to-use web3 contract instance.
    """
    if not os.path.exists(DEPLOYMENT_FILE):
        raise FileNotFoundError(
            "deployment.json not found in blockchain folder. "
            "Please deploy the contract via Remix IDE or Hardhat and configure deployment.json."
        )

    with open(DEPLOYMENT_FILE, "r") as f:
        info = json.load(f)

    w3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={"timeout": 5}))
    if not w3.is_connected():
        raise ConnectionError(
            f"Cannot connect to blockchain node at {RPC_URL}. "
            "Please start your local node (e.g. 'npx hardhat node' or connect Remix IDE local provider)."
        )

    contract_address = Web3.to_checksum_address(info["address"])
    contract = w3.eth.contract(address=contract_address, abi=info["abi"])
    return w3, contract


def store_hash_on_blockchain(patient_id: str, record_hash: str) -> str:
    """
    Sends a signed transaction calling storeHash(patientId, recordHash).
    Returns the transaction hash string.
    """
    w3, contract = _load_contract()
    account = w3.eth.account.from_key(DEPLOYER_PRIVATE_KEY)

    nonce = w3.eth.get_transaction_count(account.address)
    gas_price = w3.eth.gas_price

    tx = contract.functions.storeHash(patient_id, record_hash).build_transaction({
        "from": account.address,
        "nonce": nonce,
        "gasPrice": gas_price,
    })

    signed_tx = w3.eth.account.sign_transaction(tx, private_key=DEPLOYER_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=10)

    return receipt.transactionHash.hex()


def get_hash_from_blockchain(patient_id: str):
    """
    Calls read-only getHash() function on the smart contract.
    Returns the hash string or None if not registered.
    """
    w3, contract = _load_contract()

    has_hash = contract.functions.hasHash(patient_id).call()
    if not has_hash:
        return None

    return contract.functions.getHash(patient_id).call()


def get_record_details_from_blockchain(patient_id: str):
    """
    Calls getRecordDetails() on the smart contract.
    Returns dictionary with recordHash, timestamp, and recordedBy.
    """
    try:
        w3, contract = _load_contract()
        has_hash = contract.functions.hasHash(patient_id).call()
        if not has_hash:
            return None

        # Check if contract supports getRecordDetails
        if hasattr(contract.functions, "getRecordDetails"):
            details = contract.functions.getRecordDetails(patient_id).call()
            return {
                "record_hash": details[0],
                "timestamp": details[1],
                "recorded_by": details[2],
            }
        else:
            h = contract.functions.getHash(patient_id).call()
            return {"record_hash": h, "timestamp": None, "recorded_by": None}
    except Exception:
        return None

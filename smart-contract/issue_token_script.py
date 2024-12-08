import logging
import time
import os
from pathlib import Path
from multiversx_sdk import ProxyNetworkProvider, Transaction, TransactionComputer, UserSigner, Address, SmartContractTransactionsFactory, TransactionsConverter
from multiversx_sdk.abi import Abi
from helper import Config
from random import choice
import string

# Configuration
LOG_FILE = "sc_call.log"
PROXY_URL = "https://devnet-gateway.multiversx.com"
CHAIN_ID = "D"
ABI_PATH = "./issue-token-snow-sc/output/issue-token-snow-sc.abi.json"
SC_ADDRESS = "erd1qqqqqqqqqqqqqpgqmm40w8anjxdr9mrtcag0a4ydhg4a9ukfq7vqrfujc7"  # Replace with your smart contract address
SC_OWNER_WALLET_PATH = "../3-dec/funding_wallet.json"
TOKEN_NAME = "SantaClaus"  # Leave empty to generate a random name
TOKEN_SUPPLY = 1_000_000_000
ISSUE_COST = 0.05 * 10**18  # 0.05 EGLD in smallest denomination
TOKEN_GAS_LIMIT = 60_000_000

# Token property constants
TOKEN_PROPERTIES = {
    "can_freeze": True,
    "can_wipe": True,
    "can_pause": True,
    "can_mint": True,
    "can_burn": True,
    "can_change_owner": True,
    "can_upgrade": True,
    "can_add_special_roles": True,
}

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
proxy = ProxyNetworkProvider(PROXY_URL)


def encode_to_hex(value):
    """Encode a string or numerical value to hexadecimal."""
    if isinstance(value, int):
        # Ensure even-length hex for numerical values
        return hex(value)[2:].zfill(2 * ((len(hex(value)[2:]) + 1) // 2))
    return value.encode().hex()


def encode_boolean(value):
    """Encode a boolean value to hex (`True` -> `01`, `False` -> `00`)."""
    return "01" if value else "00"


def issue_snow_tokens():
    # Validate ABI existence
    if not Path(ABI_PATH).exists():
        logging.error("ABI file not found. Please check the path.")
        return

    # Load wallet and signer
    signer = UserSigner.from_wallet(Path(SC_OWNER_WALLET_PATH), os.getenv("WALLET_PASSWORD", "password"))
    caller_address = signer.get_pubkey().to_address(hrp="erd")
    logging.info(f"Address used to call the smart contract: [{caller_address.to_bech32()}]")

    transaction_computer = TransactionComputer()

    # Prepare the payload
    name_hex = encode_to_hex(TOKEN_NAME)
    supply_hex = encode_to_hex(TOKEN_SUPPLY)
    properties_hex = [
        encode_boolean(TOKEN_PROPERTIES["can_freeze"]),
        encode_boolean(TOKEN_PROPERTIES["can_wipe"]),
        encode_boolean(TOKEN_PROPERTIES["can_pause"]),
        encode_boolean(TOKEN_PROPERTIES["can_mint"]),
        encode_boolean(TOKEN_PROPERTIES["can_burn"]),
        encode_boolean(TOKEN_PROPERTIES["can_change_owner"]),
        encode_boolean(TOKEN_PROPERTIES["can_upgrade"]),
        encode_boolean(TOKEN_PROPERTIES["can_add_special_roles"]),
    ]

    payload = f"issue_token_snow@{name_hex}@{supply_hex}@" + "@".join(properties_hex)
    logging.info(f"Payload: {payload}")

    # Create and sign the transaction
    transaction = Transaction(
        sender=caller_address.to_bech32(),
        receiver=SC_ADDRESS,  # Issuance SC
        value=str(int(ISSUE_COST)),  # Ensure the value is a string representing an integer
        gas_limit=TOKEN_GAS_LIMIT,
        data=payload.encode(),
        chain_id=CHAIN_ID,
    )
    account_on_network = proxy.get_account(caller_address)
    transaction.nonce = account_on_network.nonce
    transaction.signature = signer.sign(transaction_computer.compute_bytes_for_signing(transaction))

    # Send the transaction
    tx_hash = proxy.send_transaction(transaction)
    logging.info(f"Issued Token (Tx: https://devnet-explorer.multiversx.com/transactions/{tx_hash})")

    time.sleep(3)  # Poll every second
    # Wait for transaction to be completed
    logging.info("Waiting for transaction to complete...")
    while True:
        tx_on_network = proxy.get_transaction(tx_hash, with_process_status=True)
        logging.info(f"Status: {str(tx_on_network.status)}, Is completed: {tx_on_network.is_completed}")
        if tx_on_network.is_completed:
            if tx_on_network.status.is_successful():
                logging.info(f"Transaction confirmed: {str(tx_on_network.status)}")
                break
            else:
                raise Exception(f"Transaction failed: {str(tx_on_network.status)}")
        time.sleep(5)  # Poll every 5 seconds


if __name__ == "__main__":
    issue_snow_tokens()

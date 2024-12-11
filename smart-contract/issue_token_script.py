import logging
import time
import os
from pathlib import Path
from multiversx_sdk import ProxyNetworkProvider, Transaction, TransactionComputer, UserSigner, Address, SmartContractTransactionsFactory, TransactionsConverter
from random import choice
from utilities import Utilities

# Configuration
LOG_FILE = "sc_call.log"
PROXY_URL = "https://devnet-gateway.multiversx.com"
CHAIN_ID = "D"
ABI_PATH = "./issue-token-snow-sc/output/issue-token-snow-sc.abi.json"
SC_ADDRESS = "erd1qqqqqqqqqqqqqpgqmm40w8anjxdr9mrtcag0a4ydhg4a9ukfq7vqrfujc7"  # Replace with your smart contract address
SC_OWNER_WALLET_PATH = "../3-dec/funding_wallet.json"
TOKEN_NAME = "SantaClaus"  # Leave empty to generate a random name
TOKEN_SUPPLY = 1_000_000_000
ISSUE_COST = 0.06 * 10**18  # 0.06 EGLD in smallest denomination
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
transaction_computer = TransactionComputer()


def issue_snow_tokens():
    # Validate ABI existence
    if not Path(ABI_PATH).exists():
        logging.error("ABI file not found. Please check the path.")
        return

    # Load wallet and signer
    signer = UserSigner.from_wallet(Path(SC_OWNER_WALLET_PATH), os.getenv("WALLET_PASSWORD", "password"))
    caller_address = signer.get_pubkey().to_address(hrp="erd")
    logging.info(f"Address used to call the smart contract: [{caller_address.to_bech32()}]")

    # Prepare the payload
    name_hex = Utilities.encode_to_hex(TOKEN_NAME)
    supply_hex = Utilities.encode_to_hex(TOKEN_SUPPLY)
    properties_hex = [
        Utilities.encode_boolean(TOKEN_PROPERTIES["can_freeze"]),
        Utilities.encode_boolean(TOKEN_PROPERTIES["can_wipe"]),
        Utilities.encode_boolean(TOKEN_PROPERTIES["can_pause"]),
        Utilities.encode_boolean(TOKEN_PROPERTIES["can_mint"]),
        Utilities.encode_boolean(TOKEN_PROPERTIES["can_burn"]),
        Utilities.encode_boolean(TOKEN_PROPERTIES["can_change_owner"]),
        Utilities.encode_boolean(TOKEN_PROPERTIES["can_upgrade"]),
        Utilities.encode_boolean(TOKEN_PROPERTIES["can_add_special_roles"]),
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
    logging.info("Waiting for transaction to complete...")
    time.sleep(3)  # sleep for 3 seconds before checking the transaction
    # Wait for the transaction to finalize
    try:
        finalized_transaction = Utilities.wait_for_transaction(proxy, tx_hash)
        logging.info("Transaction finalized successfully.")
    except (TimeoutError, RuntimeError) as e:
        logging.error(f"Failed to finalize transaction: {e}")
        return


if __name__ == "__main__":
    issue_snow_tokens()

import logging
import os
from pathlib import Path
import time
from multiversx_sdk import NetworkProviderConfig, ProxyNetworkProvider, Transaction, TransactionComputer, UserSigner
from utilities import Utilities

# Constants
LOG_FILE = "esdt_mint_role.log"
OWNER_WALLET_PATH = "../3-dec/funding_wallet.json"
CHAIN_ID = "D"
PROXY_URL = "https://devnet-gateway.multiversx.com"
SC_ADDRESS = "erd1qqqqqqqqqqqqqpgqhv6p5lk6fllusxuaq6fqgrj638gpfznsq7vqg7hj4t"
TOKEN_IDENTIFIER = "SNOW-ab6b96"
TOKEN_GAS_LIMIT = 60_000_000

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
proxy = ProxyNetworkProvider(PROXY_URL, config=NetworkProviderConfig("MvxWinterChallenge2024"))
transaction_computer = TransactionComputer()

def enable_mint_role():
    # Load wallet and signer
    signer = UserSigner.from_wallet(Path(OWNER_WALLET_PATH), os.getenv("WALLET_PASSWORD", "password"))
    caller_address = signer.get_pubkey().to_address(hrp="erd")
    logging.info(f"Address used to call the smart contract: [{caller_address.to_bech32()}]")

    # Encode arguments
    token_id_hex = Utilities.encode_to_hex(TOKEN_IDENTIFIER)
    sc_address_hex = Utilities.encode_to_hex(SC_ADDRESS)
    role_hex = Utilities.encode_to_hex("ESDTRoleLocalMint")
    payload = f"setSpecialRole@{token_id_hex}@{sc_address_hex}@{role_hex}"
    logging.info(f"Payload: {payload}")

    # Create transaction
    transaction = Transaction(
        sender=caller_address.to_bech32(),
        receiver=caller_address.to_bech32(),  # Manager's address
        value="0",
        gas_limit=TOKEN_GAS_LIMIT,
        data=payload.encode(),
        chain_id=CHAIN_ID,
    )

    # Set nonce and sign
    account_on_network = proxy.get_account(caller_address)
    transaction.nonce = account_on_network.nonce
    transaction.signature = signer.sign(transaction_computer.compute_bytes_for_signing(transaction))

    # Send the transaction
    tx_hash = proxy.send_transaction(transaction)
    logging.info(f"Transaction sent. Tx Hash: {tx_hash}")
    time.sleep(2)

    # Wait for the transaction to finalize
    try:
        Utilities.wait_for_transaction(proxy, tx_hash)
        logging.info("Transaction finalized successfully.")
    except (TimeoutError, RuntimeError) as e:
        logging.error(f"Failed to finalize transaction: {e}")

if __name__ == "__main__":
    enable_mint_role()
import logging
import os
from pathlib import Path
import time
import argparse
from multiversx_sdk import Address, NetworkProviderConfig, Transaction, UserSigner, ProxyNetworkProvider, TransactionComputer
from utilities import Utilities

LOG_FILE = "claim_tokens.log"

# Configuration
SC_OWNER_WALLET_PATH = "../3-dec/funding_wallet.json" # owner address
PROXY_URL = "https://devnet-gateway.multiversx.com" # proxy url
SC_ADDRESS = "erd1qqqqqqqqqqqqqpgqmm40w8anjxdr9mrtcag0a4ydhg4a9ukfq7vqrfujc7" # smart contract address
CHAIN_ID = "D" # chain id
GAS_LIMIT = 60_000_000 # gas limit

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
config = NetworkProviderConfig("MvxWinterChallenge2024")
proxy = ProxyNetworkProvider(PROXY_URL, config=config)

def claim_tokens(token_identifier: str):
    logging.info("Starting claim_tokens process")
    
    # Load wallet and signer
    signer = UserSigner.from_wallet(Path(SC_OWNER_WALLET_PATH), os.getenv("WALLET_PASSWORD", "password"))
    owner_address = signer.get_pubkey().to_address(hrp="erd")
    logging.info(f"Address used to call the smart contract: [{owner_address.to_bech32()}]")

    # Prepare transaction
    token_to_claim = Utilities.encode_to_hex(token_identifier)
    payload = f"claim_tokens@{token_to_claim}"
    logging.info(f"Payload: [{payload}]")
    transaction = Transaction(
        sender=owner_address.to_bech32(),
        receiver=SC_ADDRESS,
        gas_limit=GAS_LIMIT,
        data=payload.encode(),
        chain_id=CHAIN_ID,
    )

    # Sign and send transaction
    transaction_computer = TransactionComputer()
    account_on_network = proxy.get_account(owner_address)
    transaction.nonce = account_on_network.nonce
    transaction.signature = signer.sign(transaction_computer.compute_bytes_for_signing(transaction))
    tx_hash = proxy.send_transaction(transaction)

    logging.info(f"Transaction Hash: {tx_hash}")
    time.sleep(2)

    # Wait for the transfer to complete
    try:
        finalized_transaction = Utilities.wait_for_transaction(proxy, tx_hash)
        logging.info(f"Token transfer finalized successfully: {finalized_transaction.hash}")
        return tx_hash
    except (TimeoutError, RuntimeError) as e:
        logging.error(f"Failed to finalize token transfer: {e}")
        exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Claim tokens from the smart contract")
    parser.add_argument(
        "--token-identifier", 
        required=True, 
        help="The identifier of the token to claim (e.g., SNOW-8188ec)"
    )
    args = parser.parse_args()

    try:
        tx_hash = claim_tokens(args.token_identifier)
        logging.info(f"Claim transaction sent. Hash: {tx_hash}")
    except Exception as e:
        logging.error(f"An error occurred during the claim process: {e}")
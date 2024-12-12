import logging
import os
from pathlib import Path
import time
from multiversx_sdk import (
    Address,
    NetworkProviderConfig,
    ProxyNetworkProvider,
    QueryRunnerAdapter,
    SmartContractQueriesController,
    Transaction,
    TransactionComputer,
    UserSigner,
)
from multiversx_sdk.abi import Abi
from utilities import Utilities

# Configuration
LOG_FILE = "claim_batch_tokens.log"
API_URL = "https://devnet-api.multiversx.com"
PROXY_URL = "https://devnet-gateway.multiversx.com"
CHAIN_ID = "D"
ABI_PATH = "./issue-token-snow-sc/output/issue-token-snow-sc.abi.json"
SC_ADDRESS = "erd1qqqqqqqqqqqqqpgqmm40w8anjxdr9mrtcag0a4ydhg4a9ukfq7vqrfujc7"
VIEW_ENDPOINT = "get_account_tokens"
CLAIM_ENDPOINT = "claim_tokens"
SC_OWNER_WALLET_PATH = "../3-dec/output"
CLAIM_GAS_LIMIT = 60_000_000

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
config = NetworkProviderConfig("MvxWinterChallenge2024")
proxy = ProxyNetworkProvider(API_URL, config=config)
query_runner = QueryRunnerAdapter(proxy)
transaction_computer = TransactionComputer()


def query_tokens_for_wallet(wallet_path: Path):
    """Query the tokens available for a specific wallet."""
    abi = Abi.load(Path(ABI_PATH))
    query_controller = SmartContractQueriesController(query_runner, abi)

    signer = UserSigner.from_wallet(wallet_path, os.getenv("WALLET_PASSWORD", "password"))
    user_address = signer.get_pubkey().to_address(hrp="erd")

    logging.info(f"Querying tokens for wallet: {wallet_path.name}, Address: {user_address.to_bech32()}")
    query = query_controller.create_query(
        contract=SC_ADDRESS,
        function=VIEW_ENDPOINT,
        arguments=[user_address],  # Pass the address object as an argument
    )

    try:
        query_response = query_controller.run_query(query)
        tokens = query_controller.parse_query_response(query_response)
        logging.info(f"Tokens found for wallet [{user_address.to_bech32()}]: {str(tokens)}")
        return user_address, tokens
    except Exception as e:
        logging.error(f"Error querying tokens for wallet [{wallet_path.name}]: {e}")
        return user_address, []


def claim_tokens(wallet_path: Path, user_address: Address, token_identifier: str, amount: str):
    """Claim tokens for a specific wallet."""
    signer = UserSigner.from_wallet(wallet_path, os.getenv("WALLET_PASSWORD", "password"))

    payload = f"{CLAIM_ENDPOINT}@{Utilities.encode_to_hex(token_identifier)}"
    logging.info(f"Claiming {amount} of {token_identifier} for wallet: {user_address.to_bech32()}")

    transaction = Transaction(
        sender=user_address.to_bech32(),
        receiver=SC_ADDRESS,
        value="0",
        gas_limit=CLAIM_GAS_LIMIT,
        data=payload.encode(),
        chain_id=CHAIN_ID,
    )

    account_on_network = proxy.get_account(user_address)
    transaction.nonce = account_on_network.nonce
    transaction.signature = signer.sign(transaction_computer.compute_bytes_for_signing(transaction))

    time.sleep(1)
    try:
        tx_hash = proxy.send_transaction(transaction)
        logging.info(f"Claim successful for wallet [{user_address.to_bech32()}], Tx: {tx_hash}")
        return tx_hash
    except Exception as e:
        logging.error(f"Error claiming tokens for wallet [{wallet_path.name}]: {e}")
        return None


def process_wallets():
    """Process all wallets to query and claim tokens."""
    wallet_dir = Path(SC_OWNER_WALLET_PATH)
    if not wallet_dir.exists():
        logging.error(f"Wallet directory not found: {SC_OWNER_WALLET_PATH}")
        return

    wallet_files = wallet_dir.glob("*.json")
    transaction_results = []

    for wallet_path in wallet_files:
        user_address, tokens = query_tokens_for_wallet(wallet_path)
        time.sleep(0.5) # have some time in between querying the sc
        
        # Ensure tokens are a flat list of tuples
        if isinstance(tokens, list) and len(tokens) > 0 and isinstance(tokens[0], list):
            tokens = tokens[0]  # Unwrap nested list if applicable

        for token_data in tokens:
            token_identifier, amount = token_data[0], token_data[1]
            if amount > 0:  # Ensure the amount is non-zero
                tx_hash = claim_tokens(wallet_path, user_address, token_identifier, str(amount))
                time.sleep(0.5) # have some time in between querying the sc
                if tx_hash:
                    transaction_results.append({"address": user_address.to_bech32(), "tx_hash": tx_hash})

    # Log all transaction results
    logging.info("Claim Transaction Results:")
    for result in transaction_results:
        logging.info(f"Address: {result['address']}, Tx Hash: {result['tx_hash']}")


if __name__ == "__main__":
    try:
        process_wallets()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
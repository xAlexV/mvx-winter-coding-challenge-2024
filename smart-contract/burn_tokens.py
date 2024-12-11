import logging
import time
from pathlib import Path
from multiversx_sdk import (
    Address,
    Token,
    TokenTransfer,
    Transaction,
    TransactionComputer,
    UserSigner,
    ProxyNetworkProvider,
    TransferTransactionsFactory,
    TransactionsFactoryConfig,
    TransactionsConverter
)
from utilities import Utilities

LOG_FILE = "burn_token.log"

# Configuration for the blockchain connection
SC_OWNER_WALLET_PATH = "../3-dec/funding_wallet.json"
PROXY_URL = "https://devnet-gateway.multiversx.com"
CHAIN_ID = "D"
SC_ADDRESS = "erd1qqqqqqqqqqqqqpgqmm40w8anjxdr9mrtcag0a4ydhg4a9ukfq7vqrfujc7"
TOKEN_TO_BE_BURNED_TICKER = "SNOW-ab6b96"
AMOUNT_TO_BE_BURNED = 1000
TOKEN_DECIMALS = 8
TOKEN_GAS_LIMIT = 100_000_000

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
proxy = ProxyNetworkProvider(PROXY_URL)
transaction_computer = TransactionComputer()

def send_tokens_to_contract(owner_address: Address):
    # Create the ESDT token transfer
    token = Token(TOKEN_TO_BE_BURNED_TICKER)
    transfer_amount = AMOUNT_TO_BE_BURNED * (10 ** TOKEN_DECIMALS)
    token_transfer = TokenTransfer(token, transfer_amount)

    # Configure the factory
    config = TransactionsFactoryConfig(chain_id=CHAIN_ID)
    transfer_factory = TransferTransactionsFactory(config=config)

    # Create the ESDT transfer transaction
    transaction = transfer_factory.create_transaction_for_esdt_token_transfer(
        sender=owner_address,
        receiver=Address.from_bech32(SC_ADDRESS),
        token_transfers=[token_transfer],
    )
    transaction.gas_limit = TOKEN_GAS_LIMIT

    # Sign and send the transaction
    account_on_network = proxy.get_account(owner_address)
    transaction.nonce = account_on_network.nonce
    transaction.signature = signer.sign(transaction_computer.compute_bytes_for_signing(transaction))
    tx_hash = proxy.send_transaction(transaction)
    logging.info(f"Transaction Hash (ESDT Transfer): {tx_hash}")
    time.sleep(2)

     # Step 2: Wait for the transfer to complete
    try:
        finalized_transaction = Utilities.wait_for_transaction(proxy, tx_hash)
        logging.info(f"Token transfer finalized successfully: {finalized_transaction.hash}")
    except (TimeoutError, RuntimeError) as e:
        logging.error(f"Failed to finalize token transfer: {e}")
        exit(1)

    return tx_hash

def burn_tokens(owner_address: Address):
    # Prepare the burn transaction payload
    token_ticker = Utilities.encode_to_hex(TOKEN_TO_BE_BURNED_TICKER)
    amount_to_be_burned = Utilities.encode_to_hex(AMOUNT_TO_BE_BURNED * (10 ** TOKEN_DECIMALS))
    burn_function_data = f"burn_token@{token_ticker}@{amount_to_be_burned}"

    # Create the transaction
    transaction = Transaction(
        sender=owner_address.to_bech32(),
        receiver=SC_ADDRESS,
        gas_limit=TOKEN_GAS_LIMIT,
        data=burn_function_data.encode(),
        chain_id=CHAIN_ID,
    )

    # Sign and send the transaction
    account_on_network = proxy.get_account(owner_address)
    transaction.nonce = account_on_network.nonce
    transaction.signature = signer.sign(transaction_computer.compute_bytes_for_signing(transaction))
    tx_hash = proxy.send_transaction(transaction)
    logging.info(f"Transaction Hash (Burn): {tx_hash}")
    time.sleep(2)

    try:
        finalized_transaction = Utilities.wait_for_transaction(proxy, tx_hash)
        logging.info(f"Token transfer finalized successfully: {finalized_transaction.hash}")
    except (TimeoutError, RuntimeError) as e:
        logging.error(f"Failed to finalize token transfer: {e}")
        exit(1)

    return tx_hash

if __name__ == "__main__":
    signer = UserSigner.from_wallet(Path(SC_OWNER_WALLET_PATH), "password")
    owner_address = signer.get_pubkey().to_address(hrp="erd")
    logging.info(f"Address used to burn tokens: [{owner_address.to_bech32()}]")

    # Step 1: Send Tokens to the Smart Contract
    send_tx_hash = send_tokens_to_contract(owner_address)
    logging.info(f"Token transfer transaction sent. Hash: {send_tx_hash}")

    # Step 3: Call the `burn_token` endpoint
    burn_tx_hash = burn_tokens(owner_address)
    logging.info(f"Burn transaction sent. Hash: {burn_tx_hash}")
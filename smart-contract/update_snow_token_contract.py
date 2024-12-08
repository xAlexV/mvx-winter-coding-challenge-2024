import logging
import time
from pathlib import Path
from multiversx_sdk import Address, AddressComputer, SmartContractTransactionsOutcomeParser, TransactionComputer, UserSigner, ProxyNetworkProvider, SmartContractTransactionsFactory, TransactionsConverter
from multiversx_sdk.abi import Abi
from helper import Config

LOG_FILE = "sc_update.log"
# Configuration for the blockchain connection
SC_OWNER_WALLET_PATH = "../3-dec/funding_wallet.json"
WASM_PATH = "./issue-token-snow-sc/output/issue-token-snow-sc.wasm"
ABI_PATH = "./issue-token-snow-sc/output/issue-token-snow-sc.abi.json"
API_URL = "https://devnet-api.multiversx.com"
PROXY_URL = "https://devnet-gateway.multiversx.com"
CHAIN_ID = "D"
SC_ADDRESS = "erd1qqqqqqqqqqqqqpgqmm40w8anjxdr9mrtcag0a4ydhg4a9ukfq7vqrfujc7"  # Update with the deployed contract address

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
proxy = ProxyNetworkProvider(PROXY_URL)


def wait_for_transaction(proxy: ProxyNetworkProvider, tx_hash: str, timeout: int = 60):
    """
    Waits for the transaction to finalize by polling its status.
    """
    start_time = time.time()
    while True:
        transaction_on_network = proxy.get_transaction(tx_hash)
        status = transaction_on_network.status

        logging.info(f"Transaction status: {status}")

        if transaction_on_network.status.is_successful() or transaction_on_network.status.is_executed():
            logging.info("Transaction successfully finalized.")
            return transaction_on_network
        elif transaction_on_network.status.is_failed() or transaction_on_network.status.is_invalid():
            logging.error(f"Transaction failed with status: {status}")
            raise RuntimeError(f"Transaction failed with status: {status}")

        # Check for timeout
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Transaction not finalized within {timeout} seconds.")

        # Poll every 5 seconds
        time.sleep(5)


def update_smart_contract():
    # Load account and signer
    signer = UserSigner.from_wallet(Path(SC_OWNER_WALLET_PATH), "password")
    sc_owner_address = signer.get_pubkey().to_address(hrp="erd")
    logging.info(f"Address used to update the smart contract: [{sc_owner_address.to_bech32()}]")

    # Update account with nonce
    sender_on_network = proxy.get_account(sc_owner_address)
    current_nonce = sender_on_network.nonce

    # Smart contract upgrade parameters
    bytecode_path = Path(WASM_PATH)
    bytecode = bytecode_path.read_bytes()

    # Load ABI
    abi = Abi.load(Path(ABI_PATH))

    # Define config
    config = Config(chain_id=CHAIN_ID, min_gas_limit=50_000, gas_limit_per_byte=1_500)

    # Create transaction factory
    factory = SmartContractTransactionsFactory(config=config, abi=abi)

    transaction_computer = TransactionComputer()
    # Upgrade transaction
    upgrade_transaction = factory.create_transaction_for_upgrade(
        sender=sc_owner_address,
        contract=Address.new_from_bech32(SC_ADDRESS),
        bytecode=bytecode,
        gas_limit=15_000_000,
        is_upgradeable=True,
        is_readable=True,
        is_payable=True,
    )
    upgrade_transaction.nonce = current_nonce
    upgrade_transaction.signature = signer.sign(transaction_computer.compute_bytes_for_signing(upgrade_transaction))

    transaction_converter = TransactionsConverter()
    logging.info(f"Transaction: {transaction_converter.transaction_to_dictionary(upgrade_transaction)}")
    logging.info(f"Transaction data: {upgrade_transaction.data.decode()}")

    # Send the transaction
    tx_hash = proxy.send_transaction(upgrade_transaction)
    logging.info(f"Upgrade transaction sent: {tx_hash}")

    # transaction_on_network = proxy.get_transaction(tx_hash)
    # transaction_outcome = transaction_converter.transaction_on_network_to_outcome(transaction_on_network)
    # parser = SmartContractTransactionsOutcomeParser()
    # parsed_outcome = parser.parse_deploy(transaction_outcome)
    # logging.info(f"Parsed outcome: {parsed_outcome}")

    # Wait for the transaction to finalize
    try:
        finalized_transaction = wait_for_transaction(proxy, tx_hash)
        logging.info("Transaction finalized successfully.")
    except (TimeoutError, RuntimeError) as e:
        logging.error(f"Failed to finalize transaction: {e}")
        return

    logging.info(f"Smart contract updated successfully at: {SC_ADDRESS}")


if __name__ == "__main__":
    update_smart_contract()
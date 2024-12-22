import logging
import time
from pathlib import Path
from multiversx_sdk import Address, TransactionComputer, TransactionsFactoryConfig, UserSigner, ProxyNetworkProvider, SmartContractTransactionsFactory, TransactionsConverter
from multiversx_sdk.abi import Abi
from utilities import Utilities

LOG_FILE = "sc_update.log"
# Configuration for the blockchain connection
SC_OWNER_WALLET_PATH = "../3-dec/funding_wallet.json"
WASM_PATH = "./winter-staking-sc/output/winter-staking-sc.wasm"
ABI_PATH = "./winter-staking-sc/output/winter-staking-sc.abi.json"
API_URL = "https://devnet-api.multiversx.com"
PROXY_URL = "https://devnet-gateway.multiversx.com"
CHAIN_ID = "D"
SC_ADDRESS = "erd1qqqqqqqqqqqqqpgqsu4kcx5fawwhjg8acpm4wppcqdpwcsagq7vqugfwjm"  # Resource minting sc
# SC_ADDRESS = "erd1qqqqqqqqqqqqqpgqhv6p5lk6fllusxuaq6fqgrj638gpfznsq7vqg7hj4t"  # Winter staking sc
# SC_ADDRESS = "erd1qqqqqqqqqqqqqpgqmm40w8anjxdr9mrtcag0a4ydhg4a9ukfq7vqrfujc7"  # Snow token issue sc

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
proxy = ProxyNetworkProvider(PROXY_URL)
transaction_computer = TransactionComputer()
transaction_converter = TransactionsConverter()

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
    config = TransactionsFactoryConfig(CHAIN_ID)

    # Create transaction factory
    factory = SmartContractTransactionsFactory(config=config, abi=abi)

    # Upgrade transaction
    upgrade_transaction = factory.create_transaction_for_upgrade(
        sender=sc_owner_address,
        contract=Address.new_from_bech32(SC_ADDRESS),
        bytecode=bytecode,
        gas_limit=60_000_000,
        is_upgradeable=True,
        is_readable=True,
        is_payable=True,
    )
    upgrade_transaction.nonce = current_nonce
    upgrade_transaction.signature = signer.sign(transaction_computer.compute_bytes_for_signing(upgrade_transaction))

    logging.info(f"Transaction: {transaction_converter.transaction_to_dictionary(upgrade_transaction)}")
    logging.info(f"Transaction data: {upgrade_transaction.data.decode()}")

    # Send the transaction
    tx_hash = proxy.send_transaction(upgrade_transaction)
    logging.info(f"Upgrade transaction sent: {tx_hash}")

    time.sleep(2)

    # Wait for the transaction to finalize
    try:
        finalized_transaction = Utilities.wait_for_transaction(proxy, tx_hash)
        logging.info("Transaction finalized successfully.")
    except (TimeoutError, RuntimeError) as e:
        logging.error(f"Failed to finalize transaction: {e}")
        return

    logging.info(f"Smart contract updated successfully at: {SC_ADDRESS}")


if __name__ == "__main__":
    update_smart_contract()
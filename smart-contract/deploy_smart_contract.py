import logging
import time
from pathlib import Path
from multiversx_sdk import Address, AddressComputer, SmartContractTransactionsOutcomeParser, TransactionComputer, TransactionsFactoryConfig, UserSigner, ProxyNetworkProvider, SmartContractTransactionsFactory, TransactionsConverter
from multiversx_sdk.abi import Abi
from utilities import Utilities
import argparse

LOG_FILE = "sc_deploy.log"

# Configuration for the blockchain connection
API_URL = "https://devnet-api.multiversx.com"
PROXY_URL = "https://devnet-gateway.multiversx.com"
CHAIN_ID = "D"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
proxy = ProxyNetworkProvider(PROXY_URL)
transaction_computer = TransactionComputer()
transaction_converter = TransactionsConverter()

def deploy_smart_contract(sc_owner_wallet_path, wasm_path, abi_path):
    # Load account and signer
    signer = UserSigner.from_wallet(Path(sc_owner_wallet_path), "password")
    sc_owner_address = signer.get_pubkey().to_address(hrp="erd")
    logging.info(f"Address used to deploy the smart contract: [{sc_owner_address.to_bech32()}]")

    # Update account with nonce
    sender_on_network = proxy.get_account(sc_owner_address)
    current_nonce = sender_on_network.nonce

    # Smart contract deployment parameters
    bytecode_path = Path(wasm_path)
    bytecode = bytecode_path.read_bytes()

    # Load ABI
    abi = Abi.load(Path(abi_path))

    # Define config
    config = TransactionsFactoryConfig(CHAIN_ID)
    # Create transaction factory
    factory = SmartContractTransactionsFactory(config=config, abi=abi)

    logging.info(f"SmartContractTransactionsFactory created")
    logging.info(f"SmartContractTransactionsFactory config: {str(factory.config)}")

    # Deploy transaction
    deploy_transaction = factory.create_transaction_for_deploy(sender=sc_owner_address, bytecode=bytecode, gas_limit=60_000_000, is_upgradeable=True, is_readable=True, is_payable=True)
    deploy_transaction.nonce = current_nonce
    deploy_transaction.signature = signer.sign(transaction_computer.compute_bytes_for_signing(deploy_transaction))

    # Compute the address of the smart contract
    address_computer = AddressComputer()
    contract_address = address_computer.compute_contract_address(deployer=Address.new_from_bech32(deploy_transaction.sender), deployment_nonce=deploy_transaction.nonce)

    logging.info(f"Contract address: [{contract_address.to_bech32()}]")

    logging.info(f"Transaction: {transaction_converter.transaction_to_dictionary(deploy_transaction)}")
    logging.info(f"Transaction data: {deploy_transaction.data.decode()}")

    # Send the transaction
    tx_hash = proxy.send_transaction(deploy_transaction)
    logging.info(f"Deployment transaction sent: {tx_hash}")
    time.sleep(2)

    transaction_on_network = proxy.get_transaction(tx_hash)
    transaction_outcome = transaction_converter.transaction_on_network_to_outcome(transaction_on_network)
    parser = SmartContractTransactionsOutcomeParser()
    parsed_outcome = parser.parse_deploy(transaction_outcome)
    logging.info(f"Parsed outcome: {parsed_outcome}")

    # Wait for the transaction to finalize
    try:
        finalized_transaction = Utilities.wait_for_transaction(proxy, tx_hash)
        logging.info("Transaction finalized successfully.")
    except (TimeoutError, RuntimeError) as e:
        logging.error(f"Failed to finalize transaction: {e}")
        return

    logging.info(f"Smart contract deployed at: {contract_address.to_bech32()}")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Deploy a smart contract to MultiversX.")
    parser.add_argument(
        "--sc-owner-wallet-path",
        required=True,
        help="Path to the smart contract owner wallet file (e.g., '../3-dec/funding_wallet.json')."
    )
    parser.add_argument(
        "--wasm-path",
        required=True,
        help="Path to the WASM file for the smart contract (e.g., './issue-token-snow-sc/output/issue-token-snow-sc.wasm')."
    )
    parser.add_argument(
        "--abi-path",
        required=True,
        help="Path to the ABI file for the smart contract (e.g., './issue-token-snow-sc/output/issue-token-snow-sc.abi.json')."
    )

    args = parser.parse_args()

    deploy_smart_contract(
        sc_owner_wallet_path=args.sc_owner_wallet_path,
        wasm_path=args.wasm_path,
        abi_path=args.abi_path
    )
import time
import json
from pathlib import Path
from multiversx_sdk import ProxyNetworkProvider, Address, Transaction, TransactionComputer, UserSigner
import requests
import logging

# Configure logging
LOG_FILE = "script_output.log"
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])

# Constants
PROXY_URL = "https://devnet-gateway.multiversx.com"
API_URL = "https://devnet-api.multiversx.com"
OUTPUT_DIR = "../3-dec/output"  # Wallets directory
RECIPIENTS_FILE = "recipients.json"  # File to store or load recipient addresses
TOKEN_TRANSFER_AMOUNT = 10_000 * 10**8  # 10,000 units with 8 decimals
BLOCKCHAIN_ID = "D"  # Devnet chain ID
GAS_LIMIT = 500_000  # Gas limit for token transfers

# Initialize Proxy
proxy = ProxyNetworkProvider(PROXY_URL)


def load_created_wallet(wallet_file):
    """Load wallet details and signer."""
    signer = UserSigner.from_wallet(Path(wallet_file), "password")
    address = signer.get_pubkey().to_address(hrp="erd")
    return address, signer


def fetch_created_wallets(directory):
    """Fetch all wallets generated in the previous challenge."""
    wallets = []
    for wallet_file in Path(directory).glob("*.json"):
        wallets.append(wallet_file)
    return wallets


def fetch_token_list(account_address: Address):
    """Retrieve the list of WINTER tokens held by an account."""
    url = f"{API_URL}/accounts/{account_address.to_bech32()}/tokens?type=FungibleESDT&identifier=WINTER"
    response = requests.get(url)
    if response.status_code == 200:
        tokens = response.json()
        return [token["identifier"] for token in tokens]
    else:
        logging.error(f"Error fetching tokens for {account_address.to_bech32()}: {response.text}")
        return []


def fetch_recipient_addresses(sender_address: Address, n=1000):
    """Fetch recipient addresses excluding the sender and smart contract addresses."""
    url = f"{API_URL}/accounts?size={n}&isSmartContract=false"
    while True:
        response = requests.get(url)
        if response.status_code == 200:
            recipients = [account["address"] for account in response.json()]
            if sender_address.to_bech32() in recipients:
                logging.info(f"Sender address {sender_address.to_bech32()} found in recipient list. Removing...")
                recipients.remove(sender_address.to_bech32())
                n += 1  # Increase size to fetch one more address
                continue
            with open(RECIPIENTS_FILE, "w") as f:
                json.dump(recipients[:1000], f, indent=2)
            return recipients[:1000]
        else:
            logging.error(f"Error fetching recipient accounts: {response.text}")
            return []


def send_tokens(signer: UserSigner, account_address: Address, token_identifier, recipient_addresses, amount_per_transfer):
    """Send tokens to recipients."""
    transaction_computer = TransactionComputer()
    tx_hashes = []  # Store hashes for all transactions

    sender_on_network = proxy.get_account(account_address)
    current_nonce = sender_on_network.nonce

    for idx, recipient in enumerate(recipient_addresses):
        value_hex = f"{amount_per_transfer:x}"
        token_identifier_hex = token_identifier.encode().hex()
        data = f"ESDTTransfer@{token_identifier_hex}@{value_hex}".encode()

        transaction = Transaction(sender=account_address.to_bech32(), receiver=recipient, value="0", gas_limit=GAS_LIMIT, data=data, chain_id=BLOCKCHAIN_ID)
        transaction.nonce = current_nonce
        current_nonce += 1  # Increment for the next transaction

        transaction.signature = signer.sign(transaction_computer.compute_bytes_for_signing(transaction))

        tx_hash = None
        for attempt in range(5):
            try:
                tx_hash = proxy.send_transaction(transaction)
                logging.info(f"Tx {idx + 1}/{len(recipient_addresses)}: {token_identifier} to {recipient}, Hash: https://devnet-explorer.multiversx.com/transactions/{tx_hash}")
                break
            except Exception as e:
                logging.warning(f"Error sending transaction to {recipient}: {e}. Retrying ({attempt + 1}/5)...")
                time.sleep(1)

        if not tx_hash:
            logging.error(f"Failed to send transaction to {recipient} after retries. Skipping...")
            continue

        tx_hashes.append(tx_hash)

    logging.info("\nWaiting for all transactions to propagate...")
    for idx, tx_hash in enumerate(tx_hashes):
        retries = 10
        for attempt in range(retries):
            try:
                tx_on_network = proxy.get_transaction(tx_hash, with_process_status=True)
                if tx_on_network.is_completed:
                    logging.info(f"Tx {idx + 1}/{len(tx_hashes)}: {tx_hash} completed.")
                    break
                logging.info(f"Tx {idx + 1}/{len(tx_hashes)}: {tx_hash} status: {tx_on_network.status}. Retrying...")
                time.sleep(1)
            except Exception as e:
                logging.warning(f"Error fetching transaction {tx_hash} status: {e}. Retrying ({attempt + 1}/{retries})...")
                time.sleep(1)
        else:
            logging.error(f"Failed to confirm transaction {tx_hash} after retries.")


def verify_token_holders(token_identifier, account_address: Address):
    """Verify the number of holders for a given token."""
    url = f"{API_URL}/tokens/{token_identifier}/accounts/count"
    response = requests.get(url)
    if response.status_code == 200:
        # Parse the holder count directly from the response body
        holders = int(response.text.strip())  # Ensure the value is an integer
        logging.info(f"Token {token_identifier} whom owner is {account_address.to_bech32()} has {holders} holders.")
        return holders
    else:
        logging.error(f"Error fetching holders for token {token_identifier}: {response.text}")
        return 0


def main():
    logging.info(f"Fetching wallets from {OUTPUT_DIR}...")
    wallet_files = fetch_created_wallets(OUTPUT_DIR)

    logging.info(f"\nTransferring tokens from each wallet...")
    for wallet_file in wallet_files:
        account_address, signer = load_created_wallet(wallet_file)
        logging.info(f"\nWallet: {account_address.to_bech32()}")

        tokens = fetch_token_list(account_address)
        logging.info(f"Tokens found: {tokens}")

        for token in tokens:
            logging.info(f"Fetching recipient addresses for token {token}...")
            recipient_addresses = fetch_recipient_addresses(account_address)

            logging.info(f"Transferring {TOKEN_TRANSFER_AMOUNT // 10**8} units of {token}...")
            send_tokens(signer, account_address, token, recipient_addresses, TOKEN_TRANSFER_AMOUNT)

    logging.info("\nVerifying token holders...")
    for wallet_file in wallet_files:
        account_address, _ = load_created_wallet(wallet_file)
        tokens = fetch_token_list(account_address)
        for token in tokens:
            verify_token_holders(token, account_address)


if __name__ == "__main__":
    main()

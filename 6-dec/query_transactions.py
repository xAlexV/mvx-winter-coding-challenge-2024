from typing import Tuple
import requests
import csv
import json
from pathlib import Path
from multiversx_sdk import Address, UserSigner
import logging

# Configure logging
LOG_FILE = "query_transactions.log"
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])

# Constants
API_URL = "https://devnet-api.multiversx.com"
OUTPUT_DIR = "../3-dec/output"  # Wallets directory containing accounts
CSV_FILE = "transactions.csv"  # Output CSV file
JSON_FILE = "transactions.json"  # Output JSON file
MAX_TRANSACTIONS = 100  # Number of transactions to fetch per request


# Helper functions
def load_created_wallet(wallet_file) -> Tuple[Address, UserSigner]:
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


def fetch_transaction_count(account_address: Address) -> int:
    """Fetch the total transaction count for an account."""
    url = f"{API_URL}/accounts/{account_address.to_bech32()}/transactions/count"
    response = requests.get(url)
    if response.status_code == 200:
        return int(response.text.strip())
    else:
        logging.error(f"Error fetching transaction count for {account_address.to_bech32()}: {response.text}")
        return 0


def fetch_transactions(account_address: Address, page_size=50) -> list:
    """Retrieve all transactions for an account using pagination."""
    transactions = []
    page = 0

    while True:
        url = f"{API_URL}/accounts/{account_address.to_bech32()}/transactions?from={page * page_size}&size={page_size}"
        response = requests.get(url)
        if response.status_code == 200:
            tx_page = response.json()
            if not tx_page:
                break  # No more transactions
            transactions.extend(tx_page)
            page += 1
        else:
            logging.error(f"Error fetching transactions for {account_address.to_bech32()}: {response.text}")
            break

    return transactions


def save_to_csv(data, output_file):
    """Save transaction data to a CSV file."""
    with open(output_file, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Write the header
        writer.writerow(["Hash", "Sender", "Receiver", "Value", "Fee", "GasLimit", "GasUsed", "Status", "Timestamp"])
        for tx in data:
            writer.writerow(
                [
                    tx.get("txHash"),
                    tx.get("sender"),
                    tx.get("receiver"),
                    tx.get("value"),
                    tx.get("fee"),
                    tx.get("gasLimit"),
                    tx.get("gasUsed"),
                    tx.get("status"),
                    tx.get("timestamp"),
                ]
            )
    logging.info(f"Transactions saved to {output_file}")


def save_to_json(data, output_file):
    """Save transaction data to a JSON file."""
    with open(output_file, mode="w") as jsonfile:
        json.dump(data, jsonfile, indent=4)
    logging.info(f"Transactions saved to {output_file}")


def main():
    logging.info("Fetching wallets from the output directory...")
    wallet_files = fetch_created_wallets(OUTPUT_DIR)

    all_transactions = []
    for wallet_file in wallet_files:
        # Load account address
        account_address, signer = load_created_wallet(wallet_file)
        logging.info(f"\nWallet: {account_address.to_bech32()}")

        transaction_count = fetch_transaction_count(account_address)
        transactions = fetch_transactions(account_address)

        logging.info(f"Found {len(transactions)} transactions for account: {account_address.to_bech32()} (API count: {transaction_count})")

        if len(transactions) != transaction_count:
            logging.warning(f"Discrepancy found for account {account_address.to_bech32()}: API count = {transaction_count}, Retrieved = {len(transactions)}")

        # Append account-specific transactions
        for tx in transactions:
            tx["account"] = account_address.to_bech32()
        all_transactions.extend(transactions)

    # Save to CSV and JSON
    logging.info("Saving transactions to files...")
    save_to_csv(all_transactions, CSV_FILE)
    save_to_json(all_transactions, JSON_FILE)
    logging.info("All transactions processed and saved successfully!")


if __name__ == "__main__":
    main()

import time
import random
import json
from pathlib import Path
from multiversx_sdk import ProxyNetworkProvider, Address, UserSigner, Transaction, TransactionComputer
from multiversx_sdk.network_providers.transaction_status import TransactionStatus

# Constants
PROXY_URL = "https://devnet-gateway.multiversx.com"
OUTPUT_DIR = "../3-dec/output"
TOKEN_GAS_LIMIT = 60000000
ISSUE_COST = 0.05 * 10**18  # 0.05 EGLD in smallest denomination
TOKEN_SUPPLY = 100_000_000 * 10**8  # 100 million tokens with 8 decimals
TOKEN_DECIMALS = 8
TOKENS_PER_ACCOUNT = 3
TOKENS_TIKKER = ["WINTER", "SPRING", "SUMMER"]
BLOCKCHAIN_ID = "D"  # Devnet
ISSUANCE_SC = "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"  # Fixed SC issuance address

# Initialize Proxy
proxy = ProxyNetworkProvider(PROXY_URL)

def load_created_wallet(wallet_file):
    """Load wallet details from JSON and create a signer."""
    signer = UserSigner.from_wallet(Path(wallet_file), "password")
    address = signer.get_pubkey().to_address(hrp="erd")
    return address, signer

def fetch_created_wallets(directory):
    """Fetch all wallets generated in the previous challenge."""
    return [wallet_file for wallet_file in Path(directory).glob("*.json")]

def encode_to_hex(value):
    """Encode a string or numerical value to hexadecimal."""
    if isinstance(value, int):
        # Ensure even-length hex for numerical values
        return hex(value)[2:].zfill(2 * ((len(hex(value)[2:]) + 1) // 2))
    return value.encode().hex()

def issue_token(signer: UserSigner, account_address: Address,token_name:str, token_ticker: str, token_supply, token_decimals):
    """Issue a fungible ESDT token."""
    transaction_computer = TransactionComputer()

    # Prepare the payload
    name_hex = encode_to_hex(token_name)
    ticker_hex = encode_to_hex(token_ticker)
    supply_hex = encode_to_hex(token_supply)
    decimals_hex = encode_to_hex(token_decimals)

    payload = f"issue@{name_hex}@{ticker_hex}@{supply_hex}@{decimals_hex}"
    print(f"Payload: {payload}")

    # Create and sign the transaction
    transaction = Transaction(
        sender=account_address.to_bech32(),
        receiver=ISSUANCE_SC,  # Issuance SC
        value=str(int(ISSUE_COST)),  # Ensure the value is a string representing an integer
        gas_limit=TOKEN_GAS_LIMIT,
        data=payload.encode(),
        chain_id=BLOCKCHAIN_ID,
    )
    account_on_network = proxy.get_account(account_address)
    transaction.nonce = account_on_network.nonce
    transaction.signature = signer.sign(transaction_computer.compute_bytes_for_signing(transaction))

    # Send the transaction
    tx_hash = proxy.send_transaction(transaction)
    print(f"Issued Token {token_ticker} (Tx: https://devnet-explorer.multiversx.com/transactions/{tx_hash})")

    time.sleep(3)  # Poll every second
    # Wait for transaction to be completed
    print("Waiting for transaction to complete...")
    while True:
        tx_on_network = proxy.get_transaction(tx_hash, with_process_status=True)
        print(f"Status: {str(tx_on_network.status)}, Is completed: {tx_on_network.is_completed}")
        if tx_on_network.is_completed:
            if tx_on_network.status.is_successful():
                print(f"Transaction confirmed: {str(tx_on_network.status)}")
                break
            else:
                raise Exception(f"Transaction failed: {str(tx_on_network.status)}")
        time.sleep(5)  # Poll every 5 seconds

def main():
    print(f"Fetching wallets from {OUTPUT_DIR}...")
    wallet_files = fetch_created_wallets(OUTPUT_DIR)

    print(f"Issuing tokens for each wallet...")
    for wallet_file in wallet_files:
        account_address, signer = load_created_wallet(wallet_file)

        print(f"\nWallet: {account_address.to_bech32()}")
        for token_tikker in TOKENS_TIKKER:
            token_name = f"{token_tikker}MVXCHALLENGE24"
            token_ticker = token_tikker
            issue_token(signer, account_address,token_name, token_ticker, TOKEN_SUPPLY, TOKEN_DECIMALS)

if __name__ == "__main__":
    main()

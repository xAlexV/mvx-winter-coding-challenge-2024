import time
from multiversx_sdk import AccountNonceHolder, Address, AddressComputer, AddressFactory, Mnemonic, ProxyNetworkProvider, Transaction, TransactionComputer, UserSigner, UserWallet
from pathlib import Path

# Constants
PROXY_URL = "https://devnet-gateway.multiversx.com"
FUNDING_WALLET_JSON = "./funding_wallet.json"  # Path to the JSON file of the funding wallet
FUNDING_WALLET_PASSWORD = "password"  # Password to decrypt the funding wallet
OUTPUT_DIR = Path("./output")
ADDRESSES_PER_SHARD = 3
SHARDS = [0, 1, 2]
AMOUNT_EGLD = 0.0011

# Ensure output directory exists
if not OUTPUT_DIR.exists():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Initialize Proxy
proxy = ProxyNetworkProvider(PROXY_URL)


def load_funding_account(json_file_path, password):
    """Load the funding account and signer from a JSON keystore file."""
    # Load the funding wallet
    signer = UserSigner.from_wallet(Path(json_file_path), password)

    # Retrieve the associated Bech32 address
    funding_address = signer.get_pubkey().to_address(hrp="erd")
    return funding_address, signer


def generate_wallet_for_shard(target_shard, number_of_shards=3):
    """Generate a wallet for a specific shard."""
    address_computer = AddressComputer(number_of_shards=number_of_shards)
    while True:
        # Generate wallet
        mnemonic = Mnemonic.generate()
        secret_key = mnemonic.derive_key(0)
        public_key = secret_key.generate_public_key()

        # Create an Address object
        address_factory = AddressFactory(hrp="erd")
        address_obj = address_factory.create_from_public_key(public_key.buffer)

        # Calculate shard using AddressComputer
        shard = address_computer.get_shard_of_address(address_obj)
        if shard == target_shard:
            # If the shard matches, return the wallet
            address = address_obj.to_bech32()

            # Save wallet as JSON
            wallet = UserWallet.from_secret_key(secret_key, "password")
            wallet_path = OUTPUT_DIR / f"wallet_{address}.json"
            wallet.save(wallet_path)

            print(f"Wallet created for Shard {target_shard}:")
            print(f"  Address: {address}")
            print(f"  Mnemonic: {mnemonic.get_text()}")
            return {"address": address, "mnemonic": mnemonic.get_text()}


def generate_wallets_per_shard(shards, addresses_per_shard):
    """Generate wallets for the given shards."""
    wallets = {shard: [] for shard in shards}
    for shard in shards:
        while len(wallets[shard]) < addresses_per_shard:
            wallet = generate_wallet_for_shard(shard)
            wallets[shard].append(wallet)
            time.sleep(2) # add 2 seconds between wallet generation
    return wallets


def send_tokens_batch(user_signer: UserSigner, funding_address: Address, wallet_addresses, amount_egld):
    """Send tokens to all generated addresses in a batch."""
    transaction_computer = TransactionComputer()
    amount = int(amount_egld * 10**18)  # Convert EGLD to Wei (smallest unit)
    funding_account_on_network = proxy.get_account(funding_address)
    nonce_holder = AccountNonceHolder(funding_account_on_network.nonce)

    transactions = []
    for wallet in wallet_addresses:
        receiver_address = Address.new_from_bech32(wallet["address"])
        transaction = Transaction(
            sender=funding_address.to_bech32(),
            receiver=receiver_address.to_bech32(),
            value=amount,
            gas_limit=50000,
            chain_id="D",
        )
        transaction.nonce = nonce_holder.get_nonce_then_increment()
        transaction.signature = user_signer.sign(transaction_computer.compute_bytes_for_signing(transaction))
        transactions.append(transaction)

    # Broadcast transactions
    success_count, tx_hashes = proxy.send_transactions(transactions)  # Unpack the tuple

    # Log each transaction with its wallet
    print("\nTransaction hashes:")
    for idx, wallet in enumerate(wallet_addresses):
        wallet_address = wallet["address"]
        tx_hash = tx_hashes.get(str(idx))  # Retrieve hash based on wallet's index
        print(f"  Address: {wallet_address}, Tx Hash: https://devnet-explorer.multiversx.com/transactions/{tx_hash}")


def main():
    print(f"Initializing funding account...")
    funding_address, user_signer = load_funding_account(FUNDING_WALLET_JSON, FUNDING_WALLET_PASSWORD)
    print(f"Funding account loaded: {funding_address.bech32()}")

    print(f"Generating {ADDRESSES_PER_SHARD} wallets per shard for shards {SHARDS}...")
    wallets_by_shard = generate_wallets_per_shard(SHARDS, ADDRESSES_PER_SHARD)

    print(f"Distributing {AMOUNT_EGLD} EGLD to each wallet...")
    for shard, wallets in wallets_by_shard.items():
        print(f"\nShard {shard}:")
        send_tokens_batch(user_signer, funding_address, wallets, AMOUNT_EGLD)
        time.sleep(5) # add 5 seconds between sending the transactions

if __name__ == "__main__":
    main()

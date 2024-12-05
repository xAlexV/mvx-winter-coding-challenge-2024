# Prerequisites

- Python 3.x: Ensure Python 3.x is installed.
- MultiversX SDK (multiversx-sdk): Install using pip:
```shell
pip install multiversx-sdk
```
- Required Python libraries:
```shell
pip install requests
```
# Set Up Environment
- Create a virtual environment as explained in: https://pypi.org/project/multiversx-sdk/
- Ensure network access to MultiversX Devnet.

# Run the Script
- add a funding wallet (.json file) to automatically send tokens to generated addresses
- set following variables:

-FUNDING_WALLET_JSON = "./funding_wallet.json"  # Path to the JSON file of the funding wallet

-FUNDING_WALLET_PASSWORD = "password"  # Password to decrypt the funding wallet

-OUTPUT_DIR = Path("./output")

-ADDRESSES_PER_SHARD = 3

-SHARDS = [0, 1, 2]

-AMOUNT_EGLD = 0.0055
- run
```shell
python generate_wallet_and_transfer_token.py
```
- 9 wallets should be generated in output folder
- transactions hashes can be viewed in the terminal
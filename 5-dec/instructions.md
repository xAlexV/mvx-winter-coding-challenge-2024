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
- wallet addresses created on 3 dec
# Set Up Environment
- Create a virtual environment as explained in: https://pypi.org/project/multiversx-sdk/
- Ensure network access to MultiversX Devnet.

# Run the Script
- make sure that previously created wallets are in folder ../3-dec/output
- change constants if needed
```
PROXY_URL = "https://devnet-gateway.multiversx.com"
API_URL = "https://devnet-api.multiversx.com"
OUTPUT_DIR = "../3-dec/output"  # Wallets directory
RECIPIENTS_FILE = "recipients.json"  # File to store or load recipient addresses
TOKEN_TRANSFER_AMOUNT = 10_000 * 10**8  # 10,000 units with 8 decimals
BLOCKCHAIN_ID = "D"  # Devnet chain ID
GAS_LIMIT = 500_000  # Gas limit for token transfers
```
- run
```shell
python transfer_tokens.py
```
- 9000 transactions should be created
- output can be viewed in script_output.log
- each WINTER ESDT token created on 4 dec should have 1001 holder accounts
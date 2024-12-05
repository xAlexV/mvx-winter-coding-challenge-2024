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
- make sure that previously created wallets are in folder ../3-dec/output
- change constants if needed
```
-PROXY_URL = "https://devnet-gateway.multiversx.com"

-OUTPUT_DIR = "../3-dec/output"

-TOKEN_GAS_LIMIT = 60000000

-ISSUE_COST = 0.05 * 10**18  # 0.05 EGLD in smallest denomination

-TOKEN_SUPPLY = 100_000_000 * 10**8  # 100 million tokens with 8 decimals

-TOKEN_DECIMALS = 8

-TOKENS_PER_ACCOUNT = 3

-TOKENS_TIKKER = ["WINTER", "SPRING", "SUMMER"]

-BLOCKCHAIN_ID = "D"  # Devnet

-ISSUANCE_SC = "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"  # Fixed SC issuance address
```
- run
```shell
python issue_tokens.py
```
- 3 ESDT tokens should be created for each of the addresses created on 3 dec
- transactions hashes can be viewed in the terminal
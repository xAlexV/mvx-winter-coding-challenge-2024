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
API_URL = "https://devnet-api.multiversx.com"
OUTPUT_DIR = "../3-dec/output"  # Wallets directory containing accounts
CSV_FILE = "transactions.csv"  # Output CSV file
JSON_FILE = "transactions.json"  # Output JSON file
MAX_TRANSACTIONS = 100  # Number of transactions to fetch per request
```
- run
```shell
python query_transactions.py
```
- output can be viewed in query_transactions.log
- transaction.csv and transactions.json containing transactions from all 9 accounts are created
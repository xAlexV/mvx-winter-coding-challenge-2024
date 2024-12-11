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
- Rust Toolchain: Install Rust using [rustup](https://rustup.rs/)
- sc-meta: Install the multiversx-sc-meta crate to enable contract metadata generation and testing:
```
cargo install multiversx-sc-meta
```
# Set Up Environment
- Create a virtual environment as explained in: https://pypi.org/project/multiversx-sdk/
- Ensure network access to MultiversX Devnet.

# Build the contract
- go to the contract root folder
```
cd smart-contract/issue-token-snow-sc
```
- run
```
sc-meta all build
```
- this should generate the wasm and abi files in output folder

# Deploy the contract
- we're going to use the script deploy_snow_token_contract.py
- change constants if needed
```
SC_OWNER_WALLET_PATH = "../3-dec/funding_wallet.json" # replace with your wallet file
WASM_PATH = "./issue-token-snow-sc/output/issue-token-snow-sc.wasm" # path to wasm file
ABI_PATH = "./issue-token-snow-sc/output/issue-token-snow-sc.abi.json" # path to abi file
API_URL = "https://devnet-api.multiversx.com"
PROXY_URL = "https://devnet-gateway.multiversx.com"
CHAIN_ID = "D"
```
- run
```shell
python deploy_snow_token_contract.py
```
- output can be viewed in sc_deploy.log
- contract address should be visibile in the log file. save it as it will be used later.


# Issue the tokens
- we're going to use the script issue_token_script.py
- change constants if needed
```
PROXY_URL = "https://devnet-gateway.multiversx.com"
CHAIN_ID = "D"
ABI_PATH = "./issue-token-snow-sc/output/issue-token-snow-sc.abi.json" # path to abi file
SC_ADDRESS = "erd1qqqqqqqqqqqqqpgqmm40w8anjxdr9mrtcag0a4ydhg4a9ukfq7vqrfujc7"  # Replace with your smart contract address
SC_OWNER_WALLET_PATH = "../3-dec/funding_wallet.json" # replace with your wallet file
TOKEN_NAME = "SantaClaus"  # Leave empty if you want contract to generate a random name
TOKEN_SUPPLY = 1_000_000_000 # set here the initial token supply
ISSUE_COST = 0.05 * 10**18  # 0.05 EGLD in smallest denomination
TOKEN_GAS_LIMIT = 60_000_000
SC_ENDPOINT = "issue_token_snow" # use issue_token_snow_and_transfer to issue token and transfer to wallet or issue_token_snow to issue token which stays in SC

# Token property constants
TOKEN_PROPERTIES = {
    "can_freeze": True,
    "can_wipe": True,
    "can_pause": True,
    "can_mint": True,
    "can_burn": True,
    "can_change_owner": True,
    "can_upgrade": True,
    "can_add_special_roles": True,
}
```
- run
```shell
python issue_token_script.py
```
- output can be viewed in sc_call.log
- address that called the contract, should have a transaction hash and once contract is finished, and esdt with ticker SNOW and the amount set in token supply constant will be created and sent to caller

# Upgrade the contract
- we're going to use the script update_snow_token_contract.py
- change constants if needed
```
SC_OWNER_WALLET_PATH = "../3-dec/funding_wallet.json" # replace with your wallet file
WASM_PATH = "./issue-token-snow-sc/output/issue-token-snow-sc.wasm" # path to wasm file
ABI_PATH = "./issue-token-snow-sc/output/issue-token-snow-sc.abi.json" # path to abi file
API_URL = "https://devnet-api.multiversx.com"
PROXY_URL = "https://devnet-gateway.multiversx.com"
CHAIN_ID = "D"
SC_ADDRESS = "erd1qqqqqqqqqqqqqpgqmm40w8anjxdr9mrtcag0a4ydhg4a9ukfq7vqrfujc7"  # Update with the deployed contract address
```
- run
```shell
python update_snow_token_contract.py
```
- output can be viewed in sc_deploy.log
- contract address should be visibile in the log file. save it as it will be used later.


# Burn the tokens
- we're going to use the script burn_token.py
- change constants if needed
```
SC_OWNER_WALLET_PATH = "../3-dec/funding_wallet.json" # replace with your wallet file
PROXY_URL = "https://devnet-gateway.multiversx.com" # gateway url
CHAIN_ID = "D" # chain id
SC_ADDRESS = "erd1qqqqqqqqqqqqqpgqmm40w8anjxdr9mrtcag0a4ydhg4a9ukfq7vqrfujc7" # Update with the deployed contract address
TOKEN_TO_BE_BURNED_TICKER = "SNOW-ab6b96" # token ticker for which burn you want to be done
AMOUNT_TO_BE_BURNED = 1000 # amount to be burned
TOKEN_DECIMALS = 8 # token decimals
TOKEN_GAS_LIMIT = 100_000_000 # gas limit
TRANSFER_TOKENS_BEFORE_BURN = False # use false if tokens doesn't have to be transferred first (are in SC)
```
- run
```shell
python burn_token.py
```
- output can be viewed in burn_token.log
- contract address should be visibile in the log file. save it as it will be used later.

# Query the smart contract
- we're going to use the script query_sc_for_token.py
- change constants if needed
```
API_URL = "https://devnet-api.multiversx.com"
ABI_PATH = "./issue-token-snow-sc/output/issue-token-snow-sc.abi.json"
SC_ADDRESS = "erd1qqqqqqqqqqqqqpgqmm40w8anjxdr9mrtcag0a4ydhg4a9ukfq7vqrfujc7"
VIEW_ENDPOINT = "get_account_tokens"  # The view function to call
USER_ADDRESS = "erd1jvch655u7egt93vqj54ea2mxp4fsqr6v5gwftwg8qd06dwllq7vq2mkggc"  # Replace with the user's address to query
```
- run
```shell
python query_sc_for_token.py
```
- output can be viewed in query_sc.log
- Number of tokens generated by an account should be visible
```
2024-12-11 14:20:47,975 - Querying contract: erd1qqqqqqqqqqqqqpgqmm40w8anjxdr9mrtcag0a4ydhg4a9ukfq7vqrfujc7, endpoint: get_account_tokens, user: erd1jvch655u7egt93vqj54ea2mxp4fsqr6v5gwftwg8qd06dwllq7vq2mkggc
2024-12-11 14:20:48,122 - Query result (parsed): [[('SNOW-4bb1b3', 100000000000000000)]]
2024-12-11 14:20:48,123 - Tokens issued by user: 
[[('SNOW-4bb1b3', 100000000000000000)]]
```
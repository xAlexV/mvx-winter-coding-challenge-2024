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
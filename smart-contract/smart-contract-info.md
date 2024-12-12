# IssueTokenSnow Smart Contract

## Overview

The IssueTokenSnow smart contract provides functionality to issue and burn fungible tokens with customizable properties. It includes support for token issuance, burning, querying balances, claiming tokens, logging events, and contract upgradability.

## Smart Contract Features

### 1. Initialization
- **Function**: `init()`
  - Initializes the smart contract without any parameters.

### 2. Events
- **`token_issued`**: Triggered when a token is successfully issued.
  - **Parameters**:
    - `token_ticker`: The unique ticker for the issued token.
    - `token_name`: The display name of the token.
    - `initial_supply`: The initial supply of the token.
  
- **`tokens_claimed`**: Triggered when tokens are successfully claimed.
  - **Parameters**:
    - `token_identifier`: The unique identifier of the claimed token.
    - `caller`: The address of the user claiming the tokens.
    - `amount`: The amount of tokens claimed.

- **`token_burned`**: Triggered when a token is successfully burned.
  - **Parameters**:
    - `token_identifier`: The unique identifier of the burned token.
    - `amount`: The amount of the token that was burned.

- **`log_message`**: Logs a general message.
  - **Parameters**:
    - `message`: A descriptive log message.

### 3. Upgradability
- **Function**: `upgrade()`
  - Allows the contract owner to upgrade the smart contract.
  - Validates that only the owner can execute the upgrade.

### 4. Token Issuance
#### **Function**: `issue_token_snow`
- **Endpoint**: `@issue_token_snow`
- **Description**: Issues a fungible token with customizable properties but retains the tokens in the contract.

- **Parameters**:
```
token_name (optional): The display name of the token. If empty, a random name is generated.
initial_supply: The initial token supply.
Token properties: {
   can_freeze
   can_wipe
   can_pause
   can_mint
   can_burn
   can_change_owner
   can_upgrade
   can_add_special_roles
}
```
- **Details**:
  - A token ticker is hardcoded as `"SNOW"`.
  - The token supply is adjusted to have a fixed number of decimals (8).
  - An ESDT system smart contract call is made to issue the fungible token.

#### **Function**: `issue_token_snow_and_transfer`
- **Endpoint**: `@issue_token_snow_and_transfer`
- **Description**: Issues a fungible token with customizable properties and transfers the tokens to the caller's address.

- **Parameters**:
```
token_name (optional): The display name of the token. If empty, a random name is generated.
initial_supply: The initial token supply.
Token properties: {
   can_freeze
   can_wipe
   can_pause
   can_mint
   can_burn
   can_change_owner
   can_upgrade
   can_add_special_roles
}
```

- **Details**:
  - A token ticker is hardcoded as `"SNOW"`.
  - The token supply is adjusted to have a fixed number of decimals (8).
  - An ESDT system smart contract call is made to issue the fungible token.
  - Tokens are directly transferred to the caller.
  - User balances are updated in storage.

### 5. Claim Tokens
- **Function**: `claim_tokens`
- **Endpoint**: `@claim_tokens`
- **Description**: Allows users to claim tokens previously issued for them.

- **Parameters**:
```
token_identifier: The unique identifier of the token to be claimed.
```

- **Details**:
  - Checks the caller's balance in the contract storage.
  - Transfers tokens from the contract to the caller.
  - Removes the claimed tokens from storage.
  - Emits the `tokens_claimed` event upon successful transfer.

### 6. Burn Token
- **Function**: `burn_token`
- **Endpoint**: `@burn_token`
- **Description**: Allows burning of tokens sent to the smart contract.

- **Parameters**:
```
token_ticker: The unique ticker of the token to be burned.
amount: The amount of the token to be burned.
```
- **Details**:
  - The `token_ticker` is converted to a `TokenIdentifier` within the smart contract.
  - Ensures that the smart contract has sufficient balance of the specified token to burn.
  - Uses the `esdt_local_burn` system API to permanently remove the tokens.
  - Emits the `token_burned` event on successful burn.

### 7. View Token Balances
- **Function**: `get_account_tokens`
- **Endpoint**: `@get_account_tokens`
- **Description**: Queries the tokens issued by a user and their respective balances.

- **Parameters**:
  - `user_address`: The address of the user whose tokens and balances need to be queried.

- **Returns**:
  - A list of tuples, each containing:
    - `TokenIdentifier`: The unique identifier of the token.
    - `BigUint`: The balance of the token.

### 8. Utility Functions
- **`get_decimals()`**: Returns the fixed number of decimals (8) for issued tokens.
- **`generate_random_token_name()`**: Generates a random 8-character token name if none is provided.
- **`emit_log_message()`**: Emits a log message event.

---

## Workflow for Token Issuance, Claiming, and Burning

1. **Token Issuance**:
   - Use the `issue_token_snow` endpoint to issue tokens that remain in the contract.
   - Use the `issue_token_snow_and_transfer` endpoint to issue tokens and transfer them to the caller.

2. **Claim Tokens**:
   - Call the `claim_tokens` endpoint with the `token_identifier` to claim tokens issued for the user.

3. **Token Burning**:
   - Send tokens to the smart contract address.
   - Call the `burn_token` endpoint with the `token_ticker` and `amount` to initiate the burning process.
   - Tokens are burned using the `esdt_local_burn` system API, and a `token_burned` event is emitted.

4. **Querying Balances**:
   - Use the `get_account_tokens` endpoint to retrieve the list of tokens and balances for a specific user.

---

## Key Updates
- Added the `issue_token_snow_and_transfer` endpoint for direct token transfer.
- Added the `claim_tokens` endpoint for users to claim their tokens.
- Added the `get_account_tokens` view endpoint for querying balances.
- Improved the `burn_token` process with stricter validation and detailed logging.
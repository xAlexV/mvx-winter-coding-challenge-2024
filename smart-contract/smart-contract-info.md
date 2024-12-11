# IssueTokenSnow Smart Contract

## Overview

The IssueTokenSnow smart contract provides functionality to issue and burn fungible tokens with customizable properties. It includes support for token issuance, burning, logging events, and contract upgradability.

## Smart Contract Features

1. **Initialization**
   - **Function**: `init()`
   - Initializes the smart contract without any parameters.

2. **Events**
   - **token_issued**: Triggered when a token is successfully issued.
     
     **Parameters:**
     ```
     token_ticker: The unique ticker for the issued token.
     token_name: The display name of the token.
     initial_supply: The initial supply of the token.
     ```

   - **token_burned**: Triggered when a token is successfully burned.
     
     **Parameters:**
     ```
     token_identifier: The unique identifier of the burned token.
     amount: The amount of the token that was burned.
     ```

   - **log_message**: Logs a general message.
     
     **Parameters:**
     ```
     message: A descriptive log message.
     ```

3. **Upgradability**
   - **Function**: `upgrade()`
   - Allows the contract owner to upgrade the smart contract.
   - Validates that only the owner can execute the upgrade.

4. **Token Issuance**
   - **Function**: `issue_token_snow`
   - **Endpoint**: `@issue_token_snow`
   - Allows users to issue fungible tokens with customizable properties.

     **Parameters:**
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
     **Details:**
     - A token ticker is hardcoded as `"SNOW"`.
     - The token supply is adjusted to have a fixed number of decimals (8).
     - An ESDT system smart contract call is made to issue the fungible token.

5. **Burn Token**
   - **Function**: `burn_token`
   - **Endpoint**: `@burn_token`
   - Allows burning of tokens sent to the smart contract.
     
     **Parameters:**
     ```
     token_ticker: The unique ticker of the token to be burned.
     amount: The amount of the token to be burned.
     ```
     **Details:**
     - The `token_ticker` is converted to a `TokenIdentifier` within the smart contract.
     - Ensures that the smart contract has sufficient balance of the specified token to burn.
     - Uses the `esdt_local_burn` system API to permanently remove the tokens.
     - Emits the `token_burned` event on successful burn.

6. **Utility Functions**
   - **get_decimals()**: Returns the fixed number of decimals (8) for issued tokens.
   - **generate_random_token_name()**: Generates a random 8-character token name if none is provided.
   - **emit_log_message()**: Emits a log message event.
   - **biguint_to_string()**: Converts a `BigUint` value into its string representation for logging purposes.

## Workflow for Token Burning

1. **Step 1**: Send tokens to the smart contract.
   - An ESDT token transfer transaction is created and sent to the contract address.
   
2. **Step 2**: Call the `burn_token` endpoint.
   - Once the tokens are transferred, the `burn_token` endpoint is called with the `token_ticker` and `amount` to initiate the burning process.

3. **Step 3**: Tokens are burned.
   - The smart contract validates the balance and uses `esdt_local_burn` to burn the specified amount of tokens.
   - A `token_burned` event is emitted upon successful burn.

## Key Updates
- Added the `burn_token` functionality using the `esdt_local_burn` system API.
- Enhanced logging with detailed messages during token burning.
- Updated event logging for token burning (`token_burned`).
- Workflow split into two separate steps: sending tokens to the contract and calling the burn endpoint.
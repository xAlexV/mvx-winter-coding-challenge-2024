# IssueTokenSnow Smart Contract

## Overview

The IssueTokenSnow smart contract provides functionality to issue fungible tokens with customizable properties. It includes support for token issuance, logging events, and contract upgradability.

## Smart Contract Features

1. Initialization
- Function: init()
- Initializes the smart contract without any parameters.

2. Events
- token_issued: Triggered when a token is successfully issued.

Parameters:
```
token_ticker: The unique ticker for the issued token.
token_name: The display name of the token.
initial_supply: The initial supply of the token.
```
- log_message: Logs a general message.

Parameters:
```
message: A descriptive log message.
```
- token_properties_logged: Logs the serialized properties of the token.

Parameters:
```
serialized_properties: A serialized buffer containing the token properties.
```

3. Upgradability
- Function: upgrade()
- Allows the contract owner to upgrade the smart contract.
- Validates that only the owner can execute the upgrade.

4. Token Issuance
- Function: issue_token_snow
- Endpoint: @issue_token_snow
- Allows users to issue fungible tokens with customizable properties.
Parameters:
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
Details:
- A token ticker is hardcoded as "SNOW".
- The token supply is adjusted to have a fixed number of decimals (8).
- An ESDT system smart contract call is made to issue the fungible token.

5. Utility Functions
- get_decimals(): Returns the fixed number of decimals (8) for issued tokens.
- generate_random_token_name(): Generates a random 8-character token name if none is provided.
- emit_log_message(): Emits a log message event.
- serialize_properties(): Serializes the token properties into a buffer for logging.
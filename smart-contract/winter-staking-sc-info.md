# WinterStaking Smart Contract

## Overview

The WinterStaking smart contract provides functionality to allow users to stake their `WINTER` tokens. It maintains records of staked tokens and tracks the epoch when tokens were first staked by each user. The contract is designed to be simple, with support for staking, querying balances, and future expandability for features like rewards or unstaking mechanisms.

---

## Smart Contract Features

### 1. Initialization
- **Function**: `init()`
  - Initializes the smart contract with no parameters.

---

### 2. Events
#### **`stake_event`**
- **Description**: Triggered when a user successfully stakes `WINTER` tokens.
- **Parameters**:
  - **`user`**: The address of the user staking the tokens.
  - **`epoch`**: The epoch during which the staking occurred.
  - **`stake_data`**: A tuple containing:
    - `TokenIdentifier`: The identifier of the token staked.
    - `BigUint`: The amount of the token staked.

---

### 3. Staking Tokens
#### **Function**: `stake_token_winter`
- **Endpoint**: `@stake_token_winter`
- **Description**: Allows users to stake their `WINTER` tokens.

- **Details**:
  - Accepts any number of `WINTER` tokens via ESDT transfers.
  - Validates the token identifier to ensure it starts with the prefix `WINTER-`.
  - Updates the staked balance for the user.
  - Records the staking epoch for the user if this is their first stake.
  - Emits a `stake_event` upon successful staking.

---

### 4. Upgradability
- **Function**: `upgrade()`
  - Allows the contract owner to upgrade the smart contract.
  - Validates that only the owner can execute the upgrade.

---

### 5. Storage
#### **Stakes**
- **Mapper**: `stakes`
- **Type**: `MapMapper<(ManagedAddress, TokenIdentifier), BigUint>`
- **Purpose**: Tracks the staked amount of each token for every user.

#### **Stake Start Epoch**
- **Mapper**: `stake_start_epoch`
- **Type**: `SingleValueMapper<u64>`
- **Purpose**: Stores the epoch when each user first staked tokens.

---

## Workflow for Staking

### 1. Staking Tokens:
   - Users call the `stake_token_winter` endpoint with their `WINTER` tokens.
   - The contract validates the tokens, updates balances, and emits a `stake_event`.

---

## Design Considerations

### 1. Token Validation:
- Only tokens with the prefix `WINTER-` are accepted. This ensures that unrelated tokens cannot be staked.

### 2. Epoch Tracking:
- The contract records the first epoch during which a user staked tokens. This allows future features, such as rewards or lock-up periods, to use this information.

### 3. Expandability:
- Future updates can add features like:
  - Reward distribution based on staked amounts and duration.
  - Unstaking mechanisms for users to retrieve their tokens.
  - Penalty or bonus logic for early/late unstaking.

---

## Example Scenarios

### 1. Staking `WINTER` Tokens
- A user sends `WINTER-12345` tokens via the `stake_token_winter` endpoint.
- The contract:
  - Validates that the tokens start with the prefix `WINTER-`.
  - Updates the user's balance in the `stakes` storage.
  - Records the current epoch in the `stake_start_epoch` storage (if not already set).
  - Emits a `stake_event`.

### 2. Querying Staked Balances
- Developers can query the `stakes` storage to retrieve the staked amounts for a specific user and token.

---

## Technical Reference

### **Events**
#### **`stake_event`**
- **Description**: Triggered when a user stakes `WINTER` tokens.
- **Parameters**:
  - `user`: The staking user's address.
  - `epoch`: The epoch when staking occurred.
  - `stake_data`:
    - `TokenIdentifier`: The identifier of the staked token.
    - `BigUint`: The amount of tokens staked.

---

### **Mappers**
#### **`stakes`**
- **Type**: `MapMapper<(ManagedAddress, TokenIdentifier), BigUint>`
- **Purpose**: Tracks the staked amounts for each user and token.

#### **`stake_start_epoch`**
- **Type**: `SingleValueMapper<u64>`
- **Purpose**: Tracks the epoch of the first stake for each user.

---

This contract is a minimal implementation, focusing on staking functionality. Future challenges and updates will expand its capabilities.
# WinterStaking Smart Contract

## Overview

The WinterStaking smart contract allows users to stake their `WINTER` tokens, claim rewards periodically, and track their staking history. The contract supports functionalities like staking, rewards claiming, and minting reward tokens with the `SNOW` ticker.

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

#### **`reward_event`**
- **Description**: Triggered when a user successfully claims rewards.
- **Parameters**:
  - **`user`**: The address of the user claiming the rewards.
  - **`token_identifier`**: The identifier of the reward token.
  - **`reward_amount`**: The amount of reward tokens minted and distributed.

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

### 4. Claiming Rewards
#### **Function**: `claim_rewards`
- **Endpoint**: `@claim_rewards`
- **Description**: Allows users to claim rewards based on their staked tokens.

- **Details**:
  - Rewards are calculated as 1% of the staked amount.
  - Users can claim rewards once every 24 hours.
  - Minted rewards have the `SNOW` ticker and 8 decimals.
  - Emits a `reward_event` upon successful claim.

---

### 5. Upgradability
- **Function**: `upgrade()`
  - Allows the contract owner to upgrade the smart contract.
  - Validates that only the owner can execute the upgrade.

---

## Storage Mappers

### **Stakes**
- **Mapper**: `stakes`
- **Type**: `MapMapper<(ManagedAddress, TokenIdentifier), BigUint>`
- **Purpose**: Tracks the staked amount of each token for every user.

### **Stake Start Epoch**
- **Mapper**: `stake_start_epoch`
- **Type**: `SingleValueMapper<u64>`
- **Purpose**: Stores the epoch when each user first staked tokens.

### **Last Reward Claim**
- **Mapper**: `last_reward_claim`
- **Type**: `SingleValueMapper<u64>`
- **Purpose**: Tracks the timestamp of the last reward claim for each user.

---

## Workflow for Staking and Rewards

### 1. Staking Tokens:
   - Users call the `stake_token_winter` endpoint with their `WINTER` tokens.
   - The contract validates the tokens, updates balances, and emits a `stake_event`.

### 2. Claiming Rewards:
   - Users call the `claim_rewards` endpoint.
   - Rewards are calculated as 1% of staked tokens.
   - Minted rewards are transferred to the user, and the `last_reward_claim` timestamp is updated.

---

## Design Considerations

### 1. Token Validation:
- Only tokens with the prefix `WINTER-` are accepted. This ensures that unrelated tokens cannot be staked.

### 2. Rewards System:
- Rewards are minted as `SNOW` tokens with 8 decimals.
- A 24-hour lock period prevents users from claiming rewards too frequently.

### 3. Expandability:
- Future updates can add features like:
  - Enhanced reward distribution logic.
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

### 2. Claiming Rewards
- A user calls the `claim_rewards` endpoint.
- The contract:
  - Calculates rewards as 1% of the staked tokens.
  - Mints `SNOW` tokens and transfers them to the user.
  - Updates the `last_reward_claim` timestamp.
  - Emits a `reward_event`.

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

#### **`reward_event`**
- **Description**: Triggered when a user claims rewards.
- **Parameters**:
  - `user`: The claiming user's address.
  - `token_identifier`: The identifier of the reward token.
  - `reward_amount`: The amount of reward tokens distributed.

---

### **Mappers**
#### **`stakes`**
- **Type**: `MapMapper<(ManagedAddress, TokenIdentifier), BigUint>`
- **Purpose**: Tracks the staked amounts for each user and token.

#### **`stake_start_epoch`**
- **Type**: `SingleValueMapper<u64>`
- **Purpose**: Tracks the epoch of the first stake for each user.

#### **`last_reward_claim`**
- **Type**: `SingleValueMapper<u64>`
- **Purpose**: Tracks the timestamp of the last reward claim for each user.
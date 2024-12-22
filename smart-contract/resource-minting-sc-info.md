# Resource Minting Smart Contract

## Overview
This smart contract mints resources (`WOOD`, `FOOD`, `STONE`, `GOLD`) for users based on their staked `WINTER` tokens. Each resource has its own smart contract, and resources are minted at different rates based on the number of `WINTER` tokens staked. Users must claim previously minted resources before minting additional resources.

---

## Features

### 1. Initialization
- **Function**: `init()`
  - Initializes the smart contract.

---

### 2. Events
#### **`resource_mint_event`**
- **Description**: Triggered when resources are minted for a user.
- **Parameters**:
  - **`user`**: The address of the user minting resources.
  - **`amount`**: The amount of resources minted.

---

### 3. Staking WINTER Tokens
#### **Function**: `stake_winter`
- **Endpoint**: `@stake_winter`
- **Description**: Allows users to stake their `WINTER` tokens.

- **Details**:
  - Accepts multiple `WINTER` tokens via ESDT transfers.
  - Validates the token identifier prefix (`WINTER-`).
  - Updates the user's staked balance in the `stakes` storage.
  - Records the initial minting round for the user.

---

### 4. Minting Resources
#### **Function**: `mint_resources`
- **Endpoint**: `@mint_resources`
- **Description**: Allows users to mint resources based on staked tokens.

- **Details**:
  - Users can mint resources (`WOOD`, `FOOD`, `STONE`, `GOLD`) at specific intervals:
    - `WOOD`: Every 600 rounds.
    - `FOOD`: Every 1200 rounds.
    - `STONE`: Every 1800 rounds.
    - `GOLD`: Every 2400 rounds.
  - For every 1000 `WINTER` tokens staked, users receive:
    - 1 resource token per interval.
  - Emits a `resource_mint_event` for each minting operation.

---

### 5. Claiming Resources
#### **Function**: `claim_resources`
- **Endpoint**: `@claim_resources`
- **Description**: Allows users to claim minted resources.

- **Details**:
  - Users must claim previously minted resources before initiating a new minting cycle.
  - Transfers the minted resources to the user's address.

---

## Storage

### **Stakes**
- **Mapper**: `stakes`
- **Type**: `MapMapper<(ManagedAddress, TokenIdentifier), BigUint>`
- **Purpose**: Tracks the staked amount of each token for every user.

### **Last Minting Round**
- **Mapper**: `last_minting_round`
- **Type**: `SingleValueMapper<u64>`
- **Purpose**: Tracks the last round when a user minted resources.

### **Unclaimed Resources**
- **Mapper**: `unclaimed_resources`
- **Type**: `SingleValueMapper<BigUint>`
- **Purpose**: Tracks unclaimed resources for each user.

---

## Workflow

### 1. Staking WINTER Tokens
- Users call the `stake_winter` endpoint and send their `WINTER` tokens.
- The contract validates the tokens, updates balances, and sets the last minting round if not already set.

### 2. Minting Resources
- Users call the `mint_resources` endpoint.
- The contract:
  - Validates enough rounds have passed since the last mint.
  - Checks for unclaimed resources.
  - Calculates the amount of mintable resources.
  - Updates the `unclaimed_resources` storage.

### 3. Claiming Resources
- Users call the `claim_resources` endpoint.
- The contract:
  - Transfers the unclaimed resources to the user's address.
  - Clears the `unclaimed_resources` storage.

---

## Example

### 1. Staking Tokens
- A user stakes `5000 WINTER-12345` tokens.
- The contract records the staked amount and the current round.

### 2. Minting Resources
- After 600 rounds, the user calls `mint_resources` for `WOOD`.
- The contract mints `5 WOOD` tokens (5000 / 1000).
- The minted tokens are stored as `unclaimed_resources`.

### 3. Claiming Resources
- The user calls `claim_resources`.
- The contract transfers `5 WOOD` tokens to the user's address and clears `unclaimed_resources`.

---

This smart contract ensures efficient resource generation based on token staking, with clear intervals and conditions for claiming tokens.
# Ore Minting Smart Contract

## Overview

This smart contract enables users to mint "ORE" tokens by burning "STONE" tokens. Users must request to mint the "ORE" token by sending "STONE" tokens to the contract, which are then burned. The "ORE" token can be claimed by the user after 1 hour.

---

## Features

### 1. Initialization
- **Function**: `init()`
  - Initializes the smart contract.

---

### 2. Events
#### **`mint_request_event`**
- **Description**: Triggered when a user requests to mint "ORE".
- **Parameters**:
  - **`user`**: The address of the user requesting the mint.
  - **`timestamp`**: The timestamp of the mint request.

#### **`claim_event`**
- **Description**: Triggered when a user successfully claims "ORE".
- **Parameters**:
  - **`user`**: The address of the user claiming the token.

---

### 3. Minting Request
#### **Function**: `request_mint_ore`
- **Endpoint**: `@request_mint_ore`
- **Description**: Allows users to request minting of "ORE".

- **Details**:
  - Users must send at least `20 STONE` tokens.
  - The "STONE" tokens are burned upon successful validation.
  - The mint request is timestamped.
  - Emits a `mint_request_event`.

---

### 4. Claiming ORE
#### **Function**: `claim_ore`
- **Endpoint**: `@claim_ore`
- **Description**: Allows users to claim their "ORE".

- **Details**:
  - Users can claim "ORE" 1 hour after submitting a mint request.
  - The "ORE" token is minted and transferred to the user's address.
  - Emits a `claim_event`.

---

## Storage

### **Mint Requests**
- **Mapper**: `mint_requests`
- **Type**: `SingleValueMapper<u64>`
- **Purpose**: Tracks the timestamp of the user's mint request.

---

## Workflow

### 1. Requesting Minting
- Users call the `request_mint_ore` endpoint and send `20 STONE` tokens.
- The contract validates and burns the tokens.
- A mint request is recorded with the current timestamp.
- Emits a `mint_request_event`.

### 2. Claiming ORE
- After 1 hour, users call the `claim_ore` endpoint.
- The contract:
  - Validates that a mint request exists.
  - Validates the 1-hour waiting period.
  - Mints and transfers the "ORE" tokens to the user's address.
  - Emits a `claim_event`.

---

## Example

### 1. Mint Request
- A user requests to mint "ORE" by sending `20 STONE` tokens.
- The contract validates and burns the tokens.
- The mint request is recorded with the current timestamp.

### 2. Claiming ORE
- After 1 hour, the user calls `claim_ore`.
- The contract mints and transfers the "ORE" tokens to the user's address.

---

## Design Considerations

### 1. Resource Validation
- Only "STONE" tokens are accepted for minting requests.
- Tokens are burned upon receipt to maintain supply constraints.

### 2. Timing Logic
- The 1-hour waiting period is enforced to simulate a production process.

### 3. Extendability
- The contract can be extended to support additional tokens or more complex minting processes.

---

This smart contract ensures secure and efficient minting of "ORE" tokens based on burned resources and timed claims.
# Tool NFT Minting Smart Contract

## Overview

This smart contract enables users to mint a "Shield" NFT by consuming `2 ORE` tokens. Users must claim the NFT after 1 hour of submitting a mint request. The contract ensures that resources are burned, and the claim process is securely timed.

---

## Features

### 1. Initialization
- **Function**: `init()`
  - Initializes the smart contract.

---

### 2. Events
#### **`mint_request_event`**
- **Description**: Triggered when a user requests to mint a "Shield" NFT.
- **Parameters**:
  - **`user`**: The address of the user requesting the mint.
  - **`timestamp`**: The timestamp of the mint request.

#### **`claim_event`**
- **Description**: Triggered when a user successfully claims their "Shield" NFT.
- **Parameters**:
  - **`user`**: The address of the user claiming the NFT.

---

### 3. Minting Request
#### **Function**: `request_mint_shield`
- **Endpoint**: `@request_mint_shield`
- **Description**: Allows users to request minting of a "Shield" NFT.

- **Details**:
  - Users must send at least `2 ORE` tokens.
  - The tokens are burned upon successful validation.
  - The mint request is timestamped.
  - Emits a `mint_request_event`.

---

### 4. Claiming the NFT
#### **Function**: `claim_shield`
- **Endpoint**: `@claim_shield`
- **Description**: Allows users to claim their "Shield" NFT.

- **Details**:
  - Users can claim the NFT 1 hour after submitting a mint request.
  - The NFT is issued and transferred to the user's address.
  - Emits a `claim_event`.

---

## Storage

### **Mint Requests**
- **Mapper**: `mint_requests`
- **Type**: `SingleValueMapper<u64>`
- **Purpose**: Tracks the timestamp of the user's mint request.

### **Token Identifiers**
- **Mapper**: `token_identifiers`
- **Type**: `SingleValueMapper<TokenIdentifier>`
- **Purpose**: Tracks the token identifier used for burning.

---

## Workflow

### 1. Requesting Minting
- Users call the `request_mint_shield` endpoint and send:
  - `2 ORE` tokens.
- The contract validates the resources and burns them.
- A mint request is timestamped.
- Emits a `mint_request_event`.

### 2. Claiming the NFT
- After 1 hour, users call the `claim_shield` endpoint.
- The contract checks:
  - If the mint request exists.
  - If the 1-hour waiting period has passed.
- The "Shield" NFT is issued and transferred to the user's address.
- Emits a `claim_event`.

---

## Example

### 1. Mint Request
- A user requests to mint a "Shield" NFT by sending `2 ORE` tokens.
- The contract validates the tokens and burns them.
- The mint request is recorded with the current timestamp.

### 2. Claiming the NFT
- After 1 hour, the user calls `claim_shield`.
- The contract issues the NFT and transfers it to the user's address.

---

This contract provides a robust mechanism for minting tool NFTs like "Shield" using resource burning and timed claims.
# Citizen NFT Minting Smart Contract

## Overview

This smart contract enables users to mint a "CITIZEN" NFT by burning required resources (`WOOD` and `FOOD` tokens). Users must claim the NFT after 1 hour of submitting a mint request. The contract ensures that resources are burned and that the claim process is securely timed.

---

## Features

### 1. Initialization
- **Function**: `init()`
  - Initializes the smart contract.

---

### 2. Events
#### **`mint_request_event`**
- **Description**: Triggered when a user requests to mint a "CITIZEN" NFT.
- **Parameters**:
  - **`user`**: The address of the user requesting the mint.
  - **`timestamp`**: The timestamp of the mint request.

#### **`claim_event`**
- **Description**: Triggered when a user successfully claims their "CITIZEN" NFT.
- **Parameters**:
  - **`user`**: The address of the user claiming the NFT.

---

### 3. Minting Request
#### **Function**: `request_mint_citizen`
- **Endpoint**: `@request_mint_citizen`
- **Description**: Allows users to request minting of a "CITIZEN" NFT.

- **Details**:
  - Users must send at least:
    - `10 WOOD` tokens.
    - `15 FOOD` tokens.
  - The tokens are burned upon successful validation.
  - The mint request is timestamped.
  - Emits a `mint_request_event`.

---

### 4. Claiming the NFT
#### **Function**: `claim_citizen`
- **Endpoint**: `@claim_citizen`
- **Description**: Allows users to claim their "CITIZEN" NFT.

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

### **Claimable NFTs**
- **Mapper**: `claimable_nfts`
- **Type**: `SingleValueMapper<u64>`
- **Purpose**: Tracks the claimable NFTs for each user (not used directly in this version but can be extended).

---

## Workflow

### 1. Requesting Minting
- Users call the `request_mint_citizen` endpoint and send:
  - `10 WOOD` tokens.
  - `15 FOOD` tokens.
- The contract validates the resources and burns them.
- A mint request is timestamped.
- Emits a `mint_request_event`.

### 2. Claiming the NFT
- After 1 hour, users call the `claim_citizen` endpoint.
- The contract checks:
  - If the mint request exists.
  - If the 1-hour waiting period has passed.
- The "CITIZEN" NFT is issued and transferred to the user's address.
- Emits a `claim_event`.

---

## Example

### 1. Mint Request
- A user requests to mint a "CITIZEN" NFT by sending `10 WOOD` and `15 FOOD` tokens.
- The contract validates the tokens and burns them.
- The mint request is recorded with the current timestamp.

### 2. Claiming the NFT
- After 1 hour, the user calls `claim_citizen`.
- The contract issues the NFT and transfers it to the user's address.

---

## Design Considerations

### 1. Resource Validation
- The contract ensures only `WOOD` and `FOOD` tokens are accepted.
- Tokens are burned to maintain the supply constraints.

### 2. Timing Logic
- The 1-hour waiting period is enforced to simulate real-world delays in character creation.

### 3. Extendability
- The contract can be extended to support additional characters with different resource requirements and waiting periods.

---

This smart contract provides a robust and secure mechanism for minting character NFTs based on resource burning and timed claims.
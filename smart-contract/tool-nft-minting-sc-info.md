# Tool NFT Minting Smart Contract

## Overview

This smart contract enables users to mint tool NFTs, such as "Shield" and "Sword," by consuming specific resource tokens (`ORE` and `GOLD`). Users must claim the NFT after 1 hour of submitting a mint request. The contract ensures that resources are burned and the claim process is securely timed.

---

## Features

### 1. Initialization
- **Function**: `init()`
  - Initializes the smart contract.

---

### 2. Events

#### **`mint_request_event`**
- **Description**: Triggered when a user requests to mint a tool NFT (e.g., "Shield" or "Sword").
- **Parameters**:
  - **`user`**: The address of the user requesting the mint.
  - **`tool`**: The type of tool being requested (e.g., "Shield" or "Sword").
  - **`timestamp`**: The timestamp of the mint request.

#### **`claim_event`**
- **Description**: Triggered when a user successfully claims their tool NFT.
- **Parameters**:
  - **`user`**: The address of the user claiming the NFT.
  - **`tool`**: The type of tool being claimed (e.g., "Shield" or "Sword").

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

#### **Function**: `request_mint_sword`
- **Endpoint**: `@request_mint_sword`
- **Description**: Allows users to request crafting of a "Sword" NFT.

- **Details**:
  - Users must send:
    - At least `1 GOLD` token.
    - At least `3 ORE` tokens.
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

#### **Function**: `claim_sword`
- **Endpoint**: `@claim_sword`
- **Description**: Allows users to claim their "Sword" NFT.

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
- **Type**: `SingleValueMapper<[TokenIdentifier; 2]>`
- **Purpose**: Tracks the token identifiers used for burning.

---

## Workflow

### 1. Requesting Minting
- **Shield**:
  - Users call the `request_mint_shield` endpoint and send:
    - `2 ORE` tokens.
  - The contract validates the resources and burns them.
  - A mint request is timestamped.
  - Emits a `mint_request_event`.

- **Sword**:
  - Users call the `request_mint_sword` endpoint and send:
    - `1 GOLD` token.
    - `3 ORE` tokens.
  - The contract validates the resources and burns them.
  - A mint request is timestamped.
  - Emits a `mint_request_event`.

### 2. Claiming the NFT
- **Shield**:
  - After 1 hour, users call the `claim_shield` endpoint.
  - The contract checks:
    - If the mint request exists.
    - If the 1-hour waiting period has passed.
  - The "Shield" NFT is issued and transferred to the user's address.
  - Emits a `claim_event`.

- **Sword**:
  - After 1 hour, users call the `claim_sword` endpoint.
  - The contract checks:
    - If the mint request exists.
    - If the 1-hour waiting period has passed.
  - The "Sword" NFT is issued and transferred to the user's address.
  - Emits a `claim_event`.

---

## Example

### 1. Minting a "Shield"
- A user requests to mint a "Shield" NFT by sending `2 ORE` tokens.
- The contract validates the tokens and burns them.
- The mint request is recorded with the current timestamp.
- After 1 hour, the user calls `claim_shield`.
- The contract issues the "Shield" NFT and transfers it to the user's address.

### 2. Minting a "Sword"
- A user requests to mint a "Sword" NFT by sending `1 GOLD` and `3 ORE` tokens.
- The contract validates the tokens and burns them.
- The mint request is recorded with the current timestamp.
- After 1 hour, the user calls `claim_sword`.
- The contract issues the "Sword" NFT and transfers it to the user's address.

---

## Design Considerations

### 1. Resource Validation
- The contract ensures only tokens with the correct prefixes (`ORE-` and `GOLD-`) are accepted for minting.

### 2. Timing Logic
- A 1-hour waiting period is enforced for both minting requests to simulate crafting time.

### 3. Extendability
- Additional tools or NFTs can be added with unique resource requirements and waiting periods.

---

This contract provides a secure and extensible system for crafting tool NFTs like "Shield" and "Sword" through resource burning and timed claims.
# Citizen NFT Minting and Upgrade Smart Contract

## Overview

This smart contract enables users to mint a "CITIZEN" NFT by burning required resources (`WOOD` and `FOOD` tokens). Additionally, it allows users to upgrade the "CITIZEN" NFT to a "SOLDIER" NFT by burning `GOLD` and `ORE` tokens. Both processes involve validation, token burning, and timed claim mechanisms to ensure secure and transparent operations.

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

#### **`upgrade_request_event`**
- **Description**: Triggered when a user requests to upgrade a "CITIZEN" NFT to a "SOLDIER" NFT.
- **Parameters**:
  - **`user`**: The address of the user requesting the upgrade.
  - **`citizen_nonce`**: The nonce of the "CITIZEN" NFT being upgraded.
  - **`timestamp`**: The timestamp of the upgrade request.

#### **`claim_event`**
- **Description**: Triggered when a user successfully claims their "CITIZEN" NFT or completes an upgrade to "SOLDIER".
- **Parameters**:
  - **`user`**: The address of the user claiming the NFT or upgrade.

---

### 3. Minting Request
#### **Function**: `request_mint_citizen`
- **Endpoint**: `@request_mint_citizen`
- **Description**: Allows users to request minting of a "CITIZEN" NFT.

- **Details**:
  - Users must send at least:
    - `10 WOOD` tokens.
    - `15 FOOD` tokens.
  - Only tokens with the `WOOD-` and `FOOD-` prefixes are accepted.
  - The tokens are validated and burned upon successful request.
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

### 5. Upgrade Request
#### **Function**: `request_upgrade_to_soldier`
- **Endpoint**: `@request_upgrade_to_soldier`
- **Description**: Allows users to request an upgrade of a "CITIZEN" NFT to a "SOLDIER" NFT.

- **Details**:
  - Users must send at least:
    - `5 GOLD` tokens.
    - `5 ORE` tokens.
  - Only tokens with the `GOLD-` and `ORE-` prefixes are accepted.
  - The tokens are validated and burned upon successful request.
  - The upgrade request is timestamped.
  - Emits an `upgrade_request_event`.

---

### 6. Claiming the Upgrade
#### **Function**: `claim_soldier`
- **Endpoint**: `@claim_soldier`
- **Description**: Allows users to finalize the upgrade of a "CITIZEN" NFT to a "SOLDIER" NFT.

- **Details**:
  - Users can claim the upgrade 1 hour after submitting an upgrade request.
  - The "CITIZEN" NFT attributes are updated to reflect the "SOLDIER" status.
  - Emits a `claim_event`.

---

## Storage

### **Mint Requests**
- **Mapper**: `mint_requests`
- **Type**: `SingleValueMapper<u64>`
- **Purpose**: Tracks the timestamp of the user's mint request.

### **Upgrade Requests**
- **Mapper**: `upgrade_requests`
- **Type**: `SingleValueMapper<u64>`
- **Purpose**: Tracks the timestamp of the user's upgrade request.

### **Token Identifiers**
- **Mapper**: `token_identifiers`
- **Type**: `SingleValueMapper<(TokenIdentifier, TokenIdentifier)>`
- **Purpose**: Tracks the token identifiers used for burning in the minting process.

---

## Workflow

### 1. Minting a "CITIZEN" NFT
- Users call the `request_mint_citizen` endpoint and send:
  - `10 WOOD` tokens.
  - `15 FOOD` tokens.
- The contract validates the tokens and burns them.
- A mint request is recorded with the current timestamp.
- Emits a `mint_request_event`.

### 2. Claiming the "CITIZEN" NFT
- After 1 hour, users call the `claim_citizen` endpoint.
- The contract checks:
  - If the mint request exists.
  - If the 1-hour waiting period has passed.
- The "CITIZEN" NFT is issued and transferred to the user's address.
- Emits a `claim_event`.

### 3. Upgrading to a "SOLDIER" NFT
- Users call the `request_upgrade_to_soldier` endpoint with:
  - `5 GOLD` tokens.
  - `5 ORE` tokens.
- The contract validates the tokens and burns them.
- An upgrade request is recorded with the current timestamp.
- Emits an `upgrade_request_event`.

### 4. Claiming the "SOLDIER" Upgrade
- After 1 hour, users call the `claim_soldier` endpoint, providing the nonce of the "CITIZEN" NFT to be upgraded.
- The contract checks:
  - If the upgrade request exists.
  - If the 1-hour waiting period has passed.
- The "CITIZEN" NFT attributes are updated to reflect the "SOLDIER" status.
- Emits a `claim_event`.

---

## Example

### 1. Minting a "CITIZEN" NFT
- A user requests to mint a "CITIZEN" NFT by sending `10 WOOD` and `15 FOOD` tokens.
- The contract validates the tokens, burns them, and records the request timestamp.
- After 1 hour, the user calls `claim_citizen`.
- The contract issues the "CITIZEN" NFT to the user.

### 2. Upgrading to a "SOLDIER"
- A user requests an upgrade by sending `5 GOLD` and `5 ORE` tokens, along with the nonce of their "CITIZEN" NFT.
- The contract validates the tokens, burns them, and records the upgrade request timestamp.
- After 1 hour, the user calls `claim_soldier` with the nonce of their "CITIZEN" NFT.
- The contract updates the NFT attributes to reflect the "SOLDIER" status.

---

## Design Considerations

### 1. Resource Validation
- The contract ensures only tokens with the correct prefixes are accepted for minting and upgrading.

### 2. Timing Logic
- A 1-hour waiting period is enforced for both minting and upgrading to simulate real-world delays.

### 3. NFT Attribute Update
- The NFT's dynamic attributes are updated using the MultiversX `nft_update_attributes` functionality to reflect the upgraded status.

### 4. Extendability
- Additional character upgrades can be added with different resource requirements and waiting periods.

---

This smart contract provides a secure and extensible system for minting and upgrading character NFTs through resource burning and dynamic NFT attribute updates.
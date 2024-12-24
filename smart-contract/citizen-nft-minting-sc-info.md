# Citizen NFT Minting and Upgrade Smart Contract

## Overview

This smart contract enables users to:
1. Mint a "CITIZEN" NFT by burning required resources (`WOOD` and `FOOD` tokens).
2. Upgrade the "CITIZEN" NFT to a "SOLDIER" NFT by burning `GOLD` and `ORE` tokens.
3. Enhance a "SOLDIER" NFT with:
   - A "SHIELD" NFT to gain `+1 defense`.
   - A "SWORD" NFT to gain `+1 attack`.

Each process involves validation, token burning, and dynamic NFT attribute updates (dyNFT) to reflect the changes.

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

#### **`upgrade_soldier_event`**
- **Description**: Triggered when a "SOLDIER" NFT is upgraded with a "SHIELD" NFT.
- **Parameters**:
  - **`user`**: The address of the user upgrading the "SOLDIER".
  - **`token_id`**: The token identifier of the "SOLDIER" NFT.
  - **`nonce`**: The nonce of the "SOLDIER" NFT being upgraded.

#### **`upgrade_soldier_with_sword_event`**
- **Description**: Triggered when a "SOLDIER" NFT is upgraded with a "SWORD" NFT.
- **Parameters**:
  - **`user`**: The address of the user upgrading the "SOLDIER".
  - **`token_id`**: The token identifier of the "SOLDIER" NFT.
  - **`nonce`**: The nonce of the "SOLDIER" NFT being upgraded.

#### **`claim_event`**
- **Description**: Triggered when a user successfully claims their "CITIZEN" NFT or completes an upgrade.
- **Parameters**:
  - **`user`**: The address of the user claiming the NFT or upgrade.

---

## Processes

### 1. Minting a "CITIZEN" NFT
#### **Function**: `request_mint_citizen`
- **Description**: Allows users to request minting of a "CITIZEN" NFT.
- **Requirements**:
  - Burn `10 WOOD` tokens.
  - Burn `15 FOOD` tokens.
  - Only tokens with the `WOOD-` and `FOOD-` prefixes are accepted.
- **Workflow**:
  - Users send the required tokens to the contract.
  - The contract validates and burns the tokens.
  - A mint request is recorded with the current timestamp.
  - Emits a `mint_request_event`.

#### **Function**: `claim_citizen`
- **Description**: Allows users to claim their minted "CITIZEN" NFT.
- **Requirements**:
  - A 1-hour waiting period after the mint request.
- **Workflow**:
  - Users call the endpoint to claim the NFT after 1 hour.
  - The contract issues the NFT and transfers it to the user's address.
  - Emits a `claim_event`.

---

### 2. Upgrading a "CITIZEN" to a "SOLDIER"
#### **Function**: `request_upgrade_to_soldier`
- **Description**: Allows users to request an upgrade of a "CITIZEN" NFT to a "SOLDIER" NFT.
- **Requirements**:
  - Burn `5 GOLD` tokens.
  - Burn `5 ORE` tokens.
  - Only tokens with the `GOLD-` and `ORE-` prefixes are accepted.
- **Workflow**:
  - Users send the required tokens and provide the nonce of their "CITIZEN" NFT.
  - The contract validates and burns the tokens.
  - An upgrade request is recorded with the current timestamp.
  - Emits an `upgrade_request_event`.

#### **Function**: `claim_soldier`
- **Description**: Allows users to finalize the upgrade to a "SOLDIER" NFT.
- **Requirements**:
  - A 1-hour waiting period after the upgrade request.
- **Workflow**:
  - Users call the endpoint to claim the upgrade after 1 hour.
  - The contract updates the "CITIZEN" NFT attributes to reflect the "SOLDIER" status using the MultiversX `nft_update_attributes` feature.
  - Emits a `claim_event`.

---

### 3. Enhancing a "SOLDIER" with Tools
#### **Function**: `upgrade_soldier_with_shield`
- **Description**: Allows users to upgrade a "SOLDIER" NFT by consuming a "SHIELD" NFT.
- **Requirements**:
  - Provide the "SOLDIER" NFT token ID and nonce.
  - Provide the "SHIELD" NFT token ID and nonce.
- **Workflow**:
  - Users send both NFTs to the contract.
  - The contract validates the NFTs.
  - The "SHIELD" NFT is burned.
  - The "SOLDIER" NFT attributes are updated to include `defense:+1` using the MultiversX `nft_update_attributes` feature.
  - Emits an `upgrade_soldier_event`.

#### **Function**: `upgrade_soldier_with_sword`
- **Description**: Allows users to upgrade a "SOLDIER" NFT by consuming a "SWORD" NFT.
- **Requirements**:
  - Provide the "SOLDIER" NFT token ID and nonce.
  - Provide the "SWORD" NFT token ID and nonce.
- **Workflow**:
  - Users send both NFTs to the contract.
  - The contract validates the NFTs.
  - The "SWORD" NFT is burned.
  - The "SOLDIER" NFT attributes are updated to include `attack:+1` using the MultiversX `nft_update_attributes` feature.
  - Emits an `upgrade_soldier_with_sword_event`.

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

## Example Workflows

### 1. Minting a "CITIZEN" NFT
- A user calls `request_mint_citizen` and sends:
  - `10 WOOD` tokens.
  - `15 FOOD` tokens.
- The contract validates the tokens, burns them, and records the request timestamp.
- After 1 hour, the user calls `claim_citizen`.
- The contract issues the "CITIZEN" NFT to the user.

### 2. Upgrading a "CITIZEN" to a "SOLDIER"
- A user calls `request_upgrade_to_soldier` with:
  - `5 GOLD` tokens.
  - `5 ORE` tokens.
  - The nonce of their "CITIZEN" NFT.
- The contract validates the tokens, burns them, and records the request timestamp.
- After 1 hour, the user calls `claim_soldier` with the "CITIZEN" NFT nonce.
- The contract updates the NFT attributes to reflect the "SOLDIER" status.

### 3. Enhancing a "SOLDIER" with Tools
#### With a "SHIELD":
- A user calls `upgrade_soldier_with_shield` with:
  - The "SOLDIER" NFT token ID and nonce.
  - The "SHIELD" NFT token ID and nonce.
- The contract validates the NFTs and burns the "SHIELD".
- The "SOLDIER" NFT attributes are updated to include `defense:+1`.

#### With a "SWORD":
- A user calls `upgrade_soldier_with_sword` with:
  - The "SOLDIER" NFT token ID and nonce.
  - The "SWORD" NFT token ID and nonce.
- The contract validates the NFTs and burns the "SWORD".
- The "SOLDIER" NFT attributes are updated to include `attack:+1`.

---

## Design Considerations

### 1. Resource Validation
- The contract ensures only tokens with valid prefixes are accepted for minting and upgrading.

### 2. Timing Logic
- Enforces a 1-hour waiting period for both minting and upgrading operations.

### 3. Dynamic Attribute Updates
- The NFT's attributes are dynamically updated using the MultiversX `nft_update_attributes` functionality.

### 4. Extendability
- The contract can be extended to include additional characters, tools, or enhancements.

---

This smart contract provides a secure and extensible system for minting, upgrading, and enhancing NFTs through resource burning and dynamic NFT attribute updates.
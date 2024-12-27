# Arena Smart Contract

## Overview

The Arena Smart Contract is a blockchain-based gaming contract designed for a competitive arena where users can bring their `Soldier` NFTs to battle. Participants can create or join games, bet tokens, and fight using their soldiers. The winner takes the deposited tokens and retains their soldier NFT, while the loser forfeits their deposit.

This contract uses the MultiversX blockchain platform's capabilities, including dynamic NFTs, randomness from the blockchain, and token transfers.

---

## Features

### Soldier Representation
- **`Soldier` Struct**:
  - Represents a soldier NFT with attributes:
    - `token_id`: Identifier of the soldier NFT.
    - `nonce`: Unique identifier for the NFT instance.
    - `attack`: Attack power of the soldier.
    - `defense`: Defensive strength of the soldier.

---

### Game Mechanics
- **`Game` Struct**:
  - Represents an arena game with:
    - `initiator`: Address of the game creator.
    - `competitor`: Address of the challenger.
    - `soldier_initiator`: The initiator's soldier details.
    - `soldier_competitor`: The competitor's soldier details.
    - `entrance_fee`: Fee required to join the game.
    - `completed`: Status of the game.

---

## Workflow

### 1. Creating a Game
- **Function**: `createGame`
- **Description**:
  - Allows a user to create a game by depositing EGLD and registering their soldier.
- **Parameters**:
  - `game_id`: Unique identifier for the game.
  - `soldier_token_id`: Token identifier of the soldier NFT.
  - `soldier_nonce`: Nonce of the soldier NFT.
  - `entrance_fee`: The required fee for joining the game.
- **Flow**:
  - Validates the deposit against the entrance fee.
  - Registers the game with the provided details.
  - Tracks the deposit for the initiator.

---

### 2. Joining a Game
- **Function**: `joinGame`
- **Description**:
  - Allows a competitor to join an existing game by depositing EGLD and registering their soldier.
- **Parameters**:
  - `game_id`: Identifier of the game to join.
  - `soldier_token_id`: Token identifier of the competitor's soldier NFT.
  - `soldier_nonce`: Nonce of the competitor's soldier NFT.
- **Flow**:
  - Validates the deposit against the entrance fee.
  - Updates the game with the competitor's details.
  - Tracks the deposit for the competitor.

---

### 3. Starting the Fight
- **Function**: `startFight`
- **Description**:
  - Determines the winner of the game and transfers the prize to the winner.
- **Flow**:
  - Validates that the game is ready (both initiator and competitor are registered).
  - Calculates the probability of winning for each soldier based on their stats (`attack` and `defense`).
  - Uses a random seed from the blockchain to determine the winner.
  - Transfers the total deposited tokens and the initiator's soldier NFT to the winner.
  - Marks the game as completed.

---

## Storage

### Games
- **Mapper**: `games`
- **Type**: `SingleValueMapper<Game>`
- **Purpose**:
  - Tracks the details of active games.

### Deposits
- **Mapper**: `deposits`
- **Type**: `SingleValueMapper<BigUint>`
- **Purpose**:
  - Tracks the deposited tokens for each user.

---

## Randomness
- **Description**:
  - The winner is determined probabilistically using:
    - Blockchain's `get_block_random_seed` method.
    - Soldier stats to adjust winning probability:
      - For every 1-point stat difference, the probability changes by 1%.
      - Maximum advantage is capped at 50%.

---

## Contract Upgrade
- **Function**: `upgrade`
- **Description**:
  - Allows the contract owner to upgrade the contract logic.

---

## Example Workflow

### Creating a Game
1. A user calls `createGame` with:
   - `game_id`: Unique game identifier.
   - `soldier_token_id`: Token ID of their soldier.
   - `soldier_nonce`: Nonce of their soldier.
   - `entrance_fee`: Fee required for joining the game.
2. The contract:
   - Validates the deposit.
   - Registers the game details.
   - Tracks the deposit for the initiator.

### Joining a Game
1. A competitor calls `joinGame` with:
   - `game_id`: Identifier of the existing game.
   - `soldier_token_id`: Token ID of their soldier.
   - `soldier_nonce`: Nonce of their soldier.
2. The contract:
   - Validates the deposit.
   - Updates the game details with the competitor's info.
   - Tracks the deposit for the competitor.

### Starting the Fight
1. A user calls `startFight` for the game.
2. The contract:
   - Calculates the winning probability for each soldier based on their stats.
   - Uses randomness to decide the winner.
   - Transfers the total deposit and the initiator's soldier NFT to the winner.
   - Marks the game as completed.

---

## Key Design Considerations

1. **Fairness**:
   - Winning probability is influenced by soldier stats, but randomness ensures fairness.
2. **Transparency**:
   - Game details and outcomes are stored on-chain for full transparency.
3. **Security**:
   - Validates all inputs (e.g., deposits, soldier details) to prevent malicious behavior.
4. **Extendability**:
   - The contract is designed to allow future extensions, such as additional game types or features.

---

## Contract Events

1. **Game Created**:
   - Triggered when a new game is created.
2. **Game Joined**:
   - Triggered when a competitor joins a game.
3. **Fight Outcome**:
   - Logs the winner and loser of the fight.

---

## External References
- [MultiversX Blockchain Documentation](https://docs.multiversx.com/)
- [Dynamic NFTs on MultiversX](https://docs.multiversx.com/tokens/nft-tokens/#make-token-dynamic)

---

This smart contract provides a secure, transparent, and engaging platform for competitive battles using dynamic NFTs.
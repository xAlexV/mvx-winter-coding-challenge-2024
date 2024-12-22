# WinterStaking Smart Contract

## **Overview**

The **WinterStaking Smart Contract** enables users to stake `WINTER` tokens, claim rewards periodically, and designate a beneficiary for their staking rewards. The rewards are minted as `SNOW` tokens. The contract is designed with modularity and expandability to accommodate future enhancements.

---

## **Smart Contract Features**

### **1. Initialization**
- **Function**: `init()`
  - Initializes the smart contract without any parameters.

---

### **2. Events**

#### **`stake_event`**
- **Description**: Triggered when a user successfully stakes `WINTER` tokens.
- **Parameters**:
  - **`user`**: Address of the user staking tokens.
  - **`epoch`**: Epoch during which staking occurred.
  - **`stake_data`**: A tuple containing:
    - `TokenIdentifier`: Identifier of the staked token.
    - `BigUint`: Amount of the token staked.

#### **`reward_event`**
- **Description**: Triggered when a user claims rewards.
- **Parameters**:
  - **`user`**: Address of the user claiming rewards.
  - **`token_identifier`**: Identifier of the reward token.
  - **`reward_amount`**: Amount of reward tokens distributed.

#### **`beneficiary_set_event`**
- **Description**: Triggered when a user sets or updates their beneficiary.
- **Parameters**:
  - **`user`**: Address of the user setting the beneficiary.
  - **`beneficiary`**: Address of the designated beneficiary.

---

### **3. Staking Tokens**

#### **Function**: `stake_token_winter`
- **Endpoint**: `@stake_token_winter`
- **Description**: Allows users to stake their `WINTER` tokens.

- **Details**:
  - Accepts multiple `WINTER` tokens via ESDT transfers.
  - Validates the token identifier to ensure it starts with the prefix `WINTER-`.
  - Updates the user's staked balance.
  - Records the first staking epoch for the user if not previously set.
  - Emits a `stake_event` on successful staking.

---

### **4. Claiming Rewards**

#### **Function**: `claim_rewards`
- **Endpoint**: `@claim_rewards`
- **Description**: Allows users to claim staking rewards.

- **Details**:
  - Rewards are calculated as 1% of the staked amount.
  - Users can claim rewards every 24 hours.
  - If a beneficiary is set, rewards are transferred to the beneficiary's address. Otherwise, they are sent to the caller.
  - Rewards are minted as `SNOW` tokens.
  - Emits a `reward_event` upon successful reward claim.

---

### **5. Beneficiary Management**

#### **Function**: `set_beneficiary`
- **Endpoint**: `@set_beneficiary`
- **Description**: Allows users to set or update a beneficiary for their staking rewards.

- **Details**:
  - The beneficiary address cannot be the same as the caller.
  - Updates the beneficiary storage for the user.
  - Emits a `beneficiary_set_event`.

---

### **6. Upgradability**

#### **Function**: `upgrade()`
- **Description**: Allows the contract owner to upgrade the smart contract.
- **Details**:
  - Only the owner can call this function.

---

## **Storage Mappers**

### **Stakes**
- **Mapper**: `stakes`
- **Type**: `MapMapper<(ManagedAddress, TokenIdentifier), BigUint>`
- **Purpose**: Tracks the staked amount of each token for every user.

### **Stake Start Epoch**
- **Mapper**: `stake_start_epoch`
- **Type**: `SingleValueMapper<u64>`
- **Purpose**: Records the epoch when each user first staked tokens.

### **Last Reward Claim**
- **Mapper**: `last_reward_claim`
- **Type**: `SingleValueMapper<u64>`
- **Purpose**: Tracks the timestamp of the last reward claim for each user.

### **Beneficiary**
- **Mapper**: `beneficiary`
- **Type**: `SingleValueMapper<ManagedAddress>`
- **Purpose**: Stores the beneficiary address for reward transfers for each user.

---

## **Workflow for Staking and Rewards**

### **1. Staking Tokens**
1. A user calls the `stake_token_winter` endpoint with their `WINTER` tokens.
2. The contract validates the tokens to ensure they start with the `WINTER-` prefix.
3. The user's balance in the `stakes` storage is updated.
4. The first staking epoch is recorded in the `stake_start_epoch` storage if not already set.
5. A `stake_event` is emitted.

---

### **2. Claiming Rewards**
1. A user calls the `claim_rewards` endpoint.
2. The contract calculates rewards as 1% of the staked amount.
3. Rewards are minted as `SNOW` tokens.
4. If a beneficiary is set, rewards are sent to the beneficiary. Otherwise, they are sent to the caller.
5. The `last_reward_claim` timestamp is updated.
6. A `reward_event` is emitted.

---

### **3. Setting a Beneficiary**
1. A user calls the `set_beneficiary` endpoint with a valid address.
2. The beneficiary address is stored in the `beneficiary` mapper.
3. A `beneficiary_set_event` is emitted.

---

## **Design Considerations**

### **1. Token Validation**
- Only tokens with the prefix `WINTER-` are accepted for staking. This ensures that only relevant tokens are staked.

### **2. Rewards System**
- Rewards are minted as `SNOW` tokens with 8 decimals.
- A 24-hour lock period prevents users from claiming rewards too frequently.
- Beneficiaries allow flexible reward distribution.

### **3. Expandability**
- The contract can be extended to include:
  - Enhanced reward distribution logic.
  - Unstaking mechanisms for users to retrieve their tokens.
  - Additional roles or properties for the reward tokens.

---

## **Example Scenarios**

### **1. Staking `WINTER` Tokens**
- A user sends `WINTER-12345` tokens via the `stake_token_winter` endpoint.
- The contract validates the tokens, updates balances, and records the staking epoch if not already set.
- A `stake_event` is emitted.

### **2. Claiming Rewards**
- A user calls the `claim_rewards` endpoint.
- The contract calculates rewards, mints `SNOW` tokens, and transfers them to the user or their beneficiary.
- The `last_reward_claim` timestamp is updated, and a `reward_event` is emitted.

### **3. Setting a Beneficiary**
- A user calls the `set_beneficiary` endpoint with a valid address.
- The contract updates the beneficiary storage and emits a `beneficiary_set_event`.

---

## **Technical Reference**

### **Events**
#### **`stake_event`**
- Triggered when a user stakes `WINTER` tokens.
- Parameters:
  - `user`: Address of the staking user.
  - `epoch`: Epoch when staking occurred.
  - `stake_data`:
    - `TokenIdentifier`: Identifier of the staked token.
    - `BigUint`: Amount of tokens staked.

#### **`reward_event`**
- Triggered when a user claims rewards.
- Parameters:
  - `user`: Address of the claiming user.
  - `token_identifier`: Identifier of the reward token.
  - `reward_amount`: Amount of reward tokens distributed.

#### **`beneficiary_set_event`**
- Triggered when a user sets or updates their beneficiary.
- Parameters:
  - `user`: Address of the user setting the beneficiary.
  - `beneficiary`: Address of the designated beneficiary.

---

### **Mappers**
#### **`stakes`**
- Tracks staked amounts for each user and token.

#### **`stake_start_epoch`**
- Tracks the epoch of the first stake for each user.

#### **`last_reward_claim`**
- Tracks the timestamp of the last reward claim for each user.

#### **`beneficiary`**
- Stores the beneficiary address for each user's reward transfers. 

---

This documentation reflects the final version of the **WinterStaking Smart Contract**. It includes details about staking, rewards, and beneficiary management, ensuring usability and scalability for future updates.
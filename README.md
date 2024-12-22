# MultiversX Winter Coding Challenge 2024

This repository contains the solutions for the Winter Coding Challenge 2024. Each challenge is organized by date and includes corresponding scripts, logs, and instructions.

https://multiversx.notion.site/multiversx-winter-coding-challenge

---
## Challenges Overview

### **3 December - Wallet Generation and Token Transfer**
- **Description**: Generated a funding wallet and transferred tokens to multiple recipients.
- **Artifacts**:
  - [Instructions](3-dec/instructions.md)
  - [Script](3-dec/generate_wallet_and_transfer_token.py)
  - [Output Logs](3-dec/script_output.log)

---

### **4 December - Issue Tokens**
- **Description**: Implemented functionality to issue fungible tokens with customizable properties.
- **Artifacts**:
  - [Instructions](4-dec/instructions.md)
  - [Script](4-dec/issue_tokens.py)
  - [Output Logs](4-dec/script_output.log)

---

### **5 December - Token Transfers**
- **Description**: Transferred tokens to multiple recipients using a recipient list.
- **Artifacts**:
  - [Instructions](5-dec/instructions.md)
  - [Script](5-dec/transfer_tokens.py)
  - [Output Logs](5-dec/script_output.log)
  - [Recipient List](5-dec/recipients.json)

---

### **6 December - Query Transactions**
- **Description**: Queried blockchain transactions and exported results to JSON and CSV formats.
- **Artifacts**:
  - [Instructions](6-dec/instructions.md)
  - [Script](6-dec/query_transactions.py)
  - [Output Logs](6-dec/query_transactions.log)
  - [Transaction Data (JSON)](6-dec/transactions.json)
  - [Transaction Data (CSV)](6-dec/transactions.csv)

---


### **7, 8, 9, 10 and 11 December**

#### Description:
Deployed and interacted with the `IssueTokenSnow` smart contract for issuing, updating, burning, querying, and claiming tokens. 
Includes batch claim functionality.

#### **Issue Token Smart Contract**
- **Description**: Implemented a smart contract to issue and manage fungible tokens.
- **Artifacts**:
  - [Smart Contract Code](smart-contract/issue-token-snow-sc)
  - [Smart Contract Description](smart-contract/issue-token-sc-info.md)

#### Scripts:
- [Deploy Smart Contract](smart-contract/deploy_snow_token_contract.py)
- [Update Smart Contract](smart-contract/update_snow_token_contract.py)
- [Issue Tokens](smart-contract/issue_token_script.py)
- [Burn Tokens](smart-contract/burn_tokens.py)
- [Query Smart Contract](smart-contract/query_sc_for_token.py)
- [Claim Tokens](smart-contract/claim_tokens.py)
- [Batch Claim Tokens](smart-contract/claim_batch_tokens.py)

#### Artifacts:
- [Instructions](smart-contract/issue-token-sc-instructions.md)
- Output logs available in respective script folders.
---

### **12 December - Winter Token Leaderboard**
- **Description**: Generated a leaderboard for accounts holding `WINTER` tokens across multiple token types.
- **Artifacts**:
  - [Instructions](12-dec/instructions.md)
  - [Script](12-dec/generate_winter_leaderboard.py)
  - [Leaderboard Data (CSV)](12-dec/winter_leaderboard.csv)
  - [Output Logs](12-dec/winter_token_leaderboard.log)

---

### **13, 15, 16 December - Winter Staking Smart Contract**
- **Description**: Implemented a staking smart contract for `WINTER` tokens with epoch tracking and event emission.
- **Artifacts**:
  - [Smart Contract Code](smart-contract/winter-staking-sc)
  - [Smart Contract Description](smart-contract/winter-staking-sc-info.md)

---

### **17 December - Resource Minting Smart Contract**
- **Description**: Implemented a smart contract with functionality for users to mint basic resources based on staked “WINTER” tokens: stone/gold/wood/food.
- **Artifacts**:
  - [Smart Contract Code](smart-contract/resource-minting-sc)
  - [Smart Contract Description](smart-contract/resource-minting-sc-info.md)

---

Each challenge folder includes detailed instructions and scripts for reproducing the results. See the linked `.md` files for more information.
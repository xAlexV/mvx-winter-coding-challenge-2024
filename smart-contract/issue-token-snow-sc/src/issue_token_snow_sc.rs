#![no_std]

use multiversx_sc::imports::*;

#[multiversx_sc::contract]
pub trait IssueTokenSnowSc {
    #[init]
    fn init(&self) {}

    // Mapping to store issued tokens and their balances
    #[storage_mapper("issued_tokens")]
    fn issued_tokens(
        &self,
    ) -> MapMapper<
        (ManagedAddress<Self::Api>, TokenIdentifier<Self::Api>),
        BigUint<Self::Api>,
    >;
    /// Event emitted when a token is successfully issued.
    #[event("token_issued")]
    fn token_issued_event(
        &self,
        #[indexed] token_identifier: TokenIdentifier,
        #[indexed] token_name: ManagedBuffer,
        initial_supply: BigUint,
    );

    /// Event emitted when a token is burned.
    #[event("token_burned")]
    fn token_burned_event(
        &self,
        #[indexed] token_identifier: TokenIdentifier,
        amount: BigUint,
    );

    /// Event emitted when a log message is generated.
    #[event("log_message")]
    fn log_message_event(&self, #[indexed] message: ManagedBuffer);

    /// Function to handle contract upgrades
    #[upgrade]
    fn upgrade(&self) {
        let caller = self.blockchain().get_caller();
        let owner = self.blockchain().get_owner_address();

        require!(caller == owner, "Only the owner can upgrade the contract");
    }

    /// Endpoint to issue a fungible token.
    #[payable("EGLD")]
    #[endpoint(issue_token_snow)]
    fn issue_token_snow(
        &self,
        mut token_name: ManagedBuffer,
        initial_supply: BigUint<Self::Api>,
        can_freeze: bool,
        can_wipe: bool,
        can_pause: bool,
        can_mint: bool,
        can_burn: bool,
        can_change_owner: bool,
        can_upgrade: bool,
        can_add_special_roles: bool,
    ) {
        self.emit_log_message("Starting token issuance process");

        let payment = self.call_value().egld_value();
        let issue_cost = BigUint::from(50_000_000_000_000_000u64); // 0.05 EGLD
        require!(*payment >= issue_cost, "Minimum fee is 0.05 EGLD");

        if token_name.is_empty() {
            token_name = self.generate_random_token_name();
        }

        require!(
            initial_supply > BigUint::zero(),
            "Initial supply must be greater than 0"
        );

        let token_ticker = ManagedBuffer::from("SNOW");
        self.emit_log_message("Token ticker set to SNOW");

        let num_decimals = self.get_decimals();
        let adjusted_supply = initial_supply.clone() * BigUint::from(10u64).pow(num_decimals as u32);

        let properties = FungibleTokenProperties {
            num_decimals,
            can_freeze,
            can_wipe,
            can_pause,
            can_mint,
            can_burn,
            can_change_owner,
            can_upgrade,
            can_add_special_roles,
        };

        // Call the ESDT system smart contract to issue the token
        self.send()
            .esdt_system_sc_proxy()
            .issue_fungible(
                issue_cost,
                &token_name,
                &token_ticker,
                &adjusted_supply,
                properties,
            )
            .async_call_and_exit();
    }

    /// Endpoint to issue a fungible token.
    #[payable("EGLD")]
    #[endpoint(issue_token_snow_and_transfer)]
    fn issue_token_snow_and_transfer(
        &self,
        mut token_name: ManagedBuffer,
        initial_supply: BigUint<Self::Api>,
        can_freeze: bool,
        can_wipe: bool,
        can_pause: bool,
        can_mint: bool,
        can_burn: bool,
        can_change_owner: bool,
        can_upgrade: bool,
        can_add_special_roles: bool,
    ) {
        self.emit_log_message("Starting token issuance process");

        let payment = self.call_value().egld_value();
        let issue_cost = BigUint::from(50_000_000_000_000_000u64); // 0.05 EGLD
        require!(*payment >= issue_cost, "Minimum fee is 0.05 EGLD");

        if token_name.is_empty() {
            token_name = self.generate_random_token_name();
        }

        require!(
            initial_supply > BigUint::zero(),
            "Initial supply must be greater than 0"
        );

        let token_ticker = ManagedBuffer::from("SNOW");
        self.emit_log_message("Token ticker set to SNOW");

        let num_decimals = self.get_decimals();
        let adjusted_supply = initial_supply.clone() * BigUint::from(10u64).pow(num_decimals as u32);

        let properties = FungibleTokenProperties {
            num_decimals,
            can_freeze,
            can_wipe,
            can_pause,
            can_mint,
            can_burn,
            can_change_owner,
            can_upgrade,
            can_add_special_roles,
        };

        // Call the ESDT system smart contract to issue the token
        self.send()
            .esdt_system_sc_proxy()
            .issue_fungible(
                issue_cost,
                &token_name,
                &token_ticker,
                &adjusted_supply,
                properties,
            )
            .with_callback(self.callbacks().esdt_issue_callback(
                self.blockchain().get_caller(),
            ))
            .async_call_and_exit();
    }

    /// Callback for token issuance
    #[callback]
    fn esdt_issue_callback(
        &self,
        caller: ManagedAddress,
        #[call_result] result: ManagedAsyncCallResult<()>,
    ) {
        let (token_identifier, returned_tokens) = self.call_value().egld_or_single_fungible_esdt();
        match result {
            ManagedAsyncCallResult::Ok(()) => {
                self.emit_log_message("Token issuance successful");
        
                let unwrapped_identifier = token_identifier.unwrap_esdt();
        
                // Transfer tokens to the caller
                self.send()
                    .direct_esdt(
                        &caller,
                        &unwrapped_identifier,
                        0,
                        &returned_tokens,
                    );
        
                // Update the user's balance in storage
                self.update_user_balance(caller.clone(), unwrapped_identifier.clone(), returned_tokens.clone());
                
                // Track token issuance
                self.emit_log_message("Tokens transferred to the caller");

                // Emit event for successful issuance
                self.token_issued_event(
                    unwrapped_identifier, // Use the unwrapped identifier here
                    ManagedBuffer::from("Token Name"),
                    returned_tokens,
                );
            }
            ManagedAsyncCallResult::Err(_err) => {
                self.emit_log_message("Token issuance failed");
        
                // Refund the caller if necessary
                if token_identifier.is_egld() && returned_tokens > 0 {
                    self.tx().to(&caller).egld(&returned_tokens).transfer();
                }
            }
        }
    }

    /// Single endpoint to handle token transfer and burning.
    #[endpoint(burn_token)]
    fn burn_token(
        &self,
        token_ticker: ManagedBuffer<Self::Api>, // Token ticker as input
        amount: BigUint<Self::Api>,             // Amount to be burned
    ) {
        self.emit_log_message("Starting token burn process");

        // Convert the token ticker into a TokenIdentifier
        let token_identifier = TokenIdentifier::from_esdt_bytes(token_ticker.clone());

        // Get the contract's balance for the token
        let contract_address = self.blockchain().get_sc_address();
        let nonce = 0u64; // Nonce for fungible tokens is always 0
        let balance = self.blockchain().get_esdt_balance(&contract_address, &token_identifier, nonce);

        // Validate that the contract has enough tokens to burn
        require!(balance >= amount, "Insufficient token balance for burn");

        self.emit_log_message("Burning tokens using esdt_local_burn");

        // Perform the burn
        self.send()
            .esdt_local_burn(&token_identifier, nonce, &amount);

        self.emit_log_message("Token burn process completed successfully");

        // Emit an event for the burn
        self.token_burned_event(token_identifier, amount);
    }

    /// View endpoint to query token issuance and balances
    #[view(get_account_tokens)]
    fn get_account_tokens(
        &self,
        user_address: ManagedAddress,
    ) -> MultiValueEncoded<(TokenIdentifier<Self::Api>, BigUint<Self::Api>)> {
        let mut result = MultiValueEncoded::new();

        for (key, balance) in self.issued_tokens().iter() {
            if key.0 == user_address {
                result.push((key.1.clone(), balance.clone()));
            }
        }

        result
    }

    fn update_user_balance(
        &self,
        user_address: ManagedAddress<Self::Api>,
        token_identifier: TokenIdentifier<Self::Api>,
        amount: BigUint<Self::Api>,
    ) {
        let key = (user_address, token_identifier);
        if let Some(existing_balance) = self.issued_tokens().get(&key) {
            self.issued_tokens().insert(key, existing_balance + amount);
        } else {
            self.issued_tokens().insert(key, amount);
        }
    }

    /// Returns the fixed number of decimals for tokens.
    fn get_decimals(&self) -> usize {
        8
    }

    /// Generates a random token name.
    fn generate_random_token_name(&self) -> ManagedBuffer<Self::Api> {
        let mut name = ManagedBuffer::new(); // Default constructor
        let block_nonce = self.blockchain().get_block_nonce();
        let block_timestamp = self.blockchain().get_block_timestamp();

        let random_seed = block_nonce ^ block_timestamp as u64;

        for i in 0..8 {
            let char_index = ((random_seed >> (i * 5)) & 0x1F) % 36;
            let char = match char_index {
                0..=9 => b'0' + char_index as u8,
                10..=35 => b'A' + (char_index - 10) as u8,
                _ => unreachable!(),
            };

            name.append_bytes(&[char]);
        }

        name
    }

    /// Emit a log message event.
    fn emit_log_message(&self, message: &str) {
        let log_buffer = ManagedBuffer::from(message);
        self.log_message_event(log_buffer);
    }
}
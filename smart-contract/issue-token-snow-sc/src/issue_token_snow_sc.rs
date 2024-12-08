#![no_std]

use multiversx_sc::imports::*;

#[multiversx_sc::contract]
pub trait IssueTokenSnowSc {
    #[init]
    fn init(&self) {}

    /// Event emitted when a token is successfully issued.
    #[event("token_issued")]
    fn token_issued_event(
        &self,
        #[indexed] token_ticker: ManagedBuffer,
        #[indexed] token_name: ManagedBuffer,
        initial_supply: BigUint,
    );

    /// Event emitted when a log message is generated.
    #[event("log_message")]
    fn log_message_event(&self, #[indexed] message: ManagedBuffer);

    /// Event emitted when token properties are logged.
    #[event("token_properties_logged")]
    fn token_properties_logged_event(&self, serialized_properties: ManagedBuffer);

    /// Function to handle contract upgrades
    #[upgrade]
    fn upgrade(&self) {
        let caller = self.blockchain().get_caller();
        let owner = self.blockchain().get_owner_address();

        // Only the owner of the smart contract can perform the upgrade
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

        // Ensure payment meets the minimum requirement
        let payment = self.call_value().egld_value();
        let issue_cost = BigUint::from(50_000_000_000_000_000u64); // 0.05 EGLD
        require!(*payment >= issue_cost, "Minimum fee is 0.05 EGLD");

        // Generate a random token name if not provided
        if token_name.is_empty() {
            token_name = self.generate_random_token_name();
        }

        // Validate initial_supply
        require!(
            initial_supply > BigUint::zero(),
            "Initial supply must be greater than 0"
        );

        // Generate and validate a unique token ticker
        let token_ticker = ManagedBuffer::from("SNOW");
        self.emit_log_message("Token ticker set to SNOW");

        // Adjust supply for the fixed number of decimals
        let num_decimals = self.get_decimals();
        let adjusted_supply = initial_supply.clone() * BigUint::from(10u64).pow(num_decimals as u32);
        
        // Construct token properties
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

        // Serialize properties into a single buffer
        let serialized_properties = self.serialize_properties(
            can_freeze, can_wipe, can_pause, can_mint, can_burn,
            can_change_owner, can_upgrade, can_add_special_roles,
        );

        // Emit event with serialized properties
        self.token_properties_logged_event(serialized_properties);

        // Emit token issued event before exiting
        self.token_issued_event(token_ticker.clone(), token_name.clone(), initial_supply.clone());
        
        self.emit_log_message("Issuing token through the ESDT system SC");

        // Call the ESDT system SC to issue the fungible token
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

        // Emit token issued event

    }

    /// Returns the fixed number of decimals for tokens.
    fn get_decimals(&self) -> usize {
        8
    }

    /// Generates a random token name.
    fn generate_random_token_name(&self) -> ManagedBuffer<Self::Api> {
        let mut name = ManagedBuffer::new();
        let block_nonce = self.blockchain().get_block_nonce();
        let block_timestamp = self.blockchain().get_block_timestamp();

        let random_seed = block_nonce ^ block_timestamp as u64;

        for i in 0..8 {
            let char_index = ((random_seed >> (i * 5)) & 0x1F) % 36; // Limit range to 36
            let char = match char_index {
                0..=9 => b'0' + char_index as u8,    // Numbers
                10..=35 => b'A' + (char_index - 10) as u8, // Uppercase letters
                _ => unreachable!(),
            };

            name.append_bytes(&[char]);
        }

        name
    }

    /// Emit a log message event.
    fn emit_log_message(&self, message: &str) {
        self.log_message_event(ManagedBuffer::from(message));
    }

    /// Serializes token properties into a `ManagedBuffer`.
    fn serialize_properties(
        &self,
        can_freeze: bool,
        can_wipe: bool,
        can_pause: bool,
        can_mint: bool,
        can_burn: bool,
        can_change_owner: bool,
        can_upgrade: bool,
        can_add_special_roles: bool,
    ) -> ManagedBuffer<Self::Api> {
        let mut buffer = ManagedBuffer::new();
        buffer.append_bytes(&[can_freeze as u8]);
        buffer.append_bytes(&[can_wipe as u8]);
        buffer.append_bytes(&[can_pause as u8]);
        buffer.append_bytes(&[can_mint as u8]);
        buffer.append_bytes(&[can_burn as u8]);
        buffer.append_bytes(&[can_change_owner as u8]);
        buffer.append_bytes(&[can_upgrade as u8]);
        buffer.append_bytes(&[can_add_special_roles as u8]);
        buffer
    }
}
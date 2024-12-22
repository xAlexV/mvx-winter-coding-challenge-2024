#![no_std]

use multiversx_sc::imports::*;

/// Smart contract to mint "ORE" by burning "STONE".
#[multiversx_sc::contract]
pub trait OreMintingSc {
    /// Initializes the smart contract
    #[init]
    fn init(&self) {}

    /// Storage to track mint requests
    #[storage_mapper("mint_requests")]
    fn mint_requests(&self, user: &ManagedAddress) -> SingleValueMapper<u64>;

    /// Endpoint to request minting of "ORE"
    #[payable("*")]
    #[endpoint(request_mint_ore)]
    fn request_mint_ore(&self) {
        let caller = self.blockchain().get_caller();
        let current_timestamp = self.blockchain().get_block_timestamp();

        // Track the total STONE tokens sent for burning
        let mut stone_amount = BigUint::zero();

        for payment in self.call_value().all_esdt_transfers().iter() {
            let token_bytes = payment.token_identifier.as_managed_buffer().to_boxed_bytes();
            let token_bytes_slice = token_bytes.as_ref();

            // Validate token identifier prefix
            let prefix = b"STONE-";
            require!(
                token_bytes_slice.starts_with(prefix),
                "Only STONE tokens are accepted"
            );

            stone_amount += payment.amount.clone();
        }

        // Validate the required amount
        require!(stone_amount >= BigUint::from(20u64), "Insufficient STONE tokens");

        // Burn the STONE tokens
        self.send().esdt_local_burn(
            &TokenIdentifier::from("STONE".as_bytes()),
            0,
            &stone_amount,
        );

        // Set the request timestamp
        self.mint_requests(&caller).set(current_timestamp);

        // Emit mint request event
        self.mint_request_event(caller.clone(), current_timestamp);
    }

    /// Endpoint to claim "ORE"
    #[endpoint(claim_ore)]
    fn claim_ore(&self) {
        let caller = self.blockchain().get_caller();
        let request_timestamp = self.mint_requests(&caller).get();

        // Ensure a request was made
        require!(request_timestamp > 0, "No mint request found");

        // Ensure 1 hour has passed since the request
        let one_hour_in_seconds = 3600;
        let current_timestamp = self.blockchain().get_block_timestamp();
        require!(
            current_timestamp >= request_timestamp + one_hour_in_seconds,
            "1 hour must pass before claiming ORE"
        );

        // Clear the mint request
        self.mint_requests(&caller).clear();

        // Calculate the amount of ORE to mint
        let ore_amount = BigUint::from(1u64);

        // Issue the ORE token
        let ore_token = TokenIdentifier::from("ORE".as_bytes());
        self.send().esdt_local_mint(&ore_token, 0, &ore_amount);
        self.send().direct_esdt(&caller, &ore_token, 0, &ore_amount);

        // Emit claim event
        self.claim_event(caller.clone());
    }

    /// Emit an event for mint request
    #[event("mint_request_event")]
    fn mint_request_event(&self, #[indexed] user: ManagedAddress, timestamp: u64);

    /// Emit an event for ORE claim
    #[event("claim_event")]
    fn claim_event(&self, #[indexed] user: ManagedAddress);

    /// Function to handle contract upgrades
    #[only_owner]
    #[upgrade]
    fn upgrade(&self) {}
}
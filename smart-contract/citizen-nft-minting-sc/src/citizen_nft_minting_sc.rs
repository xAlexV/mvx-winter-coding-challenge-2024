#![no_std]

use multiversx_sc::imports::*;

/// Smart contract to mint "CITIZEN" NFTs by burning required tokens.
#[multiversx_sc::contract]
pub trait CitizenNftMintingSc {
    /// Initializes the smart contract
    #[init]
    fn init(&self) {}

    /// Storage to track mint requests
    #[storage_mapper("mint_requests")]
    fn mint_requests(&self, user: &ManagedAddress) -> SingleValueMapper<u64>;

    /// Storage to track claimable NFTs for users
    #[storage_mapper("claimable_nfts")]
    fn claimable_nfts(&self, user: &ManagedAddress) -> SingleValueMapper<u64>;

    /// Endpoint to request minting a "CITIZEN" NFT
    #[payable("*")]
    #[endpoint(request_mint_citizen)]
    fn request_mint_citizen(&self) {
        let caller = self.blockchain().get_caller();
        let current_timestamp = self.blockchain().get_block_timestamp();

        // Require two payments: 10 WOOD and 15 FOOD
        let mut wood_amount = BigUint::zero();
        let mut food_amount = BigUint::zero();

        for payment in self.call_value().all_esdt_transfers().iter() {
            match payment.token_identifier.as_managed_buffer().to_boxed_bytes().as_ref() {
                b"WOOD" => wood_amount += payment.amount.clone(),
                b"FOOD" => food_amount += payment.amount.clone(),
                _ => require!(false, "Only WOOD and FOOD tokens are accepted"),
            }
        }

        // Validate the required amounts
        require!(wood_amount >= BigUint::from(10u64), "Insufficient WOOD tokens");
        require!(food_amount >= BigUint::from(15u64), "Insufficient FOOD tokens");

        // Burn the tokens
        self.send().esdt_local_burn(&TokenIdentifier::from("WOOD".as_bytes()), 0, &wood_amount);
        self.send().esdt_local_burn(&TokenIdentifier::from("FOOD".as_bytes()), 0, &food_amount);

        // Set the request timestamp
        self.mint_requests(&caller).set(current_timestamp);

        // Emit mint request event
        self.mint_request_event(caller.clone(), current_timestamp);
    }

    /// Endpoint to claim a "CITIZEN" NFT
    #[endpoint(claim_citizen)]
    fn claim_citizen(&self) {
        let caller = self.blockchain().get_caller();
        let request_timestamp = self.mint_requests(&caller).get();

        // Ensure a request was made
        require!(request_timestamp > 0, "No mint request found");

        // Ensure at least 1 hour has passed since the request
        let one_hour_in_seconds = 3600;
        let current_timestamp = self.blockchain().get_block_timestamp();
        require!(
            current_timestamp >= request_timestamp + one_hour_in_seconds,
            "1 hour must pass before claiming the NFT"
        );

        // Clear the mint request
        self.mint_requests(&caller).clear();

        // Issue the NFT
        let nft_token = TokenIdentifier::from("CITIZEN".as_bytes());
        self.send().esdt_local_mint(
            &nft_token,
            1, // Nonce for NFT
            &BigUint::from(1u64), // Single NFT
        );
        self.send().direct_esdt(&caller, &nft_token, 1, &BigUint::from(1u64));

        // Emit claim event
        self.claim_event(caller.clone());
    }

    /// Emit an event for mint request
    #[event("mint_request_event")]
    fn mint_request_event(&self, #[indexed] user: ManagedAddress, timestamp: u64);

    /// Emit an event for NFT claim
    #[event("claim_event")]
    fn claim_event(&self, #[indexed] user: ManagedAddress);

    /// Function to handle contract upgrades
    #[only_owner]
    #[upgrade]
    fn upgrade(&self) {}
}
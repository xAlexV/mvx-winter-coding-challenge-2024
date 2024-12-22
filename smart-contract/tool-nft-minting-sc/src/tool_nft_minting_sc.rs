#![no_std]

use multiversx_sc::imports::*;

/// Smart contract to mint NFTs, including "Shield" and other tools.
#[multiversx_sc::contract]
pub trait ToolNftMintingSc {
    /// Initializes the smart contract
    #[init]
    fn init(&self) {}

    /// Storage to track mint requests
    #[storage_mapper("mint_requests")]
    fn mint_requests(&self, user: &ManagedAddress) -> SingleValueMapper<u64>;

    /// Storage to track the token identifiers used for minting
    #[storage_mapper("token_identifiers")]
    fn token_identifiers(&self, user: &ManagedAddress) -> SingleValueMapper<TokenIdentifier<Self::Api>>;

    /// Endpoint to request minting a "Shield" NFT
    #[payable("*")]
    #[endpoint(request_mint_shield)]
    fn request_mint_shield(&self) {
        let caller = self.blockchain().get_caller();
        let current_timestamp = self.blockchain().get_block_timestamp();

        let mut ore_token_id = None;
        let mut ore_amount = BigUint::zero();

        for payment in self.call_value().all_esdt_transfers().iter() {
            let token_bytes = payment.token_identifier.as_managed_buffer().to_boxed_bytes();
            let token_bytes_slice = token_bytes.as_ref();

            if token_bytes_slice.starts_with(b"ORE-") {
                ore_token_id = Some(payment.token_identifier.clone());
                ore_amount += payment.amount.clone();
            } else {
                require!(false, "Only ORE tokens are accepted");
            }
        }

        require!(ore_token_id.is_some(), "ORE token is missing");
        require!(ore_amount >= BigUint::from(2u64), "Insufficient ORE tokens");

        // Save the token identifier for burning
        self.token_identifiers(&caller).set(ore_token_id.unwrap());

        // Burn the tokens
        self.send().esdt_local_burn(
            &self.token_identifiers(&caller).get(),
            0,
            &ore_amount,
        );

        // Set the mint request timestamp
        self.mint_requests(&caller).set(current_timestamp);

        // Emit mint request event
        self.mint_request_event(caller.clone(), current_timestamp);
    }

    /// Endpoint to claim a "Shield" NFT
    #[endpoint(claim_shield)]
    fn claim_shield(&self) {
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

        // Clear the mint request and token identifiers
        self.mint_requests(&caller).clear();
        self.token_identifiers(&caller).clear();

        // Issue the NFT
        let nft_token = TokenIdentifier::from("SHIELD".as_bytes());
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
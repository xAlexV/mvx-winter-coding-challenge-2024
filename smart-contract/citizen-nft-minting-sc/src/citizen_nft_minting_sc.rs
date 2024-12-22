#![no_std]

use multiversx_sc::imports::*;

/// Smart contract to mint "CITIZEN" NFTs and upgrade them to "SOLDIER" NFTs using dyNFT features.
#[multiversx_sc::contract]
pub trait CitizenNftMintingSc {
    /// Initializes the smart contract
    #[init]
    fn init(&self) {}

    /// Storage to track mint requests
    #[storage_mapper("mint_requests")]
    fn mint_requests(&self, user: &ManagedAddress) -> SingleValueMapper<u64>;

    /// Storage to track the token identifiers used for minting
    #[storage_mapper("token_identifiers")]
    fn token_identifiers(&self, user: &ManagedAddress) -> SingleValueMapper<(TokenIdentifier<Self::Api>, TokenIdentifier<Self::Api>)>;

    /// Storage to track upgrade requests
    #[storage_mapper("upgrade_requests")]
    fn upgrade_requests(&self, user: &ManagedAddress) -> SingleValueMapper<u64>;

    /// Endpoint to request minting a "CITIZEN" NFT
    #[payable("*")]
    #[endpoint(request_mint_citizen)]
    fn request_mint_citizen(&self) {
        let caller = self.blockchain().get_caller();
        let current_timestamp = self.blockchain().get_block_timestamp();

        let mut wood_token_id = None;
        let mut food_token_id = None;
        let mut wood_amount = BigUint::zero();
        let mut food_amount = BigUint::zero();

        for payment in self.call_value().all_esdt_transfers().iter() {
            let token_bytes = payment.token_identifier.as_managed_buffer().to_boxed_bytes();
            let token_bytes_slice = token_bytes.as_ref();

            if token_bytes_slice.starts_with(b"WOOD-") {
                wood_token_id = Some(payment.token_identifier.clone());
                wood_amount += payment.amount.clone();
            } else if token_bytes_slice.starts_with(b"FOOD-") {
                food_token_id = Some(payment.token_identifier.clone());
                food_amount += payment.amount.clone();
            } else {
                require!(false, "Only WOOD and FOOD tokens are accepted");
            }
        }

        require!(wood_token_id.is_some(), "WOOD token is missing");
        require!(food_token_id.is_some(), "FOOD token is missing");

        require!(wood_amount >= BigUint::from(10u64), "Insufficient WOOD tokens");
        require!(food_amount >= BigUint::from(15u64), "Insufficient FOOD tokens");

        self.token_identifiers(&caller).set((wood_token_id.unwrap(), food_token_id.unwrap()));

        self.send().esdt_local_burn(
            &self.token_identifiers(&caller).get().0,
            0,
            &wood_amount,
        );
        self.send().esdt_local_burn(
            &self.token_identifiers(&caller).get().1,
            0,
            &food_amount,
        );

        self.mint_requests(&caller).set(current_timestamp);

        self.mint_request_event(caller.clone(), current_timestamp);
    }

    /// Endpoint to claim a "CITIZEN" NFT
    #[endpoint(claim_citizen)]
    fn claim_citizen(&self) {
        let caller = self.blockchain().get_caller();
        let request_timestamp = self.mint_requests(&caller).get();

        require!(request_timestamp > 0, "No mint request found");

        let one_hour_in_seconds = 3600;
        let current_timestamp = self.blockchain().get_block_timestamp();
        require!(
            current_timestamp >= request_timestamp + one_hour_in_seconds,
            "1 hour must pass before claiming the NFT"
        );

        self.mint_requests(&caller).clear();
        self.token_identifiers(&caller).clear();

        let nft_token = TokenIdentifier::from("CITIZEN".as_bytes());
        self.send().esdt_local_mint(
            &nft_token,
            1,
            &BigUint::from(1u64),
        );
        self.send().direct_esdt(&caller, &nft_token, 1, &BigUint::from(1u64));

        self.claim_event(caller.clone());
    }

    /// Endpoint to request an upgrade from Citizen to Soldier
    #[payable("*")]
    #[endpoint(request_upgrade_to_soldier)]
    fn request_upgrade_to_soldier(&self, citizen_nonce: u64) {
        let caller = self.blockchain().get_caller();
        let current_timestamp = self.blockchain().get_block_timestamp();

        let mut gold_token_id = None;
        let mut ore_token_id = None;
        let mut gold_amount = BigUint::zero();
        let mut ore_amount = BigUint::zero();

        for payment in self.call_value().all_esdt_transfers().iter() {
            let token_bytes = payment.token_identifier.as_managed_buffer().to_boxed_bytes();
            let token_bytes_slice = token_bytes.as_ref();

            if token_bytes_slice.starts_with(b"GOLD-") {
                gold_token_id = Some(payment.token_identifier.clone());
                gold_amount += payment.amount.clone();
            } else if token_bytes_slice.starts_with(b"ORE-") {
                ore_token_id = Some(payment.token_identifier.clone());
                ore_amount += payment.amount.clone();
            } else {
                require!(false, "Only GOLD and ORE tokens are accepted");
            }
        }

        require!(gold_token_id.is_some(), "GOLD token is missing");
        require!(ore_token_id.is_some(), "ORE token is missing");
        require!(gold_amount >= BigUint::from(5u64), "Insufficient GOLD tokens");
        require!(ore_amount >= BigUint::from(5u64), "Insufficient ORE tokens");

        self.send().esdt_local_burn(&gold_token_id.unwrap(), 0, &gold_amount);
        self.send().esdt_local_burn(&ore_token_id.unwrap(), 0, &ore_amount);

        self.upgrade_requests(&caller).set(current_timestamp);

        self.upgrade_request_event(caller.clone(), citizen_nonce, current_timestamp);
    }

    /// Endpoint to finalize the upgrade to Soldier
    #[endpoint(claim_soldier)]
    fn claim_soldier(&self, citizen_nonce: u64) {
        let caller = self.blockchain().get_caller();
        let request_timestamp = self.upgrade_requests(&caller).get();

        require!(request_timestamp > 0, "No upgrade request found");

        let one_hour_in_seconds = 3600;
        let current_timestamp = self.blockchain().get_block_timestamp();
        require!(
            current_timestamp >= request_timestamp + one_hour_in_seconds,
            "1 hour must pass before claiming the upgrade"
        );

        self.upgrade_requests(&caller).clear();

        let nft_token = TokenIdentifier::from("CITIZEN".as_bytes());
        let new_attributes = ManagedBuffer::new_from_bytes(b"type:SOLDIER");
        self.send().nft_update_attributes(
            &nft_token,
            citizen_nonce,
            &new_attributes,
        );

        self.claim_event(caller.clone());
    }

    /// Emit an event for mint request
    #[event("mint_request_event")]
    fn mint_request_event(&self, #[indexed] user: ManagedAddress, timestamp: u64);

    /// Emit an event for upgrade request
    #[event("upgrade_request_event")]
    fn upgrade_request_event(&self, #[indexed] user: ManagedAddress, #[indexed] citizen_nonce: u64, timestamp: u64);

    /// Emit an event for NFT claim or upgrade
    #[event("claim_event")]
    fn claim_event(&self, #[indexed] user: ManagedAddress);

    /// Function to handle contract upgrades
    #[only_owner]
    #[upgrade]
    fn upgrade(&self) {}
}
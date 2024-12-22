#![no_std]

#[allow(unused_imports)]
use multiversx_sc::imports::*;

/// An empty contract. To be used as a template when starting a new contract from scratch.
#[multiversx_sc::contract]
pub trait ResourceMintingSc {
    /// Initializes the smart contract
    #[init]
    fn init(&self) {}

    /// Storage to track staked tokens for each user
    #[storage_mapper("stakes")]
    fn stakes(
        &self,
    ) -> MapMapper<
        (ManagedAddress<Self::Api>, TokenIdentifier<Self::Api>),
        BigUint<Self::Api>,
    >;

    /// Storage to track last minting round for each user
    #[storage_mapper("last_minting_round")]
    fn last_minting_round(&self, user: &ManagedAddress) -> SingleValueMapper<u64>;

    /// Endpoint to stake WINTER tokens
    #[payable("*")]
    #[endpoint(stake_winter)]
    fn stake_winter(&self) {
        let caller = self.blockchain().get_caller();

        // Require at least one payment to stake
        require!(
            !self.call_value().all_esdt_transfers().is_empty(),
            "At least one token must be staked"
        );

        for payment in self.call_value().all_esdt_transfers().iter() {
            let token_bytes = payment.token_identifier.as_managed_buffer().to_boxed_bytes();
            let token_bytes_slice = token_bytes.as_ref();

            // Validate token identifier prefix
            let prefix = b"WINTER-";
            require!(
                token_bytes_slice.starts_with(prefix),
                "Only WINTER tokens can be staked"
            );

            require!(payment.amount > 0, "Token amount must be greater than zero");

            let key = (caller.clone(), payment.token_identifier.clone());
            let current_stake = self.stakes().get(&key).unwrap_or_default();
            let new_stake = current_stake + payment.amount.clone();

            self.stakes().insert(key, new_stake);
        }

        // Set the last minting round to the current block round if not already set
        self.last_minting_round(&caller)
            .set_if_empty(self.blockchain().get_block_round());
    }

    /// Endpoint to mint resource tokens
    #[endpoint(mint_resources)]
    fn mint_resources(&self) {
        let caller = self.blockchain().get_caller();
        let current_round = self.blockchain().get_block_round();
        let last_round = self.last_minting_round(&caller).get();
        
        let resource_rounds = if self.blockchain().get_sc_address().as_managed_buffer().to_boxed_bytes().as_ref() == b"WOOD" {
            600
        } else if self.blockchain().get_sc_address().as_managed_buffer().to_boxed_bytes().as_ref() == b"FOOD" {
            1200
        } else if self.blockchain().get_sc_address().as_managed_buffer().to_boxed_bytes().as_ref() == b"STONE" {
            1800
        } else if self.blockchain().get_sc_address().as_managed_buffer().to_boxed_bytes().as_ref() == b"GOLD" {
            2400
        } else {
            require!(false, "Invalid resource contract identifier");
            return;
        };

        // Ensure enough rounds have passed for minting
        require!(
            current_round >= last_round + resource_rounds,
            "Not enough rounds have passed for minting"
        );

        // Calculate total mintable resources
        let mut total_mintable = BigUint::zero();
        for ((user_address, _token_identifier), staked_amount) in self.stakes().iter() {
            if user_address == caller {
                let mintable = staked_amount / 1000u64; // 1 unit per 1000 tokens
                total_mintable += mintable.clone();

                // Emit event for resource minting
                self.resource_mint_event(user_address, mintable.clone());
            }
        }

        require!(total_mintable > 0, "No resources to mint");

        // Mint and transfer the resource token
        let resource_token = TokenIdentifier::from("WOOD".as_bytes()); // Adjust dynamically as needed
        self.send().esdt_local_mint(
            &resource_token,
            0,
            &total_mintable,
        );
        self.send().direct_esdt(&caller, &resource_token, 0, &total_mintable);

        // Update the last minting round
        self.last_minting_round(&caller).set(current_round);
    }

    /// Emit an event for resource minting
    #[event("resource_mint_event")]
    fn resource_mint_event(
        &self,
        #[indexed] user: ManagedAddress,
        amount: BigUint,
    );

    /// Function to handle contract upgrades
    #[only_owner]
    #[upgrade]
    fn upgrade(&self) {}

}


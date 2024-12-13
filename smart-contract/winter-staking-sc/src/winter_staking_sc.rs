#![no_std]
use multiversx_sc::imports::*;

#[multiversx_sc::contract]
pub trait WinterStakingSc {
    #[init]
    fn init(&self) {}

    /// Storage to hold the staked tokens for each user
    #[storage_mapper("stakes")]
    fn stakes(
        &self,
    ) -> MapMapper<
        (ManagedAddress<Self::Api>, TokenIdentifier<Self::Api>),
        BigUint<Self::Api>,
    >;

    /// Storage to track staking start epochs for each user
    #[storage_mapper("stake_start_epoch")]
    fn stake_start_epoch(&self, user: &ManagedAddress) -> SingleValueMapper<u64>;

    /// Endpoint to stake WINTER tokens
    #[payable("*")]
    #[endpoint(stake_token_winter)]
    fn stake_token_winter(&self) {
        let caller = self.blockchain().get_caller();
        let current_epoch = self.blockchain().get_block_epoch();

        // Require at least one payment to stake
        require!(
            !self.call_value().all_esdt_transfers().is_empty(),
            "At least one token must be staked"
        );

        // Iterate over the tokens being staked
        for payment in self.call_value().all_esdt_transfers().iter() {
            // Convert the token identifier to a byte slice
            let token_bytes_boxed = payment.token_identifier.as_managed_buffer().to_boxed_bytes();
            let token_bytes = token_bytes_boxed.as_ref();

            // Validate that the token identifier starts with "WINTER-"
            let prefix = b"WINTER-";
            require!(
                token_bytes.starts_with(prefix),
                "Only WINTER tokens can be staked"
            );
            
            require!(
                payment.amount > 0,
                "Token amount must be greater than zero"
            );

            let key = (caller.clone(), payment.token_identifier.clone());
            let current_stake = self.stakes().get(&key).unwrap_or_default();
            let new_stake = current_stake + payment.amount.clone();

            self.stakes().insert(key, new_stake);

            // Emit event
            self.stake_event(
                caller.clone(),
                current_epoch,
                (payment.token_identifier.clone(), payment.amount.clone()),
            );
        }

        // Record the epoch of the first stake for this user if not already set
        if self.stake_start_epoch(&caller).is_empty() {
            self.stake_start_epoch(&caller).set(current_epoch);
        }
    }

    /// Emit an event for staking
    #[event("stake_event")]
    fn stake_event(
        &self,
        #[indexed] user: ManagedAddress,
        #[indexed] epoch: u64,
        stake_data: (TokenIdentifier, BigUint),
    );

    /// Function to handle contract upgrades
    #[only_owner]
    #[upgrade]
    fn upgrade(&self) {}
}
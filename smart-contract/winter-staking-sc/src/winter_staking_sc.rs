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

    /// Storage to track the last reward claim timestamp for each user
    #[storage_mapper("last_reward_claim")]
    fn last_reward_claim(&self, user: &ManagedAddress) -> SingleValueMapper<u64>;

    /// Storage to track the beneficiary for reward transfers
    #[storage_mapper("beneficiary")]
    fn beneficiary(&self, user: &ManagedAddress) -> SingleValueMapper<ManagedAddress<Self::Api>>;

    /// Endpoint to set or update the beneficiary
    #[endpoint(set_beneficiary)]
    fn set_beneficiary(&self, new_beneficiary: ManagedAddress) {
        let caller = self.blockchain().get_caller();

        // Ensure the beneficiary address is valid and different from the caller
        require!(
            new_beneficiary != caller,
            "Beneficiary cannot be the same as the caller"
        );

        self.beneficiary(&caller).set(new_beneficiary.clone());

        // Emit an event for beneficiary update
        self.beneficiary_set_event(caller, new_beneficiary);
    }

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

        // Initialize the last reward claim time
        self.last_reward_claim(&caller).set_if_empty(self.blockchain().get_block_timestamp());
    }

    /// Emit an event for staking
    #[event("stake_event")]
    fn stake_event(
        &self,
        #[indexed] user: ManagedAddress,
        #[indexed] epoch: u64,
        stake_data: (TokenIdentifier, BigUint),
    );

    /// Endpoint to claim rewards
    #[endpoint(claim_rewards)]
    fn claim_rewards(&self) {
        let caller = self.blockchain().get_caller();
        let current_timestamp = self.blockchain().get_block_timestamp();
        let last_claim = self.last_reward_claim(&caller).get();

        // Ensure 24 hours have passed since the last claim
        let one_day_in_seconds = 24 * 60 * 60;
        require!(
            current_timestamp >= last_claim + one_day_in_seconds,
            "Rewards can only be claimed once every 24 hours"
        );

        let mut total_rewards = BigUint::zero();
        for ((user_address, token_identifier), staked_amount) in self.stakes().iter() {
            if user_address == caller {
                let reward = staked_amount.clone() / 100u64; // 1% of staked tokens
                total_rewards += reward.clone();

                // Emit reward distribution event
                self.reward_event(user_address.clone(), token_identifier.clone(), reward.clone());
            }
        }

        require!(total_rewards > 0, "No rewards available to claim");

        // Determine the reward recipient
        let reward_recipient = if self.beneficiary(&caller).is_empty() {
            caller.clone()
        } else {
            self.beneficiary(&caller).get()
        };

        // Mint reward tokens
        let reward_token = TokenIdentifier::from("SNOW-ab6b96".as_bytes());
        self.send().esdt_local_mint(
            &reward_token,
            0,
            &total_rewards,
        );

        // Transfer rewards to the recipient
        self.send().direct_esdt(
            &reward_recipient,
            &reward_token,
            0,
            &total_rewards,
        );

        // Update the last reward claim timestamp
        self.last_reward_claim(&caller).set(current_timestamp);
    }

    /// Emit an event for setting a beneficiary
    #[event("beneficiary_set_event")]
    fn beneficiary_set_event(
        &self,
        #[indexed] user: ManagedAddress,
        #[indexed] beneficiary: ManagedAddress,
    );


    /// Emit an event for rewards
    #[event("reward_event")]
    fn reward_event(
        &self,
        #[indexed] user: ManagedAddress,
        #[indexed] token_identifier: TokenIdentifier,
        reward_amount: BigUint,
    );

    /// Function to handle contract upgrades
    #[only_owner]
    #[upgrade]
    fn upgrade(&self) {}
}
#![no_std]

use multiversx_sc::imports::*;
use multiversx_sc::derive_imports::*;

#[type_abi]
#[derive(TopEncode, TopDecode, NestedEncode, NestedDecode)]
pub struct Soldier<M: ManagedTypeApi> {
    pub token_id: TokenIdentifier<M>,
    pub nonce: u64,
    pub attack: u32,
    pub defense: u32,
}

#[type_abi]
#[derive(TopEncode, TopDecode, NestedEncode, NestedDecode)]
pub struct Game<M: ManagedTypeApi> {
    pub initiator: ManagedAddress<M>,
    pub competitor: ManagedAddress<M>,
    pub soldier_initiator: Soldier<M>,
    pub soldier_competitor: Option<Soldier<M>>,
    pub entrance_fee: BigUint<M>,
    pub completed: bool,
}

#[multiversx_sc::contract]
pub trait ArenaSc {
    #[init]
    fn init(&self) {}

    #[storage_mapper("games")]
    fn games(&self, game_id: &ManagedBuffer) -> SingleValueMapper<Game<Self::Api>>;

    #[storage_mapper("deposits")]
    fn deposits(&self, user: &ManagedAddress<Self::Api>) -> SingleValueMapper<BigUint<Self::Api>>;

    #[payable("EGLD")]
    #[endpoint(createGame)]
    fn create_game(
        &self,
        game_id: ManagedBuffer,
        soldier_token_id: TokenIdentifier<Self::Api>,
        soldier_nonce: u64,
        entrance_fee: BigUint<Self::Api>,
    ) {
        let caller = self.blockchain().get_caller();
        let deposit = self.call_value().egld_value();

        require!(&*deposit >= &entrance_fee, "Deposit must cover the entrance fee");

        self.games(&game_id).set(Game {
            initiator: caller.clone(),
            competitor: ManagedAddress::zero(),
            soldier_initiator: Soldier {
                token_id: soldier_token_id,
                nonce: soldier_nonce,
                attack: 0,
                defense: 0,
            },
            soldier_competitor: None,
            entrance_fee: entrance_fee.clone(),
            completed: false,
        });

        self.deposits(&caller).update(|balance| balance.add_assign(&*deposit));
    }

    #[payable("EGLD")]
    #[endpoint(joinGame)]
    fn join_game(
        &self,
        game_id: ManagedBuffer,
        soldier_token_id: TokenIdentifier<Self::Api>,
        soldier_nonce: u64,
    ) {
        let caller = self.blockchain().get_caller();
        let deposit = self.call_value().egld_value();

        let mut game = self.games(&game_id).get();

        require!(game.competitor.is_zero(), "Game already has a competitor");
        require!(&*deposit >= &game.entrance_fee, "Deposit must cover the entrance fee");

        game.competitor = caller.clone();
        game.soldier_competitor = Some(Soldier {
            token_id: soldier_token_id,
            nonce: soldier_nonce,
            attack: 0,
            defense: 0,
        });

        self.games(&game_id).set(game);
        self.deposits(&caller).update(|balance| balance.add_assign(&*deposit));
    }

    #[endpoint(startFight)]
    fn start_fight(&self, game_id: ManagedBuffer) {
        let mut game = self.games(&game_id).get();

        require!(!game.completed, "Game already completed");
        require!(
            !game.competitor.is_zero() && game.soldier_competitor.is_some(),
            "Game conditions not met"
        );

        let initiator_soldier = &game.soldier_initiator;
        let competitor_soldier = game.soldier_competitor.as_ref().unwrap();

        let initiator_score = initiator_soldier.attack + initiator_soldier.defense;
        let competitor_score = competitor_soldier.attack + competitor_soldier.defense;

        let initiator_chance = if initiator_score >= competitor_score {
            (50 + ((initiator_score - competitor_score).min(5000) / 100) as u32).min(100)
        } else {
            (50 - ((competitor_score - initiator_score).min(5000) / 100) as u32).max(0)
        };

        let random_seed = self.blockchain().get_block_random_seed();
        let random_seed_buffer = random_seed.as_managed_buffer();
        let mut seed_bytes = [0u8; 8];
        random_seed_buffer.load_slice(0, &mut seed_bytes).unwrap();
        let random = u64::from_be_bytes(seed_bytes);

        let winner = if random % 100 < initiator_chance as u64 {
            &game.initiator
        } else {
            &game.competitor
        };

        let total_deposit = self.deposits(&game.initiator).get() + self.deposits(&game.competitor).get();

        self.send().direct_egld(winner, &total_deposit);
        self.send().direct_esdt(
            winner,
            &game.soldier_initiator.token_id,
            game.soldier_initiator.nonce,
            &BigUint::from(1u64),
        );

        game.completed = true;
        self.games(&game_id).set(game);
    }

    #[only_owner]
    #[upgrade]
    fn upgrade(&self) {}
}
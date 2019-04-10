from eth2spec.phase0.spec import *
from eth2spec.phase0.state_transition import expected_deposit_count
from eth2spec.phase0.state_transition import state_transition_to, process_block
from random import Random
from copy import deepcopy
from typing import List
from py_ecc import bls

from eth2spec.utils.merkle_minimal import get_merkle_root

import deposit_helpers


def apply_random_block(state: BeaconState,
                       existing_deposits: List[Deposit],
                       validator_creds: Dict[BLSPubkey, deposit_helpers.ValidatorCreds],
                       seed: int) -> BeaconBlock:

    rng = Random(seed)

    def random_randao_reveal() -> BLSSignature:
        return int_to_bytes96(rng.randint(1, 2**(96*8)-1))

    def random_root() -> Bytes32:
        return int_to_bytes32(rng.randint(1, 2**(32*8)-1))

    def random_deposits(dep_count: int) -> List[Deposit]:
        if dep_count is 0:
            return []

        # start creating new different fake privkeys based on deposit index
        validator_id = state.deposit_index

        new_validator_creds = deposit_helpers.create_validator_creds(validator_id, dep_count)
        new_deposits = deposit_helpers.create_deposits(new_validator_creds, existing_deposits)
        return new_deposits

    def random_eth1_data() -> Eth1Data:
        # 10% chance of voting for new eth1 data, 90% chance of voting for random existing data
        if rng.randint(0, 9) > 0 and len(state.eth1_data_votes) > 0:
            # Just vote for the most recently added eth1 data
            possible_target = len(state.eth1_data_votes) - 1
            # But do not vote if it is not outdated data
            # TODO: spec accepts votes for eth1 data with lower deposit count than latest,
            #  completely messing up the deposit system if a majority can get such eth1 data through.
            if state.eth1_data_votes[possible_target].eth1_data.deposit_count >= state.latest_eth1_data.deposit_count:
                return state.eth1_data_votes[possible_target].eth1_data

        dep_count = rng.randint(0, MAX_DEPOSITS * 2)
        new_deposits = random_deposits(dep_count)
        deposit_data_leaves = [hash(deposit.data.serialize()) for deposit in (existing_deposits + new_deposits)]
        deps_root = get_merkle_root((tuple(deposit_data_leaves)))

        return Eth1Data(
            deposit_root=deps_root,
            deposit_count=len(existing_deposits) + dep_count,
            block_hash=random_root()
        )

    def random_proposer_slashing(active_validators: List[int]) -> ProposerSlashing:
        proposer_slot = state.slot - rng.randint(0, SLOTS_PER_EPOCH)

        proposer_index = active_validators[rng.randint(0, len(active_validators))]
        proposer = state.validator_registry[proposer_index]
        proposer_creds = validator_creds[proposer.pubkey]
        prev_block_root=get_block_root(state, proposer_slot - 1)

        domain = get_domain(
            fork=state.fork,
            epoch=slot_to_epoch(proposer_slot),
            domain_type=DOMAIN_BEACON_BLOCK,
        )
        bh1 = BeaconBlockHeader(
            slot=proposer_slot,
            previous_block_root=prev_block_root,
            state_root=random_root(),
            block_body_root=random_root(),
            signature=EMPTY_SIGNATURE
        )
        # Too slow, BLS stub will accept empty signature
        # bh1.signature = bls.sign(
        #     privkey=proposer_creds[0][1],
        #     message_hash=signed_root(bh1),
        #     domain=domain
        # )

        bh2 = BeaconBlockHeader(
            slot=proposer_slot,
            previous_block_root=prev_block_root,
            state_root=random_root(),
            block_body_root=random_root(),
            signature=EMPTY_SIGNATURE
        )
        # Too slow, BLS stub will accept empty signature
        # bh2.signature = bls.sign(
        #     privkey=proposer_creds[0][1],
        #     message_hash=signed_root(bh2),
        #     domain=domain
        # )

        return ProposerSlashing(
            proposer_index=proposer_index,
            header_1=bh1,
            header_2=bh2,
        )

    # Note: simulation is not so pessimistic here. If there are more slots skipped,
    # then we do not reach 50% of proposers to even vote in an eth1 voting period, and cannot on-board new validators...
    # TODO: maybe improve spec here?
    slots = 1
    # 10% chance of having some drop-out of proposers
    if rng.randint(0, 9) == 0:
        slots = rng.randint(1, max(4, SLOTS_PER_EPOCH // 4))

    previous_block_header = deepcopy(state.latest_block_header)
    if previous_block_header.state_root == ZERO_HASH:
        previous_block_header.state_root = hash_tree_root(state)
    previous_block_root = signed_root(previous_block_header)

    eth1_data = random_eth1_data()
    randao_reveal = random_randao_reveal()

    target_slot = state.slot + slots

    proposer = None
    # Make the transition of the state, right up to the block itself
    for i in range(len(state.validator_registry)):
        state_transition_to(state, target_slot)

        proposer_index = get_beacon_proposer_index(state, target_slot)
        proposer = state.validator_registry[proposer_index]
        if not proposer.slashed:
            break
        # Try next slot
        target_slot += 1

    if proposer.slashed:
        # Cannot find a proposer, the chain is dead.
        return None

    current_epoch = get_current_epoch(state)
    active_validators = get_active_validator_indices(state.validator_registry, current_epoch)

    # create the expected amount of deposits
    #  (we can determine the count properly now that we transitioned right up to the slot)
    expected_deposits = expected_deposit_count(state)
    total_deposits_work = state.latest_eth1_data.deposit_count - state.deposit_index

    # Create deposits for total work, to match the root etc.
    # But only include the deposits that are expected (i.e. the allowed deposit count)
    deps = random_deposits(total_deposits_work)[:expected_deposits]

    proposer_slashings = []
    if rng.randint(0, 9) == 0:
        proposer_slashings.extend(
            [random_proposer_slashing(active_validators) for _ in
             range(rng.randint(0, min(MAX_PROPOSER_SLASHINGS, 3)))])

    # TODO: future for 0.6.x: attester slashings, attestations, exits, transfers

    block = BeaconBlock(
        slot=target_slot,
        previous_block_root=previous_block_root,
        state_root=ZERO_HASH,
        body=BeaconBlockBody(
            randao_reveal=randao_reveal,
            eth1_data=eth1_data,
            proposer_slashings=proposer_slashings,
            attester_slashings=[],
            attestations=[],
            deposits=deps,
            voluntary_exits=[],
            transfers=[],
        ),
        signature=EMPTY_SIGNATURE,
    )

    # We are not signing blocks, too slow for test generation. BLS stub will just accept it
    #
    # domain = get_domain(
    #     fork=state.fork,
    #     epoch=current_epoch,
    #     domain_type=DOMAIN_BEACON_BLOCK,
    # )

    # block.signature = bls.sign(
    #     privkey=validator_creds[proposer.pubkey][0][1],
    #     message_hash=signed_root(block),
    #     domain=domain
    # )

    process_block(state, block)

    return block

from gen_base import gen_runner, gen_suite, gen_typing

from eth_utils import (
    to_dict, to_tuple
)

from preset_loader import loader
from eth2spec.debug.encode import encode
from eth2spec.phase0 import spec
from typing import List, Dict

import deposit_helpers
import genesis
import random_block


@to_dict
def sim_blocks_case(pre_state: spec.BeaconState,
                    existing_deposits: List[spec.Deposit],
                    validator_creds: Dict[spec.BLSPubkey, deposit_helpers.ValidatorCreds]):
    # copy state before changes are made
    yield "pre", encode(pre_state, spec.BeaconState)

    state = pre_state
    blocks = []
    # simulate enough blocks to cover a good amount of epochs
    for i in range(spec.SLOTS_PER_EPOCH * 2):
        # Prepare a new block, simply use the slot number as a seed to create a new random block
        b = random_block.apply_random_block(state=state,
                                            existing_deposits=existing_deposits,
                                            validator_creds=validator_creds,
                                            seed=state.slot)
        print("simulated block %d " % len(blocks))
        blocks.append(b)

        existing_deposits.extend(b.body.deposits)

        validator_count = len(state.validator_registry)
        if validator_count > len(validator_creds):
            start_id = len(validator_creds)
            validator_creds.update(deposit_helpers.create_validator_creds(start_id=start_id, count=validator_count - start_id))

    yield "blocks", [encode(b, spec.BeaconBlock) for b in blocks]
    yield "post", encode(state, spec.BeaconState)


@to_tuple
def generate_sim_blocks_test_cases():
    validator_count = 300
    validator_creds = deposit_helpers.create_validator_creds(0, validator_count)
    deps = deposit_helpers.create_deposits(validator_creds, [])
    state = genesis.create_genesis_state(deps)
    # Create 5 test cases, extending a chain with simulated blocks from the genesis state
    for i in range(5):
        print("generating sim_blocks case %d " % i)
        yield sim_blocks_case(state, deps, validator_creds)


def sim_blocks_minimal_suite(configs_path: str) -> gen_typing.TestSuiteOutput:
    presets = loader.load_presets(configs_path, 'minimal')
    spec.apply_constants_preset(presets)

    return ("sim_blocks_mini", "core", gen_suite.render_suite(
        title="simulated blocks minimal",
        summary="Minimal configured state transition suite, testing transitions with multiple blocks at a time.",
        forks_timeline="testing",
        forks=["phase0"],
        config="minimal",
        handler="core",
        test_cases=generate_sim_blocks_test_cases()))

# Disabled for now, may do full mainnet-esque tests later. Just unnecessarily slows down CI at this point.
# def sim_blocks_mainnet_suite(configs_path: str) -> gen_typing.TestSuiteOutput:
#     presets = loader.load_presets(configs_path, 'mainnet')
#     spec.apply_constants_preset(presets)
#
#     return ("sim_blocks_full", "core", gen_suite.render_suite(
#         title="simulated blocks full",
#         summary="Mainnet-like configured state transition suite, testing transitions multiple blocks at a time.",
#         forks_timeline="mainnet",
#         forks=["phase0"],
#         config="testing",
#         handler="core",
#         test_cases=generate_sim_blocks_test_cases()))


if __name__ == "__main__":
    gen_runner.run_generator("state_transition", [sim_blocks_minimal_suite])

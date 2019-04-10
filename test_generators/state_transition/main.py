from gen_base import gen_runner, gen_suite, gen_typing

from eth_utils import (
    to_dict, to_tuple
)

from preset_loader import loader
from eth2spec.debug.encode import encode
from eth2spec.phase0 import spec
from typing import List

import deposit_helpers
import genesis
import random_block


@to_dict
def sim_blocks_case(pre_state: spec.BeaconState, existing_deposits: List[spec.Deposit]):
    # copy state before changes are made
    yield "pre", encode(pre_state, spec.BeaconState)

    state = pre_state
    blocks = []
    for i in range(spec.SLOTS_PER_EPOCH):
        # Prepare a new block, simply use the slot number as a seed to create a new random block
        b = random_block.apply_random_block(state=state, existing_deposits=existing_deposits, seed=state.slot)
        blocks.append(b)

        existing_deposits.extend(b.body.deposits)

    yield "blocks", [encode(b, spec.BeaconBlock) for b in blocks]
    yield "post", encode(state, spec.BeaconState)


@to_tuple
def generate_per_block_test_cases():
    validator_count = spec.SHARD_COUNT * spec.TARGET_COMMITTEE_SIZE * 10
    validator_creds = deposit_helpers.create_validator_creds(0, validator_count)
    deps = deposit_helpers.create_deposits(validator_creds, [])
    state = genesis.create_genesis_state(deps)
    # Create 10 test cases, extending a chain with simulated blocks from the genesis state
    for i in range(10):
        yield sim_blocks_case(state, deps)


def per_block_minimal_suite(configs_path: str) -> gen_typing.TestSuiteOutput:
    presets = loader.load_presets(configs_path, 'minimal')
    spec.apply_constants_preset(presets)

    return ("single_block_mini", "core", gen_suite.render_suite(
        title="single block minimal",
        summary="Minimal configured state transition suite, testing transitions one block at a time.",
        forks_timeline="testing",
        forks=["phase0"],
        config="minimal",
        handler="core",
        test_cases=generate_per_block_test_cases()))


def per_block_mainnet_suite(configs_path: str) -> gen_typing.TestSuiteOutput:
    presets = loader.load_presets(configs_path, 'mainnet')
    spec.apply_constants_preset(presets)

    return ("single_block_full", "core", gen_suite.render_suite(
        title="single block full",
        summary="Mainnet-like configured state transition suite, testing transitions one block at a time.",
        forks_timeline= "mainnet",
        forks=["phase0"],
        config="testing",
        handler="core",
        test_cases=generate_per_block_test_cases()))


if __name__ == "__main__":
    gen_runner.run_generator("example", [per_block_minimal_suite])

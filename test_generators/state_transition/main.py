from copy import deepcopy
from gen_base import gen_runner, gen_suite, gen_typing

from eth_utils import (
    to_dict, to_tuple
)

from preset_loader import loader
from eth2spec.phase0 import spec
from eth2spec.utils.minimal_ssz import signed_root
from eth2spec.phase0.state_transition import state_transition

import genesis


@to_dict
def example_test_case(pre_state: spec.BeaconState):
    # copy state before changes are made
    yield "pre", deepcopy(pre_state)
    blocks = []
    state = pre_state
    for i in range(10):
        # Prepare a new block
        b = spec.get_empty_block()
        b.slot = state.slot + 1
        previous_block_header = deepcopy(state.latest_block_header)
        if previous_block_header.state_root == spec.ZERO_HASH:
            previous_block_header.state_root = state.hash_tree_root()
        b.previous_block_root = signed_root(previous_block_header)
        # Fill the block with random data
        # TODO

        blocks.append(b)
        state_transition(state, b)
    yield "blocks", blocks
    yield "post", state


@to_tuple
def generate_example_test_cases():
    validator_count = spec.SHARD_COUNT * spec.TARGET_COMMITTEE_SIZE * 10
    dummies = genesis.create_dummies(validator_count)
    deps = genesis.create_mock_genesis_validator_deposits(dummies)
    state = genesis.create_genesis_state(deps)
    for i in range(20):
        yield example_test_case(state)


def example_minimal_suite(configs_path: str) -> gen_typing.TestSuiteOutput:
    presets = loader.load_presets(configs_path, 'minimal')
    spec.apply_constants_preset(presets)

    return ("mini", "core", gen_suite.render_suite(
        title="example_minimal",
        summary="Minimal example suite, testing bar.",
        forks_timeline="testing",
        forks=["phase0"],
        config="minimal",
        handler="core",
        test_cases=generate_example_test_cases()))


def example_mainnet_suite(configs_path: str) -> gen_typing.TestSuiteOutput:
    presets = loader.load_presets(configs_path, 'mainnet')
    spec.apply_constants_preset(presets)

    return ("full", "core", gen_suite.render_suite(
        title="example_main_net",
        summary="Main net based example suite.",
        forks_timeline= "mainnet",
        forks=["phase0"],
        config="testing",
        handler="core",
        test_cases=generate_example_test_cases()))


if __name__ == "__main__":
    gen_runner.run_generator("example", [example_minimal_suite, example_mainnet_suite])

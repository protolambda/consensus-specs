from gen_base import gen_runner, gen_suite, gen_typing

from eth_utils import (
    to_dict, to_tuple
)

from preset_loader import loader
from eth2spec.phase0 import spec

@to_dict
def example_test_case(v: int):
    yield "spec_SHARD_COUNT", spec.SHARD_COUNT
    yield "example", v


@to_tuple
def generate_example_test_cases():
    for i in range(10):
        yield example_test_case(i)


def example_minimal_suite(configs_path: str) -> gen_typing.TestSuite:
    minimal_presets = loader.load_presets(configs_path, 'minimal')
    spec.apply_constants_preset(minimal_presets)

    return gen_suite.render_suite(
        title="example_minimal",
        summary="Minimal example suite, testing bar.",
        fork="v0.5.1",
        config="minimal",
        test_cases=generate_example_test_cases())


def example_mainnet_suite(configs_path: str) -> gen_typing.TestSuite:
    minimal_presets = loader.load_presets(configs_path, 'main_net')
    spec.apply_constants_preset(minimal_presets)

    return gen_suite.render_suite(
        title="example_main_net",
        summary="Main net based example suite.",
        fork="v0.5.1",
        config="main_net",
        test_cases=generate_example_test_cases())


if __name__ == "__main__":
    gen_runner.run_generator("example", [example_minimal_suite, example_mainnet_suite])

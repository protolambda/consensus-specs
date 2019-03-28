from gen_base import gen_runner, gen_suite, gen_typing
from eth2.phase0 import spec

from eth_utils import (
    to_dict, to_tuple
)

@to_dict
def bar_test_case(v: int):
    yield "bar_v", v
    yield "bar_spec_thing", spec.SHARD_COUNT


@to_tuple
def generate_bar_test_cases():
    for i in range(10):
        yield bar_test_case(i)


def bar_test_suite() -> gen_typing.TestSuite:
    return gen_suite.render_suite(
        title="bar_minimal",
        summary="Minimal example suite using base gen and pyspec, testing bar.",
        fork="v0.5.1",
        config="minimal",
        test_cases=generate_bar_test_cases())


if __name__ == "__main__":
    gen_runner.run_generator("bar", [bar_test_suite])
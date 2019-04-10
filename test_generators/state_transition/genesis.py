from eth2spec.phase0.spec import *
from typing import List, Tuple

from eth2spec.utils.merkle_minimal import (
    get_merkle_root
)


def create_genesis_state(deposits: List[Deposit]) -> Tuple[BeaconState, List[Deposit]]:
    deposit_root = get_merkle_root((tuple([hash(dep.data.serialize()) for dep in deposits])))

    return get_genesis_beacon_state(
        deposits,
        genesis_time=0,
        genesis_eth1_data=Eth1Data(
            deposit_root=deposit_root,
            deposit_count=len(deposits),
            block_hash=ZERO_HASH,
        ),
    )

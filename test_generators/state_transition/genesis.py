from eth2spec.phase0.spec import *
from typing import List

from eth2spec.utils.merkle_minimal import (
    calc_merkle_tree_from_leaves,
    get_merkle_proof,
    get_merkle_root,
)

from py_ecc import bls


# ((pub key, priv key (main)), (pub key, priv key (withdrawal))
Dummy = Tuple[Tuple[BLSPubkey, int], Tuple[BLSPubkey, int]]


# create mock validator set
def create_dummies(count: int) -> List[Dummy]:
    return [((bls.privtopub(i), i), (bls.privtopub(i + 1), i + 1)) for i in range(2, (count + 1) * 2, 2)]


def create_mock_genesis_validator_deposits(dummies):
    deposit_data_leaves = []
    proof_of_possession = b'\x33' * 96

    deposit_data_list = []
    for dummy in dummies:
        i = len(deposit_data_list)
        deposit_data = DepositData(
            pubkey=dummy[0][0],
            withdrawal_credentials=BLS_WITHDRAWAL_PREFIX_BYTE + hash(dummy[1][0])[1:],
            amount=MAX_DEPOSIT_AMOUNT,
            proof_of_possession=proof_of_possession,
        )
        item = hash(deposit_data.serialize())
        deposit_data_leaves.append(item)
        tree = calc_merkle_tree_from_leaves(tuple(deposit_data_leaves))
        root = get_merkle_root((tuple(deposit_data_leaves)))
        proof = list(get_merkle_proof(tree, item_index=i))
        assert verify_merkle_branch(item, proof, DEPOSIT_CONTRACT_TREE_DEPTH, i, root)
        deposit_data_list.append(deposit_data)

    genesis_validator_deposits = [Deposit(
            proof=list(get_merkle_proof(tree, item_index=i)),
            index=i,
            data=deposit_data_list[i]
        ) for i in range(len(dummies))]

    return genesis_validator_deposits


def create_genesis_state(deposits: List[Deposit]):
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

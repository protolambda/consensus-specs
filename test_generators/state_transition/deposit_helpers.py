from eth2spec.phase0.spec import *
from typing import List, Tuple

from eth2spec.utils.merkle_minimal import (
    calc_merkle_tree_from_leaves,
    get_merkle_proof,
    get_merkle_root,
)

from py_ecc import bls


# credentials for a validator: ((pub key, priv key (main)), (pub key, priv key (withdrawal))
ValidatorCreds = Tuple[Tuple[BLSPubkey, int], Tuple[BLSPubkey, int]]


# create mock validator set, based on a range of IDs
def create_validator_creds(start_id, count: int) -> Dict[BLSPubkey, ValidatorCreds]:
    creds = [((bls.privtopub(i), i), (bls.privtopub(i + 1), i + 1)) for i in
            range(start_id * 2 + 2, (start_id + count) * 2 + 2, 2)]
    return {cred[0][0]: cred for cred in creds}


def create_deposits(new_validators: Dict[BLSPubkey, ValidatorCreds], existing_deposits: List[Deposit] = None):
    if existing_deposits is None:
        existing_deposits = []
    # Fill tree with existing deposits
    deposit_data_leaves = [hash(deposit.data.serialize()) for deposit in existing_deposits]

    # Mock proof of possession
    proof_of_possession = b'\x33' * 96

    deposit_data_list = []
    for pubkey, creds in new_validators.items():
        deposit_data = DepositData(
            pubkey=pubkey,
            withdrawal_credentials=BLS_WITHDRAWAL_PREFIX_BYTE + hash(creds[1][0])[1:],
            amount=MAX_DEPOSIT_AMOUNT,
            proof_of_possession=proof_of_possession,
        )
        item = hash(deposit_data.serialize())
        deposit_data_leaves.append(item)
        deposit_data_list.append(deposit_data)

    tree = calc_merkle_tree_from_leaves(tuple(deposit_data_leaves))

    deposits = [Deposit(
            proof=list(get_merkle_proof(tree, item_index=len(existing_deposits) + i)),
            index=len(existing_deposits) + i,
            data=deposit_data_list[i]
        ) for i in range(len(deposit_data_list))]

    return deposits



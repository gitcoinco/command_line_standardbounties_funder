import json

from two1.bitcoin.crypto import HDPrivateKey, HDKey
from eth_utils import encode_hex
from utils import sha3


def ethereumAddressFromBytes(seed):
    return encode_hex(sha3(seed[1:])[12:])

class Wallet:
    def __init__(self, mnemonic, child):
        master_key = HDPrivateKey.master_key_from_mnemonic(mnemonic)
        root_keys = HDKey.from_path(master_key,"m/44'/60'/0'")
        acct_priv_key = root_keys[-1]
        keys = HDKey.from_path(acct_priv_key,'{change}/{index}'.format(change=0, index=child))

        self.address = ethereumAddressFromBytes(bytes(keys[-1].public_key._key))
        self.private_key = keys[-1]._key.to_hex()

    @staticmethod
    def from_json(path, child):
        with open(path) as f:
            data = json.load(f)

        return Wallet(data.get('mnemonic'), child)

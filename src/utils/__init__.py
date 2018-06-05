from Crypto.Hash import keccak

sha3_256 = lambda x: keccak.new(digest_bits=256, data=x)

def sha3(seed):
    return sha3_256(seed).digest()

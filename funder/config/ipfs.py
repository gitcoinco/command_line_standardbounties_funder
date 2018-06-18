import ipfsapi

def ipfs_client():
    return ipfsapi.connect('https://ipfs.infura.io', 5001)

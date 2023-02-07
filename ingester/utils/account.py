
def is_contract(addr: str, client):
    return client.eth.get_code(addr).hex() != "0x" 
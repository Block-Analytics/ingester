
def is_contract(addr: str, client):
    if addr == "" or addr == None:
        return False
    return client.eth.get_code(addr).hex() != "0x" 
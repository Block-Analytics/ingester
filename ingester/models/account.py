from pydgraph.client import DgraphClient
# import web3

class Account:
    address: str
    account_type: str
    # transactions_send: list
    # transactions_received: list
    type: str = "Account"

    def __init__(self, address, account_type) -> None:
        self.address = address
        self.account_type = account_type
    
    def to_json(self):
        return {
            "address": self.address,
            "dgraph.type": self.type
        }

# class Contract(Account):
#     type: str = "Contract"
    
#     def __init__(self, address, w3) -> None:
#         Account.__init__(self, address, w3)

from gql import Client, gql
from web3.types import TxData

from ingester.models.account import AccountType

class Transaction:
    hash: str
    nonce: int
    from_address: str
    to_address: str
    tags: list

    def __init__(self, chain:str, txData: TxData, additionnal_info: dict):
        self.tx_hash = txData["hash"].hex()
        self.nonce = txData["nonce"]
        self.from_account = txData["from"]
        self.to_account = txData["to"]
        self.block_number = txData["blockNumber"]
        self.gas = txData["gas"]
        self.gas_price = txData["gasPrice"]
        self.input = txData.get("input", "")
        self.chain = chain
        self.additionnal_info = additionnal_info

    def to_json(self):
        values = {
            "hash": self.tx_hash,
            "nonce": self.nonce,
            "gas": self.gas,
            "gasPrice": self.gas_price,
            "input": self.input,
            "block": {"number": self.block_number},
            "chain": {"id": self.chain}
        }
        values["from"] = {
            "address": self.from_account, 
            "type": AccountType.CONTRACT.value if self.additionnal_info["is_contract_from"] else AccountType.EOA.value
        }
        
        if self.to_account != None:
            values["to"] = {
                "address": self.to_account, 
                "type": AccountType.CONTRACT.value if self.additionnal_info["is_contract_to"] else AccountType.EOA.value
            }
        return values

    @classmethod
    def get_transaction(self, client: Client, number: int):
        query = '''
            query {{
                getTransaction(number: {number}) {{
                    number
                    id
                }}
            }}
        '''.format(number=str(number))
        query = gql(query)
        return client.execute(query)

    @classmethod
    def insert_transaction(self, client: Client, params: dict):
        query = gql("""
            mutation CreateTransaction($tx: [AddTransactionInput!]!) {
                addTransaction(input: $tx) {
                    transaction {
                        hash
                    }
                }
            }
        """)
        return client.execute(query, variable_values=params)
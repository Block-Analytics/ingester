from gql import Client, gql
from pydgraph.client import DgraphClient
from web3.types import TxData


class Transaction:
    hash: str
    nonce: int
    from_address: str
    to_address: str
    tags: list

    def __init__(self, txData: TxData, chain:str):
        self.tx_hash = txData["hash"].hex()
        self.nonce = txData["nonce"]
        self.from_address = txData["from"]
        self.to_address = txData["to"]
        self.block_number = txData["blockNumber"]
        self.gas = txData["gas"]
        self.gas_price = txData["gasPrice"]
        self.input = txData.get("input", "")
        self.chain = chain

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
        if self.from_address != None:
            values["from"] = {"id": self.from_address}
        if self.to_address != None:
            values["to"] = {"id": self.to_address}
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
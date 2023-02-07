from gql import Client, gql
from web3.types import BlockData


class Chain:

    id: str
    blockchain: str

    def __init__(self, id:str, blockchain: str):
        self.id = id
        self.blockchain = blockchain

    def to_json(self):
        return {
            "id": self.id,
            "blockchain": self.blockchain,
        }

    @classmethod
    def get_chain(self, client: Client, id: str):
        query = '''
            query {{
                getChain(id: "{id}") {{
                    number
                    id
                }}
            }}
        '''.format(id=id)
        query = gql(query)
        return client.execute(query)

    @classmethod
    def insert_chain(self, client: Client, params: dict):
        query = gql("""
            mutation CreateChain($chain: [AddChainInput!]!) {
                addChain(input: $chain) {
                    chain {
                        id
                    }
                }
            }
        """)
        return client.execute(query, variable_values=params)
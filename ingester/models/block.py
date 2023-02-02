from gql import Client, gql
from web3.types import BlockData


class Block:

    number: int
    hash: str
    difficulty: int
    gas_limit: int
    gas_used: int
    transactions: list
    timestamp: int
    type: str = "Block"

    def __init__(self, blockData: BlockData, chain: str):
        self.number = blockData["number"]
        self.hash = str(blockData["hash"].hex())
        self.difficulty = blockData["difficulty"]
        self.gas_limit = blockData["gasLimit"]
        self.gas_used = blockData["gasUsed"]
        self.transactions = blockData["transactions"]
        self.timestamp = blockData["timestamp"]
        self.chain = chain

    def to_json(self):
        return {
            "number": self.number,
            "hash": self.hash,
            "difficulty": self.difficulty,
            "gas_limit": self.gas_limit,
            "gas_used": self.gas_used,
            "timestamp": self.timestamp,
            "chain": {
                "id" : self.chain
            }
        }

    @classmethod
    def get_block(self, client: Client, number: int):
        query = '''
            query {{
                getBlock(number: {number}) {{
                    number
                    id
                }}
            }}
        '''.format(number=str(number))
        query = gql(query)
        return client.execute(query)

    @classmethod
    def insert_block(self, client: Client, params: dict):
        query = gql("""
            mutation CreateBlock($block: [AddBlockInput!]!) {
                addBlock(input: $block) {
                    block {
                        number
                    }
                }
            }
        """)
        return client.execute(query, variable_values=params)
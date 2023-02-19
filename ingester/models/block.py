from gql import Client, gql
from web3.types import BlockData
import datetime

class Block:

    number: int
    hash: str
    difficulty: int
    gas_limit: int
    gas_used: int
    transactions: list
    timestamp: int

    def __init__(self, blockData: BlockData, chain: str):
        self.number = blockData["number"]
        self.hash = str(blockData["hash"].hex())
        self.difficulty = blockData["difficulty"]
        self.gas_limit = blockData["gasLimit"]
        self.gas_used = blockData["gasUsed"]
        self.transactions = blockData["transactions"]
        self.mined_at = datetime.datetime.fromtimestamp(
            blockData["timestamp"], tz=datetime.timezone.utc
        ).strftime('%Y-%m-%dT%H:%M:%SZ')
        self.chain = chain

    def to_json(self):
        return {
            "number": self.number,
            "hash": self.hash,
            "difficulty": self.difficulty,
            "gas_limit": self.gas_limit,
            "gas_used": self.gas_used,
            "mined_at": self.mined_at,
            "chain": {
                "id" : self.chain
            }
        }

    def create_query(self):
        return f'''
            CREATE block:{self.number} SET hash="{self.hash}", difficulty={self.difficulty}, 
            gas_limit={self.difficulty}, gas_used={self.gas_used}, mined_at="{self.mined_at}", chain="chain:{self.chain}";
            RELATE chain:{self.chain}->blocks->block:{self.number};
        '''
    
    @classmethod
    def get_query(self, id: int):
        return f'SELECT * from block where id={id}'
from gql import Client, gql
from web3.types import TxData

from ingester.models.account import AccountType

class Transaction:
    hash: str
    nonce: int
    from_address: str
    to_address: str
    tags: list

    def __init__(self, chain:str, txData: TxData):
        self.tx_hash = txData["hash"].hex()
        self.nonce = txData["nonce"]
        self.from_account = txData["from"]
        self.to_account = txData["to"]
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
            "chain": {"id": self.chain},
            "processed": False,
            "from": self.from_account,
            "to": self.to_account if self.to_account != None else None
        }
        return values

    def create_query(self):
        return f'''CREATE tx:{self.tx_hash} SET nonce={self.nonce},
        from_account=account:{self.from_account}, to_account=account:{self.to_account}, 
        block="block:{self.block_number}", gas={self.gas}, gas_price={self.gas_price},
        input="{self.input}", chain="chain:{self.chain}", processed=false;
        RELATE block:{self.block_number}->has->tx:{self.tx_hash};
        RELATE tx:{self.tx_hash}->in->block:{self.block_number};
        '''
    @classmethod
    def get_query(self, hash: str):
        return f'SELECT * from tx where id={hash}'
from enum import Enum
from gql import Client, gql

class AccountType(Enum):
    CONTRACT = "Contract"
    EOA = "EOA"

class Account:
    address: str
    account_type: str

    def __init__(self, address: str, account_type: str) -> None:
        self.address = address
        # TODO: Check if account type is in enum
        self.account_type = account_type
    
    def to_json(self):
        return {
            "address": self.address,
            "type": self.account_type
        }
    def create_query(self):
        return f'''
            CREATE account:{self.address} SET type="{self.account_type}";
        '''
    def get_query(self):
        return f'SELECT * from account where id=account:{self.address}'
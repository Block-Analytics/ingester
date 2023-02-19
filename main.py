from web3 import Web3
from web3.middleware import geth_poa_middleware
from loguru import logger
import traceback

import json
import os
from ingester.models.account import Account, AccountType
# Local imports
from ingester.models.block import Block
from ingester.models.chain import Chain
from ingester.models.tx import Transaction
from ingester.utils.account import is_contract
from ingester.utils.surrealdb import SurrealDBClient

# Read config
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
CONFIG = json.loads(open(os.path.join(__location__, "config.json"), "r").read())
PROVIDERS = {}
for config in CONFIG.get("providers", {}).keys():
    PROVIDERS[config] = {
        "blockchain": CONFIG["providers"][config]["blockchain"],
        "client": Web3(Web3.HTTPProvider(CONFIG["providers"][config]["rpc_url"]))
    }

client = SurrealDBClient(
    CONFIG["db"]["url"],
    CONFIG["db"]["auth"]["username"], 
    CONFIG["db"]["auth"]["password"],
    CONFIG["db"]["namespace"], 
    CONFIG["db"]["database"],
)

try:
    for provider in PROVIDERS.keys():
        c = Chain(provider, PROVIDERS[provider]["blockchain"])
        client.sql(c.create_query())
except Exception as e:
    print(e)


for provider in PROVIDERS.keys():
    w3 = PROVIDERS[provider]["client"]
    if PROVIDERS[provider]["blockchain"] in ["avalanche"]:
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    block_latest = Block(w3.eth.get_block("latest"), provider)
    last_block_number = block_latest.number
    # Take only the last 10 blocks atm
    begin = last_block_number-10
    end = last_block_number + 1
    for i in range(begin, end):
        # check if block already exist
        res_now = client.sql(Block.get_query(i))[0]
        res_now_result = res_now.get("result", [])
        if len(res_now_result) == 0:
            # Insert the block
            block = Block(w3.eth.get_block(i), provider)
            resp = client.sql(block.create_query())
            logger.info("Block {} inserted for chain {}".format(i, provider))

            # Get transactions and link them
            logger.info("{} txs found in {}".format(len(block.transactions),i))

            for tx in block.transactions:
                txhash = str(tx.hex())
                w3_tx = w3.eth.get_transaction(txhash)
               
                is_contract_from = is_contract(w3_tx["from"], w3)
                is_contract_to = is_contract(w3_tx["to"], w3)
                
                from_account = Account(w3_tx["from"], AccountType.CONTRACT.value if is_contract_from else AccountType.EOA.value)
                to_account = Account(w3_tx["to"], AccountType.CONTRACT.value if is_contract_to else AccountType.EOA.value)
                 # Insert Account if not exist and speed up
                result = client.sql(from_account.get_query())
                # If doesnt exist create
                if len(result[0]["result"]) == 0:
                    client.sql(from_account.create_query())
                result = client.sql(to_account.get_query())
                # If doesnt exist create to_address
                if len(result[0]["result"]) == 0:
                    client.sql(to_account.create_query())
                txo = Transaction(provider,w3_tx)
                resp = client.sql(txo.create_query())
                logger.info("Transaction {} inserted".format(txhash))
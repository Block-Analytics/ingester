from web3 import Web3
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from web3.middleware import geth_poa_middleware
from loguru import logger
import traceback
import json
import os
# Local imports
from ingester.models.block import Block
from ingester.models.chain import Chain
from ingester.models.tx import Transaction
from ingester.utils.account import is_contract

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

# Select your transport with a defined url endpoint
transport = RequestsHTTPTransport(
    url=CONFIG["dgraph"]["url"],
    verify=False,
    retries=3,
)

# Create a GraphQL client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True)

try:
    for provider in PROVIDERS.keys():
        c = Chain(provider, PROVIDERS[provider]["blockchain"])
        x = Chain.insert_chain(client, {"chain": c.to_json()})
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
        res_now = Block.get_block(client, i)
        if res_now["getBlock"] == None:
            try:
                # Insert the block
                block = Block(w3.eth.get_block(i), provider)
                params = {
                    "block": block.to_json()
                }
                Block.insert_block(client, params=params)
                logger.info("Block {} inserted for chain {}".format(i, provider))

                # Get current block uid
                res_now = Block.get_block(client, i)
                uid_now = res_now["getBlock"]["id"]

                # Get transactions and link them
                logger.info("{} txs found in {}".format(len(block.transactions),i))

                for tx in block.transactions:
                    txhash = str(tx.hex())
                    w3_tx = w3.eth.get_transaction(txhash)
                    is_contract_from, is_contract_to  = is_contract(w3_tx["from"], w3), is_contract(w3_tx.get("to", ""), w3)
                    txo = Transaction(
                        provider,
                        w3_tx, 
                        {"is_contract_from":is_contract_from, "is_contract_to":is_contract_to}
                    )
                    txo_dict = txo.to_json()
                    txo_dict.update({"block": {"id": uid_now}})
                    Transaction.insert_transaction(client, {"tx": txo_dict})
                    logger.info("Transaction {} inserted".format(txhash))
                    
            except Exception as e :
                logger.error("Error while block {}".format(i))
                traceback.print_exc()
        else:
            logger.info("Block {} already exist".format(i))
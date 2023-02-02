from web3 import Web3
# from web3.types import BlockData
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from web3.middleware import geth_poa_middleware

from loguru import logger
import traceback

from ingester.models.block import Block
from ingester.models.chain import Chain
from ingester.models.tx import Transaction

# Select your transport with a defined url endpoint
transport = RequestsHTTPTransport(
    url="",
    verify=False,
    retries=3,
)

# Create a GraphQL client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True)
PROVIDERS = {}


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
    begin = last_block_number-10
    # begin = 0
    end = last_block_number + 1
    for i in range(begin, end):
    # for i in range(0, 10000):
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

                    txo = Transaction(w3.eth.get_transaction(txhash), provider)
                    txo_dict = txo.to_json()
                    txo_dict.update({"block": {"id": uid_now}})
                    Transaction.insert_transaction(client, {"tx": txo_dict})
                    logger.info("Transaction {} inserted".format(txhash))
            except Exception as e :
                logger.error("Error while block {}".format(i))
                traceback.print_exc()
        else:
            logger.info("Block {} already exist".format(i))
import os
import json
import time
from loguru import logger
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from ingester.utils.contract_evm import EvmContractService
from web3.middleware import geth_poa_middleware
from web3 import Web3
import logging

from ingester.utils.surrealdb import SurrealDBClient
logging.getLogger().setLevel(logging.CRITICAL)
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
service = EvmContractService()


def get_contract(address, chain):
    contract = PROVIDERS[chain]["client"].eth.get_code(address)

def extract_id(id:str) -> str:
    return id.split(":")[1]

def process_tx(tx):
    chain = extract_id(tx["chain"]["id"])
    if tx["to_account"]["type"] == "Contract":
        to_address = extract_id(tx["to_account"]["id"])
        # logger.info(f"Processing contract {tx['to']['address']}")
        contract = PROVIDERS[chain]["client"].eth.get_code(to_address)
        
        sighaches = service.get_function_sighashes(contract.hex())
        if service.is_erc20_contract(sighaches):
            logger.info(f"Contract {to_address} is ERC20")
        if service.is_erc721_contract(sighaches):
            logger.info(f"Contract {to_address} is ERC721") 
        if service.is_erc1155_contract(sighaches):
            logger.info(f"Contract {to_address} is ERC1155")

while True:

    # Get first 10 txs to process them
    query = "SELECT * FROM (SELECT * from tx WHERE processed=false FETCH to_account, from_account, chain) LIMIT 10;"

    for tx in client.sql(query)[0]["result"]:
        process_tx(tx)
    time.sleep(1)
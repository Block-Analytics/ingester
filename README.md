# Block analytics ingester

DO NOT USE IN A PRODUCTION ENVIRONMENT 

Ingest rpc data and import everything in SurrealDB ! 

This code is splitted into multiple jobs :
 - main.py -> Main job, import blocks, txs into db
 - contract_ingester.py -> Processes all txs to check if the account is a ERC-(20,721) contract

## Troubleshooting and help

# ERC Parsing 
```
https://github.com/bjknbrrr/slither/blob/93d83dfa979a7c7d3c3939b0e80ac051f7d3bc68/slither/utils/erc.py
```
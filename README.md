# Block analytics ingester

DO NOT USE IN A PRODUCTION ENVIRONMENT 

Ingest rpc data and import everything in DGraph ! 




## Troubleshooting and help
### Push Dgraph schema 
```
curl -X POST localhost:8080/admin/schema --data-binary '@schema.graphql'
```
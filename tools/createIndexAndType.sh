#!/bin/bash

set -e
if [ $# -eq 0 ] || [ $# -ne 4 ]; then
	echo "Usage: sh createIndexAndType.sh <es-host> <IndexName> <TypeName> <default-ttl>"
	exit
fi
	set -x
	echo $1
	echo $2
	echo $3
	echo $4
	curl -XPUT "http://$1:9200/$2" -d "{
		\"settings\": {
        	\"number_of_shards\" :   1,
        	\"number_of_replicas\" : 0,
			\"index.translog.flush_threshold_ops\": 10000,
			\"index.refresh_interval\": \"30s\"
		},
		\"mappings\":{
			\"$3\":{
			  \"_ttl\": {
			    \"enabled\": true,
				\"default\": \"$4d\"
				},
			  \"_source\": {
					\"enabled\": \"false\"
				},
			  \"properties\" : {
	            \"data\" : {
	               \"type\" :    \"string\",
	               \"analyzer\": \"english\",
				   \"store\": \"no\"
				},
	            \"url\" : {
	               \"type\" :   \"string\",
	               \"index\": \"not_analyzed\",
				   \"store\": \"yes\"
	            },
				\"title\": {
				   \"type\": \"string\",
				   \"analyzer\": \"english\"
				},
				\"src\": {
				   \"type\": \"string\",
				   \"index\": \"not_analyzed\"
				},
				\"update\": {
					\"type\": \"date\",
					\"format\": \"yyyy-MM-dd HH:mm:ss\"
				}
			  }
			}
		}
	}"
	echo

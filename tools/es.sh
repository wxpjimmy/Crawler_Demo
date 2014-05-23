#!/bin/bash
set -o nounset
set -o errexit

PrintUsage() {
	echo "Elasticsearch management console"
	echo "Usage: [COMMAND] <parameters>"
	echo
	echo "Command list:"
	echo "list(ls)--------show current es cluster info, include cluster/node/index info"
	echo "stats   --------show cluster/index stats"
	echo "refresh --------refresh one or more index, maring all operations performed since the last refresh available for search"
	echo "optimize--------optimize the index file, improve search efficiency, this maybe very cost, should be careful when using"
	echo "update  --------update index settings, this should be used combined with close/open"
	echo "close   --------close specified index, index settings can only be updated when the index is already closed"
	echo "start   --------start specified index, this should be called after updating index settings"
	echo "count   --------overall doc count for the cluster/index"
	echo "delete  --------delete specified index(s)"
	echo "mapping --------show the mapping of specified index"
	echo "validate--------validate the query"
	echo
	echo "run [COMAMND] --help see more detail about the command"
}

if [[ $# -eq 0 ]]; then
	PrintUsage
	exit 1
fi

cmd=$1
echo $cmd
shift
case $cmd in
	"ls"|"list") 
		if [[ $# -gt 0 ]]
		then
			if [[ "$1" == "--help" ]]
			then
				echo "Usage: "
				echo "./es.sh list [<ip>]"
				echo "ip is optional, default ip is localhost"
				exit 0
			else
				ip=$1
			fi
		else
			ip="localhost"
		fi
		echo ""
		echo "Index summary info: "
		curl $ip:9200/_cat/indices?v
		echo 
		echo "Shard summary info: "
		curl $ip:9200/_cat/shards?v
		echo
		echo "Node summary info: "
		curl $ip:9200/_cat/nodes?v
		echo
		echo "Cluster health info: "
		curl $ip:9200/_cat/health?v
		;;
	"stats")
		if [[ $# -eq 0 ]] || [[ "$1" == "--help" ]]
		then
			echo "Usage: "
			echo "./es.sh stats [-iIcC]"
			echo "parameters:"
			echo "-i/-I: specify to show the index stats"
			echo "-c/-C: specify to show the cluster stats"
			exit 0
		elif [[ $# -eq 1 ]]
		then
			opt=$1
			case $opt in
				-i|-I)
					echo "Displaying index stats..."
					curl localhost:9200/_stats?pretty=1
					;;
				-c|-C)
					echo "Displaying cluster stats..."
					curl -XGET 'http://localhost:9200/_cluster/stats?human&pretty=1'
					;;
				*)
					echo "Bad arguments!"
					echo "Usage: es stats -ic <options>"
					echo "        -i <options>   : view index stats"
					echo "        -c <options>   : view cluster stats"
					;;
			esac
		else 
			echo ""
		fi
		;;
	"refresh")
		if [[ $# -eq 0 ]]
		then
			curl -XPOST 'http://localhost:9200/_refresh'
		else
			if [[ "$1" == "--help" ]]
			then
				echo "Usage: "
				echo "./es.sh refresh [<-iIhH>]"
				exit 0
			fi
			ip='localhost'
			indexes=""
			while [[ $# -gt 1 ]]; do
				opt=$1
				case $opt in
					-i|-I)
						indexes=$2
						;;
					-h|-H)
						ip=$2
						;;
					*)
						echo "Bad arguments: "
						;;
				esac
				shift
				shift
			done
			if [[ -z "$indexes" ]]
			then
				curl -XPOST $ip:9200/_refresh
			else
				curl -XPOST $ip:9200/$indexes/_refresh
			fi
		fi
		;;
	"optimize")
		if [[ $# -eq 0 ]]
		then
			curl -XPOST 'http://localhost:9200/_optimize'
		else
			ip="localhost"
			indexes=""
			max_segments="5"
			wait_merge="false"
			while [[ $# -gt 1 ]]; do
				opt=$1
				case $opt in
					-h|-H)
						ip=$2
						;;
					-i|-I)
						indexes=$2
						;;
					-m|-M)
						max_segments=$2
						;;
					-w|-W)
						wait_merge=$2
						;;
					*)
						echo "Wrong arguments!"
						exit 1
				esac
				shift
				shift
			done
			if [[ -z "$indexes" ]]
			then
				curl -XPOST $ip:9200/_optimize?max_num_segments=$max_segments&wait_for_merge=$wait_merge
			else
				curl -XPOST $ip:9200/$indexes/_optimize?max_num_segments=$max_segments&wait_for_merge=$wait_merge
			fi
		fi
		;;
	"update")
		if [[ $# -eq 0 ]]
		then
			echo "Must specify arguments [-ihs]"
			exit 1
		else
			index=""
			settings=""
			ip="localhost"
			while [[ $# -gt 1 ]]; do
				opt=$1
				case $opt in
					-h|-H)
						ip=$2
						;;
					-i|-I)
						index=$2
						;;
					-s|-S)
						settings=$2
						;;
					*)
						echo "Bad arguments!"

						exit 1
				esac
				shift
				shift
			done
			if [[ -z "$index" ]] || [[ -z "$settings" ]]
			then
				echo "Must specify index and settings"
				exit 1
			else
				curl -XPUT $ip:9200/$index/_settings -d "$settings"
			fi
		fi
		;;
	"close"|"open")
		if [[ $# -eq 0 ]]
		then
			echo "must specify index"

			exit 1
		else
			index=""
			ip="localhost"
			while [[ $# -gt 1 ]]; do
				opt=$1
				case $opt in
					-h|-H)
						ip=$2
						;;
					-i|-I)
						index=$2
						;;
					*)
						echo "Bad arguments"
						exit 1
				esac
				shift
				shift
			done
			if [[ -z "$index" ]]
			then
				echo "must specify an index to $cmd"
				exit 1
			else
				curl -XPOST $ip:9200/$index/_$cmd
			fi
		fi
		;;
	"count")
		ip="localhost"
		index=""
		while [[ $# -gt 1 ]]; do
			opt=$1
			case $opt in
				-h|-H)
					ip=$2
					;;
				-i|-I)
					index=$2
					;;
				*)
					echo "Bad arguments"

					exit 1
			esac
			shift
			shift
		done
		if [[ -z "$index" ]]
		then
			curl $ip:9200/_cat/count?v
		else
			curl $ip:9200/_cat/count/$index?v
		fi
		;;
	"delete")
		ip="localhost"
		indexes=""
		while [[ $# -gt 1 ]]; do
			opt=$1
			case $opt in
				-h|-H)
					ip=$2
					;;
				-i|-I)
					indexes=$2
					;;
				*)
					echo "Bad arguments"

					exit 1
			esac
			shift
			shift
		done
		if [[ -z "$indexes" ]]
		then
			echo "mush specify at least one index to delete"
			exit 1
		else
			curl -XDELETE $ip:9200/$indexes
		fi
		;;
	"mapping")
		ip="localhost"
		index=""
		while [[ $# -gt 1 ]]; do
			opt=$1
			case $opt in
				-h|-H)
					ip=$2
					;;
				-i|-I)
					index=$2
					;;
				*)
					echo "Bad arguments"

					exit 1
			esac
			shift
			shift
		done
		if [[ -z "$index" ]]
		then
			echo "mush specify at index to get mapping"
			exit 1
		else
			curl $ip:9200/$index/_mapping?pretty
		fi
		;;
	"validate")
		ip="localhost"
		index=""
		doc_type=""
		query=""
		explain="false"
		while [[ $# -gt 1 ]]; do
			opt=$1
			case $opt in
				-h|-H)
					ip=$2
					;;
				-i|-I)
					index=$2
					;;
				-t|-T)
					doc_type=$2
					;;
				-q|-Q)
					query=$2
					;;
				-e|-E)
					explain=$2
					;;
				*)
					echo "Bad arguments"

					exit 1
			esac
			shift
			shift
		done
		if [[ -z "$query" ]]
		then
			echo "mush provide a query to validate"
			exit 1
		elif [[ -z "$index" ]] && [[ -n "$doc_type" ]]
		then
			echo "can't just provide a type without index"
			exit 1
		else
			if [[ -z "$index" ]]
			then
				if [[ "$explain" == "true" ]]
				then
					curl -XGET "$ip:9200/_validate/query?pretty&explain" -d "$query"
				else
					curl -XGET "$ip:9200/_validate/query?pretty" -d "$query"
				fi
			else
				if [[ "$explain" == "true" ]]
				then
					if [[ -z "$doc_type" ]]
					then
						curl -XGET "$ip:9200/$index/_validate/query?pretty&explain" -d "$query"
					else
						curl -XGET "$ip:9200/$index/$doc_type/_validate/query?pretty&explain" -d "$query"
					fi
				else
					if [[ -z "$doc_type" ]]
					then
						curl -XGET "$ip:9200/$index/_validate/query?pretty" -d "$query"
					else
						curl -XGET "$ip:9200/$index/$doc_type/_validate/query?pretty" -d "$query"
					fi
				fi
			fi
		fi
		;;
	*)
		echo "no such command!"
		exit 1
esac


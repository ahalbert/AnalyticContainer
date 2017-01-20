#!/bin/bash

usage() {
    echo "Usage: make_snapshot.sh CLUSTER SNAPSHOT_NAME"
}
if [[ -z $1 ]]; then
    echo "Cluster name not given"
    usage
    exit 1
fi 
cluster="$1"

if [[ -z $2 ]]; then
    echo "Snapshot name not given"
    usage
    exit 2
fi
snapshot_name="$2"

aws redshift create-cluster-snapshot --snapshot-identifier $snapshot_name --cluster-identifier $cluster
aws redshift wait snapshot-available --snapshot-identifier $snapshot_name 


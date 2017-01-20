#!/bin/bash

usage() {
    echo "delete_cluster.sh CLUSTER [FINAL_SNAPSHOT]"
    exit -1
}

if [[ -z $1 ]]; then
    echo "Cluster name not given"
    usage
fi 
cluster="$1"
snapshot="$2"

aws redshift describe-clusters --cluster-identifier "$cluster" 2> /dev/null
cluster_exists="$?"

if [[ "$cluster_exists" != "0" ]]; then
    echo "Could not find $cluster. It may already be deleted."
    exit 2
fi

if [[ -n "$snapshot" ]]; then
    aws redshift delete-cluster --cluster-identifier $cluster --no-skip-final-cluster-snapshot --final-cluster-snapshot-identifier "$snapshot"
else 
    aws redshift delete-cluster --cluster-identifier $cluster --skip-final-cluster-snapshot
fi

deleted="$?"
if [[ "$deleted" -eq 0 ]]; then
    aws redshift wait cluster-deleted --cluster-identifier $cluster
else 
    echo "Could not delete $cluster. It may have already been deleted."
    exit 1
fi

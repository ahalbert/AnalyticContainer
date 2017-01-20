#!/bin/bash

usage() {
    echo "Usage: delete_snapshot.sh SNAPSHOT"
}

if [[ -z $1 ]]; then
    usage
    exit 1
fi 
snapshot="$1"

aws redshift delete-cluster-snapshot --snapshot-identifier $snapshot

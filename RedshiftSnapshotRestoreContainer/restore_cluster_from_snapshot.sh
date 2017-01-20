#!/bin/bash

usage() {
    echo "restore_cluster.sh CLUSTER SNAPSHOT_FROM"
    echo "Environment variables:"
    echo "availability_zone" 
    echo "is_publicly_accessible true|false" 
    echo "cluster_parameter_group_name" 
    echo "elastic_ip"
    echo "iam_roles"
    echo "node_type" 
    exit -1 
}

if [[ -z $1 ]]; then
    echo "Cluster name not given"
    usage
fi 
cluster="$1"

if [[ -z $2 ]]; then
    echo "Snapshot name not given"
    usage
fi 
snapshot="$2"


if ! aws redshift describe-cluster-snapshots --snapshot-identifier "$snapshot" ; then
    echo "Failed to find snapshot $snapshot. Halting"
    usage
fi 

cluster_arguments=""
#Check env variables. We'll add them to cluster_arguments if they exist
if [[ -n "$availability_zone" ]]; then
    cluster_arguments="--availability-zone $availability_zone "
fi

if [[ -n "$cluster_subnet_group_name" ]]; then
    cluster_arguments="$cluster_arguments--cluster-subnet-group-name $cluster_subnet_group_name "
fi

if [[ -n "$is_publicly_accessible" ]]; then
    if [[ "$is_publicly_accessible" == "true" ]]; then
        cluster_arguments="$cluster_arguments--publicly-accessible "
    fi
    if [[ "$is_publicly_accessible" == "false" ]]; then
        cluster_arguments="$cluster_arguments--no-publicly-accessible "
    fi
fi

if [[ -n "$cluster_elastic_ip" ]]; then
    cluster_arguments="$cluster_arguments--elastic-ip $cluster_elastic_ip "
fi

if [[ -n "$parameter_group_name" ]]; then
    cluster_arguments="$cluster_arguments--cluster-parameter-group-name $parameter_group_name "
    
fi

if [[ -n "$vpc_security_group_id" ]]; then #Think this is optional
    cluster_arguments="$cluster_arguments--vpc-security-group-ids $vpc_security_group_id "
fi

if [[ -n "$iam_roles" ]]; then
    cluster_arguments="$cluster_arguments--iam-roles $iam_roles "
fi

if [[ -n "$snapshot_cluster" ]]; then
    cluster_arguments="$cluster_arguments--snapshot-cluster-identifier $snapshot_cluster "
fi

if [[ -n "$node_type" ]]; then
    cluster_arguments="$cluster_arguments--node-type $node_type"
fi

aws redshift restore-from-cluster-snapshot --snapshot-identifier "$snapshot" --cluster-identifier "$cluster" $cluster_arguments

created="$?"
if [[ "$created" -eq 0 ]]; then
    echo "created $cluster"
    aws redshift wait cluster-available --cluster-identifier $cluster
else
    echo "An error occured while restoring $cluster"
    exit 1
fi

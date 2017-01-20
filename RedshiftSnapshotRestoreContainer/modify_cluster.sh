#!/bin/bash

usage() {
    echo "modify_cluster.sh CLUSTER"
    exit 1
}
if [[ -z $1 ]]; then
    echo "Cluster name not given"
    usage
fi 
cluster="$1"

cluster_arguments=""
if [[ -n "$cluster_type" ]]; then
    cluster_arguments="--cluster-type $cluster_type "
fi

if [[ -n "$cluster_security_groups" ]]; then
    cluster_arguments="$cluster_arguments--cluster-security-groups $cluster_security_groups "
fi

if [[ -n "$master_user_password" ]]; then
    cluster_arguments="$cluster_arguments--master-user-password $master_user_password "
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

if [[ -n "$enhanced_vpc_routing" ]]; then
    if [[ "$enhanced_vpc_routing" == "true" ]]; then
        cluster_arguments="$cluster_arguments--enhanced-vpc-routing "
    fi
    if [[ "$is_publicly_accessible" == "false" ]]; then
        cluster_arguments="$cluster_arguments--no-enhanced-vpc-routing "
    fi
fi

if [[ -n "$cluster_elastic_ip" ]]; then
    cluster_arguments="$cluster_arguments--elastic-ip $cluster_elastic_ip "
fi

if [[ -n "$parameter_group_name" ]]; then
    cluster_arguments="$cluster_arguments--cluster-parameter-group-name $parameter_group_name "
fi

if [[ -n "$automated_snapshot_retention_period" ]]; then 
    cluster_arguments="$cluster_arguments--automated-snapshot-retention-period $automated_snapshot_retention_period "
fi

if [[ -n "$vpc_security_group_id" ]]; then 
    cluster_arguments="$cluster_arguments--vpc-security-group-ids $vpc_security_group_id "
fi

if [[ -n "$iam_roles" ]]; then
    cluster_arguments="$cluster_arguments--iam-roles $iam_roles "
fi

if [[ -n "$snapshot_cluster" ]]; then
    cluster_arguments="$cluster_arguments--snapshot-cluster-identifier $snapshot_cluster "
fi

if [[ -n "$node_type" ]]; then
    cluster_arguments="$cluster_arguments--node-type $node_type "
fi

if [[ -n "$number_of_nodes" ]]; then
    if [[ -z "$node_type" ]]; then
        echo "Must also specifiy node type."
        exit 3
    fi
    cluster_arguments="$cluster_arguments--number-of-nodes $number_of_nodes "
fi

echo $cluster_arguments
aws redshift modify-cluster --cluster-identifier $cluster $cluster_arguments

modified="$?"
if [[ "$modified" -eq 0 ]]; then
    echo "Modified $cluster"
    aws redshift wait cluster-available --cluster-identifier $cluster
else
    echo "An error occured while modifying $cluster"
    exit 2
fi

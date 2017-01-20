#!/bin/bash

usage() {
    echo "make_cluster_from_snapshot.sh [-n --node-type node_type] [-s --savesnapshot SNAPSHOT_TO] CLUSTER SNAPSHOT_FROM"
    exit -1 
}

while [[ "$#" -gt 2 ]]; do
    case $1 in
        -n|--node-type)
            shift
            node_type="$1"
            shift
        ;;
        -s|--savesnapshot)
            shift
            snapshot_to="$1"
            shift
        ;;
        *)
            usage
        ;;
    esac
done


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

aws redshift describe-clusters --cluster-identifier "$cluster" 2> /dev/null
cluster_exists="$?"

#If the cluster doesn't exist, then we can't get the config variables, so check they are all there.
if [ $cluster_exists -eq 0 ]; then

    if [[ -z "$availability_zone" ]]; then
        availability_zone=$(aws redshift describe-clusters --cluster-identifier $cluster | sed '/AvailabilityZone/!d;s/[^:]*:\([^:]*\)/\1/' | sed 's/[\",]//g') 
    fi

    if [[ -z "$cluster_elastic_ip" ]]; then
        cluster_elastic_ip=$(aws redshift describe-clusters --cluster-identifier $cluster |  sed '/ElasticIp/!d;s/[^:]*:\([^:]*\)/\1/' | sed 's/[\",]//g') 
    fi

    if [[ -z "$parameter_group_name" ]]; then
        parameter_group_name=$(aws redshift describe-clusters --cluster-identifier $cluster | sed '/ParameterGroupName/!d;s/[^:]*:"\([^:]*\)":/\1/' | sed 's/.*://' | sed 's/[\",]//g')
    fi

    if [[ -z "$vpc_security_group_id" ]]; then #
        vpc_security_group_id=$(aws redshift describe-clusters --cluster-identifier $cluster | sed '/VpcSecurityGroupId/!d;s/[^:]*:\([^:]*\):/\1/' | sed 's/.*://' | sed 's/[ \",]//g')
    fi

    if [[ -z "$iam_roles" ]]; then
        iam_roles=$(aws redshift describe-clusters --cluster-identifier $cluster | sed '/IamRoleArn/!d;s/[^:]*:\([^:]*\):/\1/' | sed 's/[\",]//g')
    fi

    if [ -z "$node_type" ]; then
        node_type=$(aws redshift describe-clusters --cluster-identifier $cluster | sed '/NodeType\"/!d;s/[^:]*:\([^:]*\)/\1/' | sed 's/[ \",]//g') 
    fi 
else 
    echo "$snapshot"
    snapshot_cluster=$(aws redshift describe-cluster-snapshots --snapshot-identifier  "$snapshot" | sed '/ClusterIdentifier/!d;s/[^:]*:\([^:]*\)/\1/' | sed 's/[ \",]//g') # parses json "k": "v" line

    if [[ -z "$availability_zone" ]]; then
        availability_zone=$(aws redshift describe-cluster-snapshots --snapshot-identifier $snapshot | sed '/AvailabilityZone/!d;s/[^:]*:\([^:]*\)/\1/' | sed 's/[\",]//g') 
    fi

    if [ -z "$node_type" ]; then
        node_type=$(aws redshift describe-cluster-snapshots --snapshot-identifier "$snapshot" | sed '/NodeType\"/!d;s/[^:]*:\([^:]*\)/\1/' | sed 's/[ \",]//g') 
    fi 
fi

cluster_arguments=""
#Check env variables. We'll add them to cluster_arguments if they exist
if [[ -n "$availability_zone" ]]; then
    cluster_arguments="--availability-zone $availability_zone "
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

if [ $cluster_exists -eq 0 ]; then
    if [[ -n "$snapshot_to" ]]; then
        aws redshift delete-cluster --cluster-identifier $cluster --no-skip-final-cluster-snapshot --final-cluster-snapshot-identifier "$snapshot_to"
    else 
        aws redshift delete-cluster --cluster-identifier $cluster --skip-final-cluster-snapshot
    fi 
    deleted="$?"
    if [[ "$deleted" -eq 0 ]]; then
        aws redshift wait cluster-deleted --cluster-identifier $cluster
    else 
        echo "Could not delete $cluster. It may have already been deleted."
        # already_deleting=$(aws redshift describe-clusters --cluster-identifier $cluster | sed '/ClusterStatus/!d;s/[^:]*:\([^:]*\)/\1/' | sed 's/[\",]//g') 
        # if [[ "$already_deleting" != "Deleted" ]]; then
        # fi
    fi
fi

echo "$cluster_arguments"
aws redshift restore-from-cluster-snapshot --snapshot-identifier "$snapshot" --cluster-identifier "$cluster" --publicly-accessible $cluster_arguments

created="$?"
if [[ "$created" -eq 0 ]]; then
    echo "created $cluster"
    aws redshift wait cluster-available --cluster-identifier $cluster
else
    echo "An error occured while restoring $cluster"
    exit 1
fi

#!/bin/sh

usage() {
    echo "make_cluster.sh [-n --node-type node_type] CLUSTER [SNAPSHOT_FROM]"
    exit -1 
}

if [[ -z $1 ]]; then
    usage
fi 
cluster="$1"
   
while [[ "$#" -gt 2 ]]; do
    case $opt in
        -n|--node-type)
            shift
            node_type="$1"
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

if [[ -n $2 ]]; then
    snapshot="$2"
fi 

if ! aws redshift describe-cluster-snapshots --snapshot-identifier "$snapshot"; then
    echo "Failed to find snapshot $snapshot. Halting"
    usage
fi 
snapshot_cluster=$(aws redshift describe-cluster-snapshots --snapshot-identifier  "$snapshot" | sed '/ClusterIdentfier/!d;s/[^:]*:"\([^:]*\)":/\1/') # parses json "k": "v" line

#check config variables exist
if [   -z "$node_type" -o \ 
        -z "$AVALIABILITY_ZONE" -o \
        -z "$SUBNET_GROUP" -o \
        -z "$SUBNET_GROUP" -o \
        -z "$CLUSTER_ELASTIC_IP" -o \ 
        -z "$PARAMETER_GROUP_NAME" -o \
        -z "$VPC_SECURITY_GROUP_ID" -o \
        -z "$IAM_ROLES" ]; then
        echo "Missing configuration parameter to $cluster"
        usage
fi

if [ -z "$node_type" ]; then
    node_type=$(aws redshift describe-cluster-snapshots --snapshot-identifier "$snapshot" | sed '/NodeType\":/!d;s/[^:]*:"\([^:]*\)":/\1/')
fi 
#Check env variables
if [[ -z "$AVALIABILITY_ZONE" ]]; then
   AVALIABILITY_ZONE=$(aws redshift describe-clusters --cluster-identifier $cluster | sed '/AvailabilityZone/!d;s/[^:]*:"\([^:]*\)":/\1/');
fi

if [[ -z "$SUBNET_GROUP" ]]; then
    SUBNET_GROUP=$(aws redshift describe-clusters --cluster-identifier $cluster | sed '/ClusterSubnetGroupName/!d;s/[^:]*:"\([^:]*\)":/\1/');
fi

if [[ -z "$CLUSTER_ELASTIC_IP" ]]; then
    CLUSTER_ELASTIC_IP=$(aws redshift describe-clusters --cluster-identifier $cluster | sed '/ElasticIp/!d;s/[^:]*:"\([^:]*\)":/\1/')
fi

if [[ -z "$PARAMETER_GROUP_NAME" ]]; then
    PARAMETER_GROUP_NAME=$(aws redshift describe-clusters --cluster-identifier $cluster | sed '/ParameterGroupName/!d;s/[^:]*:"\([^:]*\)":/\1/')
fi

if [[ -z "$VPC_SECURITY_GROUP_ID" ]]; then
    VPC_SECURITY_GROUP_ID=$(aws redshift describe-clusters --cluster-identifier $cluster | sed '/VpcSecurityGroupId/!d;s/[^:]*:"\([^:]*\)":/\1/')
fi

if [[ -z "$IAM_ROLES" ]]; then
    IAM_ROLES=$(aws redshift describe-clusters --cluster-identifier $cluster | sed '/IamRoleArn/!d;s/[^:]*:"\([^:]*\)":/\1/')
fi

if [ -n "$snapshot" ]; then
    aws redshift restore-from-cluster-snapshot \
        --snapshot-identifier "$snapshot" \
        --cluster-identifier "$cluster"  \
        --snapshot-cluster-identifier "$snapshot_cluster" \
        --availability-zone $AVALIABILITY_ZONE \
        --cluster-subnet-group-name $SUBNET_GROUP \
        --publicly-accessible \
        --elastic-ip "$CLUSTER_ELASTIC_IP" \
        --cluster-parameter-group-name "$PARAMETER_GROUP_NAME" \
        --vpc-security-group-ids "$VPC_SECURITY_GROUP_ID" \
        --iam-roles "$IAM_ROLES" \
        --node-type "$node_type"
else
    aws redshift restore-from-cluster-snapshot \
        --cluster-identifier "$cluster"  \
        --availability-zone $AVALIABILITY_ZONE \
        --cluster-subnet-group-name $SUBNET_GROUP \
        --publicly-accessible \
        --elastic-ip "$CLUSTER_ELASTIC_IP" \
        --cluster-parameter-group-name "$PARAMETER_GROUP_NAME" \
        --vpc-security-group-ids "$VPC_SECURITY_GROUP_ID" \
        --iam-roles "$IAM_ROLES" \
        --node-type "$node_type"
fi 
aws redshift wait cluster-available --cluster-identifier $cluster

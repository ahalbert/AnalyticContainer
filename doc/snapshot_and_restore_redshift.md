# Redshift Snapshot Container

The DataKitchen `snapshot_restore_redshift` container allows for a number of discrete operations on redshift clusters and snapshots. They can be combined to perform large tasks on AWS redshift.

##Config.json

The config.json file for the container uses these options:
	
* `aws_access_key_id` - Your AWS access key
* `aws_secret_access_key` - Your AWS secret access key
* `aws_default_region` - Region to operate on
* `cluster` - cluster to perform `redshift_command` on
* `snapshot` - snapshot to perform `redshift_command` on
* `redshift_command` - Redshift operation to perform

In addition, any config.json creating or modifying a redshift cluster may pass in these cluster configuration options for the cluster:

* `node_type`
* `availability_zone`
* `is_publicly_accessible`
* `cluster_parameter_group_name` 
* `vpc_security_group_ids`
* `iam_roles`
* `cluster_subnet_group_name` 
* `cluster_elastic_ip` 

### Redshift command

Provided operations:

* `restore-from-cluster-snapshot` - Creates a new redshift container from a snapshot, allows cluster configuration options
* `modify-cluster` - Modifies an existing cluster without shutting it down, allows cluster configuration options 
* `create-cluster-snapshot` - Makes a new snapshot of a running cluster
* `delete-cluster` - Shuts down a cluster
    * Optional: if Snapshot is provided, a final snapshot will be created before shutting down
* `delete-snapshot` - Deletes a snapshot. `cluster` is not used with this command.

##Use Case: Swapping clusters

A more advanced use of the clusters is to shut down an existing cluster and then restore it to a new cluster with a snapshot

Swapping clusters from a build cluster to a production can be accomplished with the following 4 nodes
  
* `create-cluster-snapshot`
* `delete-cluster`
* `restore-from-cluster-snapshot`
* `delete-cluster`

######create-cluster-snapshot config.json
    {
        "aws_access_key_id": "",
        "aws_secret_access_key": "",
        "aws_default_region": "us-east-1",
        "cluster": "cluster-build",
        "snapshot": "cluster1-snapshot",
        "redshift_command" : "restore-from-cluster-snapshot"
    }

######delete-cluster config.json
    {
        "aws_access_key_id": "",
        "aws_secret_access_key": "",
        "aws_default_region": "us-east-1",
        "cluster": "cluster-production",
        "snapshot": "cluster-production-final",
        "redshift_command" : "delete-snapshot"
    }

######restore-from-cluster-snapshot config.json
    {
        "aws_access_key_id": "",
        "aws_secret_access_key": "",
        "aws_default_region": "us-east-1",
        "cluster": "cluster-production",
        "snapshot": "cluster-build-snapshot",
        "redshift_command" : "restore-from-cluster-snapshot",
        "node_type" : "dc1.xlarge"
    }

######delete-cluster config.json
    {
        "aws_access_key_id": "",
        "aws_secret_access_key": "",
        "aws_default_region": "us-east-1",
        "cluster": "cluster-build",
        "redshift_command" : "delete-snapshot"
    }

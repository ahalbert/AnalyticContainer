from AnalyticContainer.AnalyticContainerLibrary.ACBase import *
import os
import subprocess
import sys

class RedshiftSnapshotAndRestore(ACBase):
    def __init__(self):
        ACBase.__init__(self)

    def is_valid_config(self):
        isValid = True
        try: 
            if not self.configuration['aws_access_key_id']:
                ACLogger().get_logger().error('Required parameter "aws_access_key_id" not supplied in config.json')
                isValid = False
            if not self.configuration['aws_secret_access_key']:
                ACLogger().get_logger().error('Required parameter "aws_secret_access_key" not supplied in config.json')
                isValid = False
        except:
            return False
        return isValid

    def execute(self):
        os.environ['AWS_ACCESS_KEY_ID'] = self.configuration['aws_access_key_id']
        os.environ['AWS_SECRET_ACCESS_KEY'] = self.configuration['aws_secret_access_key']
        os.environ['AWS_DEFAULT_REGION'] = self.configuration['aws_default_region']
        try:
            cluster = self.configuration['cluster']
        except:
            cluster = ''
        try:
            snapshot = self.configuration['snapshot']
        except:
            snapshot = ''
        for key in self.configuration:
            if key not in ['aws_access_key_id', 'aws_secret_access_key', 'snapshot', 'cluster']:
                os.environ[key] = self.configuration[key]
        redshift_command = self.configuration['redshift_command']
        try:
            if redshift_command == "restore-from-cluster-snapshot":
                self.set_progress('restore-from-cluster-snapshot', 'Cluster: ' + cluster + 'Snapshot: ' + snapshot )
                ACLogger().get_logger().info(subprocess.check_output(['./restore_cluster_from_snapshot.sh', cluster, snapshot], stderr=subprocess.STDOUT))
            elif redshift_command == "modify-cluster":
                ACLogger().get_logger().info('modify-cluster')
                self.set_progress('Modify Cluster', 'Cluster:' + cluster)
                ACLogger().get_logger().info(subprocess.check_output(['./modify_cluster.sh', cluster], stderr=subprocess.STDOUT))
            elif redshift_command == "create-cluster-snapshot":
                self.set_progress('make snapshot', 'Cluster:' + cluster + ' Snapshot:' + snapshot)
                ACLogger().get_logger().info(subprocess.check_output(['./make_snapshot.sh', cluster, snapshot], stderr=subprocess.STDOUT))
            elif redshift_command == "delete-snapshot":
                self.set_progress('delete snapshot', 'Snapshot:' + snapshot)
                ACLogger().get_logger().info(subprocess.check_output(['./delete_snapshot.sh', snapshot], stderr=subprocess.STDOUT)) 
            elif redshift_command == "delete-cluster":
                self.set_progress('delete cluster', 'Cluster:' + cluster)
                ACLogger().get_logger().info(subprocess.check_output(['./delete_cluster.sh', cluster, snapshot], stderr=subprocess.STDOUT)) 
            else:
                self.set_progress('restore cluster', 'Cluster:' + cluster)
                ACLogger().get_logger().info(subprocess.check_output(['./restore_cluster.sh', cluster, snapshot]))
        except subprocess.CalledProcessError as e:
            ACLogger().get_logger().error(e.output)
            ACLogger().get_logger().error('Process returned error code %s' % str(e.returncode))
            raise e
        self.set_progress('Completed', 'Cluster:' + cluster)


def main():
    container = RedshiftSnapshotAndRestore()
    if container.vaild_config() is True:
        try:
            container.execute()
            container.set_container_status(CONTAINER_STATUS_SUCCESS)
        except:
            container.set_container_status(CONTAINER_STATUS_ERROR)
        container.write_log()
        container.write_progress()

if __name__ == "__main__":
    main()


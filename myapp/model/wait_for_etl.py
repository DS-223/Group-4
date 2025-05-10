import docker
import time
import sys

client = docker.DockerClient(base_url='unix://var/run/docker.sock')

def wait_for_etl(container_name='etl', timeout=600):
    print("Waiting for ETL container to finish...")
    elapsed = 0
    while elapsed < timeout:
        try:
            container = client.containers.get(container_name)
            status = container.status
            if status == 'exited':
                exit_code = container.attrs['State']['ExitCode']
                if exit_code == 0:
                    print("ETL finished successfully.")
                    return
                else:
                    print(f"ETL failed with exit code {exit_code}. Exiting.")
                    sys.exit(1)
            else:
                print(f"ETL status: {status}. Waiting...")
        except docker.errors.NotFound:
            print("ETL container not found. Retrying...")
        time.sleep(5)
        elapsed += 5
    print("Timeout waiting for ETL to finish.")
    sys.exit(1)

if __name__ == "__main__":
    wait_for_etl()

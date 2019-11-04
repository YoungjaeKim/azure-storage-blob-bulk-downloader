import argparse
import os
from azure.storage.blob import BlockBlobService, Blob
import yaml
from timeit import default_timer as timer
from datetime import timedelta


class Parameter:
    enable: bool = False
    account_name: str = ""
    account_key: str = ""
    container: str = ""
    limit: int = 5000
    download_directory: str = "download"
    timeout: int = None
    skip: int = 0

    def read(self, config):
        self.enable = bool(config['enable'])
        self.limit = int(config['limit'])
        self.account_name = str(config['account_name'])
        self.account_key = str(config['account_key'])
        self.container = str(config['container'])
        self.download_directory = str(config['download_directory']).strip("/")
        self.timeout = None if (not str(config['timeout']) or int(config['timeout']) == 0) else int(config['timeout'])
        self.skip = int(config['skip'])


if __name__ == '__main__':
    start_time: float = timer()

    limit_count = 0

    # Set configuration
    parser = argparse.ArgumentParser()
    parser.add_argument("--enable", help="run script", type=bool, default=False)
    parser.add_argument("--config", help="configuration yaml file", type=str,
                        default='config.yaml')
    parser.add_argument("--container", help="a container name of Azure Storage", type=str)
    parser.add_argument("--limit", help="if limit reached, exit immediately", type=int, default=-1)
    parser.add_argument("--download", help="download directory", type=str)
    parser.add_argument("--skip", help="skip to n-th item and continue", type=int, default=0)
    args = parser.parse_args()

    if not os.path.isfile(args.config):
        raise ValueError("ERROR: no config file exists at {0}".format(args.config))
    param = Parameter()
    with open(args.config, 'rt', encoding='UTF-8') as fin:
        print("config file: {0}".format(args.config))
        yaml_text = fin.read()
        config_nodes = yaml.load(yaml_text, Loader=yaml.Loader)
        param.read(config_nodes)

    if args.enable:
        param.enable = args.enable
    if args.limit >= 0:
        param.limit = args.limit
    if args.download:
        param.download_directory = args.download
    if args.container:
        param.container = args.container
    if args.skip > 0:
        param.skip = args.skip

    if not param.download_directory:
        print("ERROR: please set download directory")
        exit(1)
    if not os.path.exists(param.download_directory):
        os.makedirs(param.download_directory)

    if not param.enable:
        print("Exit because 'enable' is False")
        exit(0)
    print("{0} item{1} will be downloaded to '{2}' directory".format(
        param.limit, "s" if param.limit > 1 else "", param.download_directory))

    # Azure Storage access
    # name of your storage account and the access key from Settings->AccessKeys->key1
    block_blob_service = BlockBlobService(account_name=param.account_name, account_key=param.account_key)

    # name of the container
    generator = block_blob_service.list_blobs(param.container)

    # code below lists all the blobs in the container and downloads them one after another
    for blob in generator:
        limit_count += 1
        print("#{0}: {1}".format(limit_count, blob.name), end='', flush=True)

        if param.skip > 0 and limit_count < param.skip:
            print(" - skip till {0} items".format(param.skip))
            continue

        # check if the path contains a folder structure, create the folder structure
        result_blob: Blob = None
        if "/" in "{}".format(blob.name):
            print("there is a path in this")
            # extract the folder path and check if that folder exists locally, and if not create it
            head, tail = os.path.split("{}".format(blob.name))
            print(head)
            print(tail)
            if os.path.isdir(os.getcwd() + "/" + head):
                # download the files to this directory
                print("directory and sub directories exist")
                result_blob = block_blob_service.get_blob_to_path(param.container, blob.name,
                                                    "{0}/{1}/{2}/{3}".format(os.getcwd(), param.download_directory,
                                                                             head, tail), timeout=param.timeout)
            else:
                # create the diretcory and download the file to it
                print("directory doesn't exist, creating it now")
                os.makedirs(os.getcwd() + "/" + head, exist_ok=True)
                print("directory created, download initiated")
                result_blob = block_blob_service.get_blob_to_path(param.container, blob.name,
                                                    "{0}/{1}/{2}/{3}".format(os.getcwd(), param.download_directory,
                                                                             head, tail), timeout=param.timeout)
        else:
            result_blob = block_blob_service.get_blob_to_path(param.container, blob.name,
                                                              param.download_directory + "/" + blob.name,
                                                              timeout=param.timeout)

        if result_blob:
            print(" ({0} bytes)".format(result_blob.properties.content_length))
        else:
            print(" - ignored")
        if param.limit != 0 and limit_count >= param.limit:
            print("limit {0} reached. exit now.".format(param.limit))
            break

    end_time: float = timer()
    print("main process finished. ({0} elapsed)".format(timedelta(seconds=end_time-start_time)))

    exit(0)

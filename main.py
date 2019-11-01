import argparse
import json
import os
from azure.storage.blob import BlockBlobService
from azure.storage.blob import PublicAccess
import yaml


class Parameter:
    enable: bool = False
    account_name: str = ""
    account_key: str = ""
    container: str = ""
    limit: int = 5000
    download_directory: str = "download"

    def read(self, config):
        self.enable = bool(config['enable'])
        self.limit = int(config['limit'])
        self.account_name = str(config['account_name'])
        self.account_key = str(config['account_key'])
        self.container = str(config['container'])
        self.download_directory = str(config['download_directory']).strip("/")


if __name__ == '__main__':
    limit_count = 0

    # Set configuration
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="configuration yaml file", type=str,
                        default='config.yaml')
    parser.add_argument("--container", help="a container name of Azure Storage", type=str)
    parser.add_argument("--limit", help="if limit reached, exit immediately", type=int)
    parser.add_argument("--download", help="download directory", type=str, default="download")
    args = parser.parse_args()

    if not os.path.isfile(args.config):
        raise ValueError("ERROR: no config file exists at {0}".format(args.config))
    param = Parameter()
    with open(args.config, 'rt', encoding='UTF-8') as fin:
        print("config file: {0}".format(args.config))
        yaml_text = fin.read()
        config_nodes = yaml.load(yaml_text, Loader=yaml.Loader)
        param.read(config_nodes)

    if not args.limit:
        param.limit = args.limit
    if not args.download:
        param.download_directory = args.download
    if not args.container:
        param.container = args.container

    if not param.download_directory:
        print("ERROR: please set download directory")
        exit(1)
    if not os.path.exists(param.download_directory):
        os.makedirs(param.download_directory)

    if not param.enable:
        print("Exit because 'enable' is False")
        exit(0)
    print("{0} items will be downloaded to {1}/".format(param.limit, param.download_directory))

    # Azure Storage access
    # name of your storage account and the access key from Settings->AccessKeys->key1
    block_blob_service = BlockBlobService(account_name=param.account_name, account_key=param.account_key)

    # name of the container
    generator = block_blob_service.list_blobs(param.container)

    # code below lists all the blobs in the container and downloads them one after another
    for blob in generator:
        print("blob: {0}".format(blob.name))
        # check if the path contains a folder structure, create the folder structure
        if "/" in "{}".format(blob.name):
            print("there is a path in this")
            # extract the folder path and check if that folder exists locally, and if not create it
            head, tail = os.path.split("{}".format(blob.name))
            print(head)
            print(tail)
            if os.path.isdir(os.getcwd() + "/" + head):
                # download the files to this directory
                print("directory and sub directories exist")
                block_blob_service.get_blob_to_path(param.container, blob.name,
                                                    "{0}/{1}/{2}/{3}".format(os.getcwd(), param.download_directory,
                                                                             head, tail))
            else:
                # create the diretcory and download the file to it
                print("directory doesn't exist, creating it now")
                os.makedirs(os.getcwd() + "/" + head, exist_ok=True)
                print("directory created, download initiated")
                block_blob_service.get_blob_to_path(param.container, blob.name,
                                                    "{0}/{1}/{2}/{3}".format(os.getcwd(), param.download_directory,
                                                                             head, tail))
        else:
            block_blob_service.get_blob_to_path(param.container, blob.name, param.download_directory + "/" + blob.name)
        limit_count += 1
        if limit_count >= param.limit:
            print("limit {0} reached. exit now.".format(param.limit))
            break

    exit(0)

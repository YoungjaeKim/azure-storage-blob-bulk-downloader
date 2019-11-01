# azure-storage-blob-bulk-downloader

This script downloads blobs from an Azure Storage Blob container.

It is useful when you want to download only a `limit` number of items from a container.

## How to use

By default, it reads `config.yaml` file to setup Azure Storage credential and configurable values.

```bash
$ python main.py
```

### Supported Arguments
```bash
$ python main.py --config config.yaml --enable True --container 'photos' --limit 500 --download 'temp'
```

## config.yaml

```yaml
enable: True
limit: 10000  # number of blobs to download. set 0 if you want to download all
account_name: '{your_storage_name}'
account_key: '{your_storage_account_key}'
container: '{your_container_name}'  # a container(folder) name in a storage
download_directory: "download"  # local directory to store items
timeout: 30  # timeout in seconds for each blob download
```

## output example
```
config file: config.yaml
10000 items will be downloaded to 'download' directory
...
#4188: 001bab8d-bfe9-4f60-ae82-f4480e5d14d7.jpg (206399 bytes)
#4189: 001babe1-5719-4033-b133-867e9f8163b8.jpg (65658 bytes)
#4190: 001bac2c-be97-4b3a-8957-eeca0e59e61a.jpg (26708 bytes)
#4191: 001baefb-4996-47a3-bfc4-30b3c17d1eca.jpg (8124 bytes)
#4192: 001bb12d-8ca3-4f35-b49f-c114ac662a53.jpg (131410 bytes)
#4193: 001bb1fa-48cd-4f72-ad4a-53cc28b6ae7f.jpg (99048 bytes)
#4194: 001bb2f4-614a-4fe6-97a5-d643c41a968b.jpg (143516 bytes)
...
#9999: 00441f9c-896c-4e9e-a6bd-07487b596d22.jpg (33559 bytes)
#10000: 004421a9-0371-45ee-8341-ddcb8b656a86.jpg (64377 bytes)
limit 10000 reached. exit now.
```

## Reference
- Azure Blob download logic is from; https://gist.github.com/brijrajsingh/35cd591c2ca90916b27742d52a3cf6ba
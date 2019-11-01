# azure-storage-blob-bulk-downloader

This script downloads blobs from an Azure Storage Blob container.

It is useful when you want to download only a `limit` number of items from a container.

```yaml
enable: True
limit: 10000  # number of blobs to download
account_name: 'your_storage_name'
account_key: '403bICFq3cX4MIyIAxZ7VdciTMMZRiVEvSFX6g=='
container: 'images'  # a container(folder) name in a storage
download_directory: "download"
```

## Reference
- Core logic is from; https://gist.github.com/brijrajsingh/35cd591c2ca90916b27742d52a3cf6ba
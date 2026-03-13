import os
from google.cloud import storage
from typing import Optional

class GCPUtils:
      """Utilities for interacting with Google Cloud Storage."""

    def __init__(self):
              self.bucket_name = os.getenv("GCS_BUCKET_NAME", "creator-anime-assets")
              self.client = storage.Client() if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") else None

    def upload_blob(self, source_file_name: str, destination_blob_name: str):
              """Uploads a file to the bucket."""
              if not self.client:
                            print(f"[Mock] Uploading {source_file_name} to {destination_blob_name}")
                            return

        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        print(f"File {source_file_name} uploaded to {destination_blob_name}.")

    def download_blob(self, blob_name: str, destination_file_name: str):
              """Downloads a blob from the bucket."""
              if not self.client:
                            print(f"[Mock] Downloading {blob_name} to {destination_file_name}")
                            return

              bucket = self.client.bucket(self.bucket_name)
              blob = bucket.blob(blob_name)
              blob.download_to_filename(destination_file_name)
              print(f"Blob {blob_name} downloaded to {destination_file_name}.")

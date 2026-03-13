"""
GCP Utilities — Google Cloud Storage integration for Creator.
"""
import os
from typing import Optional, List
from PIL import Image
import io

from src.config import GCS_BUCKET_NAME


class GCPUtils:
    """Utilities for Google Cloud Storage operations."""

    def __init__(self, bucket_name: Optional[str] = None):
        self.bucket_name = bucket_name or GCS_BUCKET_NAME
        self._client = None

    @property
    def client(self):
        """Lazy-load the GCS client."""
        if self._client is None:
            try:
                from google.cloud import storage
                self._client = storage.Client()
            except Exception:
                self._client = None
        return self._client

    @property
    def is_available(self) -> bool:
        return self.client is not None

    def upload_blob(self, source_file_name: str, destination_blob_name: str):
        """Upload a local file to GCS."""
        if not self.is_available:
            print(f"[GCS Mock] Upload: {source_file_name} → {destination_blob_name}")
            return

        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        print(f"[GCS] Uploaded: {destination_blob_name}")

    def upload_image(self, image: Image.Image, destination_blob_name: str):
        """Upload a PIL Image directly to GCS."""
        if not self.is_available:
            print(f"[GCS Mock] Upload image → {destination_blob_name}")
            return

        buf = io.BytesIO()
        image.save(buf, format="PNG")
        buf.seek(0)

        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_file(buf, content_type="image/png")
        print(f"[GCS] Uploaded image: {destination_blob_name}")

    def download_blob(self, blob_name: str, destination_file_name: str):
        """Download a blob from GCS to a local file."""
        if not self.is_available:
            print(f"[GCS Mock] Download: {blob_name} → {destination_file_name}")
            return

        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(blob_name)
        blob.download_to_filename(destination_file_name)
        print(f"[GCS] Downloaded: {destination_file_name}")

    def download_image(self, blob_name: str) -> Optional[Image.Image]:
        """Download a blob from GCS and return as PIL Image."""
        if not self.is_available:
            print(f"[GCS Mock] Download image: {blob_name}")
            return None

        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(blob_name)
        buf = io.BytesIO()
        blob.download_to_file(buf)
        buf.seek(0)
        return Image.open(buf)

    def list_blobs(self, prefix: str = "") -> List[str]:
        """List all blobs under a prefix."""
        if not self.is_available:
            print(f"[GCS Mock] List blobs: {prefix}")
            return []

        bucket = self.client.bucket(self.bucket_name)
        return [blob.name for blob in bucket.list_blobs(prefix=prefix)]

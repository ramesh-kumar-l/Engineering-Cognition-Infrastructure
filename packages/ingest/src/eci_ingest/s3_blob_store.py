"""S3-compatible BlobStore adapter.

Implements the :class:`~eci_ingest.blob_store.BlobStore` Protocol backed by any
S3-compatible object store (AWS S3, MinIO, GCS in S3-compat mode, Cloudflare R2).

Requires ``boto3`` which is an **optional** dependency — it is lazy-imported at
instantiation time so the rest of the ingest package never depends on it.

Usage::

    ECI_BLOB_BACKEND=s3
    ECI_BLOB_S3_BUCKET=my-eci-blobs
    ECI_BLOB_S3_REGION=us-east-1
    # AWS credentials via the standard boto3 chain (env / ~/.aws / IAM role)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import types

    import boto3  # type: ignore[import-untyped]
    from mypy_boto3_s3 import S3Client  # type: ignore[import-untyped]


class S3BlobStore:
    """S3-backed BlobStore. Key layout mirrors LocalBlobStore for easy migration."""

    def __init__(
        self,
        bucket: str,
        prefix: str = "blobs/",
        region: str = "us-east-1",
        endpoint_url: str | None = None,
    ) -> None:
        if not bucket:
            raise ValueError("S3BlobStore: bucket must not be empty")
        try:
            import boto3  # type: ignore[import-untyped]
        except ImportError as exc:
            raise ImportError(
                "S3BlobStore requires boto3. Install with: pip install boto3"
            ) from exc

        self._bucket = bucket
        self._prefix = prefix.rstrip("/") + "/"
        self._s3: S3Client = boto3.client(
            "s3",
            region_name=region,
            **({"endpoint_url": endpoint_url} if endpoint_url else {}),
        )

    def _key_for(self, content_hash: str) -> str:
        if len(content_hash) < 4:
            raise ValueError(f"content_hash too short: {content_hash!r}")
        return f"{self._prefix}{content_hash[:2]}/{content_hash[2:4]}/{content_hash}"

    def uri_for(self, content_hash: str) -> str:
        return f"s3://{self._bucket}/{self._key_for(content_hash)}"

    def exists(self, content_hash: str) -> bool:
        try:
            self._s3.head_object(Bucket=self._bucket, Key=self._key_for(content_hash))
            return True
        except Exception:  # noqa: BLE001 — botocore.ClientError is optional dep
            return False

    def put(self, content_hash: str, data: bytes) -> str:
        key = self._key_for(content_hash)
        if not self.exists(content_hash):
            self._s3.put_object(
                Bucket=self._bucket,
                Key=key,
                Body=data,
                ContentType="application/octet-stream",
            )
        return self.uri_for(content_hash)

    def get(self, content_hash: str) -> bytes:
        key = self._key_for(content_hash)
        try:
            response = self._s3.get_object(Bucket=self._bucket, Key=key)
            body: bytes = response["Body"].read()
            return body
        except Exception as exc:  # noqa: BLE001
            raise FileNotFoundError(
                f"Blob not found in S3: s3://{self._bucket}/{key}"
            ) from exc

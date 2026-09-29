import os
import sys
from pathlib import Path

from google.cloud import storage


def _validate_upload_target(file_arg: str) -> tuple[str, str]:
    bucket_name = os.getenv('bucket')
    if not bucket_name:
        raise RuntimeError('bucket environment variable is not set')

    local_path = Path(file_arg).expanduser()
    if not local_path.is_absolute():
        local_path = Path('/') / local_path

    resolved = local_path.resolve(strict=True)
    allowed_roots = [Path('/shared').resolve(), Path('/').resolve()]
    if not any(str(resolved).startswith(str(root) + os.sep) or resolved == root for root in allowed_roots):
        raise ValueError(f'Upload path is outside the allowed roots: {file_arg}')

    if not resolved.is_file():
        raise FileNotFoundError(f'Upload target is not a file: {file_arg}')

    return str(resolved), bucket_name


try:
    filename = sys.argv[1]
    local_path, bucket_name = _validate_upload_target(filename)
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename.lstrip('/'))
    blob.upload_from_filename(local_path)
except Exception as exc:
    print('Error uploading to GCS')
    print(exc)
    raise SystemExit(1)

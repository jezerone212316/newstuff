import os
import sys
from pathlib import Path

import boto3


def _validate_upload_target(file_arg: str) -> tuple[str, str]:
    bucket = os.getenv('bucket')
    if not bucket:
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

    return str(resolved), bucket


try:
    filename = sys.argv[1]
    local_path, bucket = _validate_upload_target(filename)
    s3_client = boto3.client('s3')
    object_key = filename.lstrip('/')
    s3_client.upload_file(local_path, bucket, object_key)
except Exception as exc:
    print('Error uploading to s3')
    print(exc)
    raise SystemExit(1)

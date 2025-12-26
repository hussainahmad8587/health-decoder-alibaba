from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class OssConfig:
    endpoint: str
    bucket: str
    access_key_id: str
    access_key_secret: str

class AlibabaOssStorageAdapter:
    """
    Upload CSV exports to Alibaba Cloud OSS (optional, user-controlled).
    OSS SDK v2: :contentReference[oaicite:9]{index=9}
    """
    def __init__(self, cfg: OssConfig):
        self.cfg = cfg
        # TODO: initialize OSS client using alibabacloud_oss_v2
        # Keep this isolated so local mode works without OSS creds.

    def put_text(self, key: str, content: str) -> str:
        # TODO: upload to OSS and return an object URL or key
        raise NotImplementedError

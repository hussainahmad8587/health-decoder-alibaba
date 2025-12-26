from __future__ import annotations
from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    vision_backend: str = os.getenv("HD_VISION_BACKEND", "local")          # local|alibaba_imm
    storage_backend: str = os.getenv("HD_STORAGE_BACKEND", "local")        # local|alibaba_oss

    region: str = os.getenv("ALIBABA_REGION", "cn-shanghai")

    # OSS
    oss_endpoint: str = os.getenv("ALIBABA_OSS_ENDPOINT", "")
    oss_bucket: str = os.getenv("ALIBABA_OSS_BUCKET", "")
    access_key_id: str = os.getenv("ALIBABA_ACCESS_KEY_ID", "")
    access_key_secret: str = os.getenv("ALIBABA_ACCESS_KEY_SECRET", "")

    # IMM
    imm_endpoint: str = os.getenv("ALIBABA_IMM_ENDPOINT", "")
    imm_project: str = os.getenv("ALIBABA_IMM_PROJECT", "")

    # PAI EAS (optional)
    pai_eas_endpoint: str = os.getenv("PAI_EAS_ENDPOINT", "")
    pai_eas_token: str = os.getenv("PAI_EAS_TOKEN", "")

def get_settings() -> Settings:
    return Settings()

from __future__ import annotations

from typing import Annotated
from zoneinfo import ZoneInfo

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str
    admin_ids: Annotated[list[int], NoDecode] = []
    root_id: int
    database_url: str = "sqlite+aiosqlite:///data/innobot.db"

    captcha_length: int = 5
    captcha_ttl: int = 120
    captcha_max_attempts: int = 3

    throttle_rate: float = 0.7
    timezone: str = "Asia/Tashkent"

    @field_validator("admin_ids", mode="before")
    @classmethod
    def _split_admin_ids(cls, value):
        if isinstance(value, str):
            return [int(x) for x in value.replace(";", ",").split(",") if x.strip()]
        return value

    @property
    def tz(self) -> ZoneInfo:
        return ZoneInfo(self.timezone)


settings = Settings()

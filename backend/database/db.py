from __future__ import annotations

from pymongo import MongoClient
from pymongo.database import Database
from config.settings import get_settings


class MongoConnection:
    _client: MongoClient | None = None

    @classmethod
    def get_db(cls) -> Database:
        if cls._client is None:
            settings = get_settings()
            cls._client = MongoClient(settings.mongo_uri)
        settings = get_settings()
        return cls._client[settings.mongo_db_name]

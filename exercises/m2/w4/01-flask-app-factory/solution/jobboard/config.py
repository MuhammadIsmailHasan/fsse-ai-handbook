"""Configuration classes. Real secrets come from environment variables."""

import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    JSON_SORT_KEYS = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = "test-only"

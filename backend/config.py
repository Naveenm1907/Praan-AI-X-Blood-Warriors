import os

APP_MODE = os.getenv("APP_MODE", "mock")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
DYNAMODB_TABLE_PREFIX = os.getenv("DYNAMODB_TABLE_PREFIX", "praan")

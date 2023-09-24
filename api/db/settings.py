import os

TEST = 'test'
ENVIRONMENT = os.getenv('ENVIRONMENT', TEST)

DATABASE_FILENAME = f"database_{ENVIRONMENT}.sqlite"
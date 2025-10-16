import os

"""
Global application settings, which are obtained from environment variables
"""

# DATABASE
DB_TYPE = os.environ.get("DB_TYPE", "postgresql+asyncpg")
DB_USER = os.environ.get("DB_USER", "frontend_settings_admin")
DB_PASS = os.environ.get("DB_PASS", "")
DB_HOST = os.environ.get("DB_HOST", "pgbouncer")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "frontend_settings")
DB_SCHEMA = os.environ.get("DB_SCHEMA", "public")

POSTGRES_ITEMS_LIMIT_IN_QUERY = 32_000

DATABASE_URL = f"{DB_TYPE}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


# KEYCLOAK
KEYCLOAK_PROTOCOL = os.environ.get("KEYCLOAK_PROTOCOL", "http")
KEYCLOAK_HOST = os.environ.get("KEYCLOAK_HOST", "keycloak")
KEYCLOAK_PORT = os.environ.get("KEYCLOAK_PORT", "")
KEYCLOAK_REDIRECT_PROTOCOL = os.environ.get("KEYCLOAK_REDIRECT_PROTOCOL", None)
KEYCLOAK_REDIRECT_HOST = os.environ.get("KEYCLOAK_REDIRECT_HOST", None)
KEYCLOAK_REDIRECT_PORT = os.environ.get("KEYCLOAK_REDIRECT_PORT", None)
KEYCLOAK_REALM = os.environ.get("KEYCLOAK_REALM", "avataa")
KEYCLOAK_CLIENT_ID = os.environ.get("KEYCLOAK_CLIENT_ID", "frontend-settings")
KEYCLOAK_CLIENT_SECRET = os.environ.get("KEYCLOAK_CLIENT_SECRET", None)

if KEYCLOAK_REDIRECT_PROTOCOL is None:
    KEYCLOAK_REDIRECT_PROTOCOL = KEYCLOAK_PROTOCOL
if KEYCLOAK_REDIRECT_HOST is None:
    KEYCLOAK_REDIRECT_HOST = KEYCLOAK_HOST
if KEYCLOAK_REDIRECT_PORT is None:
    KEYCLOAK_REDIRECT_PORT = KEYCLOAK_PORT

KEYCLOAK_URL = f"{KEYCLOAK_PROTOCOL}://{KEYCLOAK_HOST}:{KEYCLOAK_PORT}"
KEYCLOAK_PUBLIC_KEY_URL = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}"
KEYCLOAK_REDIRECT_URL = f"{KEYCLOAK_REDIRECT_PROTOCOL}://{KEYCLOAK_REDIRECT_HOST}:{KEYCLOAK_REDIRECT_PORT}"
KEYCLOAK_TOKEN_URL = f"{KEYCLOAK_REDIRECT_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
KEYCLOAK_AUTHORIZATION_URL = f"{KEYCLOAK_REDIRECT_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/auth"


# OPA
OPA_PROTOCOL = os.environ.get("OPA_PROTOCOL", "http")
OPA_HOST = os.environ.get("OPA_HOST", "opa")
OPA_PORT = os.environ.get("OPA_PORT", "8181")
OPA_POLICY = os.environ.get("OPA_POLICY", "main")

OPA_URL = f"{OPA_PROTOCOL}://{OPA_HOST}:{OPA_PORT}"
OPA_POLICY_PATH = f"/v1/data/{OPA_POLICY}"


# OTHER
DEBUG = os.environ.get("DEBUG", "False").upper() in ("TRUE", "Y", "YES", "1")
SECURITY_TYPE = os.environ.get("SECURITY_TYPE", "DISABLE").upper()


# STATE
EXPIRES_IN_MINUTES_LIMIT = int(
    os.environ.get("EXPIRES_IN_MINUTES_LIMIT", "10080")
)  # 7 * 24 * 60
DROP_EXPIRED_MINUTES = int(
    os.environ.get("DROP_EXPIRED_MINUTES", "43200")
)  # 30 * 24 * 60
DROP_INTERVAL_MINUTES = int(os.environ.get("DROP_INTERVAL_MINUTES", "60"))

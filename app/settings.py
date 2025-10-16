import os

"""
Global application settings, which are obtained from environment variables
"""

# APP
TITLE = "Frontend Settings"
PREFIX = f"/api/{TITLE.replace(' ', '_').lower()}"


# OTHER
DEBUG = os.environ.get("DEBUG", "False").upper() in ("TRUE", "Y", "YES", "1")
SECURITY_TYPE = os.environ.get("SECURITY_TYPE", "DISABLE").upper()
UVICORN_WORKERS = os.environ.get("UVICORN_WORKERS", "")

# DOCUMENTATION
DOCS_ENABLED = os.environ.get("DOCS_ENABLED", "True").upper() in (
    "TRUE",
    "Y",
    "YES",
    "1",
)
DOCS_CUSTOM_ENABLED = os.environ.get(
    "DOCS_CUSTOM_ENABLED", "False"
).upper() in ("TRUE", "Y", "YES", "1")
SWAGGER_JS_URL = os.environ.get("DOCS_SWAGGER_JS_URL", None)
SWAGGER_CSS_URL = os.environ.get("DOCS_SWAGGER_CSS_URL", None)
REDOC_JS_URL = os.environ.get("DOCS_REDOC_JS_URL", None)

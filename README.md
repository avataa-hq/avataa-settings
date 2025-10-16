# Frontend Settings

Microservice for storing frontend settings

## Environments variables

```toml
DB_HOST=<pgbouncer/postgres_host>
DB_NAME=<pgbouncer/postgres_frontend_settings_db_name>
DB_PASS=<pgbouncer/postgres_frontend_settings_password>
DB_PORT=<pgbouncer/postgres_port>
DB_TYPE=postgresql+asyncpg
DB_USER=<pgbouncer/postgres_frontend_settings_user>
DEBUG=<True/False>
DOCS_CUSTOM_ENABLED=<True/False>
DOCS_REDOC_JS_URL=<redoc_js_url>
DOCS_SWAGGER_CSS_URL=<swagger_css_url>
DOCS_SWAGGER_JS_URL=<swagger_js_url>
KEYCLOAK_CLIENT_ID=<frontend_settings_client>
KEYCLOAK_CLIENT_SECRET=<frontend_settings_client_secret>
KEYCLOAK_HOST=<keycloak_host>
KEYCLOAK_PORT=<keycloak_port>
KEYCLOAK_PROTOCOL=<keycloak_protocol>
KEYCLOAK_REALM=avataa
KEYCLOAK_REDIRECT_HOST=<keycloak_external_host>
KEYCLOAK_REDIRECT_PORT=<keycloak_external_port>
KEYCLOAK_REDIRECT_PROTOCOL=<keycloak_external_protocol>
OPA_HOST=<opa_host>
OPA_POLICY=main
OPA_PORT=<opa_port>
OPA_PROTOCOL=<opa_protocol>
SECURITY_MIDDLEWARE_HOST=security-middleware
SECURITY_MIDDLEWARE_PORT=8000
SECURITY_MIDDLEWARE_PROTOCOL=http
SECURITY_TYPE=<security_type>
UVICORN_WORKERS=<uvicorn_workers_number>
```

### Explanation

#### Database
`DB_TYPE` Type of database
(default: _postgresql_)
`DB_USER` Pre-created user in the database with rights to edit the database
(default: _generator_admin_)
`DB_PASS` Database user password
(default: _generator_pass_)
`DB_HOST` Database host
(default: _localhost_)
`DB_PORT`  Database port
(default: _5432_)
`DB_NAME`  Name of the previously created database
(default: _settings_)
`DB_SCHEMA`  Database schema for work
(default: _public_)

#### Keycloak
`KEYCLOAK_PROTOCOL` Protocol for internal communication of microservice with Keycloak
(default: _http_)
`KEYCLOAK_HOST` Host for internal communication of microservice with Keycloak
(default: _keycloak_)
`KEYCLOAK_PORT` Port for internal communication of microservice with Keycloak
(default: _8080_)
`KEYCLOAK_REDIRECT_PROTOCOL` Protocol that is used to redirect the user for authorization in Keycloak
(default: _as in key `KEYCLOAK_PROTOCOL`_)
`KEYCLOAK_REDIRECT_HOST` Host that is used to redirect the user for authorization in Keycloak
(default: _as in key `KEYCLOAK_HOST`_)
`KEYCLOAK_REDIRECT_PORT` Port that is used to redirect the user for authorization in Keycloak
(default: _as in key `KEYCLOAK_PORT`_)
`KEYCLOAK_REALM`  Realm for the current microservice
(default: _master_)
`KEYCLOAK_CLIENT_ID` Client ID for the current microservice
`KEYCLOAK_CLIENT_SECRET` Client secret for the current microservice
(default: _EMPTY_)

#### Other
`DEBUG` Debug mode
(default: _False_)
`DISABLE_SECURITY` disable keycloak
(default: _False_)

#### Compose

- `REGISTRY_URL` - Docker regitry URL, e.g. `harbor.domain.com`
- `PLATFORM_PROJECT_NAME` - Docker regitry project Docker image can be downloaded from, e.g. `avataa`

### Requirements
```
$ pip install -r requirements.txt
```

### Migrations
```
$ alembic -c v1/alembic.ini upgrade head
```

### Running

```
$ cd app
$ uvicorn main:app --reload

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720]
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```
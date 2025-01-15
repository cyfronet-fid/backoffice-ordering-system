# backoffice-ordering-system


## Backend

All commands are executed in `/backend` dir and inside a poetry shell (unless stated otherwise).


### Dependencies
I recommend using [mise](https://mise.jdx.dev) for python versioning (check `/.mise.toml` for exact version)

- [python 3.12](https://docs.python.org/3/whatsnew/3.12.html)
- [poetry](https://python-poetry.org) - dependency management, building, packaging, scripting (after installing python, run `python -m pip install poetry` to install)

### Tech stack
- [fastapi](https://fastapi.tiangolo.com) - server framework
- [sqlmodel](https://sqlmodel.tiangolo.com) - ORM
- [pydantic](https://docs.pydantic.dev/latest/) - models, serialization, ENV
- [alembic](https://alembic.sqlalchemy.org/en/latest/) - migrations
- [postgresql](https://www.postgresql.org/) - db

Refer to the documentations linked if some info is missing here.

### Install deps

```shell
poetry install
```

From now on, execute every command inside a poetry shell:
```shell
poetry shell
```

### Run dev server
```shell
uvicorn app.main:app --reload --host localhost
```

### Run docker dependencies

Excluding the actual service. When developing, you should be using ["bare-metal" uvicorn](#run-server) because it allows you to reload seamlessly, and you don't need to rebuild the image on every code change.

Remove the `--scale` param to also launch the backend.

```shell
docker compose up --scale bos-backend=0
```

### Migrations

Run pending migrations:
```shell
alembic upgrade head
```

Generate a new migration based on your new models
```shell
alembic revision --autogenerate -m "{MIGRATION NAME}"
```

### Run tests

```shell
poetry run pytest tests/
```

### Run linters/formatters

Check mode
```shell
black --check --verbose app/ && isort --check-only --verbose app/ && bandit -r --verbose app/ && mypy app/ && pylint --verbose app/
```

Write mode
```shell
black app && isort app
```

*PS: Tests and linters will also run on GitHub push so you better run and check them locally first :)*


### ENV

We're using automatic env parsing lib ([pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)). 
Check `/backend/app/config.py` for more details.

**NOTE**: They need to be present on the server host/container BEFORE starting the server to be respected.

- `DB_HOST` - host of the postgres server (default: `localhost`)
- `DB_PORT` - port of the postgres server (default: `5432`)
- `DB_USER` - user of the postgres server (default: `pg`)
- `DB_PASSWORD` - password of the postgres server (default: `pg`), for production this needs to be changes, obviously
- `DB_NAME` - name of the postgres db (default `postgres`)

## Frontend

All commands are executed in `/frontend` dir (unless stated otherwise).

### Dependencies
I recommend using [mise](https://mise.jdx.dev) for node versioning (check `/.mise.toml` for exact version)

- [node@21](https://nodejs.org/en) - js runtime
- [npm](https://www.npmjs.com/) - dependency management, building, packaging, scripting (will be installed alongside node)

### Tech stack
- [Typescript](https://www.typescriptlang.org/) - typing, transpiler
- [React 18](https://react.dev/) - frontend framework
- [React Router](https://reactrouter.com/en/main) - client-side routing
- [Vite](https://vite.dev/guide/) - react initialization/management
- [hey-api/openapi-ts](https://github.com/hey-api/openapi-ts) - automatic client generation

### Install deps

```shell
npm install
```

### Run dev server
```shell
npm run dev
```

### Build production assets
They will be in the `/frontend/dist/` directory. They will be ready to be served on production.

```shell
npm run build
```

### Run linters/formatters

Check-only mode
```shell
npm run lint
```

Write mode
```shell
npm run format
```

*PS: Linters will also run on GitHub push so you better run and check them locally first :)*


### Generate Typescript client (for dev)

**NOTE**: Backend must be running (on http://localhost:8000) for this to work

```shell
npm run generate-client
```

### ENV

**NOTE**: They need to be present to be respected while *building* the app with `npm run build` for production.

- `VITE_BACKEND_URL` - url of the backend server (default: `http://localhost:8000`)
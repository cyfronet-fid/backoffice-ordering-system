FROM python:3.12

RUN python -m pip install poetry
RUN export PATH="$HOME/.local/bin:$PATH"

WORKDIR /backend
COPY . /backend

RUN poetry install --no-interaction --no-cache --without dev

EXPOSE 8080
ENTRYPOINT ["poetry", "run", "uvicorn", "app.main:app", "--port", "8000", "--host", "0.0.0.0"]


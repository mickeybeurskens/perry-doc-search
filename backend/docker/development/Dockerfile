FROM python:3.11 as requirements-stage

WORKDIR /tmp
 
RUN pip install poetry
 
COPY ./pyproject.toml ./poetry.lock* /tmp/
 
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --with dev
 
FROM python:3.11

WORKDIR /app
 
COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt
 
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
 
COPY ./perry /perry
 
CMD ["uvicorn", "perry.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Perry Backend
Backend instance of the perry app built for deployment.


## Installing Locally
Install [Poetry](https://python-poetry.org/) and run:
```bash
pip install poetry
poetry install
```

Then run the backend using FastAPI: 
```bash
uvicorn perry.api.app:app --host 0.0.0.0 --port 8000 --reload
```

This runs the app in development mode and reloads automatically when the source files are changed. 

## Environment variables
In order to use the OpenAI models, you need to store a key in a `.env` file locally (in the `backend` directory). It is not tracked by version management and should contain the key:
```
OPENAI_API_KEY="YOUR_KEY_HERE"
```

## Tests
To run the tests, run:
```bash
pytest tests
```
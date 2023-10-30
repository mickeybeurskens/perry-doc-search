# 🕵 Perry AI Powered Document Analysis
Perry - AI Powered Document Analysis.
Perry allows you to upload PDF documents for question answering and information search.
The project contains a fully functioning backend with authentication built in [FastAPI](https://fastapi.tiangolo.com/), with document search built using [LLamaIndex](https://github.com/run-llama/llama_index). 
The frontend has been built using [Streamlit](https://github.com/run-llama/llama_index), and deployment is done through Docker.

## Disclaimer
Everything is this repository has served as a proof of concept for a limited amount of users. You can use if for inspiration, but it is not production ready out of the box. Especially document uploads and session management will not scale with user demand. 


## Getting Started
Read the README is the subdirectories for more information on how to get started.

## Docker
This repository can be developed and deployed using docker. The docker setup is split into `development.yml` and `production.yml`. The development file is used for local development and the production file is used for deployment to production.

### Running Docker
A local docker setup:
```
docker compose -f docker/development.yml up
```

### Deploying To Production
A production docker setup with a reverse proxy and https encryption:
```
docker compose -f docker/production.yml up
```

## Attribution
This project has been created by Mickey Beurskens. Check my blog [Mickey.Coffee](https://mickey.coffee) ☕ or my company website at [Forge Fire AI Engineering](https://forgefire.dev/) 🔥.
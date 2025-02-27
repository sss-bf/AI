# AI Backend Server

## Dependencies

- Python 3
- Fast API
  - fastapi
  - "uvicorn[standard]"
- LangChain
  - langchain
  - langchain-community
  - langchain-openai
- Python Dotenv
  - python-dotenv

### Environment

- Create `.env` using `.env.example` file
- `ENVIRONMENT` need to set to `publish` when you publish this project
- If you want to run in development environment, you should set `ENVIRONMENT`to `dev`

## How to run

- Run API Server using below command root path in this Repository.

```
> uvicorn api_server:app --host 0.0.0.0 --port 9000
// if you want to change port number, modify value of `--port`
```

## Documentation

- Use Open API Document (Swagger Page)
  - During server is running, Access `http://127.0.0.1:9000` in Web Browser.
  - you can see the documents of API and you can also test it.

# AI Backend Server

## Setup

### 1. Install Python

### 2. install modules of Python

```
pip3 install fastapi
pip3 install "uvicorn[standard]"
pip3 install langchain
pip3 install langchain
pip3 install -U langchain-community langchain-openai
pip3 install python-dotenv
```

### 3. Setup Environment File

- Create `.env` File in this root path. (the same path with api_server.py)
- write below text. (you must replace the `real api key` to real your api key)

```
OPENAI_API_KEY=real api key
```

## How To Run API Server

### Run API Server

```
> uvicorn api_server:app --host 0.0.0.0 --port 9000
// if you want to change port number, modify value of `--port`
```

## Documentation

- Use Open API Document (Swagger Page)
  - During server is running, Access `http://127.0.0.1:9000` in Web Browser.
  - you can see the documents of API and you can also test it.

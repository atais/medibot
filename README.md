# Medibot

Trying to automate search process in Medicover

## Inspired on

- https://github.com/apqlzm/medihunter
- https://github.com/dyrkin/luxmed-bot

## Running

```commandline
docker build -t medibot .
docker run --rm -p 3333:8000 medibot
```

## Development

first time:
```commandline
python3 -m venv 
pip install -r requirements.txt
```

venv:
```commandline
source .venv/bin/activate
deactivate
```

start server from cmd
```commandline
uvicorn app:app --reload
```
start server from code
```commandline
python app.py
```

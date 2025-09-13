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

## License

This project is licensed under the MIT License, one of the most permissive open-source licenses. 
You are free to use, modify, and distribute this software with minimal restrictions. 
See the LICENSE file for details.

## Disclaimer

This project is provided for educational and personal use only. 
It is not affiliated with, endorsed by, or associated with any third-party service. 
The authors make no representations or warranties of any kind, express or implied, about the completeness, accuracy, reliability, suitability, or availability 
with respect to the project or the information, products, services, or related graphics contained in the project for any purpose. 
Any use of this software is at your own risk. 
The authors shall not be liable for any loss or damage, including without limitation, indirect or consequential loss or damage, 
or any loss or damage whatsoever arising from loss of data or profits arising out of, or in connection with, the use of this software.

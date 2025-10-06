# Medibot

Exploring AI-assisted programming by interacting with online services using Python. 
The project experiments with automation of the search process in Medicover by providing 
a multi-user platform with a WebUI. The app sends real-time Firebase push notifications when appointments become available.

## Inspired on

- https://github.com/apqlzm/medihunter
- https://github.com/dyrkin/luxmed-bot

## Running

### Docker Compose

Use this template to expose medibot on port 3333

```
services:
  medibot:
    image: atais/medibot:latest
    container_name: medibot
    ports:
      - "3333:8000"
    volumes:
      - /your/path/medibot.sqlite:/app/medibot.sqlite
      - /your/path/firebase-service-account.json:/app/firebase-service-account.json
      - /your/path/.env:/app/.env
    restart: unless-stopped
```

### Prepare .env file

1. Copy `.env.example` as `.env`
2. Fill with your values

### Prepare firebase project

To enable push notifications, you need to set up Firebase Cloud Messaging (FCM):

1. https://console.firebase.google.com/
2. Create a Firebase Project
3. Generate Service Account Key, place `firebase-service-account.json` in the project root
4. Get Web App Configuration, update `/static/firebase-config.js` with your configuration.
5. Generate VAPID Key, update it in `/static/firebase-config.js`
6. Enable Notifications in Browser

### Build & run the application with docker

```commandline
docker build -t medibot .
docker run --rm -p 3333:8000 -v /local/medibot.sqlite:/app/medibot.sqlite --name medibot medibot
```

This will expose the WebUI on port 3333

## Development

first time:
```commandline
npm install
npm run build

python3.13 -m venv .venv
pip install -r requirements.txt
```

venv:
```commandline
source .venv/bin/activate
deactivate
```

start server from code
```commandline
python app.py
```

If you change JS or CSS, rebuild the frontend with `npm run build`!

## _scripts

Folder contains helpers to generate:

- `static/locations.json`
- `static/specialities.json`

files. Their content should contain all the available options.

If it does not, this approach allows for manual fixes :smile:.

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

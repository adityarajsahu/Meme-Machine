# Meme-Machine
The Meme Machine is a fully autonomous AI-powered meme generator that takes a user-submitted idea and turns it into a ready-to-post meme—no human curation involved. Built using Google’s Agent Development Kit, FastAPI, OpenCV, and PRAW, this multi-agent system includes content moderation, meme template selection via sentence embeddings, witty caption generation using Gemini API, and automated Reddit publishing. It’s a fun experiment in real-time, scalable, and safe AI-driven humor. This project was developed for the **Agent Development Kit Hackathon with Google Cloud**.

## Getting Started
Follow these steps to set up the application on your local machine:

### Dependencies
- Update the local package index from the online software repositories and installs the latest versions of currently installed packages.
```
sudo apt-get update
sudo apt-get upgrade
```
- Install OpenGL runtime library, if not already installed.
```
sudo apt install libgl1
```
- Install Python virtual environment package, if not already installed.
```
sudo apt install python3-venv
```

### Setup Virtual Environments
- Create separate virtual environments for backend microservice and frontend.
```
python3 -m venv fastapi_env
python3 -m venv streamlit_env
```
- Install backend microservice python dependencies in fastapi_env
```
source fastapi_env/bin/activate
pip install -r requirements.txt
```
- Install frontend python dependencies in streamlit_env
```
source streamlit_env/bin/activate
pip install -r UI/requirements.txt
```

### Run Frontend & Backend Service
- Run the backend service using it's shell script
```
chmod +x start_service.sh stop_service.sh
./start_service.sh
```
- Run the streamlit frontend using it's shell script
```
cd UI/
chmod +x start_ui_service.sh stop_ui_service.sh
./start_ui_service.sh
```

The fastapi backend service runs on port 8080 and streamlit frontend service runs on port 8501. In order to verify if the services are running using the following command,
```
sudo apt install net-tools
netstat -plunt | grep <PORT_NUMBER>
```
This command will display if there is any service running on the corresponding port, if not check the logs to debug.

To stop any of the service, use it's corresponding stop shell script,
```
./stop_service.sh

cd UI/
./stop_ui_service.sh
```

### Environment Variables
The FastAPI service requires a set of environment variables, which are saved in `agents/` sub-directory inside `.env` file

```
GOOGLE_API_KEY = "..."
GOOGLE_GENAI_USE_VERTEXAI = FALSE
CLIENT_ID = "..."
CLIENT_SECRET = "..."
REDDIT_USER_AGENT = "..."
REDDIT_USERNAME = "..."
REDDIT_PASSWORD = "..."
```

- Google API key is actually Gemini API key from [Google AI for Developer](https://ai.google.dev/gemini-api/docs/api-key).
- Get the Client ID, Client Secret and Reddit User Agent from [Reddit Preferences](https://www.reddit.com/prefs/apps).
- Reddit Username and Password is your regular Reddit login credentials.
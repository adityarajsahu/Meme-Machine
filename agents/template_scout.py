from google.adk.agents import BaseAgent
import requests
from bs4 import BeautifulSoup

class TemplateScoutAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name = "TemplateScout",
            description = "Scrape Imgflip for top meme templates."
        )

    async def run(self, query, session, tools):
        prompt = session.state.get("prompt")
        res = requests.get("https://api.imgflip.com/get_memes")
        return res.json()
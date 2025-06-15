from google.adk.agents import BaseAgent
from sentence_transformers import SentenceTransformer
import json

class TemplateScoutAgent(BaseAgent):
    class Config:
        extra = "allow"

    def __init__(self):
        super().__init__(
            name = "TemplateScout",
            description = "Scrape Imgflip for top meme templates.",
        )
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.meme_data = None
        self.get_meme_data()

    def get_meme_data(self):
        with open("data/meme_data_with_embeddings.json", "r") as file:
            self.meme_data = json.load(file)

    async def run(self, query, session, tools):
        prompt = session.state.get("prompt")

        prompt_embedding = self.model.encode([prompt])
        meme_embeddings = [meme["embedding"] for meme in self.meme_data]
        similarities = self.model.similarity(meme_embeddings, prompt_embedding).tolist()
        flattened_similarities = [sim[0] for sim in similarities]
        idx = flattened_similarities.index(max(flattened_similarities))

        return self.meme_data[idx]["url"]
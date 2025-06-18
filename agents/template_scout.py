from google.adk.agents import BaseAgent, Agent
from google.genai import types
from sentence_transformers import SentenceTransformer
import json
from dotenv import load_dotenv
import os

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = os.getenv("GOOGLE_GENAI_USE_VERTEXAI")

# class TemplateScoutAgent(BaseAgent):
#     class Config:
#         extra = "allow"

#     def __init__(self):
#         super().__init__(
#             name = "TemplateScout",
#             description = "Scrape Imgflip for top meme templates.",
#         )
#         self.model = SentenceTransformer("all-MiniLM-L6-v2")
#         self.meme_data = None
#         self.get_meme_data()

#     def get_meme_data(self):
#         with open("data/meme_data_with_embeddings.json", "r") as file:
#             self.meme_data = json.load(file)

#     async def run(self, query, session, tools):
#         prompt = session.state.get("prompt")

#         prompt_embedding = self.model.encode([prompt])
#         meme_embeddings = [meme["embedding"] for meme in self.meme_data]
#         similarities = self.model.similarity(meme_embeddings, prompt_embedding).tolist()
#         flattened_similarities = [sim[0] for sim in similarities]
#         idx = flattened_similarities.index(max(flattened_similarities))

#         return self.meme_data[idx]["url"]

agent_instruction = """You are an agent whose task is to execute the 'get_template_url' tool with state key 'prompt' as argument. Strictly, just provide the output from tool as response, DO NOT add any prefixes, explanations, hashtags, or any other extra text."""

def get_template_url(prompt: str):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    with open("data/meme_data_with_embeddings.json", "r") as file:
        meme_data = json.load(file)

    prompt_embedding = model.encode([prompt])
    meme_embeddings = [meme["embedding"] for meme in meme_data]
    similarities = model.similarity(meme_embeddings, prompt_embedding).tolist()
    flattened_similarities = [sim[0] for sim in similarities]
    idx = flattened_similarities.index(max(flattened_similarities))
    return meme_data[idx]["url"]

TemplateScoutAgent = Agent(
    name = "template_scout",
    model = "gemini-2.0-flash",
    instruction = agent_instruction,
    output_key = "image_url",
    tools = [get_template_url],
    generate_content_config = types.GenerateContentConfig(
        temperature = 0.1
    )
)
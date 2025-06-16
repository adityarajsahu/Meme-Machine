from google.adk.agents import LlmAgent
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = os.getenv("GOOGLE_GENAI_USE_VERTEXAI")

agent_instruction = """You are a creative content writer specializing in short, funny, and sarcastic captions for meme posts. Your voice is witty, clever, and embraces modern internet humor. For the state key 'prompt', your single task is to generate a fitting caption. Do not provide explanations, hashtags, or any extra text—only the caption itself. Do not write captions longer than 20 words."""

CaptionGenerationAgent = LlmAgent(
    name = "trend_captionist",
    model = "gemini-2.0-flash",
    instruction = agent_instruction,
    output_key = "caption",
    generate_content_config = types.GenerateContentConfig(
        temperature = 0.8,
        max_output_tokens = 40
    )
)
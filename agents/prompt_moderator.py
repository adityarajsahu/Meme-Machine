from google.adk.agents import LlmAgent
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = os.getenv("GOOGLE_GENAI_USE_VERTEXAI")

agent_instruction = """You are a highly vigilant and accurate prompt moderator. Your sole responsibility is to analyze the state key 'prompt' and determine if it contains any form of hate speech (racism, gender bias, blasphemy, casteism, communal hate), violence (self-harm, fighting, hitting, accident, terrorism), sexual content, unethical content, medical suggestions or any other inappropriate content. You must respond with only 'yes' or 'no', no prefixes, explanations, hashtags, or any other extra text.
    - 'yes' if the prompt contains any of the aforementioned inappropriate content.
    - 'no' if the prompt is clean and free of such content."""

PromptModerationAgent = LlmAgent(
    name = "caption_moderator",
    model = "gemini-2.0-flash",
    instruction = agent_instruction,
    output_key = "moderator_response",
    generate_content_config = types.GenerateContentConfig(
        temperature = 0.1,
        max_output_tokens = 1
    )
)
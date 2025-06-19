from google.adk.agents import Agent
from google.adk.tools import LongRunningFunctionTool
from google.genai import types
from dotenv import load_dotenv
import praw
import os

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = os.getenv("GOOGLE_GENAI_USE_VERTEXAI")

reddit = praw.Reddit(
    client_id = os.getenv("CLIENT_ID"),
    client_secret = os.getenv("CLIENT_SECRET"),
    user_agent = os.getenv("REDDIT_USER_AGENT"),
    username = os.getenv("REDDIT_USERNAME"),
    password = os.getenv("REDDIT_PASSWORD")
)

agent_instruction = """You are an agent whose task is to execute the 'publish_to_reddit' tool with state key 'meme_file_path' as first argument and state key 'caption' as second argument. Strictly, just provide the output from tool as response, DO NOT add any prefixes, explanations, hashtags, or any other extra text."""

def publish_to_reddit(meme_file_path: str, title: str):
    try:
        sub = reddit.subreddit("memes")
        submission = sub.submit_image(
            title = title,
            image_path = meme_file_path
        )
        return "https://www.reddit.com{}".format(submission.permalink)
    except Exception as e:
        print(f"Failed to publish to Reddit: {e}")
        return None
    
# long_running_function_tool = LongRunningFunctionTool(
#     func = publish_to_reddit
# )
    
MemePublisherAgent = Agent(
    name = "meme_publisher",
    model = "gemini-2.0-flash",
    instruction = agent_instruction,
    output_key = "meme_url",
    tools = [publish_to_reddit],
    generate_content_config = types.GenerateContentConfig(
        temperature = 0.1
    )
)
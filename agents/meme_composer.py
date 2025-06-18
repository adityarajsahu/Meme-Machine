from google.adk.agents import Agent
from google.genai import types
import cv2
import numpy as np
import requests
import datetime
from dotenv import load_dotenv
import os

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = os.getenv("GOOGLE_GENAI_USE_VERTEXAI")

agent_instruction = """You are an agent whose task is to execute the 'generate_meme_image' tool with state key 'image_url' as first argument and state key 'caption' as second argument. Strictly, just provide the output from tool as response, DO NOT add any prefixes, explanations, hashtags, or any other extra text."""

def read_image_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"Failed to fetch image: {e}")
        return None

def generate_meme_image(image_url: str, text: str):
    img = read_image_from_url(image_url)
    if img is None:
        raise FileNotFoundError("Image not found")
    
    h, w, c = img.shape

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    white_region = None
    max_area = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area >= 5000 and area > max_area:
            max_area = area
            white_region = cnt

    if white_region is not None:
        x, y, rw, rh = cv2.boundingRect(white_region)
        (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)

        text_x = x + (rw - text_w) // 2
        text_y = y + (rh + text_h) // 2

        color = (0, 0, 0)
    else:
        (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
        text_x = (w - text_w) // 2
        text_y = h - 10

        color = (255, 255, 255)

        cv2.putText(img, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2, cv2.LINE_AA)
        output_path = "images/{}.jpg".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
        cv2.imwrite(output_path, img)
        return output_path

MemeComposerAgent = Agent(
    name = "meme_composer",
    model = "gemini-2.0-flash",
    instruction = agent_instruction,
    output_key = "meme_file_path",
    tools = [generate_meme_image],
    generate_content_config = types.GenerateContentConfig(
        temperature = 0.1
    )
)
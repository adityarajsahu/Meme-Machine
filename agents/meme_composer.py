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
    
def wrap_text(text, font, font_scale, thickness, max_width):
    words = text.split()
    if not words:
        return []
    
    lines = []
    current_line = words[0]
    for word in words[1:]:
        test_line = "{} {}".format(current_line, word)
        (w, _), _ = cv2.getTextSize(test_line, font, font_scale, thickness)
        if w <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines

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
        region_x, region_y, region_w, region_h = x + 10, y + 10, rw - 20, rh - 20
        text_color = (0, 0, 0)
    else:
        region_x, region_y = 10, 10
        region_w, region_h = w - 20, h - 20
        region_y = h - 10 - region_h
        text_color = (255, 255, 255)

    lines = wrap_text(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2, region_w)
    if not lines:
        return None
    
    sizes = [cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0] for line in lines]
    line_height = sizes[0][1] + 5
    total_text_height = line_height * len(lines) - 5
    start_y = region_y + (region_h - total_text_height) // 2 + sizes[0][1]

    for i, line in enumerate(lines):
        text_w, text_h = sizes[i]
        text_x = region_x + (region_w - text_w) // 2
        text_y = start_y + i * line_height
        cv2.putText(img, line, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, text_color, 2, cv2.LINE_AA)

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

# output_path = "images/{}.jpg".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
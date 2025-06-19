from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from google.adk.agents import ParallelAgent, SequentialAgent
from google.adk.sessions import InMemorySessionService
from google.adk.events import Event, EventActions
from google.adk.runners import Runner
from google.genai import types
import uvicorn
import time
import os
import base64
from pathlib import Path

from agents.template_scout import TemplateScoutAgent
from agents.caption_generator import CaptionGenerationAgent
from agents.prompt_moderator import PromptModerationAgent
from agents.meme_composer import MemeComposerAgent
from agents.meme_publisher import MemePublisherAgent

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MemeRequest(BaseModel):
    user_id: str
    prompt: str

session_service = InMemorySessionService()

@app.get("/")
async def root():
    return JSONResponse(
        status_code = 200,
        content = {
            "message": "The Meme Machine is up and running!"
        }
    )

def delete_meme_image(meme_image_path: str):
    try:
        os.remove(meme_image_path)
        print("Meme Image has been deleted successfully.")
    except Exception as e:
        print("An error occurred: {}".format(e))

@app.post("/generate_meme")
async def generate_meme(request: MemeRequest, background_tasks: BackgroundTasks):
    user_id = request.user_id
    text_prompt = request.prompt
    if not text_prompt:
        return JSONResponse(
            status_code = 400, 
            content = {
                "error": "Prompt cannot be empty."
            }
        )
    
    session = await session_service.create_session(
        app_name = "meme_machine",
        user_id = user_id
    )
    # print(f"Initial state: {session.state}")
    
    try:
        current_time = time.time()
        state_change = {
            "prompt": text_prompt
        }
        actions_with_update = EventActions(state_delta = state_change)
        system_event = Event(
            invocation_id = "inv_prompt_update",
            author = "system",
            actions = actions_with_update,
            timestamp = current_time
        )
        await session_service.append_event(
            session,
            system_event
        )

        ### PROMPT MODERATOR AGENT ###
        runner_prompt_moderator = Runner(
            agent = PromptModerationAgent, 
            app_name = "meme_machine", 
            session_service = session_service
        )

        content_prompt_moderator = types.Content(role = "user", parts = [types.Part(text = session.state["prompt"])])
        events_prompt_moderator = runner_prompt_moderator.run(user_id = user_id, session_id = session.id, new_message = content_prompt_moderator)

        moderator_response = ""
        for event in events_prompt_moderator:
            if event.is_final_response() and event.content and event.content.parts:
                # print(f"Potential final response from [{event.author}]: {event.content.parts[0].text}")
                moderator_response = event.content.parts[0].text

        print("Moderator Final Response: ", moderator_response)

        new_session = await session_service.get_session(
            app_name = "meme_machine",
            user_id = user_id,
            session_id = session.id
        )

        if new_session.state["moderator_response"].lower() == "yes":
            return JSONResponse(
                status_code = 400,
                content = {
                    "error": "Prompt is not suitable for meme generation."
                }
            )
        
        ParallelMemeAgent = ParallelAgent(
            name = "parallel_meme_agent",
            sub_agents = [
                TemplateScoutAgent,
                CaptionGenerationAgent
            ],
            description = "Parallel agent to scout meme templates and generate caption."
        )

        SequentialMemeAgent = SequentialAgent(
            name = "sequential_meme_agent",
            sub_agents = [
                ParallelMemeAgent,
                MemeComposerAgent,
                MemePublisherAgent
            ],
            description = "Sequential agent to compose and publish the meme."
        )

        runner = Runner(
            agent = SequentialMemeAgent, 
            app_name = "meme_machine", 
            session_service = session_service
        )

        content = types.Content(role = "user", parts = [types.Part(text = session.state["prompt"])])
        events = runner.run(user_id = user_id, session_id = session.id, new_message = content)

        for event in events:
            if event.is_final_response() and event.content and event.content.parts:
                print(event.content.parts)

        updated_session = await session_service.get_session(
            app_name = "meme_machine",
            user_id = user_id,
            session_id = session.id
        )

        meme_file_path = Path(updated_session.state["meme_file_path"].strip())
        if not meme_file_path.is_file():
            return JSONResponse(
                status_code = 500,
                content = {
                    "error": "Internal Server Error: Please try again later."
                }
            )
        
        img_bytes = meme_file_path.read_bytes()
        b64_str = base64.b64encode(img_bytes).decode("ascii")
        payload = {
            "image": f"data:image/png;base64,{b64_str}",
            "meme_url": updated_session.state["meme_url"].strip()
        }
        background_tasks.add_task(delete_meme_image, updated_session.state["meme_file_path"].strip())
        return payload
    
    except Exception as e:
        return JSONResponse(
            status_code = 500,
            content = {
                "error": f"An error occurred: {str(e)}"
            }
        )
    
if __name__ == "__main__":
    uvicorn.run("app:app", port = 8080, reload = True)

# ### TEMPLATE SCOUT AGENT ###
# runner_template_scout = Runner(
#     agent = TemplateScoutAgent, 
#     app_name = "meme_machine", 
#     session_service = session_service
# )

# content_template_scout = types.Content(role = "user", parts = [types.Part(text = session.state["prompt"])])
# events_template_scout = runner_template_scout.run(user_id = user_id, session_id = session.id, new_message = content_template_scout) 

# template_response = "No final response captured."
# for event in events_template_scout:
#     if event.is_final_response() and event.content and event.content.parts:
#         # print(f"Potential final response from [{event.author}]: {event.content.parts[0].text}")
#         template_response = event.content.parts[0].text

# print("Template Scout Final Response: ", template_response)

# ### CAPTION GENERATOR AGENT ###
# runner_caption_generator = Runner(
#     agent = CaptionGenerationAgent, 
#     app_name = "meme_machine", 
#     session_service = session_service
# )

# content_caption_generator = types.Content(role = "user", parts = [types.Part(text = session.state["prompt"])])
# events_caption_generator = runner_caption_generator.run(user_id = user_id, session_id = session.id, new_message = content_caption_generator)

# caption_response = "No final response captured."
# for event in events_caption_generator:
#     if event.is_final_response() and event.content and event.content.parts:
#         # print(f"Potential final response from [{event.author}]: {event.content.parts[0].text}")
#         caption_response = event.content.parts[0].text

# print("Caption Generator Final Response: ", caption_response)

# ### MEME COMPOSER ###
# runner_meme_composer = Runner(
#     agent = MemeComposerAgent,
#     app_name = "meme_machine", 
#     session_service = session_service
# )

# content_meme_composer = types.Content(role = "user", parts = [types.Part(text = session.state["prompt"])])
# events_meme_composer = runner_meme_composer.run(user_id = user_id, session_id = session.id, new_message = content_meme_composer)

# for event in events_meme_composer:
#     if event.is_final_response() and event.content and event.content.parts:
#         print(event.content.parts)

# ### MEME PUBLISHER AGENT ###
# runner_meme_publisher = Runner(
#     agent = MemePublisherAgent,
#     app_name = "meme_machine",
#     session_service = session_service
# )

# content_meme_publisher = types.Content(role = "user", parts = [types.Part(text = session.state["prompt"])])
# events_meme_publisher = runner_meme_publisher.run(user_id = user_id, session_id = session.id, new_message = content_meme_publisher)

# for event in events_meme_publisher:
#     if event.is_final_response() and event.content and event.content.parts:
#         print(event.content.parts)
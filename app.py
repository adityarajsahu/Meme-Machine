from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from google.adk.sessions import InMemorySessionService
from google.adk.events import Event, EventActions
from google.adk.runners import Runner
from google.genai import types
import uvicorn
import time

from agents.template_scout import TemplateScoutAgent
from agents.caption_generator import CaptionGenerationAgent
from agents.prompt_moderator import PromptModerationAgent

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

@app.post("/generate_meme")
async def generate_meme(request: MemeRequest):
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

        agent = TemplateScoutAgent()
        image_url = await agent.run(query="test", session=session, tools=None)

        runner_caption_generator = Runner(
            agent = CaptionGenerationAgent, 
            app_name = "meme_machine", 
            session_service = session_service
        )

        content_caption_generator = types.Content(role = "user", parts = [types.Part(text = session.state["prompt"])])
        events_caption_generator = runner_caption_generator.run(user_id = user_id, session_id = session.id, new_message = content_caption_generator)

        caption_response = "No final response captured."
        for event in events_caption_generator:
            if event.is_final_response() and event.content and event.content.parts:
                # print(f"Potential final response from [{event.author}]: {event.content.parts[0].text}")
                caption_response = event.content.parts[0].text

        print("Agent Final Response: ", caption_response)

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

        updated_session = await session_service.get_session(
            app_name = "meme_machine",
            user_id = user_id,
            session_id = session.id
        )

        return JSONResponse(
            status_code = 200,
            content = {
                "prompt": updated_session.state["prompt"],
                "image_url": image_url,
                "caption": updated_session.state["caption"],
                "moderator_response": updated_session.state["moderator_response"]
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code = 500,
            content = {
                "error": f"An error occurred: {str(e)}"
            }
        )
    
if __name__ == "__main__":
    uvicorn.run("app:app", port = 8080, reload = True)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from google.adk.sessions import InMemorySessionService
from google.adk.events import Event, EventActions
import uvicorn
import time

from agents.template_scout import TemplateScoutAgent

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
        updated_session = await session_service.get_session(
            app_name = "meme_machine",
            user_id = user_id,
            session_id = session.id
        )
        # print(f"State after event: {updated_session.state}")

        agent = TemplateScoutAgent()
        result = await agent.run(query="test", session=session, tools=None)
        return JSONResponse(
            status_code = 200,
            content = {
                "result": result
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
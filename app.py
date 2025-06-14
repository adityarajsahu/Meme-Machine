from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MemeRequest(BaseModel):
    prompt: str

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
    text_prompt = request.prompt
    if not text_prompt:
        return JSONResponse(
            status_code = 400, 
            content = {
                "error": "Prompt cannot be empty."
            }
        )
    
    try:
        print(f"Received prompt: {text_prompt}")
        return JSONResponse(
            status_code = 200,
            content = {
                "message": f"Meme generation started for prompt: {text_prompt}"
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
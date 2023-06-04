from fastapi import FastAPI, Request
import uvicorn
import os
from dotenv import load_dotenv
from src.routes.chat import chat

load_dotenv()

api = FastAPI()
api.include_router(chat)

@api.get("/test")
async def root():
    return {"msg": "API is Online"}


if __name__ == "__main__":
    if os.environ.get('APP_ENV') == "development":
        uvicorn.run("main:api", host="0.0.0.0", port=3500,
                    workers=4, reload=True)
    else:
      pass

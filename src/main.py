from dotenv import load_dotenv

load_dotenv()

import logging

from fastapi import FastAPI

from src.router import agent_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="langgraph-agent", version="0.1.0")
app.include_router(agent_router.router, prefix="/api")


@app.get("/")
def health_check():
    return {"status": "online", "message": "langgraph-agent server is running"}

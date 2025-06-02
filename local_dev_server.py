# Thought into existence by Darbot
# Simple development server with local memory
import asyncio
from fastapi import FastAPI, HTTPException, Header, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional, Union
from datetime import datetime
import json
import uuid
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)

# Create FastAPI app
app = FastAPI(title="Darbot Agent Engine API - Local Development Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Local storage
tasks = []
plans = []
steps = []
messages = []

# Helper function to generate IDs
def generate_id() -> str:
    return str(uuid.uuid4())

# Helper function to get timestamp
def get_timestamp() -> str:
    return datetime.now().isoformat()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0-local", "timestamp": get_timestamp()}

# API documentation endpoint
@app.get("/docs")
async def get_docs():
    return Response(
        content="<html><body><h1>Darbot Agent Engine API Documentation</h1><p>This is a local development server.</p></body></html>",
        media_type="text/html"
    )

# Create a new plan/task
@app.post("/api/plans")
async def create_plan(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    agent_type = data.get("agent_type", "PlannerAgent")
    model = data.get("model", "gpt-35-turbo")
    
    session_id = generate_id()
    plan_id = generate_id()
    
    new_plan = {
        "session_id": session_id,
        "plan_id": plan_id,
        "initial_goal": prompt,
        "agent_type": agent_type,
        "model": model,
        "overall_status": "planned",
        "total_steps": 3,
        "completed": 0,
        "created_at": get_timestamp(),
        "updated_at": get_timestamp(),
        "human_clarification_request": None,
        "human_clarification_response": None
    }
    
    plans.append(new_plan)
    
    # Create some mock steps for the plan
    step_actions = ["Research", "Design", "Implement"]
    for i, action in enumerate(step_actions):
        steps.append({
            "id": generate_id(),
            "session_id": session_id,
            "action": f"{action} {prompt}",
            "status": "planned",
            "agent": agent_type,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp(),
            "sequence": i + 1,
            "requires_human_feedback": False,
            "human_feedback": None,
            "human_approval_status": None
        })
    
    # Create a welcome message
    messages.append({
        "id": generate_id(),
        "session_id": session_id,
        "content": f"I'll help you with: {prompt}",
        "role": "assistant",
        "source": "PlannerAgent",
        "timestamp": get_timestamp()
    })
    
    logging.info(f"Created new plan: {session_id} for goal: {prompt}")
    
    return {
        "session_id": session_id,
        "plan_id": plan_id
    }

# Get a specific plan
@app.get("/api/plans/{session_id}")
async def get_plan(session_id: str):
    for plan in plans:
        if plan["session_id"] == session_id:
            return plan
    
    raise HTTPException(status_code=404, detail="Plan not found")

# Get all plans
@app.get("/api/plans")
async def get_plans():
    return plans

# Get steps for a plan
@app.get("/api/plans/{session_id}/steps")
async def get_steps(session_id: str):
    plan_steps = [step for step in steps if step["session_id"] == session_id]
    return plan_steps

# Get messages for a plan
@app.get("/api/plans/{session_id}/messages")
async def get_messages(session_id: str):
    plan_messages = [msg for msg in messages if msg["session_id"] == session_id]
    return plan_messages

# Add a message to a plan
@app.post("/api/plans/{session_id}/messages")
async def add_message(session_id: str, request: Request):
    data = await request.json()
    content = data.get("content", "")
    
    # Check if plan exists
    plan_exists = False
    for plan in plans:
        if plan["session_id"] == session_id:
            plan_exists = True
            break
    
    if not plan_exists:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    new_message = {
        "id": generate_id(),
        "session_id": session_id,
        "content": content,
        "role": "user",
        "source": "HumanUser",
        "timestamp": get_timestamp()
    }
    
    messages.append(new_message)
    
    # Add a mock response
    response_message = {
        "id": generate_id(),
        "session_id": session_id,
        "content": f"I've received your message: '{content}'. I'll work on this right away.",
        "role": "assistant",
        "source": "PlannerAgent",
        "timestamp": get_timestamp()
    }
    
    messages.append(response_message)
    
    return new_message

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

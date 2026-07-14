import os
from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from ollama import AsyncClient, ResponseError

from app.vector_db import search_chunks

router = APIRouter()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")
OLLAMA_KEEP_ALIVE = os.getenv("OLLAMA_KEEP_ALIVE", "30m")
OLLAMA_NUM_THREAD = int(os.getenv("OLLAMA_NUM_THREAD", "2"))

class ChatRequest(BaseModel):
    question: str
    file_names: List[str]

@router.post("/chat")
async def get_answer(data: ChatRequest):
    # 1. Quick Interception for Greetings to optimize CPU performance
    clean_question = data.question.strip().lower().rstrip("?.!")
    greetings = {"hi", "hello", "hey", "good morning", "good afternoon", "greetings"}
    
    if clean_question in greetings:
        async def greeting_generator():
            yield "Hello! How can I help you with your documents today?"
        return StreamingResponse(greeting_generator(), media_type="text/plain")

    # Initialize the client lazily inside the route handler
    client = AsyncClient()

    # 2. Retrieve matching document text chunks
    chunks = search_chunks(
        data.question,
        file_names=data.file_names
    )

    if not chunks:
        async def empty_generator():
            yield "No relevant content found in the selected documents."
        return StreamingResponse(empty_generator(), media_type="text/plain")

    context = "\n\n".join(chunks)

    # 3. Dynamic Prompt Layout
    prompt = f"""Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context:
{context}

Question:
{data.question}
Answer:"""

    async def stream_generator():
        try:
            stream = await client.chat(
                model=OLLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                keep_alive=OLLAMA_KEEP_ALIVE,
                options={
                    "num_ctx": 1500,     
                    "num_predict": 512,  
                    "temperature": 0.2,
                    "num_thread": OLLAMA_NUM_THREAD,
                },
            )
        except ResponseError as e:
            yield f"[Ollama error: {e}. Run `ollama pull {OLLAMA_MODEL}`]"
            return

        async for chunk in stream:
            content = chunk.get("message", {}).get("content", "")
            if content:
                yield content

    return StreamingResponse(stream_generator(), media_type="text/plain")
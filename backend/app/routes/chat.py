import os
from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from groq import AsyncGroq, APIError

from app.vector_db import search_chunks

router = APIRouter()

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

class ChatRequest(BaseModel):
    question: str
    file_names: List[str]

@router.post("/chat")
async def get_answer(data: ChatRequest):
    # 1. Quick Interception for Greetings to optimize performance
    clean_question = data.question.strip().lower().rstrip("?.!")
    greetings = {"hi", "hello", "hey", "good morning", "good afternoon", "greetings"}

    if clean_question in greetings:
        async def greeting_generator():
            yield "Hello! How can I help you with your documents today?"
        return StreamingResponse(greeting_generator(), media_type="text/plain")

    # Initialize the client lazily inside the route handler
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        async def missing_key_generator():
            yield "[Groq error: GROQ_API_KEY environment variable is not set.]"
        return StreamingResponse(missing_key_generator(), media_type="text/plain")

    client = AsyncGroq(api_key=api_key)

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
            stream = await client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                temperature=0.2,
                max_tokens=512,
            )
        except APIError as e:
            yield f"[Groq error: {e}]"
            return

        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content

    return StreamingResponse(stream_generator(), media_type="text/plain")
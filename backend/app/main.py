print("MAIN.PY START")
from fastapi import FastAPI
from app.routes import upload,chat,files,auth
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI()
app.include_router(upload.router)
app.include_router(chat.router)
app.include_router(files.router)
app.include_router(auth.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
if os.path.exists("static"):
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

    # 3. Serve index.html at the root path "/"
    @app.get("/")
    async def serve_frontend():
        return FileResponse("static/index.html")

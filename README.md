---
title: "Doc Intellect"
emoji: "📄"
colorFrom: "blue"
colorTo: "purple"
sdk: "docker"
app_port: 7860
pinned: false
---

# Doc Intellect
Local Ollama-powered PDF Chatbot.

## Authentication configuration

Add your login settings in the backend environment file:

1. Copy [backend/.env.example](backend/.env.example) to [backend/.env](backend/.env)
2. Fill in the values:
   - `AUTH_DB` = path to your SQLite auth database file
   - `JWT_SECRET` = long random secret for signing JWTs
   - `GOOGLE_CLIENT_ID` = your Google OAuth client ID
   - `GOOGLE_CLIENT_SECRET` = your Google OAuth client secret
   - `GOOGLE_REDIRECT_URI` = callback URL, usually `http://localhost:3000/oauth2callback`

Example:
```env
AUTH_DB=auth.db
JWT_SECRET=replace-with-a-long-random-secret
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000/oauth2callback
```

The backend reads these values from [backend/app/config.py](backend/app/config.py) and the auth routes use them in [backend/app/routes/auth.py](backend/app/routes/auth.py).
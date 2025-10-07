import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader

from routes.role_routes import role  
from routes.user_routes import user

load_dotenv()

app = FastAPI()

origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY_NAME = "X-API-Key"
API_KEY = os.getenv("API_KEY")

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_KEY:
        return api_key
    raise HTTPException(status_code=403, detail="API Key inválida o faltante")

app.include_router(role, dependencies=[Depends(get_api_key)])
app.include_router(user, dependencies=[Depends(get_api_key)])

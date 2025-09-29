from fastapi import FastAPI;

from routes.role import role

app = FastAPI()

app.include_router(role)
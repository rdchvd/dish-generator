from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

# app.include_router(auth_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

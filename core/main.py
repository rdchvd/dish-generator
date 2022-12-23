from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.products.views import products_router

app = FastAPI(openapi_url="/openapi/", docs_url="/docs/")

app.include_router(products_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

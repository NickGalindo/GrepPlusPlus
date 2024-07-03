from manager.load_config import CONFIG

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

import pymilvus

import colorama 
from colorama import Fore

from sentence_transformers import SentenceTransformer

from vectordb.setupCollections import setup_collection
from endpoints import router as endpoints_router

colorama.init(autoreset=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.milvus_connection = pymilvus.connections.connect(
        alias="default",
        host="127.0.0.1",
        port="19530"
    )

    app.state.tokens_collection = setup_collection()
    
    if CONFIG["VECTOR_FUNCTION"] == "transformers":
        app.state.transformer_model = SentenceTransformer("all-mpnet-base-v2")
    else:
        app.state.transformer_model = None

    app.state.num_inserts_not_indexed = 0

    yield

    if not pymilvus.connections.has_connection("default"):
        return

    app.state.tokens_collection.flush()
    app.state.tokens_collection.release()

    pymilvus.connections.disconnect("default")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints_router)

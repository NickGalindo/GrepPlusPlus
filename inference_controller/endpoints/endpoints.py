from typing import Dict, List
from fastapi import APIRouter, Request

from endpoints.models import TokenizedFile, FilePath
from endpoints import service

router = APIRouter()

@router.post("/update")
async def update(request: Request, tokenized_file: TokenizedFile) -> Dict:
    request.app.state.num_inserts_not_indexed = service.vectorize_file(request.app.state.tokens_collection, request.app.state.transformer_model, request.app.state.num_inserts_not_indexed, tokenized_file)

    return {"status": "success"}

@router.post("/delete")
async def delete(request: Request, file: FilePath) -> Dict:
    service.delete_file(request.app.state.tokens_collection, file)
    return {"status": "success"}

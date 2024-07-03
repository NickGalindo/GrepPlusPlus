from typing import List, Set, Tuple, Dict

import warnings

import pymilvus
from utilities.setup_collection import setupCollection
from sentence_transformers import SentenceTransformer

from utilities.tokenizer import tokenize_line
from utilities.transform import vector_function

from .print_entities import printEntities, printQuery


def __lazy_setup() -> Tuple[pymilvus.Collection, SentenceTransformer | None]:
    milvus_connection: pymilvus.Connections = pymilvus.connections.connect(
        alias="default",
        host="127.0.0.1",
        port="19530"
    )
    
    collection: pymilvus.Collection = setupCollection()

    with warnings.catch_warnings(action="ignore"):
        model: SentenceTransformer = SentenceTransformer("all-mpnet-base-v2")

    return collection, model


def baseFind(find_str: str, n: int):
    collection: pymilvus.Collection
    model: SentenceTransformer | None
    collection, model = __lazy_setup()

    tokenized_str: List = tokenize_line(find_str)
    search_vector: List = vector_function([t["token_type"] for t in tokenized_str], model).flatten().tolist()

    search_params: Dict = {"metric_type": "L2", "params": {"nprobe": 10}}
    output_fields: List[str] = ["token_code", "token_dir", "token_line", "token_path"]

    res = collection.search(
        data=[search_vector],
        anns_field="token_vector",
        param=search_params,
        limit=n,
        output_fields=output_fields
    )

    results: Set = set()
    for aux in res: #type: ignore
        for entity in aux:
            results.add(entity)

    printEntities(results)

def projectFind(find_str: str, n: int, proj_dir: str):
    collection: pymilvus.Collection
    model: SentenceTransformer | None
    collection, model = __lazy_setup()

    tokenized_str: List = tokenize_line(find_str)
    search_vector: List = vector_function([t["token_type"] for t in tokenized_str], model).flatten().tolist()

    search_params: Dict = {"metric_type": "L2", "params": {"nprobe": 10}}
    output_fields: List[str] = ["token_code", "token_dir", "token_line", "token_path"]

    res = collection.search(
        data=[search_vector],
        anns_field="token_vector",
        param=search_params,
        limit=n,
        output_fields=output_fields,
        expr=f"token_dir == \"{proj_dir}\""
    )

    results: Set = set()
    for aux in res: #type: ignore
        for entity in aux:
            results.add(entity)

    printEntities(results)

def findAll():
    collection: pymilvus.Collection
    collection, _ = __lazy_setup()

    output_fields: List[str] = ["token_code", "token_dir", "token_line", "token_path"]

    res = collection.query(
        output_fields=output_fields,
        expr=f"token_id >= \"0\""
    )

    printQuery(res)

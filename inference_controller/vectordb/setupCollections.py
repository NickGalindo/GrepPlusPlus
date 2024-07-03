from typing import Dict
from manager.load_config import CONFIG

from pymilvus import Collection, utility

from vectordb.models import schema

def setup_collection() -> Collection:
    index_params: Dict = {
        "metric_type": "L2" if CONFIG["VECTOR_TYPE"] == "float_vector" else "HAMMING",
        "index_type": "IVF_SQ8" if CONFIG["VECTOR_TYPE"] == "float_vector" else "BIN_IVF_FLAT",
        "params":{"nlist": 1024}
    }

    if not utility.has_collection("TOKENS"):
        col = Collection(
            name="TOKENS",
            schema=schema,
            using="default"
        )
        col.create_index(field_name="token_vector", index_params=index_params)
    else:
        col = Collection("TOKENS")

    col.load()

    return col

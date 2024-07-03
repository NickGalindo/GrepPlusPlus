from typing import Dict
from pymilvus import DataType, FieldSchema, CollectionSchema
from manager.load_config import CONFIG

__vector_type_mapping: Dict = {"float_vector": DataType.FLOAT_VECTOR, "binary_vector": DataType.BINARY_VECTOR}

token_id = FieldSchema(
    name="token_id",
    dtype=DataType.VARCHAR,
    max_length=200,
    is_primary=True,
)

token_vector = FieldSchema(
    name="token_vector",
    dtype=__vector_type_mapping[CONFIG["VECTOR_TYPE"]],
    dim=CONFIG["VECTOR_SIZE"],
)

token_code = FieldSchema(
    name="token_code",
    dtype=DataType.VARCHAR,
    max_length=1024
)

token_path = FieldSchema(
    name="token_path",
    dtype=DataType.VARCHAR,
    max_length=1024
)

token_line = FieldSchema(
    name="token_line",
    dtype=DataType.INT64
)

token_dir = FieldSchema(
    name="token_dir",
    dtype=DataType.VARCHAR,
    max_length=1024
)


schema = CollectionSchema(
    fields=[token_id, token_vector, token_code, token_path, token_line, token_dir],
    description="Token Collection for Vector Search"
)

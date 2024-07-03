from typing import List
from pymilvus import Collection
from sentence_transformers import SentenceTransformer
import uuid

from endpoints.models import FilePath, TokenizedFile
from vectordb.transform import vector_function

from colorama import Fore

def __delete_vectorized_file(collection: Collection, path: str):
    res = collection.delete(expr=f"token_path == \"{path}\"")
    collection.flush()
    print(Fore.BLUE + f"[NOTIFIACTION]: Delete result: {res}")


def vectorize_file(collection: Collection, model: SentenceTransformer | None, num_inserts_not_indexed: int, tokenized_file: TokenizedFile) -> int:
    __delete_vectorized_file(collection, tokenized_file.path)

    for line in tokenized_file.lines:
        if line.code.strip() == "" or len(line.tokens) == 0:
            continue
        token_id: str = str(uuid.uuid4())
        token_vector: List = vector_function([t.token_type for t in line.tokens], model).flatten().tolist()
        token_code: str = line.code
        token_path: str = tokenized_file.path
        token_line: int = line.line
        token_dir: str = tokenized_file.dir

        new_tokenized_file: List = [
            [token_id],
            [token_vector],
            [token_code],
            [token_path],
            [token_line],
            [token_dir]
        ]

        res = collection.insert(new_tokenized_file)

        print(Fore.BLUE + f"[NOTIFIACTION]: Insert result: {res}")

        if num_inserts_not_indexed >= 1000:
            collection.flush()
            num_inserts_not_indexed = 0
        else:
            num_inserts_not_indexed += 1

    return num_inserts_not_indexed

def delete_file(collection: Collection, file_path: FilePath) -> None:
    __delete_vectorized_file(collection, file_path.path)

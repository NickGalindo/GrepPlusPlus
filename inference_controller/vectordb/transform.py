from typing import List
from sentence_transformers import SentenceTransformer
from manager.load_config import CONFIG
from torch import Tensor
import numpy as np

def __transform(sentence: str, model: SentenceTransformer) -> np.ndarray:
    res: List[Tensor] | np.ndarray | Tensor = model.encode(sentence, convert_to_numpy=True)
    assert(isinstance(res, np.ndarray))

    return res

def __bagging(tokens: List[str]) -> np.ndarray:
    return np.zeros([768])


def vector_function(tokens: List[str], model: SentenceTransformer | None = None) -> np.ndarray:
    if CONFIG["VECTOR_FUNCTION"] == "transformers":
        if model is None:
            raise ValueError("model passed in is not a valid SentenceTransformer")
        return __transform(" ".join([tok.replace("_", " ").lower() for tok in tokens]), model)
    else:
        return __bagging(tokens)

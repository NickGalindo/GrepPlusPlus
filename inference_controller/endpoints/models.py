from typing import List, Any
from pydantic import BaseModel

class Token(BaseModel):
    end_pos: str
    start_pos: str
    token_str: str
    token_type: str

class CodeLine(BaseModel):
    code: str
    line: int
    tokens: List[Token]

class TokenizedFile(BaseModel):
    path: str
    dir: str
    lines: List[CodeLine]

class FilePath(BaseModel):
    path: str
    dir: str

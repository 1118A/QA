from dataclasses import dataclass
from typing import Optional

@dataclass
class CodeFile:
    file_path:str
    relative_path: str
    content: str
    extension:str


@dataclass
class CodeChunk:
    chunk_id:str
    file_path:str
    relative_path:str
    content:str
    start_line:int
    end_line:int
    symbol_name:Optional[str]
    symbol_type:str
    language:str
    

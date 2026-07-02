import hashlib
from typing import List

from app.models.schemas import CodeFile, CodeChunk

PYTHON_SYMBOLS = {
    "function_definition": "funtion",
    "class_definition": "class",
}


JS_TS_SYMBOLS = {
    "function_declaration":"function",
    "class_declaration":"class",
    "method_definition":"method",
    "arrow_function":"function",
}

def detect_language(extension: str) -> str:
    if extension == ".py":
        return "python"

    if extension in [".js", ".jsx"]:
        return "javascript"
    
    if extension in [".ts", ".tsx"]:
        return "typescript"
    
    return "unknown"

def make_chunk_id(relative_path: str, start_line: int, end_line: int, content: str) -> str:
    raw = f"{relative_path}:{start_line}:{end_line}:{content}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()

def get_node_text(content:str, start_byte: int, end_byte: int) -> str:
    return content.encode("utd-8")[start_byte:end_byte].decode("utf-8", errors="ignore")

def get_symbol_name(node, content:str) -> str:
    name_node = node.child_by_field_name("name")

    if name_node is None:
        return "anonymous"
    
    return get_node_text(content, name_node.start_byte, name_node.end_byte)
import hashlib
from typing import List

from app.models.schemas import CodeFile, CodeChunk


PYTHON_SYMBOLS = {
    "function_definition": "function",
    "class_definition": "class",
}


JS_TS_SYMBOLS = {
    "function_declaration": "function",
    "class_declaration": "class",
    "method_definition": "method",
    "arrow_function": "function",
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


def get_node_text(content: str, start_byte: int, end_byte: int) -> str:
    return content.encode("utf-8")[start_byte:end_byte].decode("utf-8", errors="ignore")


def get_symbol_name(node, content: str) -> str:
    name_node = node.child_by_field_name("name")

    if name_node is None:
        return "anonymous"

    return get_node_text(content, name_node.start_byte, name_node.end_byte)


def fallback_line_chunks(code_file: CodeFile, max_lines: int = 80) -> List[CodeChunk]:
    lines = code_file.content.splitlines()
    chunks = []
    language = detect_language(code_file.extension)

    for i in range(0, len(lines), max_lines):
        chunk_lines = lines[i:i + max_lines]
        chunk_content = "\n".join(chunk_lines)

        if not chunk_content.strip():
            continue

        start_line = i + 1
        end_line = i + len(chunk_lines)

        chunk_id = make_chunk_id(
            code_file.relative_path,
            start_line,
            end_line,
            chunk_content,
        )

        chunks.append(
            CodeChunk(
                chunk_id=chunk_id,
                file_path=code_file.file_path,
                relative_path=code_file.relative_path,
                content=chunk_content,
                start_line=start_line,
                end_line=end_line,
                symbol_name=None,
                symbol_type="block",
                language=language,
            )
        )

    return chunks


def parse_python_file(code_file: CodeFile) -> List[CodeChunk]:
    try:
        import tree_sitter_python
        from tree_sitter import Language, Parser

        language = Language(tree_sitter_python.language())
        parser = Parser(language)
        tree = parser.parse(code_file.content.encode("utf-8"))
    except Exception:
        return fallback_line_chunks(code_file)

    chunks = []
    root = tree.root_node

    def walk(node):
        if node.type in PYTHON_SYMBOLS:
            symbol_type = PYTHON_SYMBOLS[node.type]
            symbol_name = get_symbol_name(node, code_file.content)

            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1

            chunk_content = get_node_text(
                code_file.content,
                node.start_byte,
                node.end_byte,
            )

            chunk_id = make_chunk_id(
                code_file.relative_path,
                start_line,
                end_line,
                chunk_content,
            )

            chunks.append(
                CodeChunk(
                    chunk_id=chunk_id,
                    file_path=code_file.file_path,
                    relative_path=code_file.relative_path,
                    content=chunk_content,
                    start_line=start_line,
                    end_line=end_line,
                    symbol_name=symbol_name,
                    symbol_type=symbol_type,
                    language="python",
                )
            )

        for child in node.children:
            walk(child)

    walk(root)

    if not chunks:
        return fallback_line_chunks(code_file)

    return chunks


def parse_js_ts_file(code_file: CodeFile) -> List[CodeChunk]:
    try:
        from tree_sitter import Language, Parser

        if code_file.extension in [".js", ".jsx"]:
            language = Language(tree_sitter_javascript.language())
            lang_name = "javascript"
        else:
            language = Language(tree_sitter_typescript.language_typescript())
            lang_name = "typescript"

        parser = Parser(language)
        tree = parser.parse(code_file.content.encode("utf-8"))
    except Exception:
        return fallback_line_chunks(code_file)

    chunks = []
    root = tree.root_node

    def walk(node):
        if node.type in JS_TS_SYMBOLS:
            symbol_type = JS_TS_SYMBOLS[node.type]
            symbol_name = get_symbol_name(node, code_file.content)

            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1

            chunk_content = get_node_text(
                code_file.content,
                node.start_byte,
                node.end_byte,
            )

            chunk_id = make_chunk_id(
                code_file.relative_path,
                start_line,
                end_line,
                chunk_content,
            )

            chunks.append(
                CodeChunk(
                    chunk_id=chunk_id,
                    file_path=code_file.file_path,
                    relative_path=code_file.relative_path,
                    content=chunk_content,
                    start_line=start_line,
                    end_line=end_line,
                    symbol_name=symbol_name,
                    symbol_type=symbol_type,
                    language=lang_name,
                )
            )

        for child in node.children:
            walk(child)

    walk(root)

    if not chunks:
        return fallback_line_chunks(code_file)

    return chunks


def parse_code_file(code_file: CodeFile) -> List[CodeChunk]:
    if code_file.extension == ".py":
        return parse_python_file(code_file)

    if code_file.extension in [".js", ".jsx", ".ts", ".tsx"]:
        return parse_js_ts_file(code_file)

    return fallback_line_chunks(code_file)


def parse_code_files(code_files: List[CodeFile]) -> List[CodeChunk]:
    all_chunks = []

    for code_file in code_files:
        chunks = parse_code_file(code_file)
        all_chunks.extend(chunks)

    return all_chunks
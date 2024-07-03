import os
import time
import json
import hashlib
import xxhash
import tokenize
import io
import requests
from io import BytesIO
from token import tok_name
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Define mappings for token types
KEYWORDS = {
    'def': 'DEF',
    'print': 'PRINT',
    'if': 'IF',
    'else': 'ELSE',
    'elif': 'ELSE_IF',
    'for': 'FOR',
    'while': 'WHILE',
    'try': 'TRY',
    'except': 'EXCEPT',
    'finally': 'FINALLY',
    'return': 'RETURN',
    'import': 'IMPORT',
    'from': 'FROM',
    'as': 'AS',
    'pass': 'PASS',
    'continue': 'CONTINUE',
    'break': 'BREAK',
    'assert': 'ASSERT',
    'raise': 'RAISE',
    'global': 'GLOBAL',
    'nonlocal': 'NONLOCAL',
    'lambda': 'LAMBDA',
    'with': 'WITH',
    'yield': 'YIELD',
    'in': 'IN',
    'is': 'IS',
    'not': 'NOT',
    'and': 'AND',
    'or': 'OR'
}

LITERALS = {
    tokenize.NUMBER: 'NUMBER',
    tokenize.STRING: 'STRING'
}

PUNCTUATIONS = {
    tokenize.LPAR: 'LEFT_PARENTHESIS',
    tokenize.RPAR: 'RIGHT_PARENTHESIS',
    tokenize.LSQB: 'LEFT_SQUARE_BRACKET',
    tokenize.RSQB: 'RIGHT_SQUARE_BRACKET',
    tokenize.COLON: 'COLON',
    tokenize.COMMA: 'COMMA',
    tokenize.SEMI: 'SEMICOLON',
    tokenize.DOT: 'DOT',
    tokenize.PLUS: 'ADD',
    tokenize.MINUS: 'SUBTRACT',
    tokenize.STAR: 'MULTIPLY',
    tokenize.SLASH: 'DIVIDE',
    tokenize.PERCENT: 'MODULO',
    tokenize.EQEQUAL: 'EQUALS_EQUALS',  # == operator
    tokenize.EQUAL: 'ASSIGN',  # = assignment operator
    tokenize.VBAR: 'BITWISE_OR',
    tokenize.AMPER: 'BITWISE_AND',
    tokenize.CIRCUMFLEX: 'BITWISE_XOR',
    tokenize.TILDE: 'BITWISE_NOT',
    tokenize.DOUBLESLASH: 'FLOOR_DIVIDE',
    tokenize.AT: 'AT',
}

BOOLEAN = {
    'True': 'BOOLEAN_TRUE',
    'False': 'BOOLEAN_FALSE'
}

class MyHandler(FileSystemEventHandler):
    def __init__(self, files_info, cache_dir):
        self.files_info = files_info
        self.cache_dir = self.initialize_cache_dir(cache_dir)
        self.initialize_existing_files()
        self.cleanup_orphaned_json_files()

    def initialize_cache_dir(self, cache_dir):
        current_dir = os.getcwd()
        grep_plus_plus_dir = os.path.join(current_dir, '.grep++')

        if not os.path.exists(grep_plus_plus_dir):
            os.makedirs(grep_plus_plus_dir)

        cache_dir_full = os.path.join(grep_plus_plus_dir, 'object_cache')

        if not os.path.exists(cache_dir_full):
            os.makedirs(cache_dir_full)

        return cache_dir_full

    def initialize_existing_files(self):
        monitored_dir = os.getcwd()  # Get the current working directory
        script_name = os.path.basename(__file__)  # Get the script file name

        for root, _, files in os.walk(monitored_dir):
            if 'grep_plus_plus_ignore' in root:
                continue  # Skip files in 'grep_plus_plus_ignore' directory
            for file in files:
                if not file.endswith('.py'):
                    continue  # Only monitor .py files

                file_path_abs = os.path.abspath(os.path.join(root, file))
                if file_path_abs == os.path.abspath(__file__):
                    continue  # Skip the script file itself

                if file_path_abs.startswith(self.cache_dir):
                    continue  # Skip files within the cache directory itself

                if file_path_abs not in self.files_info:
                    self.files_info[file_path_abs] = {
                        'name': os.path.basename(file_path_abs),
                        'size': os.path.getsize(file_path_abs),
                        'hash_sha256': self.calculate_sha256(file_path_abs),
                        'hash_xxhash': self.calculate_xxhash(file_path_abs)
                    }
                    self.create_or_update_json_file(
                        file_path_abs,
                        self.files_info[file_path_abs]['name'],
                        self.files_info[file_path_abs]['size'],
                        self.files_info[file_path_abs]['hash_sha256'],
                        self.files_info[file_path_abs]['hash_xxhash']
                    )

        self.update_files_info()

    def cleanup_orphaned_json_files(self):
        for root, _, files in os.walk(self.cache_dir):
            for file in files:
                if file.endswith('.json'):
                    json_file_path = os.path.join(root, file)
                    try:
                        with open(json_file_path, 'r') as json_file:
                            data = json.load(json_file)
                            original_file_path = data['path']
                        if not os.path.exists(original_file_path):
                            os.remove(json_file_path)
                            print(original_file_path)
                            self.print_and_send_file_deleted(original_file_path)
                            print(f"Orphaned JSON file deleted: {json_file_path}")
                    except PermissionError:
                        print(f"PermissionError: Could not access {json_file_path}. Skipping.")
                    except json.JSONDecodeError:
                        print(f"JSONDecodeError: Could not decode JSON in {json_file_path}. Skipping.")
                    except Exception as e:
                        print(f"Unexpected error: {e}. Skipping.")

    def update_files_info(self):
        for path, info in self.files_info.items():
            print(f"Path: {path}, Name: {info['name']}, Size: {info['size']} bytes, SHA256: {info['hash_sha256']}, XXHash: {info['hash_xxhash']}")
            self.print_and_send_file_info(path)
        print("="*40)

    def create_or_update_json_file(self, file_path, name, size, hash_sha256, hash_xxhash):
        json_filename = os.path.join(self.cache_dir, f"{hash_xxhash}.json")
        data = {
            "path": file_path,  # Replace backslashes with forward slashes
            "name": name,
            "size": size,
            "hash_sha256": hash_sha256,
            "hash_xxhash": hash_xxhash
        }
        try:
            with open(json_filename, 'w') as json_file:
                json.dump(data, json_file, indent=4, ensure_ascii=False)
            print(f"JSON file created/updated: {json_filename}")
        except PermissionError:
            print(f"PermissionError: Could not write to {json_filename}. Skipping.")

    def delete_json_file(self, file_path):
        file_hash = self.calculate_xxhash(file_path)
        json_filename = os.path.join(self.cache_dir, f"{file_hash}.json")
        if os.path.exists(json_filename):
            try:
                os.remove(json_filename)
                print(f"JSON file deleted: {json_filename}")
            except PermissionError:
                print(f"PermissionError: Could not delete {json_filename}. Skipping.")

    def calculate_sha256(self, file_path):
        sha256_hash = hashlib.sha256(file_path.encode()).hexdigest()
        return sha256_hash

    def calculate_xxhash(self, file_path):
        xxhash_hasher = xxhash.xxh128(file_path.encode()).hexdigest()
        return xxhash_hasher

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.py'):
            file_path = os.path.normpath(event.src_path)
            file_path_abs = os.path.abspath(file_path)
            if file_path_abs.startswith(self.cache_dir) or 'grep_plus_plus_ignore' in file_path_abs:
                return
            if file_path_abs not in self.files_info:
                hash_sha256 = self.calculate_sha256(file_path_abs)
                hash_xxhash = self.calculate_xxhash(file_path_abs)
                self.files_info[file_path_abs] = {
                    'name': os.path.basename(file_path_abs),
                    'size': os.path.getsize(file_path_abs),
                    'hash_sha256': hash_sha256,
                    'hash_xxhash': hash_xxhash
                }
                print(f"File created: {file_path_abs}")
                self.update_files_info()
                self.create_or_update_json_file(file_path_abs, self.files_info[file_path_abs]['name'], self.files_info[file_path_abs]['size'], hash_sha256, hash_xxhash)
                self.print_and_send_file_info(file_path_abs)

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.py'):
            file_path = os.path.normpath(event.src_path)
            file_path_abs = os.path.abspath(file_path)
            if file_path_abs.startswith(self.cache_dir) or 'grep_plus_plus_ignore' in file_path_abs:
                return
            if file_path_abs in self.files_info:
                self.files_info[file_path_abs]['size'] = os.path.getsize(file_path_abs)
                self.files_info[file_path_abs]['hash_sha256'] = self.calculate_sha256(file_path_abs)
                self.files_info[file_path_abs]['hash_xxhash'] = self.calculate_xxhash(file_path_abs)
                print(f"File modified: {file_path_abs}")
                self.update_files_info()
                self.create_or_update_json_file(file_path_abs, self.files_info[file_path_abs]['name'], self.files_info[file_path_abs]['size'], self.files_info[file_path_abs]['hash_sha256'], self.files_info[file_path_abs]['hash_xxhash'])
                self.print_and_send_file_info(file_path_abs)

    def on_deleted(self, event):
        if not event.is_directory and event.src_path.endswith('.py'):
            file_path = os.path.normpath(event.src_path)
            file_path_abs = os.path.abspath(file_path)
            if file_path_abs.startswith(self.cache_dir) or 'grep_plus_plus_ignore' in file_path_abs:
                return
            if file_path_abs in self.files_info:
                self.delete_json_file(file_path_abs)
                del self.files_info[file_path_abs]
                print(f"File deleted: {file_path_abs}")
                self.update_files_info()
                self.print_and_send_file_deleted(file_path_abs)

    def print_and_send_file_info(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            token_list = []

            for line_number, line in enumerate(lines, start=1):
                tokens = self.tokenize_line(line)
                token_list.append((tokens, line_number, line.strip()))

            file_info = {
                "directory": os.getcwd(),
                "path": file_path,
                "tokens": token_list
            }
            print(json.dumps(file_info, indent=4, ensure_ascii=False))
            self.send_info_to_server(file_info, False)
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")

    def tokenize_line(self, line):
        tokens = []
        for token in tokenize.generate_tokens(io.StringIO(line).readline):
            token_type = token.exact_type
            token_string = token.string.strip()

            if token_type in {tokenize.NL, tokenize.INDENT, tokenize.DEDENT, tokenize.ENCODING}:
                continue

            if token_type == tokenize.NAME:
                if token_string in KEYWORDS:
                    token_type_str = KEYWORDS[token_string]
                elif token_string in BOOLEAN:
                    token_type_str = BOOLEAN[token_string]
                else:
                    token_type_str = 'IDENTIFIER'
                tokens.append({
                    "type": token_type_str,
                    "token": token_string,
                    "start_pos": f"{token.start[0]},{token.start[1]}",
                    "end_pos": f"{token.end[0]},{token.end[1]}"
                })
            elif token_type in LITERALS:
                tokens.append({
                    "type": LITERALS[token_type],
                    "token": token_string,
                    "start_pos": f"{token.start[0]},{token.start[1]}",
                    "end_pos": f"{token.end[0]},{token.end[1]}"
                })
            elif token_type in PUNCTUATIONS:
                tokens.append({
                    "type": PUNCTUATIONS[token_type],
                    "token": token_string,
                    "start_pos": f"{token.start[0]},{token.start[1]}",
                    "end_pos": f"{token.end[0]},{token.end[1]}"
                })
        
        return tokens

    def print_and_send_file_deleted(self, file_path):
        file_info = {
            "directory": os.getcwd(),
            "path": file_path
        }
        print(json.dumps(file_info, indent=4, ensure_ascii=False))
        self.send_info_to_server(file_info, True)

    def send_info_to_server(self, data, delete):
        try:
            linkTo = ""
            if delete:
                linkTo = "http://localhost:8002/delete"
            else:
                linkTo = "http://localhost:8002/update"
                
            response = requests.post(linkTo, json=data)
            if response.status_code == 200:
                print(f"Data successfully sent to server: {data}")
            else:
                print(f"Failed to send data to server, status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending data to server: {e}")

def monitor_directory():
    files_info = {}
    current_dir = os.getcwd()
    cache_dir = os.path.join(current_dir, "object_cache")
    event_handler = MyHandler(files_info, cache_dir)
    observer = Observer()
    observer.schedule(event_handler, current_dir, recursive=True)
    observer.start()
    print(f"Monitoring directory: {current_dir}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    monitor_directory()

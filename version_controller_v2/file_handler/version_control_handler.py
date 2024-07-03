from typing import Dict, List, Set
import os
import shutil
import requests
from watchdog.events import FileSystemEvent, FileSystemEventHandler
import xxhash
import hashlib
import json 
import pickle
from pprint import pprint

from colorama import Fore

from tokenizer.tokenize import tokenize_lines

class VersionControlHandler(FileSystemEventHandler):
    def __init__(self, proj_dir: str, verbose: bool =False):
        self.verbose: bool = verbose

        self.proj_dir: str = proj_dir
        self.grep_dir: str = os.path.join(proj_dir, ".grep++")
        self.cache_dir: str = os.path.join(proj_dir, ".grep++", "object_cache")
        self.obj_store_dir: str = os.path.join(self.cache_dir, "objects")
        self.obj_index_path: str = os.path.join(self.cache_dir, "index.json")

        self.__initialize_cache_dirs()
        self.grep_ignore: Set = self.__initialize_grep_ignore()
        self.obj_index: Dict = self.__initialize_object_index()

        self.__clean_orphaned_object_files()
        self.obj_index = self.__update_project_objects()

    def __clean_orphaned_object_files(self):
        indexed_objs: Set = set(self.obj_index.keys())
        for dirpath, _, filenames in os.walk(self.obj_store_dir):
            for name in filenames:
                obj_path: str = os.path.join(dirpath, name)
                if obj_path not in indexed_objs:
                    try:
                        with open(obj_path, "rb") as file:
                            obj: Dict = pickle.load(file)
                        self.__send_file_deleted(obj["path"])
                        os.remove(obj_path)
                        print(Fore.GREEN + f"[SUCCESS] Cleaned orphaned object file \"{obj_path}\" reindexing and retokenizing will occur if file still in project")
                    except Exception as e:
                        print(Fore.RED + f"[ERROR] Couldn't clean up orphaned object file \"{obj_path}\" recommended reindexing and retokenizing whole project to avoid inconsistencies")
                        print(e)

    def __initialize_object_index(self) -> Dict:
        try:
            with open(self.obj_index_path, "r") as file:
                obj_index: Dict = json.load(file)
        except Exception as e:
            print(Fore.YELLOW + "[WARNING]: Couldn't load index file \".grep++/object_cache/index.json\" file didn't exist or file corrupted. Recalculating object indexing")
            obj_index: Dict = {}

        return obj_index

    def __initialize_grep_ignore(self):
        if not os.path.exists(os.path.join(self.proj_dir, ".grepignore")):
            return {self.grep_dir}
        grep_ignore: Set = {self.grep_dir}
        with open(os.path.join(self.proj_dir, ".grepignore"), "r") as file:
            for line in file.readlines():
                grep_ignore.add(os.path.join(self.proj_dir, line.strip()))
        return grep_ignore

    def __initialize_cache_dirs(self) -> None:
        if not os.path.exists(self.grep_dir):
            print(Fore.BLUE + "[NOTIFICATION]: Creating \".grep++\" directory")
            os.makedirs(self.grep_dir)

        if not os.path.exists(self.cache_dir):
            print(Fore.BLUE + "[NOTIFICATION]: Creating \".grep++/object_cache directory\"")
            os.makedirs(self.cache_dir)

        if not os.path.exists(self.obj_store_dir):
            os.makedirs(self.obj_store_dir)
            print(Fore.BLUE + f"[NOTIFICATION]: Creating object store directory \"{self.obj_store_dir}\"")

        return

    def __update_project_objects(self) -> Dict:
        new_obj_index: Dict = {}

        # Update existing objects
        for file_path in self.obj_index:
            obj_path: str = os.path.join(self.obj_store_dir, self.obj_index[file_path])

            try:
                with open(obj_path, "rb") as file:
                    obj: Dict = pickle.load(file)
            except Exception as _:
                print(Fore.YELLOW + f"[WARNING]: \"{obj_path}\" file's object couldn't be loaded. Retokenizing and reindexing")
                obj: Dict = {"size": 0, "sha256": "", "xxhash": "", "path": ""}
            
            indexed: bool = self.__index_object(obj, file_path, obj_path)
            if indexed:
                new_obj_index[file_path] = self.obj_index[file_path]

        # Iterate over directory files and check for new files that need to be indexed
        for dirpath, _, filenames in os.walk(self.proj_dir):
            for name in filenames:
                if not name.endswith(".py"):
                    continue

                file_path: str = os.path.join(dirpath, name)

                ignore: bool = False
                for grep_ignore in self.grep_ignore:
                    if file_path.startswith(grep_ignore):
                        ignore = True
                        break

                if ignore:
                    continue

                if file_path in new_obj_index:
                    continue


                print(Fore.BLUE + f"[NOTIFICATION]: Found new file in project directory \"{file_path}\"")
                file_path_hash: str = self.__calculate_file_path_hash(file_path)
                obj_path: str = os.path.join(self.obj_store_dir, file_path_hash)
                indexed: bool = self.__index_object(None, file_path, obj_path)
                if indexed:
                    new_obj_index[file_path] = file_path_hash

        with open(self.obj_index_path, "w") as file:
            json.dump(new_obj_index, file, indent=1)

        return new_obj_index
            
    def __calculate_file_path_hash(self, file_path: str) -> str:
        return hashlib.sha256(file_path.encode()).hexdigest()

    def __calculate_file_hashes(self, file_contents: str) -> Dict:
        sha256_hash = hashlib.sha256(file_contents.encode()).hexdigest()
        xxhash_hash = xxhash.xxh128(file_contents.encode(), seed=69).hexdigest()

        return {"sha256": sha256_hash, "xxhash": xxhash_hash}

    def __index_object(self, obj: Dict | None, file_path: str, obj_path: str) -> bool:
        try:
            with open(file_path, "r") as file:
                file_contents = file.readlines()
        except Exception as _:
            print(Fore.BLUE + f"[NOTIFICATION]: File \"{file_path}\" doesn't exist or is unreadable. Removing from object store.")

            if os.path.exists(obj_path):
                os.remove(obj_path)

            return False

        file_hashes: Dict = self.__calculate_file_hashes("".join(file_contents))

        if obj is not None and obj["size"] == os.path.getsize(file_path) and obj["sha256"] == file_hashes["sha256"] and obj["xxhash"] == file_hashes["xxhash"]:
            return True


        file_details: Dict = file_hashes
        file_details["size"] = os.path.getsize(file_path)
        file_details["path"] = file_path

        with open(obj_path, "wb") as file:
            pickle.dump(file_details, file)

        if obj is not None:
            self.__send_file_deleted(file_path)
        self.__send_file_updated(file_contents, file_path)

        print(Fore.GREEN + f"[SUCCESS]: Indexed file \"{file_path}\"")

        return True

    def __delete_object(self, file_path: str):
        obj_path: str = os.path.join(self.obj_store_dir, self.obj_index[file_path])
        os.remove(obj_path)
        del self.obj_index[file_path]

        print(f"[SUCCESS]: Deleted indexed object \"{file_path}\"")

        self.__send_file_deleted(file_path)

    def __send_file_updated(self, file_contents: List[str], file_path: str) -> None:
        code_lines: List = []
        code_list: List
        doc_tokens: List
        doc_tokens, code_list = tokenize_lines("".join(file_contents), file_contents)
        for i, elem in enumerate(zip(doc_tokens, code_list)):
            tokens, code = elem
            code_lines.append({
                "tokens": tokens,
                "code": code.strip(),
                "line": i
            })

        try:
            if self.verbose:
                print(Fore.BLUE + "[NOTIFICATION]: Update request data:")
                pprint({
                    "dir": self.proj_dir,
                    "path": file_path,
                    "lines": code_lines
                })
            response: requests.Response = requests.post("http://127.0.0.1:8002/update", json={
                "dir": self.proj_dir,
                "path": file_path,
                "lines": code_lines
            })

            if response.status_code == 200:
                print(Fore.GREEN + f"[SUCCESS]: Tokenized file \"{file_path}\" sent to server")
            else:
                print(Fore.RED + f"[ERROR]: Tokenized file \"{file_path}\" couldn't be sent to server status code: {response.status_code}")
        except Exception as e:
            print(Fore.RED + f"[ERROR]: Request error: {e}")

        return


    def __send_file_deleted(self, file_path: str):
        try:
            if self.verbose:
                print(Fore.BLUE + "[NOTIFICATION]: Delete request data")
                pprint({
                    "dir": self.proj_dir,
                    "path": file_path
                })

            response: requests.Response = requests.post("http://127.0.0.1:8002/delete", json={
                "dir": self.proj_dir,
                "path": file_path
            })

            if response.status_code == 200:
                print(Fore.GREEN + "[SUCCESS]: File \"{file_path}\" sent to server for deletion")
            else:
                print(Fore.RED + f"[ERROR]: File \"{file_path}\" couldn't be sent to server for deletion, status code: {response.status_code}")
        except Exception as e:
            print(Fore.RED + f"[ERROR]: Request error: {e}")

        return


    def on_created(self, event: FileSystemEvent) -> None:
        if not event.is_directory and event.src_path.endswith(".py"):
            file_norm_path: str = os.path.normpath(event.src_path)
            file_path: str = os.path.abspath(file_norm_path)

            ignore: bool = False
            for grep_ignore in self.grep_ignore:
                if file_path.startswith(grep_ignore):
                    ignore = True
                    break
            if ignore:
                return super().on_created(event)

            print(Fore.BLUE + f"[NOTIFICATION]: File created \"{file_path}\"")
            file_path_hash: str = self.__calculate_file_path_hash(file_path)
            obj_path: str = os.path.join(self.obj_store_dir, file_path_hash)
            if self.__index_object(None, file_path, obj_path):
                self.obj_index[file_path] = file_path_hash

        return super().on_created(event)

    def on_deleted(self, event: FileSystemEvent) -> None:
        if not event.is_directory and event.src_path.endswith(".py"):
            file_norm_path: str = os.path.normpath(event.src_path)
            file_path: str = os.path.abspath(file_norm_path)

            ignore: bool = False
            for grep_ignore in self.grep_ignore:
                if file_path.startswith(grep_ignore):
                    ignore = True
                    break
            if ignore:
                return super().on_created(event)

            self.__delete_object(file_path)

        return super().on_created(event)

    def on_modified(self, event: FileSystemEvent) -> None:
        if not event.is_directory and event.src_path.endswith(".py"):
            file_norm_path: str = os.path.normpath(event.src_path)
            file_path: str = os.path.abspath(file_norm_path)

            ignore: bool = False
            for grep_ignore in self.grep_ignore:
                if file_path.startswith(grep_ignore):
                    ignore = True
                    break
            if ignore:
                return super().on_created(event)

            print(Fore.BLUE + f"[NOTIFICATION]: File modified \"{file_path}\"")


            file_path_hash: str = self.__calculate_file_path_hash(file_path)
            obj_path: str = os.path.join(self.obj_store_dir, file_path_hash)
            if self.__index_object({"size": 0, "sha256": "", "xxhash": "", "path": ""}, file_path, obj_path):
                self.obj_index[file_path] = file_path_hash

        return super().on_created(event)

    def handle_exit(self):
        with open(self.obj_index_path, "w") as file:
            json.dump(self.obj_index, file, indent=1)
        print(Fore.GREEN + "[SUCCESS]: Exit handled, indexing saved")

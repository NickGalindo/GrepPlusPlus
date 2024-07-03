from typing import Any, Dict, Set

from colorama import Fore

def printEntities(entities: Set):
    grouped_tities: Dict = {}
    for e in entities:
        tity = e.entity

        if tity.token_dir not in grouped_tities:
            grouped_tities[tity.token_dir] = {}

        if tity.token_path not in grouped_tities[tity.token_dir]:
            grouped_tities[tity.token_dir][tity.token_path] = []

        grouped_tities[tity.token_dir][tity.token_path].append({"line": tity.token_line, "code": tity.token_code})

    for proj_dir in grouped_tities:
        print(Fore.GREEN + f"[PROJECT DIR]: {proj_dir}")

        for file_path in grouped_tities[proj_dir]:
            print("\t", end="")
            print(Fore.YELLOW + f"[FILE PATH]: {file_path}")

            for code_line in grouped_tities[proj_dir][file_path]:
                print("\t\t", end="")
                print(Fore.BLUE + f"[{code_line['line']}]: ", end="")
                print(f"{code_line['code']}")
            
def printQuery(entities: Any):
    grouped_tities: Dict = {}
    for e in entities:
        tity = e

        if tity["token_dir"] not in grouped_tities:
            grouped_tities[tity["token_dir"]] = {}

        if tity["token_path"] not in grouped_tities[tity["token_dir"]]:
            grouped_tities[tity["token_dir"]][tity["token_path"]] = []

        grouped_tities[tity["token_dir"]][tity["token_path"]].append({"line": tity["token_line"], "code": tity["token_code"]})

    for proj_dir in grouped_tities:
        print(Fore.GREEN + f"[PROJECT DIR]: {proj_dir}")

        for file_path in grouped_tities[proj_dir]:
            print("\t", end="")
            print(Fore.YELLOW + f"[FILE PATH]: {file_path}")

            for code_line in grouped_tities[proj_dir][file_path]:
                print("\t\t", end="")
                print(Fore.BLUE + f"[{code_line['line']}]: ", end="")
                print(f"{code_line['code']}")

from pymilvus import Collection, utility

from colorama import Fore

def setupCollection() -> Collection:
    if not utility.has_collection("TOKENS"):
        print(Fore.RED + "[ERROR]: milvus collection not instantiated please initiate vector database before trying to find")
        raise RuntimeError("milvus collection \"TOKENS\" does not exist")
    else:
        col = Collection("TOKENS")

    col.load()

    return col

import argparse
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))
from src.chromadb_client import ChromaClient


def load_from_dir(data_dir, collection='faculty', use_chroma=True):
    docs = []
    for fn in sorted(os.listdir(data_dir)):
        path = os.path.join(data_dir, fn)
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read().strip()
        docs.append({'id': fn, 'text': text, 'name': fn.replace('.txt','')})
    client = ChromaClient(use_chroma=use_chroma)
    client.add_profiles(docs, collection_name=collection)
    store_name = 'chroma' if use_chroma else 'memory'
    print(f'Loaded {len(docs)} profiles into collection "{collection}" using "{store_name}" store')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', default='data/faculty')
    parser.add_argument('--store', choices=['chroma','memory'], default='chroma')
    args = parser.parse_args()
    load_from_dir(args.dir, use_chroma=(args.store == 'chroma'))

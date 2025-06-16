import numpy as np
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load metadata
def load_embeddings():
    path = os.path.join(BASE_DIR, "data/embeddings.npy")
    return np.load(path)

# Load precomputed embeddings
def load_metadata():
    path = os.path.join(BASE_DIR, "data/metadata.json")
    with open(path) as f:
        return json.load(f)

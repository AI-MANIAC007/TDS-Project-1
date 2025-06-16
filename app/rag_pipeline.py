import os
import json
import re
import glob
import numpy as np
from openai import OpenAI
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = OpenAI(
    api_key=os.environ.get("AIPROXY_TOKEN"),
    base_url="https://aiproxy.sanand.workers.dev/openai/v1"
)

CHUNK_SIZE = 500
OVERLAP = 50
EMBED_DIM = 1536

def clean_html(md_text):
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', md_text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'#+ ', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def clean_discourse_html(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    text = soup.get_text(separator=" ").strip()
    text = re.sub(r'\s+', ' ', text)
    return text

def chunk_text(text):
    words = text.split()
    chunks = []
    for i in range(0, len(words), CHUNK_SIZE - OVERLAP):
        chunk = " ".join(words[i:i + CHUNK_SIZE])
        chunks.append(chunk)
    return chunks

def load_course_pages(course_path="app/data/scrape_pages.json"):
    with open(course_path) as f:
        return json.load(f)

def load_discourse_posts(discourse_dir="app/discourse_raw_json/"):
    discourse_pages = []
    for file in glob.glob(os.path.join(discourse_dir, "topic_*.json")):
        with open(file) as f:
            data = json.load(f)
            posts = data.get("post_stream", {}).get("posts", [])
            for post in posts:
                content = clean_discourse_html(post.get("cooked", ""))
                discourse_pages.append({
                    "title": f"Discourse Post by {post.get('username')}",
                    "source": f"https://discourse.onlinedegree.iitm.ac.in{post.get('post_url', '')}",
                    "content": content
                })
    return discourse_pages

def get_embeddings(text_chunks):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text_chunks
    )
    return [np.array(e.embedding, dtype='float32') for e in response.data]

def build_vector_store(course_pages, discourse_pages):
    all_chunks = []
    metadata = []

    for page in course_pages:
        clean_text = clean_html(page['content'])
        chunks = chunk_text(clean_text)
        for chunk in chunks:
            all_chunks.append(chunk)
            metadata.append({
                "title": page["title"],
                "source": page["source"],
                "chunk": chunk,
                "source_type": "course"
            })

    for post in discourse_pages:
        chunks = chunk_text(post['content'])
        for chunk in chunks:
            all_chunks.append(chunk)
            metadata.append({
                "title": post["title"],
                "source": post["source"],
                "chunk": chunk,
                "source_type": "discourse"
            })

    print(f"Total chunks: {len(all_chunks)}")

    batch_size = 1000
    vectors = []
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i + batch_size]
        embeddings = get_embeddings(batch)
        vectors.extend(embeddings)

    vectors = np.array(vectors, dtype='float32')
    np.save("app/data/embeddings.npy", vectors)

    with open("app/data/metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)

    print("✅ Vector store saved.")

if __name__ == "__main__":
    course_pages = load_course_pages()
    discourse_pages = load_discourse_posts()

    print(f"Loaded {len(course_pages)} course pages.")
    print(f"Loaded {len(discourse_pages)} discourse posts.")

    build_vector_store(course_pages, discourse_pages)

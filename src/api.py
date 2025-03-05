import os
import pickle
import pandas as pd
import numpy as np
from scipy.spatial.distance import cosine
from sentence_transformers import SentenceTransformer
from fastapi import FastAPI
from functools import lru_cache
from src.preprocess import preprocess

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "API is running"}


@lru_cache(maxsize=1)
def load_cached_embeddings():
    """Load or compute embeddings and store them in memory for fast retrieval."""
    DATA_FILE = "/shared/data/sample_data.csv"
    EMBEDDINGS_FILE = "/shared/embeddings/embeddings.pkl"
    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

    # Ensure embeddings directory exists
    os.makedirs(os.path.dirname(EMBEDDINGS_FILE), exist_ok=True)

    df = pd.read_csv(DATA_FILE)
    df = preprocess(df)
    embedding_model = SentenceTransformer(MODEL_NAME)

    try:
        with open(EMBEDDINGS_FILE, "rb") as f:
            embeddings_dict = pickle.load(f)

        df["embedding"] = df["product_name"].map(embeddings_dict)

        if df["embedding"].isnull().sum() > 0:
            raise ValueError("Some embeddings are missing, recalculating...")

        print("✅ Loaded embeddings from cache file.")

    except (FileNotFoundError, ValueError, EOFError, pickle.UnpicklingError):
        print("⚠️ Cache file missing or corrupted. Recomputing embeddings...")

        df["embedding"] = df["product_name"].astype(str).apply(lambda x: embedding_model.encode(x, convert_to_numpy=True))
        embeddings_dict = {name: emb.tolist() for name, emb in zip(df["product_name"], df["embedding"])}

        # Ensure dictionary is not empty before saving
        if not embeddings_dict:
            raise RuntimeError("Embeddings dictionary is empty! Check dataset and model output.")

        with open(EMBEDDINGS_FILE, "wb") as f:
            pickle.dump(embeddings_dict, f, protocol=pickle.HIGHEST_PROTOCOL)

        print(f"✅ Computed and saved embeddings to {EMBEDDINGS_FILE}.")

    # Convert embeddings to numpy array for faster computation
    df["embedding"] = df["embedding"].apply(np.array)
    return df


df = load_cached_embeddings()  # Load embeddings once at startup


def get_top_matching_products(customer_id, top_n=5):
    """Retrieve the top N product recommendations for a given customer ID."""
    customer_products = df[df["customer_id"] == customer_id]
    if customer_products.empty:
        return {"error": "No products found for this customer"}

    customer_embeddings = np.vstack(customer_products["embedding"].values)
    product_scores = {}

    # Precompute all similarities in one operation
    for _, row in df.iterrows():
        product_name = row["product_name"]
        product_embedding = row["embedding"]
        similarities = 1 - np.dot(customer_embeddings, product_embedding) / (
            np.linalg.norm(customer_embeddings, axis=1) * np.linalg.norm(product_embedding)
        )
        avg_score = float(np.mean(1 - similarities))  # Convert cosine distance back to similarity

        product_scores[product_name] = avg_score

    # Get top N recommendations
    all_products = sorted(product_scores.items(), key=lambda x: x[1], reverse=True)
    top_matches = [{"product_name": name, "average_score": float(score)} for name, score in all_products[:top_n]]
    recall_count = int(sum(1 for _, score in all_products if score > 0.6))

    return top_matches, recall_count


@app.get("/recommend/")
def recommend_products(customer_id: int, top_n: int = 5):
    """Endpoint to retrieve top N recommendations for a customer."""
    top_matches, recall_count = get_top_matching_products(customer_id, top_n)
    if isinstance(top_matches, dict) and "error" in top_matches:
        return top_matches

    return {
        "customer_id": int(customer_id),
        "top_matches": top_matches,
        "recall_count": recall_count
    }

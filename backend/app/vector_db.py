import os
import threading
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone


# ---------------- CPU tuning ----------------

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import torch

torch.set_num_threads(
    int(os.environ.get("OMP_NUM_THREADS", "2"))
)


# ---------------- Embedding Model ----------------

print("Loading embedding model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2",
    device="cpu"
)

model.eval()

print("Embedding model loaded")


_encode_lock = threading.Lock()


def _encode(texts):

    with _encode_lock:

        return model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
            batch_size=32
        )


# ---------------- Pinecone ----------------


print("Connecting Pinecone...")


pc = Pinecone(
    api_key=os.environ["PINECONE_API_KEY"]
)


index_name = os.environ["PINECONE_INDEX_NAME"]


# IMPORTANT:
# Do not create index here.
# Create it once from Pinecone dashboard.

index = pc.Index(index_name)


print("Pinecone connected")


# ---------------- Store ----------------


def store_chunks(chunks, embeddings, file_name):

    vectors = []


    for i, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):

        vectors.append(
            {
                "id": f"{file_name}_{i}",

                "values": embedding.tolist(),

                "metadata":
                {
                    "file_name": file_name,
                    "text": chunk
                }
            }
        )


    index.upsert(
        vectors=vectors
    )



# ---------------- Search ----------------


def search_chunks(
        query,
        file_names,
        k=4
):

    query_embedding = _encode(
        [query]
    )[0].tolist()



    query_filter = None


    if file_names:

        if len(file_names) == 1:

            query_filter = {
                "file_name": file_names[0]
            }

        else:

            query_filter = {
                "file_name":
                {
                    "$in": file_names
                }
            }



    result = index.query(

        vector=query_embedding,

        top_k=k,

        include_metadata=True,

        filter=query_filter
    )


    documents=[]


    for item in result["matches"]:

        documents.append(
            item["metadata"]["text"]
        )


    return documents



# ---------------- Delete ----------------


def delete_pdf(file_name):

    index.delete(
        filter={
            "file_name": file_name
        }
    )
import json
import os
import threading
from pathlib import Path

try:
    from sentence_transformers import SentenceTransformer
except Exception as exc:  # pragma: no cover - environment dependent
    SentenceTransformer = None
    _MODEL_ERROR = exc
else:
    _MODEL_ERROR = None

try:
    from pinecone import Pinecone
except Exception as exc:  # pragma: no cover - environment dependent
    Pinecone = None
    _PINECONE_ERROR = exc
else:
    _PINECONE_ERROR = None


os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

try:
    import torch
except Exception:  # pragma: no cover - torch may be unavailable
    torch = None
else:
    torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "2")))


_encode_lock = threading.Lock()
_local_index_path = Path(os.environ.get("VECTOR_DB_PATH", "uploads/.vector_index.json"))
_local_index_path.parent.mkdir(parents=True, exist_ok=True)

_model = None
_index = None


def _get_model():
    global _model
    if _model is None:
        if SentenceTransformer is None:
            raise RuntimeError(f"SentenceTransformer is unavailable: {_MODEL_ERROR}")
        _model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
        _model.eval()
    return _model


def _encode(texts):
    with _encode_lock:
        model = _get_model()
        return model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
            batch_size=32,
        )


def _get_index():
    global _index
    if _index is not None:
        return _index

    if Pinecone is None:
        return None

    api_key = os.environ.get("PINECONE_API_KEY")
    index_name = os.environ.get("PINECONE_INDEX_NAME")
    if not api_key or not index_name:
        return None

    try:
        pc = Pinecone(api_key=api_key)
        _index = pc.Index(index_name)
    except Exception as exc:
        print(f"Pinecone connection failed: {exc}")
        return None

    return _index


def _load_local_index():
    if not _local_index_path.exists():
        return {}
    try:
        return json.loads(_local_index_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_local_index(data):
    _local_index_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def store_chunks(chunks, embeddings, file_name):
    if not chunks:
        return

    index = _get_index()
    if index is not None and embeddings:
        vectors = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            vectors.append(
                {
                    "id": f"{file_name}_{i}",
                    "values": embedding.tolist(),
                    "metadata": {"file_name": file_name, "text": chunk},
                }
            )

        try:
            index.upsert(vectors=vectors)
            return
        except Exception as exc:
            print(f"Pinecone upsert failed, falling back to local storage: {exc}")

    data = _load_local_index()
    data[file_name] = {"file_name": file_name, "chunks": chunks}
    _save_local_index(data)


def search_chunks(query, file_names, k=4):
    query_text = (query or "").strip().lower()
    if not query_text:
        return []

    index = _get_index()
    if index is not None:
        try:
            query_embedding = _encode([query])[0].tolist()
            query_filter = None
            if file_names:
                if len(file_names) == 1:
                    query_filter = {"file_name": file_names[0]}
                else:
                    query_filter = {"file_name": {"$in": file_names}}

            result = index.query(
                vector=query_embedding,
                top_k=k,
                include_metadata=True,
                filter=query_filter,
            )
            documents = []
            for item in result.get("matches", []):
                documents.append(item["metadata"]["text"])
            if documents:
                return documents
        except Exception as exc:
            print(f"Pinecone query failed, using local fallback: {exc}")

    data = _load_local_index()
    records = list(data.values())
    if file_names:
        allowed = set(file_names)
        records = [record for record in records if record.get("file_name") in allowed]

    documents = []
    for record in records:
        for chunk in record.get("chunks", []):
            if query_text in chunk.lower():
                documents.append(chunk)
                if len(documents) >= k:
                    break
        if len(documents) >= k:
            break

    return documents


def delete_pdf(file_name):
    index = _get_index()
    if index is not None:
        try:
            index.delete(filter={"file_name": file_name})
        except Exception as exc:
            print(f"Pinecone delete failed: {exc}")

    data = _load_local_index()
    data.pop(file_name, None)
    _save_local_index(data)
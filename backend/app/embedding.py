try:
    from sentence_transformers import SentenceTransformer
except Exception as exc:  # pragma: no cover - depends on environment
    SentenceTransformer = None
    _MODEL_ERROR = exc
else:
    _MODEL_ERROR = None

_model = None


def _get_model():
    global _model
    if _model is None:
        if SentenceTransformer is None:
            raise RuntimeError(f"SentenceTransformer is unavailable: {_MODEL_ERROR}")
        _model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
        _model.eval()
    return _model


def create_embeddings(chunks):
    if not chunks:
        return []

    try:
        model = _get_model()
        return model.encode(
            chunks,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
            batch_size=32,
        )
    except Exception as exc:
        print(f"Embedding generation failed: {exc}")
        return []
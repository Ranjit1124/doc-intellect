FROM python:3.10-slim


# Install system dependencies
RUN apt-get update && \
    apt-get install -y curl zstd && \
    rm -rf /var/lib/apt/lists/*


# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh


# Environment configuration
ENV HOME=/code
ENV OLLAMA_NUM_PARALLEL=1
ENV OLLAMA_NUM_THREAD=2
ENV OLLAMA_KEEP_ALIVE=30m
ENV OLLAMA_MODELS=/code/.ollama/models

# HuggingFace cache
ENV HF_HOME=/code/.cache/huggingface


WORKDIR /code


# Create user
RUN useradd -m -u 1000 user


# Copy requirements
COPY --chown=user:user requirements.txt /code/requirements.txt


# Install Python packages
RUN pip install --no-cache-dir --upgrade -r requirements.txt


# Copy backend application
COPY --chown=user:user backend /code/backend


# Download embedding model during build
RUN mkdir -p /code/.cache/huggingface && \
    python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"


# Create Ollama directories
RUN mkdir -p /code/.ollama/models /code/uploads /code/.cache && \
    chmod -R 777 /code/.ollama /code/uploads /code/.cache


# Download Ollama model during build
RUN ollama serve > /tmp/ollama-build.log 2>&1 & \
    OLLAMA_PID=$! && \
    sleep 5 && \
    ollama pull qwen2.5:0.5b && \
    kill $OLLAMA_PID && \
    wait $OLLAMA_PID 2>/dev/null || true


USER user


EXPOSE 7860


# Runtime startup
CMD ollama serve > /tmp/ollama-runtime.log 2>&1 & \
    for i in $(seq 1 30); do \
        curl -s http://localhost:11434/api/tags > /dev/null && break; \
        echo "Waiting for Ollama... ($i)"; \
        sleep 2; \
    done && \
    cd /code/backend && \
    uvicorn app.main:app --host 0.0.0.0 --port 7860
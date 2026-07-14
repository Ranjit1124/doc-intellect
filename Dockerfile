FROM python:3.10-slim


# Environment configuration
ENV HOME=/code

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


# Create app directories
RUN mkdir -p /code/uploads /code/.cache && \
    chmod -R 777 /code/uploads /code/.cache


USER user


EXPOSE 7860


# Runtime startup
CMD cd /code/backend && \
    uvicorn app.main:app --host 0.0.0.0 --port 7860
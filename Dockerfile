FROM python:3.12-slim

WORKDIR /app

RUN useradd --create-home appuser

COPY requirements.txt .

# Render's free tier is CPU-only. Installing the CPU-only torch wheel first
# (instead of letting sentence-transformers pull the default CUDA build)
# saves ~2GB of unused NVIDIA dependencies and a much slower build/deploy.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY data/ data/
RUN chown -R appuser:appuser /app

USER appuser

# Bake the embedding model into the image (cached under appuser's home) at
# build time so cold starts (the free Render tier spins the container down
# after 15min idle) don't need to hit the Hugging Face Hub before the API
# can serve a request.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
RUN python -c "from sentence_transformers import CrossEncoder; CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"

EXPOSE 8000
ENV PORT=8000

CMD ["sh", "-c", "uvicorn src.api.app:app --host 0.0.0.0 --port ${PORT}"]

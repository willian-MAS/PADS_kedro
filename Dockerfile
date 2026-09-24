FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

WORKDIR /app

# dependencias primeiro, para aproveitar o cache
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

COPY conf/ conf/
COPY src/ src/
COPY data/01_raw/ data/01_raw/

RUN mkdir -p data/02_intermediate data/03_primary data/04_feature \
    data/05_model_input data/06_models data/07_model_output \
    data/08_reporting data/tmp

RUN uv sync --frozen --no-dev

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

CMD ["uv", "run", "--frozen", "--no-dev", "uvicorn", "diabetes.api:app", "--host", "0.0.0.0", "--port", "8000"]

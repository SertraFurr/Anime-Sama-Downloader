FROM ghcr.io/astral-sh/uv:python3.14-alpine
LABEL authors="flastar"

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-cache

COPY . .

ENV PYTHONPATH="/app/src:/app/gui"

CMD ["uv", "run", "-m", "gui"]

FROM python:3.13-alpine

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app

# Copy the application into the container.
COPY . .

# Install the application dependencies.
RUN uv sync --frozen --no-cache 

RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

CMD ["uv", "run", "main.py"]
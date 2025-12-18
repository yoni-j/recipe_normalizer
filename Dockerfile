FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ src/

# Install dependencies using uv
RUN uv pip install --system .

# Create directories for input/output
RUN mkdir -p /data/input /data/output

# Set entrypoint
ENTRYPOINT ["recipe-normalizer"]

# Default command shows help
CMD ["--help"]
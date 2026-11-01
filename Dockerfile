FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml README.md ./
COPY sockboi ./sockboi
COPY agent ./agent
COPY skills ./skills
COPY mcp ./mcp
COPY docs ./docs
COPY README_TH.md ./README_TH.md
RUN pip install --no-cache-dir .
USER 10001
EXPOSE 8000
CMD ["uvicorn", "sockboi.main:app", "--host", "0.0.0.0", "--port", "8000"]

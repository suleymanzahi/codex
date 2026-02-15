FROM python:latest

WORKDIR /app
# Install libseccomp2 and development headers

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libseccomp2 \
    libseccomp-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install pyseccomp
RUN pip install -r requirements.txt --no-cache-dir

COPY . .

# Default command
CMD ["python", "worker.py"]
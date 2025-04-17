FROM python:3.10-alpine

WORKDIR /app

# Install build dependencies if needed
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    python3-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Remove build dependencies to keep image small
RUN apk del .build-deps

COPY . .

CMD ["python", "terabox.py"]

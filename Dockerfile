FROM python:3.10-alpine

WORKDIR /app

RUN apk add --no-cache \
    git gcc musl-dev python3-dev libffi-dev openssl-dev \
    aria2 curl ffmpeg

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "start.sh"]

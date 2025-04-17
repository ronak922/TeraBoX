FROM python:3.10-alpine

WORKDIR /app

# Install git and build dependencies
RUN apk add --no-cache git gcc musl-dev python3-dev libffi-dev openssl-dev

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Command to run the application
CMD ["python", "terabox.py"]
